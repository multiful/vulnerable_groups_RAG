# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: 청킹 품질 검증 — answerability, redundancy, cert_id 해결률, 표 헤더 보존
"""
check_chunk_quality(chunks, config) → QualityReport

answerability는 LLM 호출 없이 휴리스틱으로 판정:
    1. 최소 토큰 수 충족 여부 (>= config.min_tokens)
    2. 문장이 완결된 형태인지 (문장 종결 부호 포함 또는 표/목록)
    3. 대명사만으로 시작하지 않는지

목표:
    answerability_pass_rate >= 0.60
    redundancy_rate         <= 0.05
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..chunk.chunk_schema import ChunkConfig, ChunkRecord
from ..chunk.token_utils import count_tokens


@dataclass
class QualityReport:
    """청킹 품질 보고서."""

    total_chunks: int
    answerability_pass_rate: float
    """답변 가능한 청크 비율. 목표: >= 0.60"""

    redundancy_rate: float
    """중복 청크 비율 (text 해시 기준). 목표: <= 0.05"""

    cert_id_resolved_rate: float
    """MULTI/UNKNOWN이 아닌 cert_id 해결 비율."""

    table_header_preserved: bool
    """표 청크 중 헤더 구분선이 있는 비율 >= 0.9."""

    flags: list[str] = field(default_factory=list)
    """품질 경고 플래그 목록."""

    def is_acceptable(self) -> bool:
        """최소 품질 기준 통과 여부."""
        return (
            self.answerability_pass_rate >= 0.60
            and self.redundancy_rate <= 0.05
        )

    def summary(self) -> str:
        status = "PASS" if self.is_acceptable() else "FAIL"
        return (
            f"[{status}] total={self.total_chunks} "
            f"answerability={self.answerability_pass_rate:.1%} "
            f"redundancy={self.redundancy_rate:.1%} "
            f"cert_resolved={self.cert_id_resolved_rate:.1%} "
            f"table_header={'OK' if self.table_header_preserved else 'LOW'}"
        )


def check_chunk_quality(
    chunks: list[ChunkRecord],
    config: ChunkConfig,
) -> QualityReport:
    """청크 목록의 품질을 검증하고 QualityReport를 반환한다."""
    if not chunks:
        return QualityReport(
            total_chunks=0,
            answerability_pass_rate=0.0,
            redundancy_rate=0.0,
            cert_id_resolved_rate=0.0,
            table_header_preserved=True,
            flags=["no_chunks_generated"],
        )

    total = len(chunks)
    flags: list[str] = []

    # 1. answerability
    answerable = sum(1 for c in chunks if _is_answerable(c.text, config))
    answerability_rate = answerable / total

    # 2. redundancy (text 기준 중복)
    seen_texts: set[str] = set()
    duplicates = 0
    for c in chunks:
        key = c.text.strip()
        if key in seen_texts:
            duplicates += 1
        else:
            seen_texts.add(key)
    redundancy_rate = duplicates / total

    # 3. cert_id 해결률
    resolved = sum(
        1 for c in chunks
        if c.metadata.cert_id not in ("UNKNOWN", "MULTI", "")
    )
    cert_resolved_rate = resolved / total

    # 4. 표 헤더 보존
    table_chunks = [c for c in chunks if _is_table_chunk(c.text)]
    if table_chunks:
        header_ok = sum(1 for c in table_chunks if _has_table_header(c.text))
        table_header_preserved = (header_ok / len(table_chunks)) >= 0.9
    else:
        table_header_preserved = True

    # 플래그 추가
    if answerability_rate < 0.60:
        flags.append(f"low_answerability:{answerability_rate:.2f}")
    if redundancy_rate > 0.05:
        flags.append(f"high_redundancy:{redundancy_rate:.2f}")
    if cert_resolved_rate < 0.5:
        flags.append(f"low_cert_resolution:{cert_resolved_rate:.2f}")
    if not table_header_preserved:
        flags.append("table_header_preservation_low")

    return QualityReport(
        total_chunks=total,
        answerability_pass_rate=answerability_rate,
        redundancy_rate=redundancy_rate,
        cert_id_resolved_rate=cert_resolved_rate,
        table_header_preserved=table_header_preserved,
        flags=flags,
    )


# ---------------------------------------------------------------------------
# 휴리스틱 판정
# ---------------------------------------------------------------------------

# 한국어 대명사 시작 패턴
_PRONOUN_START_RE = re.compile(r"^(이|그|저|여기|거기|저기|이것|그것|저것|이런|그런)\s")
# 문장 종결 부호
_SENTENCE_END_RE = re.compile(r"[.!?。다임함\|]")


def _is_answerable(text: str, config: ChunkConfig) -> bool:
    """청크가 답변 가능한지 휴리스틱 판정."""
    # 1. 최소 토큰 수
    if count_tokens(text) < config.min_tokens:
        return False

    # 2. 대명사만으로 시작하는 경우 제외
    stripped = text.strip()
    if _PRONOUN_START_RE.match(stripped):
        return False

    # 3. 문장 종결 부호 또는 표/목록 포함
    if _SENTENCE_END_RE.search(stripped):
        return True

    # 표 또는 목록이면 허용
    if stripped.startswith("|") or re.match(r"^\s*[-*•\d]", stripped):
        return True

    return False


def _is_table_chunk(text: str) -> bool:
    """표 청크 여부 간단 판정."""
    return bool(re.search(r"\|.+\|", text))


def _has_table_header(text: str) -> bool:
    """Markdown 표 헤더 구분선 존재 여부."""
    return bool(re.search(r"\|[-: ]+\|", text))

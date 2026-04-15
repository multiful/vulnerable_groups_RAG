# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: 청크 데이터클래스 — chunk_loader.py JSONL 계약과 완전 호환
"""
ChunkRecord: 청크 1개의 완전한 표현.
직렬화 결과가 기존 backend/rag/ingest/chunk_loader.py 입력 형식과 일치해야 한다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChunkMetadata:
    """청크 메타데이터. Evidence 검색 필터 및 provenance 추적에 사용."""

    cert_id: str
    """Evidence 검색 @> 필터용 필수 필드.
    cert_master.csv의 cert_id 또는 'MULTI'(종합문서) / 'UNKNOWN'(미매칭)."""

    source_type: str
    """'pdf' | 'html'"""

    doc_type: str
    """'official_guide' | 'faq' | 'schedule' | 'statistics' | 'announcement'"""

    doc_id: str
    chunk_id: str

    chunk_hash: str
    """sha256:hex — 증분 임베딩 판정용."""

    section_path: list[str] = field(default_factory=list)
    source_loc: str = ""
    doc_version: str = "v1"
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    domain_sub_label: Optional[str] = None
    domain_top_label: Optional[str] = None
    risk_stage_id: Optional[str] = None
    chunk_seq: int = 0


@dataclass
class ChunkRecord:
    """청크 1개의 완전한 표현. JSONL 직렬화 대상."""

    chunk_id: str
    doc_id: str
    text: str
    metadata: ChunkMetadata


@dataclass
class ChunkConfig:
    """청킹 파라미터. 변경 시 chunk_version을 올려야 한다."""

    max_tokens: int = 512
    """tiktoken cl100k_base 기준 최대 토큰 수."""

    overlap_tokens: int = 64
    """청크 간 overlap 토큰 수. 표/일정 문서는 0으로 오버라이드."""

    min_tokens: int = 20
    """이 미만은 청크로 생성하지 않는다."""

    doc_type: str = "official_guide"
    """청킹 전략 결정에 사용."""

    doc_version: str = "v1"
    valid_from: Optional[str] = None

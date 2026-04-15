# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: cert_id 매핑 — cert_master.csv 기반 3단계 폴백, MULTI/UNKNOWN 센티넬
"""
map_cert_ids(): 청크 목록의 cert_id를 cert_master.csv 기반으로 해결한다.

매핑 전략 (3단계 폴백):
    1. canonical_name 완전 일치
    2. normalized_key 일치 (공백/괄호 제거 + 소문자)
    3. aliases 컬럼 역참조

실패 시:
    - statistics/schedule 문서 → cert_id = "MULTI"
    - 기타 → cert_id = "UNKNOWN" + quality_flag 추가

doc_type = 'official_guide' 인 경우:
    section_path 최상위 섹션명으로 section-level 매핑을 시도하고 하위 청크에 전파한다.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Optional

from .chunk_schema import ChunkRecord


# ---------------------------------------------------------------------------
# 공개 API
# ---------------------------------------------------------------------------

def load_cert_lookup(cert_master_path: Path) -> dict:
    """cert_master.csv를 읽어 검색용 딕셔너리를 반환한다.

    Returns:
        {
            "by_canonical": {canonical_name: cert_id},
            "by_normalized": {normalized_key: cert_id},
            "by_alias": {alias_text: cert_id},
        }
    """
    lookup: dict = {
        "by_canonical": {},
        "by_normalized": {},
        "by_alias": {},
    }

    if not cert_master_path.exists():
        return lookup

    with open(cert_master_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cert_id = row.get("cert_id", "").strip()
            if not cert_id:
                continue

            canonical = row.get("canonical_name", "").strip()
            if canonical:
                lookup["by_canonical"][canonical] = cert_id

            norm_key = row.get("normalized_key", "").strip()
            if norm_key:
                lookup["by_normalized"][norm_key] = cert_id

            aliases_raw = row.get("aliases", "").strip()
            if aliases_raw:
                for alias in _split_aliases(aliases_raw):
                    alias = alias.strip()
                    if alias:
                        lookup["by_alias"][alias] = cert_id

    return lookup


def map_cert_ids(
    chunks: list[ChunkRecord],
    lookup: dict,
    doc_type: str,
    *,
    quality_flags: Optional[list[str]] = None,
) -> list[ChunkRecord]:
    """청크 목록의 cert_id를 lookup 기반으로 해결하고 갱신된 목록을 반환한다.

    doc_type이 'statistics' 또는 'schedule'이면 미해결 cert_id를 "MULTI"로 설정.
    그 외에는 "UNKNOWN"으로 설정하고 quality_flags에 추가.
    """
    multi_doc = doc_type in ("statistics", "schedule")

    # doc_type == 'official_guide': section_path 최상위로 섹션-레벨 매핑 시도
    # 섹션명 → cert_id 캐시
    section_cert_cache: dict[str, Optional[str]] = {}

    updated: list[ChunkRecord] = []
    for chunk in chunks:
        resolved = _resolve_cert_id(chunk, lookup, section_cert_cache)
        if resolved:
            chunk.metadata.cert_id = resolved
        else:
            if multi_doc:
                chunk.metadata.cert_id = "MULTI"
            else:
                chunk.metadata.cert_id = "UNKNOWN"
                if quality_flags is not None and "unresolved_cert_id" not in quality_flags:
                    quality_flags.append("unresolved_cert_id")
        updated.append(chunk)

    return updated


# ---------------------------------------------------------------------------
# 내부 유틸
# ---------------------------------------------------------------------------

def _resolve_cert_id(
    chunk: ChunkRecord,
    lookup: dict,
    section_cache: dict[str, Optional[str]],
) -> Optional[str]:
    """3단계 폴백으로 cert_id 해결."""
    # 섹션 경로 기반 캐시 확인
    section_key = " > ".join(chunk.metadata.section_path) if chunk.metadata.section_path else ""
    if section_key and section_key in section_cache:
        cached = section_cache[section_key]
        if cached:
            return cached

    # 텍스트에서 자격증명 후보 추출
    candidates = _extract_cert_mentions(chunk.text)

    # 단계 1: canonical_name
    for name in candidates:
        if name in lookup["by_canonical"]:
            result = lookup["by_canonical"][name]
            if section_key:
                section_cache[section_key] = result
            return result

    # 단계 2: normalized_key
    for name in candidates:
        norm = _normalize_cert_name(name)
        if norm in lookup["by_normalized"]:
            result = lookup["by_normalized"][norm]
            if section_key:
                section_cache[section_key] = result
            return result

    # 단계 3: aliases
    for name in candidates:
        if name in lookup["by_alias"]:
            result = lookup["by_alias"][name]
            if section_key:
                section_cache[section_key] = result
            return result
        norm = _normalize_cert_name(name)
        if norm in lookup["by_alias"]:
            result = lookup["by_alias"][norm]
            if section_key:
                section_cache[section_key] = result
            return result

    # section_path 최상위로 추가 시도
    if chunk.metadata.section_path:
        top_section = chunk.metadata.section_path[0]
        for lookup_dict in [lookup["by_canonical"], lookup["by_normalized"], lookup["by_alias"]]:
            if top_section in lookup_dict:
                result = lookup_dict[top_section]
                if section_key:
                    section_cache[section_key] = result
                return result
        norm = _normalize_cert_name(top_section)
        for lookup_dict in [lookup["by_normalized"], lookup["by_alias"]]:
            if norm in lookup_dict:
                result = lookup_dict[norm]
                if section_key:
                    section_cache[section_key] = result
                return result

    if section_key:
        section_cache[section_key] = None
    return None


def _extract_cert_mentions(text: str) -> list[str]:
    """텍스트에서 자격증명 후보를 추출한다.

    '자격증', '기사', '기능사', '기술사', '산업기사', '관리사' 등 키워드 앞 명사구 추출.
    """
    # 자격증 유형 키워드
    cert_keywords = r"(기술사|기사|산업기사|기능사|관리사|기능장|자격|정보처리|전문사)"
    # N어절 + 키워드 패턴
    pattern = re.compile(r"[\w가-힣]{2,20}" + cert_keywords + r"[\w가-힣]*")
    return list(dict.fromkeys(pattern.findall(text)))  # 순서 유지 중복 제거


def _normalize_cert_name(name: str) -> str:
    """자격증명 정규화: 공백·괄호·특수문자 제거 + 소문자."""
    return re.sub(r"[\s\(\)\[\]\-·/]", "", name).lower()


def _split_aliases(aliases_raw: str) -> list[str]:
    """aliases 컬럼 값을 분리. 쉼표 또는 파이프 구분자 지원."""
    if "|" in aliases_raw:
        return aliases_raw.split("|")
    return aliases_raw.split(",")

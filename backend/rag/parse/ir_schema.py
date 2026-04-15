# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: Parse IR 데이터클래스 — RAG_PIPELINE.md §6.7 최소 계약 준수
"""
ParseIR: PDF 파서 출력 중간 표현 (Intermediate Representation)
ChunkBuilder의 입력으로만 사용한다. 추천 계산에 쓰지 않는다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParseBlock:
    """Parse IR의 기본 단위 블록."""

    block_id: str
    """동일 parse_hash 내에서 안정적인 블록 식별자."""

    block_type: str
    """heading | paragraph | list | table | other"""

    text: str
    """청킹 대상 정규화 텍스트. 표는 Markdown 표현으로 통일."""

    reading_order_index: int
    """다단·재배열 시 원문 순서 복원용 인덱스."""

    source_loc: str
    """원문 위치. 예: 'page:3'"""

    heading_level: Optional[int] = None
    """제목 단계. heading 타입이 아닌 경우 None."""

    section_path: list[str] = field(default_factory=list)
    """상위 heading 경로. 예: ['시험 개요', '응시 자격']"""


@dataclass
class ParseIR:
    """PDF 1개 파싱 결과 중간 표현."""

    doc_id: str
    """DATA_SCHEMA.md SourceDocument와 동일 식별자 체계."""

    source_path: str
    """원본 PDF 절대 경로."""

    file_hash: str
    """원본 파일 sha256. 형식: 'sha256:hex'"""

    parse_hash: str
    """blocks 직렬화 기준 sha256. 증분 처리 판정용."""

    parser_used: str
    """실제 사용된 파서. 'pymupdf4llm' | 'pdfplumber' | 'ocr_fallback'"""

    page_count: int

    blocks: list[ParseBlock] = field(default_factory=list)

    parse_quality_flags: list[str] = field(default_factory=list)
    """파싱 품질 경고 플래그. 예: ['table_preservation_low', 'scan_pages_detected']"""

    parsed_at: str = ""
    """ISO 8601 datetime 문자열."""

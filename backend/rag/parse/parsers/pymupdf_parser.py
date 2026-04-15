# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: PyMuPDF 직접 기반 텍스트 중심 PDF 파서 (pymupdf4llm ONNX 우회)
"""
born-digital, 줄글 중심 PDF에 사용하는 주 파서.

pymupdf4llm은 내부 ONNX 레이아웃 모델이 onnxruntime 버전 불일치로 실패하므로
pymupdf (fitz)의 get_text("dict")를 직접 사용한다.

블록 분류:
    - span 크기 기준 heading 판정 (페이지 최대 폰트 크기 대비)
    - 표는 pdfplumber_parser가 담당. pymupdf 경로에서는 표 감지를 생략하고 paragraph로 처리.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import pymupdf  # fitz

from ..ir_schema import ParseBlock, ParseIR
from ..profiler import PdfProfile
from ..cleanup import (
    assign_section_paths,
    compute_parse_hash,
    remove_boilerplate,
    restore_reading_order,
)

# 폰트 크기 비율 기준: page_max_font * HEADING_RATIO 이상이면 heading으로 간주
_HEADING_RATIO = 0.85
# 절대 최소 폰트 크기: 이 이하는 주석/캡션으로 간주해 skip 가능
_MIN_FONT_SIZE = 6.0


def parse_with_pymupdf(path: Path, profile: PdfProfile) -> ParseIR:
    """pymupdf (fitz)로 PDF를 파싱하여 ParseIR 반환.

    pymupdf4llm 대신 fitz.get_text('dict')를 직접 사용한다.
    표 감지는 하지 않는다 (표 중심 문서는 pdfplumber_parser가 처리).
    """
    path = Path(path)
    blocks: list[ParseBlock] = []
    idx = 0

    doc = pymupdf.open(str(path))
    try:
        for page_num, page in enumerate(doc, start=1):
            page_blocks, idx = _extract_page_blocks(page, page_num, idx)
            blocks.extend(page_blocks)
    finally:
        doc.close()

    blocks = remove_boilerplate(blocks)
    blocks = restore_reading_order(blocks)
    blocks = assign_section_paths(blocks)

    parse_hash = compute_parse_hash(blocks)

    flags: list[str] = []
    if profile.multi_column:
        flags.append("multi_column_detected")

    return ParseIR(
        doc_id=profile.doc_id,
        source_path=str(path),
        file_hash=profile.file_hash,
        parse_hash=parse_hash,
        parser_used="pymupdf",
        page_count=profile.page_count,
        blocks=blocks,
        parse_quality_flags=flags,
        parsed_at=datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# 내부 유틸
# ---------------------------------------------------------------------------

def _extract_page_blocks(
    page, page_num: int, start_idx: int
) -> tuple[list[ParseBlock], int]:
    """단일 페이지를 fitz dict 블록으로 분석하여 ParseBlock 목록으로 변환."""
    blocks: list[ParseBlock] = []
    idx = start_idx

    # 페이지 최대 폰트 크기 계산 (heading 판정 기준)
    max_font_size = _get_max_font_size(page)

    raw_blocks = page.get_text("dict", flags=pymupdf.TEXT_PRESERVE_LIGATURES)["blocks"]

    # 연속 paragraph 버퍼
    para_buffer: list[str] = []

    def flush_para():
        nonlocal idx
        text = "\n".join(para_buffer).strip()
        if text and len(text) > 3:
            blocks.append(ParseBlock(
                block_id=f"b{idx:05d}",
                block_type="paragraph",
                text=text,
                reading_order_index=idx,
                source_loc=f"page:{page_num}",
            ))
            idx += 1
        para_buffer.clear()

    for raw in raw_blocks:
        # 이미지 블록 (type=1) 스킵
        if raw.get("type", 0) == 1:
            continue

        lines_data = raw.get("lines", [])
        block_text_parts: list[str] = []
        block_max_size = 0.0
        is_bold_dominant = False
        bold_count = 0
        span_count = 0

        for line in lines_data:
            line_parts: list[str] = []
            for span in line.get("spans", []):
                t = span.get("text", "").strip()
                if not t:
                    continue
                size = span.get("size", 0.0)
                flags = span.get("flags", 0)
                is_bold = bool(flags & 16)  # bold bit
                if size > _MIN_FONT_SIZE:
                    line_parts.append(t)
                    if size > block_max_size:
                        block_max_size = size
                    if is_bold:
                        bold_count += 1
                    span_count += 1
            if line_parts:
                block_text_parts.append(" ".join(line_parts))

        block_text = "\n".join(block_text_parts).strip()
        if not block_text or len(block_text) <= 3:
            continue

        if span_count > 0:
            is_bold_dominant = bold_count / span_count >= 0.6

        # Heading 판정: 폰트 크기가 페이지 최대 크기의 HEADING_RATIO 이상이거나, bold 단일 행
        is_heading = (
            max_font_size > 0
            and block_max_size >= max_font_size * _HEADING_RATIO
            and "\n" not in block_text  # 단일 행
        ) or (
            is_bold_dominant
            and "\n" not in block_text
            and len(block_text) <= 80  # 짧은 bold 텍스트
        )

        if is_heading:
            flush_para()
            # heading level: 크기 비율 기반 1~3 추정
            level = _estimate_heading_level(block_max_size, max_font_size)
            blocks.append(ParseBlock(
                block_id=f"b{idx:05d}",
                block_type="heading",
                text=block_text,
                reading_order_index=idx,
                heading_level=level,
                source_loc=f"page:{page_num}",
            ))
            idx += 1
        else:
            para_buffer.append(block_text)

    flush_para()
    return blocks, idx


def _get_max_font_size(page) -> float:
    """페이지 내 최대 폰트 크기를 반환한다."""
    max_size = 0.0
    raw_blocks = page.get_text("dict", flags=0)["blocks"]
    for raw in raw_blocks:
        if raw.get("type", 0) == 1:
            continue
        for line in raw.get("lines", []):
            for span in line.get("spans", []):
                size = span.get("size", 0.0)
                if size > max_size:
                    max_size = size
    return max_size


def _estimate_heading_level(font_size: float, max_font_size: float) -> int:
    """폰트 크기 비율로 heading 레벨(1~3)을 추정한다."""
    if max_font_size <= 0:
        return 2
    ratio = font_size / max_font_size
    if ratio >= 0.98:
        return 1
    if ratio >= 0.90:
        return 2
    return 3

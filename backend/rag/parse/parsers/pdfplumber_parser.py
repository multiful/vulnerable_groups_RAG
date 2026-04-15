# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: pdfplumber 기반 표 중심 PDF 파서
"""
table_count >= TABLE_COUNT_THRESHOLD 인 문서에 사용.
pdfplumber로 표를 정확히 추출하고, 비표 텍스트는 paragraph/heading으로 분류한다.

표 보존 정확도가 90% 미만이면 parse_quality_flags에 'table_preservation_low' 추가.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pdfplumber

from ..ir_schema import ParseBlock, ParseIR
from ..profiler import PdfProfile
from ..cleanup import (
    assign_section_paths,
    compute_parse_hash,
    remove_boilerplate,
    restore_reading_order,
)


def parse_with_pdfplumber(path: Path, profile: PdfProfile) -> ParseIR:
    """pdfplumber로 PDF를 파싱하여 ParseIR 반환."""
    path = Path(path)
    blocks: list[ParseBlock] = []
    idx = 0

    with pdfplumber.open(path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_blocks, idx = _extract_page_blocks(page, page_num, idx)
            blocks.extend(page_blocks)

    blocks = remove_boilerplate(blocks)
    blocks = restore_reading_order(blocks)
    blocks = assign_section_paths(blocks)

    parse_hash = compute_parse_hash(blocks)

    flags: list[str] = []
    table_blocks = [b for b in blocks if b.block_type == "table"]
    if table_blocks:
        preservation_acc = _compute_table_preservation_accuracy(table_blocks)
        if preservation_acc < 0.9:
            flags.append("table_preservation_low")

    if profile.multi_column:
        flags.append("multi_column_detected")

    return ParseIR(
        doc_id=profile.doc_id,
        source_path=str(path),
        file_hash=profile.file_hash,
        parse_hash=parse_hash,
        parser_used="pdfplumber",
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
    """단일 페이지에서 표와 텍스트 블록을 추출한다."""
    blocks: list[ParseBlock] = []
    idx = start_idx

    # 표 영역 bbox 수집
    tables = page.find_tables()
    table_bboxes: list[tuple[float, float, float, float]] = []
    for table in tables:
        if table.bbox:
            table_bboxes.append(table.bbox)

    # 표 블록 먼저 추출
    for table in tables:
        table_data = table.extract()
        if table_data:
            md_table = _table_to_markdown(table_data)
            if md_table:
                blocks.append(ParseBlock(
                    block_id=f"b{idx:05d}",
                    block_type="table",
                    text=md_table,
                    reading_order_index=idx,
                    source_loc=f"page:{page_num}",
                ))
                idx += 1

    # 표 영역 외 텍스트 추출
    # pdfplumber의 crop으로 표 영역 제외
    if table_bboxes:
        text_blocks = _extract_non_table_text(page, table_bboxes, page_num, idx)
    else:
        raw_text = page.extract_text() or ""
        text_blocks = _text_to_blocks(raw_text, page_num, idx)

    blocks.extend(text_blocks)
    idx += len(text_blocks)

    return blocks, idx


def _extract_non_table_text(
    page,
    table_bboxes: list[tuple[float, float, float, float]],
    page_num: int,
    start_idx: int,
) -> list[ParseBlock]:
    """표 영역을 제외한 텍스트를 추출한다."""
    # 페이지 전체 bbox
    page_bbox = (0, 0, float(page.width), float(page.height))

    # 표 영역을 제외한 영역들 계산 (y축 기준 슬라이스)
    excluded_y_ranges = sorted(
        [(bb[1], bb[3]) for bb in table_bboxes], key=lambda r: r[0]
    )

    text_parts: list[str] = []
    prev_y = page_bbox[1]

    for y0, y1 in excluded_y_ranges:
        if y0 > prev_y:
            try:
                cropped = page.crop((page_bbox[0], prev_y, page_bbox[2], y0))
                text = cropped.extract_text() or ""
                if text.strip():
                    text_parts.append(text)
            except Exception:
                pass
        prev_y = max(prev_y, y1)

    # 마지막 표 아래 영역
    if prev_y < page_bbox[3]:
        try:
            cropped = page.crop((page_bbox[0], prev_y, page_bbox[2], page_bbox[3]))
            text = cropped.extract_text() or ""
            if text.strip():
                text_parts.append(text)
        except Exception:
            pass

    combined = "\n".join(text_parts)
    return _text_to_blocks(combined, page_num, start_idx)


def _text_to_blocks(text: str, page_num: int, start_idx: int) -> list[ParseBlock]:
    """텍스트를 heading/paragraph 블록으로 분류한다."""
    blocks: list[ParseBlock] = []
    idx = start_idx
    buffer: list[str] = []
    current_type = "paragraph"

    def flush():
        nonlocal idx
        t = "\n".join(buffer).strip()
        if t and len(t) > 3:
            blocks.append(ParseBlock(
                block_id=f"b{idx:05d}",
                block_type=current_type,
                text=t,
                reading_order_index=idx,
                source_loc=f"page:{page_num}",
            ))
            idx += 1
        buffer.clear()

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            if buffer:
                flush()
                current_type = "paragraph"
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)", stripped)
        if heading_match:
            flush()
            level = len(heading_match.group(1))
            h_text = heading_match.group(2).strip()
            if h_text:
                blocks.append(ParseBlock(
                    block_id=f"b{idx:05d}",
                    block_type="heading",
                    text=h_text,
                    reading_order_index=idx,
                    heading_level=level,
                    source_loc=f"page:{page_num}",
                ))
                idx += 1
            continue

        buffer.append(stripped)

    if buffer:
        flush()

    return blocks


def _table_to_markdown(table_data: list[list[Optional[str]]]) -> str:
    """pdfplumber 표 데이터를 Markdown 표 형식으로 변환한다."""
    if not table_data:
        return ""

    # None → 빈 문자열, 개행 제거
    rows: list[list[str]] = []
    for row in table_data:
        cleaned = [str(cell).replace("\n", " ").strip() if cell is not None else "" for cell in row]
        rows.append(cleaned)

    if not rows:
        return ""

    # 컬럼 수 맞추기
    max_cols = max(len(r) for r in rows)
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    lines: list[str] = []
    # 헤더 행
    header = rows[0]
    lines.append("| " + " | ".join(header) + " |")
    # 구분선
    lines.append("| " + " | ".join(["---"] * max_cols) + " |")
    # 데이터 행
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def _compute_table_preservation_accuracy(table_blocks: list[ParseBlock]) -> float:
    """표 보존 정확도를 추정한다.

    헤더 구분선이 있는 표 비율을 반환한다.
    """
    if not table_blocks:
        return 1.0
    good = sum(1 for b in table_blocks if _has_table_header(b.text))
    return good / len(table_blocks)


def _has_table_header(table_text: str) -> bool:
    """Markdown 표에 헤더 구분선(---|---) 이 있는지 확인."""
    return bool(re.search(r"\|[-: ]+\|", table_text))

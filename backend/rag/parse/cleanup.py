# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: Parse IR 후처리 — boilerplate 제거, reading order 복원, section_path 할당, parse_hash 계산
"""
파서가 생성한 블록 목록을 정규화한다.

함수 목록:
    remove_boilerplate(blocks)   — 쪽번호·반복 헤더·빈 블록 제거
    remove_empty_tables(blocks)  — 내용이 거의 없는 빈 템플릿 표 블록 제거
    deduplicate_blocks(blocks)   — 정규화 텍스트 기준 중복 블록 제거
    restore_reading_order(blocks) — reading_order_index 기준 정렬
    assign_section_paths(blocks)  — heading 계층 추적 후 하위 블록에 section_path 부여
    compute_parse_hash(blocks)    — 블록 직렬화 sha256 계산
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter

from .ir_schema import ParseBlock


# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------

# 쪽번호 패턴: 독립 행에 숫자만 있는 경우
_PAGE_NUMBER_RE = re.compile(r"^\s*-?\s*\d{1,4}\s*-?\s*$")
# 반복 허용 횟수: 동일 텍스트가 이 횟수 이상이면 boilerplate
_BOILERPLATE_REPEAT_THRESHOLD = 3
# 최소 의미 텍스트 길이
_MIN_TEXT_LEN = 3
# 빈 셀 판정 기준: 셀 내용이 이 길이 이하면 빈 셀로 간주
_EMPTY_CELL_MAX_LEN = 4
# 빈 셀 비율 임계값: 비-헤더 행의 이 비율 이상이 빈 셀이면 빈 템플릿 표로 간주
_EMPTY_TABLE_CELL_RATIO = 0.70


# ---------------------------------------------------------------------------
# 공개 API
# ---------------------------------------------------------------------------

def remove_boilerplate(blocks: list[ParseBlock]) -> list[ParseBlock]:
    """쪽번호·반복 헤더·너무 짧은 블록을 제거한다.

    boilerplate 판정 기준:
    1. 텍스트가 _MIN_TEXT_LEN 이하
    2. 숫자만 있는 독립 행 (쪽번호 패턴)
    3. 동일 텍스트(정규화)가 문서 전체에서 _BOILERPLATE_REPEAT_THRESHOLD 이상 반복
    """
    if not blocks:
        return blocks

    # 반복 텍스트 빈도 계산 (heading 블록만 대상)
    heading_texts = [
        _normalize_text(b.text)
        for b in blocks
        if b.block_type == "heading"
    ]
    repeat_counter: Counter = Counter(heading_texts)

    result: list[ParseBlock] = []
    for block in blocks:
        text = block.text.strip()

        # 1. 빈/짧은 블록
        if len(text) <= _MIN_TEXT_LEN:
            continue

        # 2. 쪽번호 패턴
        if _PAGE_NUMBER_RE.match(text):
            continue

        # 3. 반복 heading boilerplate
        if (
            block.block_type == "heading"
            and repeat_counter[_normalize_text(text)] >= _BOILERPLATE_REPEAT_THRESHOLD
        ):
            continue

        result.append(block)

    return result


def remove_empty_tables(blocks: list[ParseBlock]) -> list[ParseBlock]:
    """내용이 대부분 비어 있는 템플릿 표 블록을 제거한다.

    Markdown 표 블록에서 헤더 구분선 이후 데이터 행을 분석한다.
    비-헤더 행의 _EMPTY_TABLE_CELL_RATIO 이상의 셀이 비어 있으면 빈 템플릿 표로 간주해 제거한다.

    예: | 구분 | 내용 |\\n|---|---|\\n| | |\\n| | | → 제거 대상
    """
    result: list[ParseBlock] = []
    for block in blocks:
        if block.block_type != "table":
            result.append(block)
            continue
        if not _is_empty_template_table(block.text):
            result.append(block)
    return result


def deduplicate_blocks(blocks: list[ParseBlock]) -> list[ParseBlock]:
    """정규화 텍스트 기준 중복 블록을 제거한다.

    같은 정규화 텍스트가 두 번 이상 나타나는 경우 첫 번째만 유지한다.
    heading 블록은 중복 제거 대상에서 제외한다 (section_path 전파에 필요).
    """
    seen: set[str] = set()
    result: list[ParseBlock] = []
    for block in blocks:
        if block.block_type == "heading":
            result.append(block)
            continue
        key = _normalize_text(block.text)
        if key in seen:
            continue
        seen.add(key)
        result.append(block)
    return result


def restore_reading_order(blocks: list[ParseBlock]) -> list[ParseBlock]:
    """reading_order_index 기준으로 블록을 정렬하고 인덱스를 재부여한다."""
    sorted_blocks = sorted(blocks, key=lambda b: b.reading_order_index)
    for i, block in enumerate(sorted_blocks):
        block.reading_order_index = i
    return sorted_blocks


def assign_section_paths(blocks: list[ParseBlock]) -> list[ParseBlock]:
    """heading 블록 계층을 추적하여 하위 블록에 section_path를 부여한다.

    heading_level 1~6에 따라 스택을 관리한다.
    heading 자신에게는 자신을 포함하지 않은 상위 경로를 부여한다.
    하위 paragraph/list/table/other 블록에는 현재 heading 스택 전체를 부여한다.
    """
    # heading 스택: [(level, text), ...]
    heading_stack: list[tuple[int, str]] = []

    for block in blocks:
        if block.block_type == "heading" and block.heading_level is not None:
            level = block.heading_level
            # 현재 레벨 이상의 항목을 스택에서 제거
            heading_stack = [(l, t) for l, t in heading_stack if l < level]
            # heading 자신에게는 상위 경로만 부여
            block.section_path = [t for _, t in heading_stack]
            # 스택에 현재 heading 추가
            heading_stack.append((level, block.text.strip()))
        else:
            # 비-heading 블록에는 현재 전체 스택 부여
            block.section_path = [t for _, t in heading_stack]

    return blocks


def compute_parse_hash(blocks: list[ParseBlock]) -> str:
    """블록 목록을 직렬화하여 sha256 해시를 계산한다.

    parse_hash는 아래 필드만 포함한다 (ID/인덱스 제외):
        block_type, text, source_loc, heading_level
    """
    canonical: list[dict] = [
        {
            "block_type": b.block_type,
            "text": b.text,
            "source_loc": b.source_loc,
            "heading_level": b.heading_level,
        }
        for b in blocks
    ]
    payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# 내부 유틸
# ---------------------------------------------------------------------------

def _normalize_text(text: str) -> str:
    """공백 정규화 + 소문자 변환."""
    return re.sub(r"\s+", " ", text).strip().lower()


def _is_empty_template_table(text: str) -> bool:
    """Markdown 표 텍스트가 빈 템플릿 표인지 판정한다.

    헤더 구분선(|---|) 이후의 데이터 행만 분석한다.
    데이터 행 셀의 _EMPTY_TABLE_CELL_RATIO 이상이 비어 있으면 True.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # 구분선(|---|...) 이후 데이터 행만 추출
    separator_idx = None
    for i, ln in enumerate(lines):
        if re.match(r"\|[-: |]+\|", ln):
            separator_idx = i
            break

    if separator_idx is None:
        return False

    data_lines = [ln for ln in lines[separator_idx + 1:] if ln.startswith("|")]
    if not data_lines:
        return True  # 헤더만 있고 데이터 없는 표

    total_cells = 0
    empty_cells = 0
    for ln in data_lines:
        cells = [c.strip() for c in ln.strip("|").split("|")]
        for cell in cells:
            total_cells += 1
            if len(cell) <= _EMPTY_CELL_MAX_LEN:
                empty_cells += 1

    if total_cells == 0:
        return True
    return (empty_cells / total_cells) >= _EMPTY_TABLE_CELL_RATIO

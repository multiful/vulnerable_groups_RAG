# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: BeautifulSoup 기반 HTML 파서 — SSR 정적 HTML에서 텍스트/표 추출
"""
born-digital SSR HTML (hakjum.com, ITQ, Q-net 등 저장 HTML)에 사용하는 파서.

콘텐츠 선택 전략 (우선순위 순):
    1. #content
    2. article
    3. main
    4. body

블록 추출 순서:
    - h1~h4 → heading 블록
    - table  → Markdown 표 블록
    - p, li  → paragraph 블록
    - div (직접 텍스트 노드) → paragraph 블록

nav / header / footer / script / style / noscript 는 제거한다.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from bs4 import BeautifulSoup, Tag, NavigableString
except ImportError as exc:  # pragma: no cover
    raise ImportError("beautifulsoup4가 설치되지 않았습니다. pip install beautifulsoup4") from exc

from ..ir_schema import ParseBlock, ParseIR
from ..cleanup import (
    assign_section_paths,
    compute_parse_hash,
    deduplicate_blocks,
    remove_boilerplate,
    remove_empty_tables,
    restore_reading_order,
)

# HTML heading 태그 → heading_level 매핑
_HEADING_LEVEL_MAP = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}

# 콘텐츠 영역 선택자 우선순위
_CONTENT_SELECTORS = ["#content", "article", "main"]

# 제거 대상 태그
_STRIP_TAGS = [
    "script", "style", "noscript", "nav", "footer", "header",
    "meta", "link", "iframe", "form", "button", "input", "select",
]


def compute_html_file_hash(path: Path) -> str:
    """HTML 파일 sha256 계산. 형식: 'sha256:hex'"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def slugify_html(name: str) -> str:
    """파일명 → doc_id 슬러그. 비ASCII·특수문자를 _로 치환."""
    stem = Path(name).stem
    slug = re.sub(r"[^\w가-힣]", "_", stem)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug[:80]


def parse_with_html(path: Path, doc_id: Optional[str] = None, file_hash: Optional[str] = None) -> ParseIR:
    """HTML 파일을 파싱하여 ParseIR 반환.

    doc_id / file_hash를 명시하지 않으면 파일명/파일 내용에서 자동 계산한다.
    """
    path = Path(path)

    if doc_id is None:
        doc_id = slugify_html(path.name)
    if file_hash is None:
        file_hash = compute_html_file_hash(path)

    html_text = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html_text, "html.parser")

    # 불필요한 태그 제거
    for tag_name in _STRIP_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # 콘텐츠 영역 선택
    content = None
    for selector in _CONTENT_SELECTORS:
        content = soup.select_one(selector)
        if content:
            break
    if content is None:
        content = soup.find("body") or soup

    blocks: list[ParseBlock] = []
    idx = 0
    idx = _extract_blocks(content, blocks, idx)

    blocks = remove_boilerplate(blocks)
    blocks = remove_empty_tables(blocks)
    blocks = deduplicate_blocks(blocks)
    blocks = restore_reading_order(blocks)
    blocks = assign_section_paths(blocks)

    parse_hash = compute_parse_hash(blocks)

    return ParseIR(
        doc_id=doc_id,
        source_path=str(path),
        file_hash=file_hash,
        parse_hash=parse_hash,
        parser_used="html",
        page_count=1,
        blocks=blocks,
        parse_quality_flags=[],
        parsed_at=datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# 내부 유틸
# ---------------------------------------------------------------------------

def _extract_blocks(
    content,
    blocks: list[ParseBlock],
    idx: int,
) -> int:
    """콘텐츠 영역에서 블록을 순서대로 추출한다."""
    # 방문 추적 (table/list 내부 요소 이중 방문 방지)
    visited: set[int] = set()

    for element in content.descendants:
        if not isinstance(element, Tag):
            continue
        eid = id(element)
        if eid in visited:
            continue

        tag_name = element.name.lower() if element.name else ""

        # --- heading ---
        if tag_name in _HEADING_LEVEL_MAP:
            visited.add(eid)
            text = _clean_text(element.get_text(separator=" ", strip=True))
            if len(text) > _MIN_LEN:
                blocks.append(ParseBlock(
                    block_id=f"b{idx:05d}",
                    block_type="heading",
                    text=text,
                    reading_order_index=idx,
                    heading_level=_HEADING_LEVEL_MAP[tag_name],
                    source_loc="html:1",
                ))
                idx += 1

        # --- table ---
        elif tag_name == "table":
            visited.add(eid)
            # 모든 하위 요소도 visited 처리
            for child in element.descendants:
                if isinstance(child, Tag):
                    visited.add(id(child))
            md = _table_to_markdown(element)
            if md and len(md) > _MIN_LEN:
                blocks.append(ParseBlock(
                    block_id=f"b{idx:05d}",
                    block_type="table",
                    text=md,
                    reading_order_index=idx,
                    source_loc="html:1",
                ))
                idx += 1

        # --- paragraph ---
        elif tag_name in ("p", "li", "dd", "dt"):
            visited.add(eid)
            text = _clean_text(element.get_text(separator=" ", strip=True))
            if len(text) > _MIN_LEN:
                blocks.append(ParseBlock(
                    block_id=f"b{idx:05d}",
                    block_type="paragraph",
                    text=text,
                    reading_order_index=idx,
                    source_loc="html:1",
                ))
                idx += 1

        # --- div/section/article with direct text (avoid deep re-traversal) ---
        elif tag_name in ("div", "section", "article", "span"):
            visited.add(eid)
            # 직접 텍스트 노드만 수집 (자식 태그 텍스트 제외)
            direct_text_parts: list[str] = []
            for child in element.children:
                if isinstance(child, NavigableString):
                    t = child.strip()
                    if t:
                        direct_text_parts.append(t)
            text = _clean_text(" ".join(direct_text_parts))
            if len(text) > _MIN_LEN:
                blocks.append(ParseBlock(
                    block_id=f"b{idx:05d}",
                    block_type="paragraph",
                    text=text,
                    reading_order_index=idx,
                    source_loc="html:1",
                ))
                idx += 1

    return idx


_MIN_LEN = 5  # 최소 의미 텍스트 길이


def _clean_text(text: str) -> str:
    """공백 정규화."""
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _table_to_markdown(table_tag) -> str:
    """HTML table 태그를 Markdown 표로 변환한다."""
    rows: list[list[str]] = []

    # thead / tbody / tr 순서대로
    for row in table_tag.find_all("tr"):
        cells = [
            _clean_text(cell.get_text(separator=" ", strip=True))
            for cell in row.find_all(["th", "td"])
        ]
        if cells:
            rows.append(cells)

    if not rows:
        return ""

    # 열 수 통일 (가장 긴 행 기준)
    max_cols = max(len(r) for r in rows)
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    # 첫 행을 헤더로 사용
    header = rows[0]
    separator = ["---"] * max_cols
    data_rows = rows[1:]

    lines: list[str] = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(separator) + " |")
    for row in data_rows:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)

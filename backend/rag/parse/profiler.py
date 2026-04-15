# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: PDF 레이아웃 프로파일링 — PdfProfile 생성, 파서 라우팅 신호 계산
"""
profile_pdf()로 PDF 1개를 분석하여 PdfProfile을 반환한다.
실제 파서 선택은 router.py가 담당한다.

평가 지표:
    text_density    : 페이지당 평균 추출 문자 수
    image_ratio     : 이미지 면적 합 / 전체 페이지 면적 합
    table_count     : pdfplumber table detection 총 수
    scan_page_ratio : text_density 하한 미만 페이지 비율
    multi_column    : BBox 패턴 기반 다단 추정
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# pdfplumber는 profiling과 pdfplumber_parser 양쪽에서 사용
import pdfplumber

# 텍스트 밀도 하한 — 이 미만인 페이지는 스캔 페이지 후보
_TEXT_DENSITY_LOW = 30.0


@dataclass
class PdfProfile:
    """PDF 1개의 레이아웃 프로파일."""

    doc_id: str
    """파일명 기반 결정론적 슬러그 ID."""

    source_path: str
    file_hash: str
    """sha256:hex"""

    page_count: int

    text_density: float
    """페이지당 평균 추출 문자 수 (페이지 면적 무관 단순 평균)."""

    image_ratio: float
    """이미지 면적 합 / 전체 페이지 면적 합. 0~1."""

    table_count: int
    """pdfplumber로 감지된 표 총 수."""

    scan_page_ratio: float
    """text_density < _TEXT_DENSITY_LOW 인 페이지 비율. 0~1."""

    multi_column: bool
    """다단 레이아웃 추정 여부."""

    recommended_parser: str = "pymupdf4llm"
    """router.py가 채워주는 필드. 기본값만 표시."""

    per_page_text_lengths: list[int] = field(default_factory=list)
    """페이지별 문자 수. router와 OCR 판단에 사용."""


def compute_file_hash(path: Path) -> str:
    """파일 전체 sha256 계산. 형식: 'sha256:hex'"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def _slugify(name: str) -> str:
    """파일명 → doc_id 슬러그 변환. 비ASCII·특수문자를 _로 치환."""
    # 확장자 제거
    stem = Path(name).stem
    # 공백/괄호/특수문자 → _
    slug = re.sub(r"[^\w가-힣]", "_", stem)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug[:80]  # 최대 80자


def profile_pdf(path: Path) -> PdfProfile:
    """PDF 파일을 분석하여 PdfProfile 반환.

    pdfplumber를 사용해 텍스트·이미지·표 통계를 수집한다.
    OCR은 수행하지 않는다.
    """
    path = Path(path)
    file_hash = compute_file_hash(path)
    doc_id = _slugify(path.name)

    per_page_text_lengths: list[int] = []
    total_image_area = 0.0
    total_page_area = 0.0
    total_table_count = 0
    scan_page_count = 0
    multi_col_signals = 0

    with pdfplumber.open(path) as pdf:
        page_count = len(pdf.pages)

        for page in pdf.pages:
            # --- 텍스트 밀도 ---
            text = page.extract_text() or ""
            char_count = len(text.replace("\n", "").replace(" ", ""))
            per_page_text_lengths.append(char_count)

            if char_count < _TEXT_DENSITY_LOW:
                scan_page_count += 1

            # --- 이미지 면적 ---
            pw = float(page.width or 595)
            ph = float(page.height or 842)
            page_area = pw * ph
            total_page_area += page_area

            for img in page.images:
                w = float(img.get("width", 0) or 0)
                h = float(img.get("height", 0) or 0)
                total_image_area += w * h

            # --- 표 감지 ---
            tables = page.find_tables()
            total_table_count += len(tables)

            # --- 다단 추정: 텍스트 블록 x0 분포로 간단 추정 ---
            words = page.extract_words()
            if words:
                x0_vals = [w["x0"] for w in words]
                x0_min = min(x0_vals)
                x0_max = max(x0_vals)
                # 페이지 너비의 40% 이상 떨어진 x0 클러스터가 있으면 다단 신호
                mid = (x0_min + x0_max) / 2
                right_words = sum(1 for x in x0_vals if x > mid + pw * 0.1)
                left_words = sum(1 for x in x0_vals if x < mid - pw * 0.1)
                if right_words > 10 and left_words > 10:
                    multi_col_signals += 1

    text_density = (
        sum(per_page_text_lengths) / page_count if page_count > 0 else 0.0
    )
    image_ratio = (
        total_image_area / total_page_area if total_page_area > 0 else 0.0
    )
    scan_page_ratio = scan_page_count / page_count if page_count > 0 else 0.0
    multi_column = multi_col_signals >= max(1, page_count // 3)

    return PdfProfile(
        doc_id=doc_id,
        source_path=str(path),
        file_hash=file_hash,
        page_count=page_count,
        text_density=text_density,
        image_ratio=image_ratio,
        table_count=total_table_count,
        scan_page_ratio=scan_page_ratio,
        multi_column=multi_column,
        per_page_text_lengths=per_page_text_lengths,
    )

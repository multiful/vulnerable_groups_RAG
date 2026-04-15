# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: PdfProfile → 파서 라우팅 결정 + 페이지별 OCR 필요 여부 판정
"""
라우팅 임계값 (변경 시 parse_version 올릴 것):
    TEXT_DENSITY_THRESHOLD   = 30.0    이하 → OCR 후보 페이지
    IMAGE_RATIO_THRESHOLD    = 0.7     이상 → 홍보물 경고, pymupdf 유지
    TABLE_COUNT_THRESHOLD    = 8       이상 → pdfplumber
    SCAN_PAGE_RATIO_THRESHOLD = 0.4   이상 → page-level OCR 마크
"""
from __future__ import annotations

from .profiler import PdfProfile

# --- 임계값 (parse_version: v1) ---
TEXT_DENSITY_THRESHOLD: float = 30.0
IMAGE_RATIO_THRESHOLD: float = 0.7
TABLE_COUNT_THRESHOLD: int = 8
SCAN_PAGE_RATIO_THRESHOLD: float = 0.4


def route(profile: PdfProfile) -> str:
    """PdfProfile을 받아 사용할 파서 이름을 반환한다.

    Returns:
        'pymupdf4llm' | 'pdfplumber'
        ('ocr_fallback'은 페이지 단위 예외 처리이므로 문서 수준 라우팅에서는 반환하지 않음)
    """
    # 표 중심 문서 → pdfplumber
    if profile.table_count >= TABLE_COUNT_THRESHOLD:
        return "pdfplumber"

    # 기본값 → pymupdf4llm
    return "pymupdf4llm"


def get_ocr_pages(profile: PdfProfile) -> list[int]:
    """page-level OCR이 필요한 페이지 인덱스(0-based) 목록 반환.

    scan_page_ratio가 임계값 이상이면 전체 페이지를 대상으로 OCR 필요 페이지를 추린다.
    born-digital PDF 전체에 OCR을 적용하는 것은 금지 (CLAUDE.md §9).
    """
    if profile.scan_page_ratio < SCAN_PAGE_RATIO_THRESHOLD:
        return []

    ocr_pages = []
    for i, char_count in enumerate(profile.per_page_text_lengths):
        if char_count < TEXT_DENSITY_THRESHOLD:
            ocr_pages.append(i)
    return ocr_pages


def describe_routing(profile: PdfProfile) -> dict:
    """dry-run 출력용 라우팅 근거 딕셔너리."""
    parser = route(profile)
    ocr_pages = get_ocr_pages(profile)

    warnings = []
    if profile.image_ratio >= IMAGE_RATIO_THRESHOLD:
        warnings.append(f"image_ratio={profile.image_ratio:.2f} 높음 — 홍보물/전단지 가능성")
    if profile.scan_page_ratio >= SCAN_PAGE_RATIO_THRESHOLD:
        warnings.append(f"scan_page_ratio={profile.scan_page_ratio:.2f} — {len(ocr_pages)}페이지 OCR 필요")
    if profile.multi_column:
        warnings.append("multi_column=True — reading order 복원 필요")

    return {
        "doc_id": profile.doc_id,
        "recommended_parser": parser,
        "ocr_page_count": len(ocr_pages),
        "metrics": {
            "text_density": round(profile.text_density, 1),
            "image_ratio": round(profile.image_ratio, 3),
            "table_count": profile.table_count,
            "scan_page_ratio": round(profile.scan_page_ratio, 3),
            "multi_column": profile.multi_column,
            "page_count": profile.page_count,
        },
        "warnings": warnings,
    }

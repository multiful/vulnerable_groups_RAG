# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: 페이지 단위 OCR 예외 처리 — born-digital 전체 OCR 금지 (CLAUDE.md §9)
"""
ocr_page(): 단일 페이지 이미지에 Tesseract OCR을 적용하고 텍스트를 반환한다.
전체 문서 OCR은 금지. page-level 예외 처리 용도만 허용.

Tesseract 미설치 환경에서는 ImportError/OSError를 잡아 graceful skip 처리한다.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Tesseract 사용 가능 여부 (런타임에 1회 판정)
_TESSERACT_AVAILABLE: Optional[bool] = None


def _check_tesseract() -> bool:
    """pytesseract + Tesseract 바이너리 가용 여부 확인."""
    global _TESSERACT_AVAILABLE
    if _TESSERACT_AVAILABLE is not None:
        return _TESSERACT_AVAILABLE
    try:
        import pytesseract  # noqa: F401
        pytesseract.get_tesseract_version()
        _TESSERACT_AVAILABLE = True
    except Exception:
        _TESSERACT_AVAILABLE = False
        logger.warning(
            "Tesseract not available — page-level OCR will be skipped. "
            "Install Tesseract and pytesseract to enable OCR fallback."
        )
    return _TESSERACT_AVAILABLE


def ocr_page(pdf_path: Path, page_index: int, dpi: int = 200) -> str:
    """PDF 특정 페이지(0-based)에 OCR을 적용하고 텍스트 반환.

    Args:
        pdf_path: PDF 파일 경로.
        page_index: 0-based 페이지 인덱스.
        dpi: 렌더링 해상도. 기본 200dpi.

    Returns:
        OCR 결과 텍스트. Tesseract 미설치 또는 실패 시 빈 문자열.
    """
    if not _check_tesseract():
        return ""

    try:
        import pytesseract
        from PIL import Image
        import pymupdf  # PyMuPDF (fitz)

        doc = pymupdf.open(str(pdf_path))
        if page_index >= len(doc):
            logger.warning("ocr_page: page_index=%d out of range (total=%d)", page_index, len(doc))
            doc.close()
            return ""

        page = doc[page_index]
        # 페이지를 이미지로 렌더링
        mat = pymupdf.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, colorspace=pymupdf.csGRAY)
        doc.close()

        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))

        text = pytesseract.image_to_string(img, lang="kor+eng")
        return text.strip()

    except Exception as exc:  # noqa: BLE001
        logger.error("ocr_page failed (page=%d, path=%s): %s", page_index, pdf_path, exc)
        return ""


def ocr_pages(pdf_path: Path, page_indices: list[int], dpi: int = 200) -> dict[int, str]:
    """여러 페이지 OCR. 반환: {page_index: text}."""
    return {i: ocr_page(pdf_path, i, dpi) for i in page_indices}

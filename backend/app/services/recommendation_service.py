# File: recommendation_service.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:79a46c012a081ec5e7473452e88a229e88ca599811c71e3d8a374fdaf8b019ab
# Role: 추천 후보 스텁(준비 단계 — 실행 연결은 후속) + evidence 위임
from __future__ import annotations

from typing import Any

from backend.app.core.config import Settings
from backend.app.schemas.envelope import err_envelope
from backend.app.services import retrieval_service


def recommendations_placeholder(_body: dict[str, Any]) -> dict:
    """실행 단계 전: 후보 조회는 구현하지 않는다. 산출물 형식은 `DATA_SCHEMA.md` §9.1·`candidates.jsonl.example`."""
    return err_envelope(
        "NOT_IMPLEMENTED",
        "추천 후보 조회는 준비(스키마·JSONL 예시·문서)만 갖춘 상태이며, 실행 연결은 후속 단계에서 연다.",
        {
            "route": "POST /api/v1/recommendations",
            "prep": [
                "DATA_SCHEMA.md §9.1 certificate_candidate_row",
                "data/canonical/candidates/candidates.jsonl.example",
                "PROJECT_SUMMARY.md §8",
            ],
        },
    )


def recommendations_evidence(body: dict[str, Any], settings: Settings) -> dict:
    return retrieval_service.search_evidence(body, settings)

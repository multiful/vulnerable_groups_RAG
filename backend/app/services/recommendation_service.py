# File: recommendation_service.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: 추천 후보 스텁 + evidence 위임
from __future__ import annotations

from typing import Any

from backend.app.core.config import Settings
from backend.app.schemas.envelope import err_envelope
from backend.app.services import retrieval_service


def recommendations_placeholder(_body: dict[str, Any]) -> dict:
    return err_envelope(
        "NOT_IMPLEMENTED",
        "추천 후보 조회는 canonical candidate 파이프라인 구현 후 활성화됩니다.",
        {"route": "POST /api/v1/recommendations"},
    )


def recommendations_evidence(body: dict[str, Any], settings: Settings) -> dict:
    return retrieval_service.search_evidence(body, settings)

# File: recommendation.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:be3209f3b66cd34aa9cde9dff19c9cfdf6444456f3f504113afbccc2a29aa180
# Role: POST /api/v1/recommendations, /recommendations/evidence
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.app.api.deps import SettingsDep
from backend.app.services import recommendation_service

router = APIRouter()


@router.post("/recommendations")
def post_recommendations(
    body: dict[str, Any] | None,
    settings: SettingsDep,
) -> dict:
    return recommendation_service.recommendations(body or {}, settings)


@router.post("/recommendations/evidence")
def post_recommendations_evidence(
    body: dict[str, Any] | None,
    settings: SettingsDep,
) -> dict:
    return recommendation_service.recommendations_evidence(body or {}, settings)

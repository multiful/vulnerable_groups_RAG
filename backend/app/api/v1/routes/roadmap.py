# File: roadmap.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: POST /api/v1/roadmaps 스켈
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.app.services import roadmap_service

router = APIRouter()


@router.post("/roadmaps")
def post_roadmaps(body: dict[str, Any] | None = None) -> dict:
    return roadmap_service.roadmaps_placeholder(body or {})

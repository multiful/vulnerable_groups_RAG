# File: health.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: GET /api/v1/health
from __future__ import annotations

from fastapi import APIRouter

from backend.app.schemas.envelope import ok_envelope
from backend.app.services import health_service

router = APIRouter()


@router.get("/health")
def get_health() -> dict:
    body = health_service.build_health_payload()
    return ok_envelope(body)

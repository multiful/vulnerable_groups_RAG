# File: risk.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: 위험군 관련 스켈 라우트 (비즈니스 로직은 서비스에서 후속 구현)
from __future__ import annotations

from fastapi import APIRouter

from backend.app.services import risk_stage_service

router = APIRouter()


@router.get("/risk/stages")
def list_risk_stages() -> dict:
    """위험군 단계 메타 조회 스텁. canonical 데이터 연동 전까지 NOT_IMPLEMENTATION."""
    return risk_stage_service.stages_list()

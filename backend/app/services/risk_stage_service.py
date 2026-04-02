# File: risk_stage_service.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: 위험군 단계 서비스 스텁
from __future__ import annotations

from backend.app.schemas.envelope import err_envelope


def stages_placeholder() -> dict:
    return err_envelope(
        "NOT_IMPLEMENTED",
        "위험군 단계 목록 API는 canonical 데이터 연동 후 구현 예정입니다.",
        {"route": "GET /api/v1/risk/stages"},
    )

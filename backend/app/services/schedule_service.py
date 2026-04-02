# File: schedule_service.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: 일정·지원 링크 API reserved 응답
from __future__ import annotations

from fastapi import Response

from backend.app.schemas.envelope import err_envelope


def reserved_response(response: Response, *, feature: str, cert_id: str) -> dict:
    response.status_code = 501
    return err_envelope(
        "NOT_IMPLEMENTED",
        f"{feature} 는 현재 reserved 상태입니다. 실데이터/API 연동 전까지 사용할 수 없습니다.",
        {"feature": feature, "cert_id": cert_id},
    )

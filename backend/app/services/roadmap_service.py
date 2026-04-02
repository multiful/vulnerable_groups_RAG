# File: roadmap_service.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: 로드맵 서비스 스텁
from __future__ import annotations

from typing import Any

from backend.app.schemas.envelope import err_envelope


def roadmaps_placeholder(_body: dict[str, Any]) -> dict:
    return err_envelope(
        "NOT_IMPLEMENTED",
        "로드맵 조회는 후속 스프린트에서 구현 예정입니다.",
        {"route": "POST /api/v1/roadmaps"},
    )

# File: deps.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: FastAPI 의존성 — 설정·요청 컨텍스트
from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from backend.app.core.config import Settings, get_settings


def get_request_context() -> dict:
    """요청 단위 컨텍스트 스텁."""
    return {}


RequestCtx = Annotated[dict, Depends(get_request_context)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

# File: metadata_service.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: 메타데이터·admin 배치 트리거 스텁
from __future__ import annotations

from typing import Any

from backend.app.schemas.envelope import err_envelope


def not_implemented(operation: str, _body: dict[str, Any]) -> dict:
    return err_envelope(
        "NOT_IMPLEMENTED",
        f"관리 작업 '{operation}' 은 아직 구현되지 않았습니다.",
        {"operation": operation},
    )

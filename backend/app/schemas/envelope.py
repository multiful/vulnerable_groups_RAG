# File: envelope.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: API_SPEC 공통 Response / Error envelope 조립
from __future__ import annotations

import uuid
from typing import Any


def new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"


def ok_envelope(data: dict[str, Any], request_id: str | None = None) -> dict[str, Any]:
    rid = request_id or new_request_id()
    return {
        "success": True,
        "data": data,
        "meta": {"request_id": rid, "version": "v1"},
        "error": None,
    }


def err_envelope(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    rid = request_id or new_request_id()
    err: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        err["details"] = details
    return {
        "success": False,
        "data": None,
        "meta": {"request_id": rid, "version": "v1"},
        "error": err,
    }

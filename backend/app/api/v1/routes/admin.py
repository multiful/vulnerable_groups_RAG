# File: admin.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: POST /admin/* 스켈 (canonicalize, candidates 등)
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.app.services import metadata_service

router = APIRouter()


@router.post("/admin/canonicalize")
def post_canonicalize(body: dict[str, Any] | None = None) -> dict:
    return metadata_service.not_implemented("canonicalize", body or {})


@router.post("/admin/candidates/rebuild")
def post_candidates_rebuild(body: dict[str, Any] | None = None) -> dict:
    return metadata_service.not_implemented("candidates_rebuild", body or {})


@router.get("/admin/validation")
def get_validation() -> dict:
    return metadata_service.not_implemented("validation", {})

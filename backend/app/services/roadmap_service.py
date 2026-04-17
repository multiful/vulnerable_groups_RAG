# File: roadmap_service.py
# Last Updated: 2026-04-17
# Content Hash: SHA256:TBD
# Role: 위험군 기반 로드맵 단계 조회 — roadmap_stage_master.csv 기반

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any

from backend.app.schemas.envelope import err_envelope, ok_envelope

_ROADMAP_MASTER  = Path(__file__).parents[3] / "data/processed/master/roadmap_stage_master.csv"
_RISK_TO_ROADMAP = Path(__file__).parents[3] / "data/canonical/relations/risk_stage_to_roadmap_stage.csv"


@lru_cache(maxsize=1)
def _load_roadmap_stages() -> list[dict]:
    if not _ROADMAP_MASTER.exists():
        return []
    with _ROADMAP_MASTER.open(encoding="utf-8-sig") as f:
        return sorted(csv.DictReader(f), key=lambda r: int(r.get("stage_order", 0)))


@lru_cache(maxsize=1)
def _load_risk_to_roadmap() -> dict[str, str]:
    if not _RISK_TO_ROADMAP.exists():
        return {}
    with _RISK_TO_ROADMAP.open(encoding="utf-8-sig") as f:
        return {r["risk_stage_id"]: r["roadmap_stage_id"] for r in csv.DictReader(f)}


def roadmap_for_risk(body: dict[str, Any]) -> dict:
    """
    POST /api/v1/roadmaps
    body: { risk_stage_id: str }
    → 시작 단계부터 전체 로드맵 단계 목록 반환.
    """
    risk_stage_id = body.get("risk_stage_id") or body.get("risk_stage")
    if not risk_stage_id:
        return err_envelope("MISSING_REQUIRED_FIELD", "risk_stage_id 필요")

    r2rm = _load_risk_to_roadmap()
    starting_id = r2rm.get(risk_stage_id)
    if not starting_id:
        return err_envelope("NOT_FOUND", f"risk_stage_id '{risk_stage_id}'에 대한 로드맵 매핑 없음")

    all_stages = _load_roadmap_stages()
    starting_order = next(
        (int(s["stage_order"]) for s in all_stages if s["roadmap_stage_id"] == starting_id), 1
    )

    stages_out = [
        {
            "id": s["roadmap_stage_id"],
            "name": s["roadmap_stage_name"],
            "description": s.get("description", ""),
            "order": int(s["stage_order"]),
            "is_starting_point": s["roadmap_stage_id"] == starting_id,
        }
        for s in all_stages
        if int(s["stage_order"]) >= starting_order
    ]

    return ok_envelope({
        "risk_stage_id": risk_stage_id,
        "starting_roadmap_stage_id": starting_id,
        "stages": stages_out,
    })


def roadmaps_placeholder(body: dict[str, Any]) -> dict:
    """하위 호환 — route에서 기존 함수명 사용."""
    return roadmap_for_risk(body)

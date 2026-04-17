# File: recommendation_service.py
# Last Updated: 2026-04-17
# Content Hash: SHA256:TBD
# Role: cert_candidates.jsonl 기반 구조적 추천 + 순서형 로드맵 조립
#
# 추천 흐름:
#   1. risk_stage_id → 시작 roadmap_stage 결정
#   2. domain_ids / job_ids 필터 (OR 조건)
#   3. risk_stage 필터 → 직접 매칭 없으면 domain-only fallback
#   4. 자격증별 sequence_score 계산 (아래 우선순위)
#   5. 오름차순 정렬 → 순서형 로드맵 반환
#
# ★ 레벨 추론 우선순위 (모두 기존 CSV 데이터 기반):
#   1순위 — cert_grade_tier (cert_master.csv 출처, NCS 공식 체계):
#     1_기능사=10/roadmap_0003, 2_산업기사=20/roadmap_0004,
#     3_기사=30/roadmap_0004, 4_기술사=40/roadmap_0005, 5_기능장=45/roadmap_0005
#   2순위 — avg_pass_rate_3yr (cert_master.csv 출처, 비기술자격에 적용):
#     합격률이 낮을수록 더 어려운 자격증 = 높은 roadmap_stage
#     ≥50% → roadmap_0002, 20-50% → roadmap_0003, 5-20% → roadmap_0004, <5% → roadmap_0005
#   3순위 — 자격증명 키워드 (pass_rate 데이터 없을 때만 fallback):
#     3급→0002, 2급→0002, 준전문가→0003, 개발자→0003, 1급→0004, 전문가→0005
#   동일 레벨 내: avg_pass_rate 높을수록 먼저 (쉬운 것부터)
#
# evidence 검색은 retrieval_service 담당.

from __future__ import annotations

import csv
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from backend.app.core.config import Settings
from backend.app.schemas.envelope import err_envelope, ok_envelope
from backend.app.services import retrieval_service

# ---------- 경로 ----------
_PROJECT_ROOT    = Path(__file__).parents[3]
_CANDIDATES_JSONL = _PROJECT_ROOT / "data/canonical/candidates/cert_candidates.jsonl"
_CERT_MASTER_CSV  = _PROJECT_ROOT / "data/processed/master/cert_master.csv"
_RISK_MASTER_CSV  = _PROJECT_ROOT / "data/processed/master/risk_stage_master.csv"
_ROADMAP_MASTER   = _PROJECT_ROOT / "data/processed/master/roadmap_stage_master.csv"
_RISK_TO_ROADMAP  = _PROJECT_ROOT / "data/canonical/relations/risk_stage_to_roadmap_stage.csv"
_DOMAIN_MASTER    = _PROJECT_ROOT / "data/processed/master/domain_master.csv"

_RISK_ORDER = ["risk_0001", "risk_0002", "risk_0003", "risk_0004", "risk_0005"]

# ---------- 레벨 → roadmap_stage 매핑 ----------
# tier 기반 (기존 로직과 동일)
_TIER_SEQUENCE: dict[str, tuple[int, str]] = {
    "1_기능사":   (10, "roadmap_stage_0003"),
    "2_산업기사": (20, "roadmap_stage_0004"),
    "3_기사":     (30, "roadmap_stage_0004"),
    "4_기술사":   (40, "roadmap_stage_0005"),
    "5_기능장":   (45, "roadmap_stage_0005"),
}

# 비기술자격 합격률 → (레벨 점수, 유효 roadmap_stage) — PRIMARY (데이터 기반)
# 합격률 낮을수록 어려운 자격증 → 높은 stage에 배치
_PASSRATE_STAGE_MAP: list[tuple[float, int, str]] = [
    (50.0, 15, "roadmap_stage_0002"),  # 쉬움: 합격률 ≥50%
    (20.0, 22, "roadmap_stage_0003"),  # 중간: 20~50%
    (5.0,  30, "roadmap_stage_0004"),  # 어려움: 5~20%
    (0.0,  40, "roadmap_stage_0005"),  # 매우 어려움: <5%
]

# 비기술자격 키워드 패턴 → (레벨 점수, 유효 roadmap_stage) — FALLBACK (pass_rate 없을 때만)
# ★ 순서 중요: 준전문가가 전문가보다 먼저
_NONTECH_KEYWORD_RULES: list[tuple[str, int, str]] = [
    (r"준전문가",          20, "roadmap_stage_0003"),
    (r"전문가",            40, "roadmap_stage_0005"),
    (r"1급",               30, "roadmap_stage_0004"),
    (r"개발자",            25, "roadmap_stage_0003"),
    (r"준$|준\(",          20, "roadmap_stage_0003"),
    (r"2급",               15, "roadmap_stage_0002"),
    (r"3급",               10, "roadmap_stage_0002"),
]
_NONTECH_DEFAULT = (15, "roadmap_stage_0002")

# achievability: risk_stage 거리 기준
_ACHIEVABILITY = {0: "immediate", 1: "near_term", 2: "long_term"}


# ---------- 로드 ----------
@lru_cache(maxsize=1)
def _load_candidates() -> list[dict]:
    if not _CANDIDATES_JSONL.exists():
        return []
    out = []
    with _CANDIDATES_JSONL.open(encoding="utf-8") as f:
        for line in f:
            if s := line.strip():
                out.append(json.loads(s))
    return out


@lru_cache(maxsize=1)
def _load_pass_rate_map() -> dict[str, float]:
    if not _CERT_MASTER_CSV.exists():
        return {}
    out: dict[str, float] = {}
    with _CERT_MASTER_CSV.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            try:
                out[r["cert_id"]] = float(r.get("avg_pass_rate_3yr", ""))
            except ValueError:
                pass
    return out


@lru_cache(maxsize=1)
def _load_risk_stages() -> dict[str, dict]:
    if not _RISK_MASTER_CSV.exists():
        return {}
    out: dict[str, dict] = {}
    with _RISK_MASTER_CSV.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            out[r["risk_stage_id"]] = {
                "id": r["risk_stage_id"],
                "name": r["risk_stage_name"],
                "description": r.get("description", ""),
                "order": int(r.get("risk_stage_order", 0)),
            }
    return out


@lru_cache(maxsize=1)
def _load_roadmap_stages() -> dict[str, dict]:
    if not _ROADMAP_MASTER.exists():
        return {}
    out: dict[str, dict] = {}
    with _ROADMAP_MASTER.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            out[r["roadmap_stage_id"]] = {
                "id": r["roadmap_stage_id"],
                "name": r["roadmap_stage_name"],
                "description": r.get("description", ""),
                "order": int(r.get("stage_order", 0)),
            }
    return out


@lru_cache(maxsize=1)
def _load_risk_to_roadmap() -> dict[str, str]:
    if not _RISK_TO_ROADMAP.exists():
        return {}
    with _RISK_TO_ROADMAP.open(encoding="utf-8-sig") as f:
        return {r["risk_stage_id"]: r["roadmap_stage_id"] for r in csv.DictReader(f)}


@lru_cache(maxsize=1)
def _load_domain_map() -> dict[str, str]:
    if not _DOMAIN_MASTER.exists():
        return {}
    out: dict[str, str] = {}
    with _DOMAIN_MASTER.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            out[r["domain_sub_label_name"].strip().lower()] = r["domain_sub_label_id"]
    return out


# ---------- 레벨 추론 ----------
def _cert_level(cand: dict, pass_rate: float | None = None) -> tuple[int, str]:
    """
    (sequence_score, effective_roadmap_stage_id) 반환.

    우선순위:
      1. cert_grade_tier (NCS 공식 체계, cert_master.csv 출처)
      2. avg_pass_rate (합격률 기반, 비기술자격에 적용) ← 주요 데이터 신호
      3. 자격증명 키워드 fallback (pass_rate 없을 때만)
    """
    tier = cand.get("cert_grade_tier", "")
    if tier and tier in _TIER_SEQUENCE:
        return _TIER_SEQUENCE[tier]

    # 비기술자격: 합격률 기반 (데이터 기반 primary)
    if pass_rate is not None:
        for min_rate, level, stage in _PASSRATE_STAGE_MAP:
            if pass_rate >= min_rate:
                return (level, stage)
        return (40, "roadmap_stage_0005")

    # 합격률 없음: 키워드 fallback
    name = cand.get("cert_name", "")
    for pattern, score, stage in _NONTECH_KEYWORD_RULES:
        if re.search(pattern, name):
            return (score, stage)
    return _NONTECH_DEFAULT


def _achievability(cand: dict, user_risk_id: str) -> str:
    """사용자 위험군 대비 자격증 접근 가능성."""
    rec = cand.get("recommended_risk_stages", [])
    if user_risk_id in rec:
        return "immediate"
    user_idx = _RISK_ORDER.index(user_risk_id) if user_risk_id in _RISK_ORDER else -1
    # rec에서 가장 가까운 위험군과의 거리 계산
    if not rec or user_idx < 0:
        return "long_term"
    min_dist = min(
        abs(user_idx - _RISK_ORDER.index(r))
        for r in rec if r in _RISK_ORDER
    )
    return _ACHIEVABILITY.get(min_dist, "long_term")


# ---------- 필터 ----------
def _filter_candidates(
    candidates: list[dict],
    risk_stage_id: str | None,
    domain_ids: list[str],
    job_ids: list[str],
    use_fallback: bool = True,
) -> tuple[list[dict], bool]:
    def _domain_job_match(c: dict) -> bool:
        if domain_ids and not any(d in c.get("related_domains", []) for d in domain_ids):
            if not job_ids or not any(j in c.get("related_jobs", []) for j in job_ids):
                return False
        if job_ids and not domain_ids:
            return any(j in c.get("related_jobs", []) for j in job_ids)
        return True

    def _risk_match(c: dict, risk_id: str) -> bool:
        return risk_id in c.get("recommended_risk_stages", [])

    results = [c for c in candidates if _domain_job_match(c)
               and (not risk_stage_id or _risk_match(c, risk_stage_id))]

    if not results and use_fallback and (domain_ids or job_ids):
        # 도메인/직무 조건만으로 전체 반환 (risk stage 제약 해제)
        # 이 케이스는 주로 risk_0005처럼 직접 매핑이 없는 경우:
        # 해당 도메인의 전체 자격증을 로드맵 순서로 제시
        domain_only = [c for c in candidates if _domain_job_match(c)]
        return domain_only, True

    return results, False


# ---------- 로드맵 조립 ----------
def _build_roadmap_sequence(
    candidates: list[dict],
    starting_roadmap_id: str,
    roadmap_stages: dict[str, dict],
    pass_rate_map: dict,
    user_risk_id: str,
    top_n: int,
) -> tuple[list[dict], list[dict]]:
    """
    Returns:
      sequence: 순서형 평탄화 리스트 (step 1, 2, 3, ...)
      by_stage: stage별 그룹 리스트
    """
    starting_order = roadmap_stages.get(starting_roadmap_id, {}).get("order", 1)

    # 각 cert에 유효 roadmap_stage 할당
    # pass_rate를 먼저 조회해 _cert_level에 전달 → 합격률 기반 순서 도출
    enriched = []
    for c in candidates:
        pass_rate = pass_rate_map.get(c["cert_id"])
        level_score, eff_stage = _cert_level(c, pass_rate)
        eff_stage_info = roadmap_stages.get(eff_stage, {})
        eff_order = eff_stage_info.get("order", 2)
        # 시작 단계보다 낮은 stage는 시작 단계로 올림
        if eff_order < starting_order:
            eff_stage = starting_roadmap_id
            eff_stage_info = roadmap_stages.get(eff_stage, {})
        enriched.append({
            **c,
            "_level_score": level_score,
            "_eff_stage_id": eff_stage,
            "_eff_stage_info": eff_stage_info,
            "_pass_rate": pass_rate,
            "_achievability": _achievability(c, user_risk_id),
        })

    # 전체 오름차순 정렬 (sequence용)
    enriched.sort(key=lambda x: (x["_level_score"], -(x["_pass_rate"] or 0.0)))

    # ── 순서형 flat 리스트 ──
    sequence: list[dict] = []
    for i, c in enumerate(enriched, 1):
        pr = c["_pass_rate"]
        sequence.append({
            "step": i,
            "candidate_id": c["candidate_id"],
            "cert_id": c["cert_id"],
            "cert_name": c["cert_name"],
            "cert_grade_tier": c.get("cert_grade_tier", "") or "비기술자격",
            "roadmap_stage_id": c["_eff_stage_id"],
            "roadmap_stage_name": c["_eff_stage_info"].get("name", ""),
            "avg_pass_rate": round(pr, 1) if pr is not None else None,
            "achievability": c["_achievability"],
            "primary_domain": c["primary_domain"],
            "related_jobs": c.get("related_jobs", [])[:5],
            "text_for_dense": c.get("text_for_dense", ""),
        })

    # ── stage별 그룹 (top_n 제한) ──
    sorted_stages = sorted(
        [s for s in roadmap_stages.values() if s["order"] >= starting_order],
        key=lambda s: s["order"],
    )
    stage_groups: dict[str, list] = {s["id"]: [] for s in sorted_stages}
    for c in enriched:
        sid = c["_eff_stage_id"]
        if sid in stage_groups:
            stage_groups[sid].append(c)

    by_stage: list[dict] = []
    for stage_info in sorted_stages:
        sid = stage_info["id"]
        certs_here = sorted(
            stage_groups.get(sid, []),
            key=lambda x: (x["_level_score"], -(x["_pass_rate"] or 0.0)),
        )[:top_n]
        by_stage.append({
            "stage": stage_info,
            "is_starting_point": sid == starting_roadmap_id,
            "recommended_certs": [
                {
                    "step": next(
                        (s["step"] for s in sequence if s["cert_id"] == c["cert_id"]), None
                    ),
                    "cert_id": c["cert_id"],
                    "cert_name": c["cert_name"],
                    "cert_grade_tier": c.get("cert_grade_tier", "") or "비기술자격",
                    "avg_pass_rate": round(c["_pass_rate"], 1) if c["_pass_rate"] is not None else None,
                    "achievability": c["_achievability"],
                    "related_jobs": c.get("related_jobs", [])[:5],
                }
                for c in certs_here
            ],
        })

    return sequence, by_stage


# ---------- 공개 API ----------
def recommendations(body: dict[str, Any]) -> dict:
    """
    POST /api/v1/recommendations
    body:
      risk_stage_id: str
      domain_ids: list[str]
      domain_names: list[str]   ← 이름으로도 가능 (e.g. "데이터/AI")
      job_ids: list[str]
      top_n_per_stage: int      (default 5)
    """
    risk_stage_id = body.get("risk_stage_id") or body.get("risk_stage")
    domain_ids: list[str] = list(body.get("domain_ids") or [])
    job_ids: list[str]    = list(body.get("job_ids") or [])
    top_n = int(body.get("top_n_per_stage") or 5)

    if body.get("domain_names"):
        domain_map = _load_domain_map()
        for name in body["domain_names"]:
            if did := domain_map.get(name.strip().lower()):
                if did not in domain_ids:
                    domain_ids.append(did)

    if not risk_stage_id and not domain_ids and not job_ids:
        return err_envelope(
            "MISSING_REQUIRED_FIELD",
            "risk_stage_id 또는 domain_ids / job_ids 중 하나 이상 필요합니다.",
        )

    candidates     = _load_candidates()
    pass_rate_map  = _load_pass_rate_map()
    risk_stages    = _load_risk_stages()
    roadmap_stages = _load_roadmap_stages()
    risk_to_roadmap = _load_risk_to_roadmap()

    if not candidates:
        return err_envelope(
            "DATA_NOT_READY",
            "cert_candidates.jsonl을 찾을 수 없습니다. scripts/build_cert_candidates.py를 먼저 실행하세요.",
        )

    filtered, used_fallback = _filter_candidates(
        candidates, risk_stage_id, domain_ids, job_ids
    )

    starting_roadmap_id = risk_to_roadmap.get(risk_stage_id or "", "roadmap_stage_0002")

    sequence, by_stage = _build_roadmap_sequence(
        filtered, starting_roadmap_id, roadmap_stages,
        pass_rate_map, risk_stage_id or "", top_n,
    )

    risk_info = risk_stages.get(risk_stage_id or {})

    return ok_envelope({
        "risk_stage": risk_info or None,
        "starting_roadmap_stage": roadmap_stages.get(starting_roadmap_id),
        "query": {
            "risk_stage_id": risk_stage_id,
            "domain_ids": domain_ids,
            "job_ids": job_ids,
        },
        "fallback_used": used_fallback,
        "fallback_note": (
            "선택 도메인에 해당 위험군 직접 매핑 자격증이 없어 전체 도메인 자격증을 로드맵 순서로 제시합니다."
            if used_fallback else None
        ),
        "roadmap_sequence": sequence,
        "roadmap_by_stage": by_stage,
        "total_certs_in_roadmap": len(sequence),
    })


def recommendations_placeholder(body: dict[str, Any]) -> dict:
    return recommendations(body)


def recommendations_evidence(body: dict[str, Any], settings: Settings) -> dict:
    return retrieval_service.search_evidence(body, settings)

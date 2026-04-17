# File: recommendation_service.py
# Last Updated: 2026-04-18
# Content Hash: SHA256:TBD
# Role: cert_candidates.jsonl 기반 구조적 추천 + 순서형 로드맵 조립
#
# 추천 흐름:
#   1. risk_stage_id → 시작 roadmap_stage 결정
#   2. held_cert_ids / major_name → 동적 진입점 조정
#   3. domain_ids / job_ids / major_name 필터 (OR 조건)
#   4. risk_stage 필터 → 직접 매칭 없으면 domain-only fallback
#   5. 자격증별 sequence_score 계산 (아래 우선순위)
#   6. (stage_order, level_score, -pass_rate) 오름차순 정렬 → 순서형 로드맵 반환
#
# ★ 레벨 추론 우선순위 (모두 기존 CSV 데이터 기반):
#   1순위 — cert_grade_tier (cert_master.csv 출처, NCS 공식 체계):
#     1_기능사=10/roadmap_0003, 2_산업기사=20/roadmap_0004,
#     3_기사=30/roadmap_0004, 4_기술사=40/roadmap_0005, 5_기능장=45/roadmap_0005
#   2순위 — avg_pass_rate_3yr (cert_master.csv 출처, 비기술자격에 적용):
#     합격률이 낮을수록 더 어려운 자격증 = 높은 roadmap_stage
#     ≥50% → roadmap_0002, 30-50% → roadmap_0003, 10-30% → roadmap_0004, <10% → roadmap_0005
#   3순위 — 자격증명 키워드 (pass_rate 데이터 없을 때만 fallback):
#     3급→0002, 2급→0002, 준전문가→0003, 개발자→0003, 1급→0004, 전문가→0005
#   동일 레벨 내: avg_pass_rate 높을수록 먼저 (쉬운 것부터)
#
# is_bottleneck: pass_rate < 10% 자격증에 플래그 부여 — 사용자 고지용
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
_MAJOR_MASTER     = _PROJECT_ROOT / "data/processed/master/major_master.csv"
_MAJOR_TO_DOMAIN  = _PROJECT_ROOT / "data/canonical/relations/major_to_domain.csv"
_CERT_TO_ROADMAP  = _PROJECT_ROOT / "data/canonical/relations/cert_to_roadmap_stage.csv"

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
# 임계값: 50/30/10 (변별력 강화)
_PASSRATE_STAGE_MAP: list[tuple[float, int, str]] = [
    (50.0, 15, "roadmap_stage_0002"),  # 쉬움: 합격률 ≥50%
    (30.0, 22, "roadmap_stage_0003"),  # 중간: 30~50%
    (10.0, 30, "roadmap_stage_0004"),  # 어려움: 10~30%
    (0.0,  40, "roadmap_stage_0005"),  # 매우 어려움: <10%
]

_BOTTLENECK_THRESHOLD = 10.0  # 합격률 < 10%: is_bottleneck 플래그

# tier 점수 (redundancy 비교용) — 빈값은 0 (비기술자격, 비교 대상 제외)
_TIER_SCORE: dict[str, int] = {
    "1_기능사": 10, "2_산업기사": 20, "3_기사": 30,
    "4_기술사": 40, "5_기능장": 45,
}

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


@lru_cache(maxsize=1)
def _load_major_to_domain_map() -> dict[str, str]:
    """normalized major_name → domain_sub_label_id (2단계 join: major_master + major_to_domain)"""
    if not _MAJOR_MASTER.exists() or not _MAJOR_TO_DOMAIN.exists():
        return {}
    major_id_map: dict[str, str] = {}
    with _MAJOR_MASTER.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            key = r.get("normalized_key", "").strip().lower() or r.get("major_name", "").strip().lower()
            if key:
                major_id_map[key] = r["major_id"]
    m2d: dict[str, str] = {}
    with _MAJOR_TO_DOMAIN.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            m2d[r["major_id"]] = r["domain_sub_label_id"]
    return {k: m2d[v] for k, v in major_id_map.items() if v in m2d}


@lru_cache(maxsize=1)
def _load_cert_to_roadmap_map() -> dict[str, str]:
    """cert_id → roadmap_stage_id"""
    if not _CERT_TO_ROADMAP.exists():
        return {}
    with _CERT_TO_ROADMAP.open(encoding="utf-8-sig") as f:
        return {r["cert_id"]: r["roadmap_stage_id"] for r in csv.DictReader(f)}


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
        if not domain_ids and not job_ids:
            return True
        domain_match = domain_ids and any(d in c.get("related_domains", []) for d in domain_ids)
        job_match = job_ids and any(j in c.get("related_jobs", []) for j in job_ids)
        return bool(domain_match or job_match)

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


# ---------- 보유 자격증 tier 기반 redundancy 계산 ----------
def _held_domain_max_tier(
    held_cert_ids: list[str],
    candidates: list[dict],
) -> dict[str, int]:
    """
    보유 자격증별 primary_domain → 최고 tier_score 매핑.
    비기술자격(tier 빈값)은 비교 대상에서 제외.
    """
    cand_map = {c["cert_id"]: c for c in candidates}
    out: dict[str, int] = {}
    for cid in held_cert_ids:
        c = cand_map.get(cid)
        if not c:
            continue
        score = _TIER_SCORE.get(c.get("cert_grade_tier", ""), 0)
        if score == 0:
            continue
        domain = c.get("primary_domain", "")
        if domain:
            out[domain] = max(out.get(domain, 0), score)
    return out


# ---------- 로드맵 조립 ----------
def _build_roadmap_sequence(
    candidates: list[dict],
    starting_roadmap_id: str,
    roadmap_stages: dict[str, dict],
    pass_rate_map: dict,
    user_risk_id: str,
    top_n: int,
    held_max_tier: dict[str, int] | None = None,
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
        # is_redundant: 보유 자격증의 같은 domain 내 tier보다 낮은 기술자격
        cert_tier_score = _TIER_SCORE.get(c.get("cert_grade_tier", ""), 0)
        domain_held_max = (held_max_tier or {}).get(c.get("primary_domain", ""), 0)
        is_redundant = cert_tier_score > 0 and cert_tier_score < domain_held_max

        enriched.append({
            **c,
            "_level_score": level_score,
            "_eff_stage_id": eff_stage,
            "_eff_stage_info": eff_stage_info,
            "_pass_rate": pass_rate,
            "_achievability": _achievability(c, user_risk_id),
            "_is_redundant": is_redundant,
        })

    # 전체 오름차순 정렬 (sequence용): stage_order 먼저 → 동일 stage 내 level_score → pass_rate 높을수록 앞
    enriched.sort(key=lambda x: (
        x["_eff_stage_info"].get("order", 2),
        x["_level_score"],
        -(x["_pass_rate"] or 0.0),
    ))

    # ── 순서형 flat 리스트 ──
    sequence: list[dict] = []
    for i, c in enumerate(enriched, 1):
        pr = c["_pass_rate"]
        is_bn = pr is not None and pr < _BOTTLENECK_THRESHOLD
        sequence.append({
            "step": i,
            "candidate_id": c["candidate_id"],
            "cert_id": c["cert_id"],
            "cert_name": c["cert_name"],
            "cert_grade_tier": c.get("cert_grade_tier", "") or "비기술자격",
            "roadmap_stage_id": c["_eff_stage_id"],
            "roadmap_stage_name": c["_eff_stage_info"].get("name", ""),
            "avg_pass_rate": round(pr, 1) if pr is not None else None,
            "is_bottleneck": is_bn,
            "bottleneck_note": (
                f"해당 단계에서 정체 위험이 높습니다 (합격률 {round(pr, 1)}%)" if is_bn else None
            ),
            "is_redundant": c["_is_redundant"],
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
                    "is_bottleneck": (c["_pass_rate"] is not None and c["_pass_rate"] < _BOTTLENECK_THRESHOLD),
                    "bottleneck_note": (
                        f"해당 단계에서 정체 위험이 높습니다 (합격률 {round(c['_pass_rate'], 1)}%)"
                        if c["_pass_rate"] is not None and c["_pass_rate"] < _BOTTLENECK_THRESHOLD else None
                    ),
                    "is_redundant": c["_is_redundant"],
                    "achievability": c["_achievability"],
                    "related_jobs": c.get("related_jobs", [])[:5],
                }
                for c in certs_here
            ],
        })

    return sequence, by_stage


# ---------- 동적 진입점 헬퍼 ----------
def _resolve_dynamic_entry(
    held_cert_ids: list[str],
    roadmap_stages: dict[str, dict],
    base_starting_id: str,
) -> tuple[str, list[str]]:
    """
    held_cert_ids 기반으로 starting_roadmap_id 동적 조정.
    Returns:
      (adjusted_starting_roadmap_id, held_cert_ids_to_exclude)
    """
    if not held_cert_ids:
        return base_starting_id, []

    cert_to_roadmap = _load_cert_to_roadmap_map()
    held_orders = [
        roadmap_stages.get(cert_to_roadmap.get(cid, ""), {}).get("order", 0)
        for cid in held_cert_ids
    ]
    max_held_order = max((o for o in held_orders if o > 0), default=0)
    if not max_held_order:
        return base_starting_id, held_cert_ids

    base_order = roadmap_stages.get(base_starting_id, {}).get("order", 2)
    if max_held_order < base_order:
        return base_starting_id, held_cert_ids

    # 보유 자격증 최고 단계 다음 stage로 진입점 전진
    sorted_stages = sorted(roadmap_stages.values(), key=lambda s: s["order"])
    advanced_id = next(
        (s["id"] for s in sorted_stages if s["order"] > max_held_order),
        base_starting_id,
    )
    return advanced_id, held_cert_ids


# ---------- 공개 API ----------
def recommendations(body: dict[str, Any]) -> dict:
    """
    POST /api/v1/recommendations
    body:
      risk_stage_id: str
      domain_ids: list[str]
      domain_names: list[str]     ← 이름으로도 가능 (e.g. "데이터/AI")
      major_name: str             ← 전공명 → domain 자동 추가
      job_ids: list[str]
      held_cert_ids: list[str]    ← 보유 자격증 → 동적 진입점 조정 + 결과에서 제외
      top_n_per_stage: int        (default 5)
    """
    risk_stage_id = body.get("risk_stage_id") or body.get("risk_stage")
    domain_ids: list[str] = list(body.get("domain_ids") or [])
    job_ids: list[str]    = list(body.get("job_ids") or [])
    held_cert_ids: list[str] = list(body.get("held_cert_ids") or [])
    top_n = int(body.get("top_n_per_stage") or 5)

    if body.get("domain_names"):
        domain_map = _load_domain_map()
        for name in body["domain_names"]:
            if did := domain_map.get(name.strip().lower()):
                if did not in domain_ids:
                    domain_ids.append(did)

    if body.get("major_name"):
        major_domain_map = _load_major_to_domain_map()
        norm_key = body["major_name"].strip().lower()
        # normalized_key 먼저, 없으면 그대로 검색
        if did := major_domain_map.get(norm_key):
            if did not in domain_ids:
                domain_ids.append(did)

    if not risk_stage_id and not domain_ids and not job_ids:
        return err_envelope(
            "MISSING_REQUIRED_FIELD",
            "risk_stage_id 또는 domain_ids / job_ids 중 하나 이상 필요합니다.",
        )

    candidates      = _load_candidates()
    pass_rate_map   = _load_pass_rate_map()
    risk_stages     = _load_risk_stages()
    roadmap_stages  = _load_roadmap_stages()
    risk_to_roadmap = _load_risk_to_roadmap()

    if not candidates:
        return err_envelope(
            "DATA_NOT_READY",
            "cert_candidates.jsonl을 찾을 수 없습니다. scripts/build_cert_candidates.py를 먼저 실행하세요.",
        )

    filtered, used_fallback = _filter_candidates(
        candidates, risk_stage_id, domain_ids, job_ids
    )

    # 보유 자격증 제외 + redundancy 계산용 held tier 맵
    held_set = set(held_cert_ids)
    held_max_tier = _held_domain_max_tier(held_cert_ids, candidates)
    if held_set:
        filtered = [c for c in filtered if c["cert_id"] not in held_set]

    base_starting_id = risk_to_roadmap.get(risk_stage_id or "", "roadmap_stage_0002")
    starting_roadmap_id, _ = _resolve_dynamic_entry(
        held_cert_ids, roadmap_stages, base_starting_id
    )
    entry_advanced = (starting_roadmap_id != base_starting_id)

    sequence, by_stage = _build_roadmap_sequence(
        filtered, starting_roadmap_id, roadmap_stages,
        pass_rate_map, risk_stage_id or "", top_n,
        held_max_tier=held_max_tier,
    )

    risk_info = risk_stages.get(risk_stage_id) if risk_stage_id else None

    return ok_envelope({
        "risk_stage": risk_info or None,
        "starting_roadmap_stage": roadmap_stages.get(starting_roadmap_id),
        "query": {
            "risk_stage_id": risk_stage_id,
            "domain_ids": domain_ids,
            "job_ids": job_ids,
            "held_cert_ids": held_cert_ids,
            "major_name": body.get("major_name"),
        },
        "entry_advanced": entry_advanced,
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

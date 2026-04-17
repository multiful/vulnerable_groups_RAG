# Content Hash: SHA256:TBD
# Role: cert_candidates.csv 기반 구조적 추천 동작 검증 스크립트
# 사용법: python scripts/test_recommendation.py
# 출력: 콘솔 — 시나리오별 추천 결과 (Top-N)
#
# 추천 로직: canonical data 기반 구조적 필터링
#   1. risk_stage → 대상 후보 필터 (recommended_risk_stages 포함 여부)
#   2. domain 또는 job → 관심 분야 필터
#   3. roadmap_stage → 현재 단계 필터 (optional)
#   4. 정렬: avg_pass_rate_3yr 기준 (없으면 cert_name 알파벳)
#
# 이 스크립트는 RAG/임베딩 없이 structured 필터링만으로 추천을 수행한다.
# evidence(설명 근거) 검색은 retrieval_service 담당 — 여기서는 다루지 않는다.

import os
import sys
import json
import csv
from typing import Optional

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR    = os.path.normpath(os.path.join(_SCRIPT_DIR, ".."))

CANDIDATES_PATH = os.path.join(BASE_DIR, "data", "canonical", "candidates", "cert_candidates.csv")
DOMAIN_MASTER   = os.path.join(BASE_DIR, "data", "processed", "master", "domain_master.csv")
JOB_MASTER      = os.path.join(BASE_DIR, "data", "processed", "master", "job_master.csv")
RISK_MASTER     = os.path.join(BASE_DIR, "data", "processed", "master", "risk_stage_master.csv")
ROADMAP_MASTER  = os.path.join(BASE_DIR, "data", "processed", "master", "roadmap_stage_master.csv")
CERT_MASTER     = os.path.join(BASE_DIR, "data", "processed", "master", "cert_master.csv")


# ---------- 로드 ----------
def _load_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _id_name_map(path: str, id_col: str, name_col: str) -> dict[str, str]:
    return {r[id_col]: r[name_col] for r in _load_csv(path)}


def load_data():
    candidates = _load_csv(CANDIDATES_PATH)
    # list 컬럼 파싱
    list_cols = [
        "aliases", "related_domains", "related_jobs", "related_majors",
        "recommended_risk_stages", "roadmap_stages", "source_ids",
    ]
    for c in candidates:
        for col in list_cols:
            try:
                c[col] = json.loads(c.get(col, "[]") or "[]")
            except Exception:
                c[col] = []

    domain_map  = _id_name_map(DOMAIN_MASTER,  "domain_sub_label_id", "domain_sub_label_name")
    job_map     = _id_name_map(JOB_MASTER,      "job_role_id",          "job_role_name")
    risk_map    = _id_name_map(RISK_MASTER,     "risk_stage_id",        "risk_stage_name")
    roadmap_map = _id_name_map(ROADMAP_MASTER,  "roadmap_stage_id",     "roadmap_stage_name")

    # cert_master에서 pass_rate 가져오기 (정렬용)
    pass_rate_map: dict[str, float] = {}
    for r in _load_csv(CERT_MASTER):
        v = r.get("avg_pass_rate_3yr", "").strip()
        try:
            pass_rate_map[r["cert_id"]] = float(v)
        except ValueError:
            pass

    return candidates, domain_map, job_map, risk_map, roadmap_map, pass_rate_map


# ---------- 추천 엔진 ----------
def recommend(
    candidates: list[dict],
    risk_stage_id: Optional[str] = None,
    domain_ids: Optional[list[str]] = None,
    job_ids: Optional[list[str]] = None,
    roadmap_stage_id: Optional[str] = None,
    pass_rate_map: Optional[dict] = None,
    top_n: int = 10,
) -> list[dict]:
    results = []

    for c in candidates:
        # 1. risk_stage 필터
        if risk_stage_id and risk_stage_id not in c["recommended_risk_stages"]:
            continue

        # 2. domain 필터 (OR — 하나라도 겹치면 통과)
        if domain_ids:
            if not any(d in c["related_domains"] for d in domain_ids):
                continue

        # 3. job 필터 (OR)
        if job_ids:
            if not any(j in c["related_jobs"] for j in job_ids):
                continue

        # 4. roadmap_stage 필터
        if roadmap_stage_id and roadmap_stage_id not in c["roadmap_stages"]:
            continue

        results.append(c)

    # 정렬: 합격률 높은 순 (없으면 낮게)
    if pass_rate_map:
        results.sort(key=lambda c: pass_rate_map.get(c["cert_id"], 0.0), reverse=True)

    return results[:top_n]


# ---------- 출력 ----------
def print_results(
    results: list[dict],
    domain_map: dict,
    job_map: dict,
    roadmap_map: dict,
    scenario_label: str,
):
    print(f"\n{'='*60}")
    print(f"시나리오: {scenario_label}")
    print(f"추천 결과: {len(results)}개")
    print('='*60)
    for i, c in enumerate(results, 1):
        domain_names = [domain_map.get(d, d) for d in c["related_domains"][:3]]
        job_names    = [job_map.get(j, j) for j in c["related_jobs"][:3]]
        rm_names     = [roadmap_map.get(r, r) for r in c["roadmap_stages"]]
        print(f"\n  [{i:2}] {c['cert_name']}  (tier: {c.get('cert_grade_tier','?')})")
        print(f"       도메인: {', '.join(domain_names)}")
        if job_names:
            print(f"       직무:   {', '.join(job_names)}")
        print(f"       로드맵: {', '.join(rm_names)}")
        print(f"       위험군: {', '.join(c['recommended_risk_stages'])}")


# ---------- 시나리오 ----------
def run_scenarios(
    candidates, domain_map, job_map, risk_map, roadmap_map, pass_rate_map
):
    print("\n[마스터 통계]")
    print(f"  전체 후보: {len(candidates)}개")
    tier_dist: dict[str, int] = {}
    for c in candidates:
        t = c.get("cert_grade_tier", "") or "비기술"
        tier_dist[t] = tier_dist.get(t, 0) + 1
    for t, n in sorted(tier_dist.items()):
        print(f"    {t or '(빈값=비기술)': <15}: {n}개")

    # ── 시나리오 1: risk_0005 (취업 가장 어려운 단계) + IT 도메인 ──
    it_domains = ["domain_0002", "domain_0003", "domain_0004"]  # 소프트웨어/IT/정보통신
    results = recommend(
        candidates, risk_stage_id="risk_0005",
        domain_ids=it_domains, pass_rate_map=pass_rate_map, top_n=10
    )
    print_results(results, domain_map, job_map, roadmap_map,
                  f"risk_0005({risk_map['risk_0005']}) + IT 도메인 (domain_0002/0003/0004)")

    # ── 시나리오 2: risk_0003 (중간) + 건설/건축 도메인 ──
    const_domains = ["domain_0010", "domain_0011"]  # 건축, 토목
    results = recommend(
        candidates, risk_stage_id="risk_0003",
        domain_ids=const_domains, pass_rate_map=pass_rate_map, top_n=10
    )
    print_results(results, domain_map, job_map, roadmap_map,
                  f"risk_0003({risk_map['risk_0003']}) + 건축/토목 도메인")

    # ── 시나리오 3: risk_0001 (안정권) + 전기/전자 + roadmap_stage_0005 (유지·정착) ──
    results = recommend(
        candidates, risk_stage_id="risk_0001",
        domain_ids=["domain_0005"], roadmap_stage_id="roadmap_stage_0005",
        pass_rate_map=pass_rate_map, top_n=10
    )
    print_results(results, domain_map, job_map, roadmap_map,
                  f"risk_0001({risk_map['risk_0001']}) + 전기/전자 + 로드맵 유지·정착")

    # ── 시나리오 4: risk_0004 + 조리/식품 도메인 (기능사 위주) ──
    results = recommend(
        candidates, risk_stage_id="risk_0004",
        domain_ids=["domain_0030"], pass_rate_map=pass_rate_map, top_n=10
    )
    print_results(results, domain_map, job_map, roadmap_map,
                  f"risk_0004({risk_map['risk_0004']}) + 조리/식품")


# ---------- 진입점 ----------
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("cert_candidates.csv 기반 추천 동작 검증")
    candidates, domain_map, job_map, risk_map, roadmap_map, pass_rate_map = load_data()
    run_scenarios(candidates, domain_map, job_map, risk_map, roadmap_map, pass_rate_map)

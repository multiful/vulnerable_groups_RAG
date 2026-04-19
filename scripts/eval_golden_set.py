# File: eval_golden_set.py
# Last Updated: 2026-04-19
# Content Hash: SHA256:TBD
# Role: golden_set.jsonl 자동 평가 runner — 추천 정책 변경 회귀 감지
#
# 실행: python scripts/eval_golden_set.py
#        python scripts/eval_golden_set.py --persona P21   (단일 persona)
#        python scripts/eval_golden_set.py --fail-fast      (첫 FAIL 시 중단)
#
# 출력:
#   각 persona 별 evaluation_criteria 패턴 매칭 결과 (PASS/FAIL/WARN/MANUAL)
#   MANUAL: 자동 검증 불가 — 사람 검토 필요
#   Jaccard: P21은 hard-fail, 나머지는 drift-warning
#   마지막 줄: 전체 통과율 요약

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(_ROOT))

from backend.app.services.recommendation_service import (  # noqa: E402
    _load_candidates,
    recommendations,
)

_GOLDEN_SET = _ROOT / "docs/evaluation/golden_set.jsonl"

# P21만 expected_roadmap_cert_ids Jaccard hard-fail
_HARD_JACCARD_PERSONAS: set[str] = {"P21"}
_JACCARD_THRESHOLD = 0.6

# ── 출력 레이블 ──
PASS   = "✅ PASS  "
FAIL   = "❌ FAIL  "
WARN   = "⚠️  WARN  "
MANUAL = "👁  MANUAL"


# ── 보조 함수 ──

def _seq(data: dict) -> list[dict]:
    return data.get("roadmap_sequence", [])

def _seq_cert_ids(data: dict) -> list[str]:
    return [s["cert_id"] for s in _seq(data)]

def _seq_tiers(data: dict) -> list[str]:
    return [s.get("cert_grade_tier", "") or "" for s in _seq(data)]

def _seq_stages(data: dict) -> list[str]:
    return [s.get("roadmap_stage_id", "") for s in _seq(data)]

def _seq_domains(data: dict) -> list[str]:
    return [s.get("primary_domain", "") for s in _seq(data)]

def _stage_num(stage_id: str) -> int:
    """'roadmap_stage_0004' → 4. 파싱 실패 시 0."""
    m = re.search(r"(\d+)$", stage_id)
    return int(m.group(1)) if m else 0

def jaccard(a: list[str], b: list[str]) -> float:
    s1, s2 = set(a), set(b)
    if not s1 and not s2:
        return 1.0
    inter = len(s1 & s2)
    union = len(s1 | s2)
    return inter / union if union else 0.0


# ── 단일 criterion 검사 ──

def _check_criterion(criterion: str, data: dict, tier_map: dict[str, str]) -> tuple[str, str]:
    """
    Returns (status_label, detail_str).
    매칭되는 패턴이 없으면 MANUAL 반환 (절대 silently skip 금지).
    """

    # 1. starting_roadmap_stage=xxx
    m = re.search(r"starting_roadmap_stage=(roadmap_stage_\w+)", criterion)
    if m:
        expected = m.group(1)
        actual = (data.get("starting_roadmap_stage") or {}).get("id", "")
        if actual == expected:
            return PASS, f"starting={actual}"
        return FAIL, f"expected={expected}, actual={actual}"

    # 2. entry_advanced=true/false
    m = re.search(r"entry_advanced=(true|false)", criterion, re.I)
    if m:
        exp_bool = m.group(1).lower() == "true"
        actual = data.get("entry_advanced", False)
        if actual == exp_bool:
            return PASS, f"entry_advanced={actual}"
        return FAIL, f"expected={exp_bool}, actual={actual}"

    # 3. fallback_used=true/false  (괄호·주석 포함 형태도 처리)
    m = re.search(r"fallback_used=(true|false)", criterion, re.I)
    if m:
        exp_bool = m.group(1).lower() == "true"
        actual = data.get("fallback_used", False)
        if actual == exp_bool:
            return PASS, f"fallback_used={actual}"
        return FAIL, f"expected={exp_bool}, actual={actual}"

    # 4. cert 결과에서 제외 / 결과에 없는가  (cert_XXXX·cert_YYYY 형태 포함)
    if "결과에서 제외" in criterion or "결과에 없는가" in criterion:
        cert_ids = re.findall(r"cert_\w+", criterion)
        if cert_ids:
            seq_ids = set(_seq_cert_ids(data))
            leaked = [cid for cid in cert_ids if cid in seq_ids]
            if not leaked:
                return PASS, f"{cert_ids} 모두 제외됨"
            return FAIL, f"제외 실패: {leaked}"

    # 5. domain_XXXX 관련 자격증 포함
    m = re.search(r"(domain_\w+).*(?:자격증 포함|관련 자격증)", criterion)
    if m:
        domain_id = m.group(1)
        if domain_id in _seq_domains(data):
            return PASS, f"{domain_id} 포함"
        return FAIL, f"{domain_id} 미포함 (실제 domains: {set(_seq_domains(data))})"

    # 6. achievability immediate/near_term 포함
    if "achievability" in criterion and ("immediate" in criterion or "near_term" in criterion):
        achievs = {s.get("achievability", "") for s in _seq(data)}
        if "immediate" in achievs or "near_term" in achievs:
            return PASS, f"achievability 분포: {achievs}"
        return FAIL, f"immediate/near_term 없음. 분포: {achievs}"

    # 7. cert_paths[0].path_score >= X.XX
    m = re.search(r"cert_paths\[0\]\.path_score\s*>=\s*([\d.]+)", criterion)
    if m:
        threshold = float(m.group(1))
        paths = data.get("cert_paths", [])
        if not paths:
            return FAIL, "cert_paths 비어 있음"
        score = paths[0].get("path_score", 0.0)
        if score >= threshold:
            return PASS, f"path_score={score:.4f}"
        return FAIL, f"path_score={score:.4f} < {threshold}"

    # 8. cert_paths 최소 N개
    m = re.search(r"cert_paths 최소 (\d+)개", criterion)
    if m:
        min_n = int(m.group(1))
        count = len(data.get("cert_paths", []))
        if count >= min_n:
            return PASS, f"cert_paths={count}"
        return FAIL, f"cert_paths={count} < {min_n}"

    # 9. cert_paths start=기능사, end=기술사/기능장
    if "cert_paths" in criterion and ("path의 start" in criterion or "각 path의 start" in criterion):
        paths = data.get("cert_paths", [])
        if not paths:
            return FAIL, "cert_paths 비어 있음"
        ok_start = ok_end = 0
        for p in paths:
            start_tier = tier_map.get(p.get("start_cert_id", ""), "")
            end_tier   = tier_map.get(p.get("end_cert_id", ""), "")
            if start_tier == "1_기능사":
                ok_start += 1
            if end_tier in ("4_기술사", "5_기능장"):
                ok_end += 1
        total = len(paths)
        starts = [tier_map.get(p.get("start_cert_id",""),"?") for p in paths]
        ends   = [tier_map.get(p.get("end_cert_id",""),"?") for p in paths]
        if ok_start > 0 and ok_end > 0:
            return PASS, f"starts={starts} ends={ends}"
        return FAIL, f"starts={starts} ends={ends}"

    # 10. roadmap_sequence top N 모두 특정 tier
    m = re.search(r"roadmap_sequence top (\d+) 모두.*cert_grade_tier", criterion)
    if m:
        n = int(m.group(1))
        allowed = re.findall(r"'([^']+)'", criterion)
        top_tiers = _seq_tiers(data)[:n]
        # 비기술자격은 tier 없음 — 허용 tier 목록에 없으면 주의
        bad = [t for t in top_tiers if t and t != "비기술자격" and t not in allowed]
        if not bad:
            return PASS, f"top {n} tiers={set(t for t in top_tiers if t)}"
        return FAIL, f"비허용 tier: {set(bad)} (허용: {allowed})"

    # 11. tier 자격증만 포함되는가 (특정 tier만 허용)
    if "자격증만 포함되는가" in criterion:
        allowed_tiers = re.findall(r"(\d_\S+?) tier", criterion)
        if allowed_tiers:
            tech_tiers = [t for t in _seq_tiers(data) if t and t != "비기술자격"]
            bad = [t for t in tech_tiers if t not in allowed_tiers]
            if not bad:
                return PASS, f"all tech tiers in {allowed_tiers}"
            return FAIL, f"비허용 tier: {set(bad)}"

    # 12. tier 자격증이 포함되는가 (특정 tier 존재 확인)
    if "자격증이 포함되는가" in criterion:
        required_tiers = re.findall(r"(\d_\S+?) tier", criterion)
        if required_tiers:
            tiers = set(_seq_tiers(data))
            found = [t for t in required_tiers if t in tiers]
            if found:
                return PASS, f"tier {found} 포함"
            return FAIL, f"필요 tier {required_tiers} 미포함. 실제: {tiers}"

    # 13. stage_NNNN 이상 자격증만 추천되는가
    m = re.search(r"stage_(\d+) 이상 자격증만 추천", criterion)
    if m:
        min_num = int(m.group(1))
        stages = _seq_stages(data)
        bad = [s for s in stages if s and _stage_num(s) < min_num]
        if not bad:
            return PASS, f"all stages >= {min_num}"
        return FAIL, f"stage < {min_num}: {set(bad)}"

    # 14. roadmap_sequence의 첫 자격증 stage 확인
    if "첫 자격증" in criterion and "속하는가" in criterion:
        stage_ids = re.findall(r"roadmap_stage_\d+", criterion)
        # "stage_0001" 형태도 허용
        stage_nums = re.findall(r"stage_(\d+)", criterion)
        seq_list = _seq(data)
        if not seq_list:
            return FAIL, "roadmap_sequence 비어 있음"
        first_stage = seq_list[0].get("roadmap_stage_id", "")
        first_num = _stage_num(first_stage)
        if first_stage in stage_ids or str(first_num).zfill(4) in stage_nums:
            return PASS, f"첫 stage={first_stage}"
        return FAIL, f"첫 stage={first_stage}, 기대: {stage_ids or stage_nums}"

    # 15. is_bottleneck 자격증이 후반부에만 등장
    if "is_bottleneck" in criterion and "후반부" in criterion:
        seq_list = _seq(data)
        bn_steps = [s["step"] for s in seq_list if s.get("is_bottleneck")]
        total = len(seq_list)
        half = total // 2
        early = [s for s in bn_steps if s <= half]
        if not early:
            return PASS, f"bottleneck steps={bn_steps} (total={total})"
        return WARN, f"전반부 bottleneck 존재: {early} (total={total})"

    # 16. is_bottleneck 자격증 0건
    if "is_bottleneck" in criterion and "0건" in criterion:
        seq_list = _seq(data)
        bn = [s["cert_name"] for s in seq_list if s.get("is_bottleneck")]
        if not bn:
            return PASS, "is_bottleneck=0건"
        return WARN, f"is_bottleneck 있음: {bn[:5]}"

    # 17. roadmap_by_stage[order=N]는 비어 있거나 0 certs
    m = re.search(r"roadmap_by_stage\[order=(\d+)\]", criterion)
    if m:
        target_order = int(m.group(1))
        for entry in data.get("roadmap_by_stage", []):
            if (entry.get("stage") or {}).get("order") == target_order:
                cnt = len(entry.get("recommended_certs", []))
                if cnt == 0:
                    return PASS, f"stage order={target_order} certs=0"
                return FAIL, f"stage order={target_order} certs={cnt} (기대=0)"
        return WARN, f"stage order={target_order} 없음"

    # 18. 기능사가 step 1~5에 집중
    if "기능사" in criterion and "step 1" in criterion:
        first5 = _seq(data)[:5]
        funcs = [s for s in first5 if s.get("cert_grade_tier") == "1_기능사"]
        if len(funcs) >= 3:
            return PASS, f"step 1~5 기능사={len(funcs)}개"
        return WARN, f"step 1~5 기능사={len(funcs)}개 (기대 ≥3)"

    # 19. total_certs_in_roadmap 관찰 (hard check 없음 — WARN만)
    if "total_certs_in_roadmap" in criterion:
        total = data.get("total_certs_in_roadmap", 0)
        return WARN, f"total_certs_in_roadmap={total} (수동 비교 필요)"

    return MANUAL, criterion[:100]


# ── 구조적 체크 (expected_* 필드 기반) ──

def _structural_checks(persona: dict, data: dict) -> list[tuple[str, str, str]]:
    """[(check_name, status, detail), ...]"""
    checks = []

    # entry_stage
    exp_stage = persona.get("expected_entry_stage", "")
    if exp_stage:
        actual = (data.get("starting_roadmap_stage") or {}).get("id", "")
        if actual == exp_stage:
            checks.append(("entry_stage", PASS, f"{actual}"))
        else:
            checks.append(("entry_stage", FAIL, f"expected={exp_stage} actual={actual}"))

    # entry_advanced
    exp_adv = persona.get("expected_entry_advanced")
    if exp_adv is not None:
        actual = data.get("entry_advanced", False)
        if actual == exp_adv:
            checks.append(("entry_advanced", PASS, f"{actual}"))
        else:
            checks.append(("entry_advanced", FAIL, f"expected={exp_adv} actual={actual}"))

    # fallback_used (P21에만 있음)
    exp_fb = persona.get("expected_fallback_used")
    if exp_fb is not None:
        actual = data.get("fallback_used", False)
        if actual == exp_fb:
            checks.append(("fallback_used", PASS, f"{actual}"))
        else:
            checks.append(("fallback_used", FAIL, f"expected={exp_fb} actual={actual}"))

    # baseline_total_certs (INFO)
    baseline = persona.get("baseline_total_certs")
    if baseline is not None:
        actual = data.get("total_certs_in_roadmap", 0)
        diff = actual - baseline
        label = PASS if abs(diff) <= 5 else WARN
        checks.append(("total_certs", label, f"actual={actual} baseline={baseline} diff={diff:+d}"))

    return checks


# ── Jaccard 체크 ──

def _jaccard_check(persona: dict, data: dict) -> tuple[str, str, str]:
    expected_ids = persona.get("expected_roadmap_cert_ids", [])
    if not expected_ids:
        return ("jaccard", MANUAL, "expected_roadmap_cert_ids 없음")
    actual_ids = _seq_cert_ids(data)[:len(expected_ids)]
    j = jaccard(actual_ids, expected_ids)
    hard = persona["persona_id"] in _HARD_JACCARD_PERSONAS
    if j >= _JACCARD_THRESHOLD:
        label = PASS
    elif hard:
        label = FAIL
    else:
        label = WARN
    mode = "hard" if hard else "drift-warn"
    return ("jaccard", label, f"J={j:.2f} ({mode}) expected={expected_ids[:3]}...")


# ── 전체 평가 ──

def eval_persona(persona: dict, tier_map: dict[str, str]) -> dict:
    pid = persona["persona_id"]
    query = persona["input_query"]
    criteria = persona.get("evaluation_criteria", [])

    resp = recommendations(query)
    if not resp.get("success"):
        return {
            "persona_id": pid,
            "error": resp.get("error"),
            "checks": [],
            "pass": 0, "fail": 1, "warn": 0, "manual": 0,
        }

    data = resp["data"]
    results: list[tuple[str, str, str]] = []

    # 구조적 체크
    results += _structural_checks(persona, data)

    # Jaccard
    results.append(_jaccard_check(persona, data))

    # evaluation_criteria 패턴 매칭
    for i, crit in enumerate(criteria):
        status, detail = _check_criterion(crit, data, tier_map)
        results.append((f"criteria[{i}]", status, detail))

    counts = {
        "pass":   sum(1 for _, s, _ in results if s == PASS),
        "fail":   sum(1 for _, s, _ in results if s == FAIL),
        "warn":   sum(1 for _, s, _ in results if s == WARN),
        "manual": sum(1 for _, s, _ in results if s == MANUAL),
    }
    return {"persona_id": pid, "data": data, "checks": results, **counts}


# ── 출력 ──

def print_persona_result(result: dict) -> None:
    pid = result["persona_id"]
    print(f"\n{'='*60}")
    print(f"  Persona: {pid}")
    print(f"{'='*60}")
    if "error" in result:
        print(f"  {FAIL} API error: {result['error']}")
        return
    for name, status, detail in result["checks"]:
        print(f"  {status}  {name:<22} {detail}")
    data = result.get("data", {})
    total = data.get("total_certs_in_roadmap", 0)
    paths = data.get("cert_paths", [])
    print(f"\n  INFO  total_certs={total}  cert_paths={len(paths)}", end="")
    if paths:
        print(f"  top_path_score={paths[0].get('path_score', 0):.4f}", end="")
    print()
    print(f"\n  Summary  PASS={result['pass']}  FAIL={result['fail']}  WARN={result['warn']}  MANUAL={result['manual']}")


def print_summary(results: list[dict]) -> None:
    print(f"\n{'='*60}")
    print(f"  OVERALL SUMMARY")
    print(f"{'='*60}")
    total_pass = total_fail = total_warn = total_manual = 0
    for r in results:
        total_pass   += r["pass"]
        total_fail   += r["fail"]
        total_warn   += r["warn"]
        total_manual += r["manual"]
        status = FAIL if r["fail"] > 0 else (WARN if r["warn"] > 0 else PASS)
        print(f"  {status}  {r['persona_id']}  PASS={r['pass']} FAIL={r['fail']} WARN={r['warn']} MANUAL={r['manual']}")
    print(f"\n  TOTAL  PASS={total_pass}  FAIL={total_fail}  WARN={total_warn}  MANUAL={total_manual}")
    rate = total_pass / (total_pass + total_fail) * 100 if (total_pass + total_fail) else 0
    print(f"  PASS RATE  {rate:.1f}%  ({total_pass}/{total_pass+total_fail})")
    if total_fail == 0:
        print("\n  ✅ All automated checks passed.")
    else:
        print(f"\n  ❌ {total_fail} check(s) FAILED — see details above.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Golden set 자동 평가 runner")
    parser.add_argument("--persona", help="단일 persona_id만 실행 (예: P21)")
    parser.add_argument("--fail-fast", action="store_true", help="첫 FAIL 시 중단")
    args = parser.parse_args()

    if not _GOLDEN_SET.exists():
        print(f"[ERROR] golden_set.jsonl 없음: {_GOLDEN_SET}", file=sys.stderr)
        return 1

    personas = []
    with _GOLDEN_SET.open(encoding="utf-8") as f:
        for line in f:
            if s := line.strip():
                personas.append(json.loads(s))

    if args.persona:
        personas = [p for p in personas if p["persona_id"] == args.persona]
        if not personas:
            print(f"[ERROR] persona '{args.persona}' 없음", file=sys.stderr)
            return 1

    # cert_id → tier 맵 (단일 로드)
    tier_map = {c["cert_id"]: c.get("cert_grade_tier", "") for c in _load_candidates()}
    print(f"[INFO] tier_map {len(tier_map)}개 로드 | persona {len(personas)}개 평가")

    results = []
    for persona in personas:
        result = eval_persona(persona, tier_map)
        print_persona_result(result)
        results.append(result)
        if args.fail_fast and result["fail"] > 0:
            print("\n[FAIL-FAST] 첫 FAIL 감지 — 중단")
            break

    print_summary(results)
    total_fail = sum(r["fail"] for r in results)
    return 1 if total_fail > 0 else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

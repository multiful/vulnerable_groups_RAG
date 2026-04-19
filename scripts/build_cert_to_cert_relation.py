# File: build_cert_to_cert_relation.py
# Last Updated: 2026-04-19
# Content Hash: SHA256:TBD
# Change: A1 fix — _RELATION_TYPE_MAP 제거 (recommended_prior→next_step 오매핑 수정)
#         N6 add — _TIER_ORDER 기반 역방향 행 자동 swap/drop 빌드 가드
# Role: cert_prerequisite.csv(NCS 체계) + parse_ir 텍스트 스캔 → cert_to_cert_relation.csv 생성
#
# 실행: python scripts/build_cert_to_cert_relation.py
#
# 출처 처리 (§P4 통합 규칙):
#   1. parse_ir/ JSONL 블록에서 선행/후행 관계 문장 추출 → reasoning_evidence 직접 기입.
#   2. cert_prerequisite.csv (NCS 기능사→산업기사→기사 체계) → evidence="NCS 공식 자격 체계 기준".
#   3. 동일 (from, to) pair 가 두 소스에 동시 존재하면 MERGE:
#      - relation_type  : 강한 타입 우선 (prerequisite > recommended_prior > next_step)
#      - source         : "parse_ir|cert_prerequisite" 로 병합 표기
#      - reasoning_evidence: parse_ir 문장을 우선 (NCS 일반 문구보다 구체적)
#      - confidence     : 1.0 (양쪽 확인), parse_ir 단독 0.8, prereq 단독 1.0
#
# 컬럼: relation_id, from_cert_id, to_cert_id, relation_type, reasoning_evidence, source, confidence, is_active

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).parents[1]
_PREREQ_CSV   = _ROOT / "data/canonical/relations/cert_prerequisite.csv"
_OUT_CSV      = _ROOT / "data/canonical/relations/cert_to_cert_relation.csv"
_PARSE_IR_DIR = _ROOT / "data/index_ready/parse_ir"
_CANDIDATES   = _ROOT / "data/canonical/candidates/cert_candidates.jsonl"

# 관계 키워드 (선행·선수·취득 후 등)
_REL_KEYWORDS = [
    "선행", "선수", "취득 후", "취득후", "기능사 취득", "산업기사 취득",
    "기사 취득", "이수 후", "취득하여야", "취득해야",
]

# N6: cert_grade_tier 기반 방향 검증 (낮은 tier → 높은 tier 방향만 허용)
_TIER_ORDER: dict[str, int] = {
    "1_기능사": 1, "2_산업기사": 2, "3_기사": 3, "4_기술사": 4, "5_기능장": 5,
}


def _cert_name_map() -> dict[str, str]:
    """cert_name → cert_id (cert_candidates.jsonl 기준)"""
    out: dict[str, str] = {}
    if not _CANDIDATES.exists():
        return out
    with _CANDIDATES.open(encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            out[c["cert_name"].strip()] = c["cert_id"]
            for alias in c.get("aliases", []):
                if isinstance(alias, str):
                    out[alias.strip()] = c["cert_id"]
    return out


def _cert_tier_map() -> dict[str, str]:
    """cert_id → cert_grade_tier (cert_candidates.jsonl 기준). 비기술자격은 포함 안 함."""
    out: dict[str, str] = {}
    if not _CANDIDATES.exists():
        return out
    with _CANDIDATES.open(encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            tier = c.get("cert_grade_tier", "")
            if tier:
                out[c["cert_id"]] = tier
    return out


def _extract_parse_ir_evidence(cert_name_map: dict[str, str]) -> list[dict]:
    """parse_ir/ 파일 스캔 → cert 이름이 두 개 이상 포함된 관계 문장 추출"""
    if not _PARSE_IR_DIR.exists():
        return []
    rows: list[dict] = []
    cert_names = list(cert_name_map.keys())

    for fpath in sorted(_PARSE_IR_DIR.glob("*.json")):
        try:
            with fpath.open(encoding="utf-8") as f:
                doc = json.load(f)
        except Exception:
            continue
        blocks = doc.get("blocks", [])
        for block in blocks:
            txt = str(block.get("text", "")).strip()
            if len(txt) < 20:
                continue
            if not any(k in txt for k in _REL_KEYWORDS):
                continue
            # 문장 내 cert 이름 탐색
            found = [name for name in cert_names if name in txt]
            if len(found) < 2:
                continue
            # 쌍 생성 (앞 cert → 뒤 cert: 앞이 선행으로 추정)
            sentence = re.sub(r"\s+", " ", txt)[:300]
            for i in range(len(found) - 1):
                from_id = cert_name_map.get(found[i])
                to_id   = cert_name_map.get(found[i + 1])
                if from_id and to_id and from_id != to_id:
                    rows.append({
                        "from_cert_id": from_id,
                        "to_cert_id": to_id,
                        "relation_type": "next_step",
                        "reasoning_evidence": sentence,
                        "source": f"parse_ir:{fpath.stem}",
                    })
    return rows


def _load_prereq_rows() -> list[dict]:
    """cert_prerequisite.csv → cert_to_cert_relation 형식으로 변환"""
    if not _PREREQ_CSV.exists():
        print(f"[WARN] {_PREREQ_CSV} not found — skipping NCS rows")
        return []
    rows = []
    with _PREREQ_CSV.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get("is_active", "True").lower() != "true":
                continue
            rows.append({
                "from_cert_id":      r["prerequisite_cert_id"],
                "to_cert_id":        r["cert_id"],
                "relation_type":     r.get("relation_kind", "next_step"),
                "reasoning_evidence": "NCS 공식 자격 체계 기준",
                "source":            "cert_prerequisite",
            })
    return rows


# relation_type 우선순위 (강한 타입이 약한 타입을 덮어쓴다)
_REL_TYPE_RANK = {
    "prerequisite":      3,
    "recommended_prior": 2,
    "next_step":         1,
    "":                  0,
}


def _stronger_type(a: str, b: str) -> str:
    return a if _REL_TYPE_RANK.get(a, 0) >= _REL_TYPE_RANK.get(b, 0) else b


def _merge_sources(src_a: str, src_b: str) -> str:
    tokens: list[str] = []
    for s in (src_a, src_b):
        if not s:
            continue
        base = s.split(":")[0]
        if base not in tokens:
            tokens.append(base)
    return "|".join(tokens)


def build():
    print("=== cert_to_cert_relation.csv 생성 ===")
    cert_name_map = _cert_name_map()
    cert_tier_map = _cert_tier_map()
    print(f"cert_name_map: {len(cert_name_map)}개 이름 로드")
    print(f"cert_tier_map: {len(cert_tier_map)}개 tier 로드")

    # 1. parse_ir 추출
    ir_rows = _extract_parse_ir_evidence(cert_name_map)
    print(f"parse_ir 추출: {len(ir_rows)}건")

    # 2. NCS cert_prerequisite.csv
    prereq_rows = _load_prereq_rows()
    print(f"NCS 체계(cert_prerequisite): {len(prereq_rows)}건")

    # 3. §P4 통합 규칙: 동일 (from,to) pair 는 merge (둘 다 있으면 강한 relation_type,
    #    parse_ir reasoning, source 합본, confidence=1.0)
    merged_map: dict[tuple[str, str], dict] = {}

    # parse_ir 먼저 적재 (reasoning_evidence 기준으로 삼기 위함)
    for row in ir_rows:
        key = (row["from_cert_id"], row["to_cert_id"])
        merged_map[key] = {
            **row,
            "source":     row.get("source", "parse_ir"),
            "confidence": 0.8,
        }

    for row in prereq_rows:
        key = (row["from_cert_id"], row["to_cert_id"])
        if key in merged_map:
            prev = merged_map[key]
            prev["relation_type"] = _stronger_type(prev["relation_type"], row["relation_type"])
            prev["source"]        = _merge_sources(prev.get("source", ""), row.get("source", ""))
            prev["confidence"]    = 1.0  # 양쪽 확인
            # reasoning_evidence: parse_ir 원문을 유지 (구체적 원문 선호)
        else:
            merged_map[key] = {
                **row,
                "source":     row.get("source", "cert_prerequisite"),
                "confidence": 1.0,  # NCS 공식 체계 단독
            }

    merged_raw = list(merged_map.values())

    # N6: 방향 검증 — from_tier ≤ to_tier (낮은 등급 → 높은 등급 방향만 허용)
    # 양쪽 tier가 있고 from_tier > to_tier면 swap. 동일 tier면 drop (자기 참조성).
    direction_swapped = 0
    direction_dropped = 0
    merged: list[dict] = []
    for row in merged_raw:
        from_tier_order = _TIER_ORDER.get(cert_tier_map.get(row["from_cert_id"], ""), 0)
        to_tier_order   = _TIER_ORDER.get(cert_tier_map.get(row["to_cert_id"],   ""), 0)
        if from_tier_order > 0 and to_tier_order > 0:
            if from_tier_order > to_tier_order:
                # 역방향 — swap
                row["from_cert_id"], row["to_cert_id"] = row["to_cert_id"], row["from_cert_id"]
                direction_swapped += 1
            elif from_tier_order == to_tier_order:
                # 동일 tier — 무의미한 관계 drop
                direction_dropped += 1
                continue
        merged.append(row)
    print(f"N6 방향 검증: swapped={direction_swapped}, dropped={direction_dropped}")

    # 안정 순서: from → to
    merged.sort(key=lambda r: (r["from_cert_id"], r["to_cert_id"]))

    # 4. relation_id 부여
    #    §P4 안전장치: parse_ir 단독 (confidence<1.0) 은 추출 로직 신뢰성 이슈로
    #    is_active=False 로 내린다. NCS 단독 (1.0) 및 양측 확인 (1.0) 만 그래프에 반영.
    #    (build_cert_to_cert_relation.py 의 reasoning_evidence 추출기는 키워드 근접성 검사를
    #     수행하지 않아 긴 자격증 리스트에서 인접쌍을 기계적으로 만들어내는 노이즈가 있다.)
    out_rows = []
    disabled_cnt = 0
    for idx, row in enumerate(merged, 1):
        rid = f"c2c_{idx:05d}"
        active = row["confidence"] >= 1.0
        if not active:
            disabled_cnt += 1
        out_rows.append({
            "relation_id":        rid,
            "from_cert_id":       row["from_cert_id"],
            "to_cert_id":         row["to_cert_id"],
            "relation_type":      row["relation_type"],
            "reasoning_evidence": row["reasoning_evidence"],
            "source":             row["source"],
            "confidence":         f"{row['confidence']:.2f}",
            "is_active":          "True" if active else "False",
        })

    # 5. 저장
    _OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["relation_id", "from_cert_id", "to_cert_id",
                  "relation_type", "reasoning_evidence", "source",
                  "confidence", "is_active"]
    with _OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"저장 완료: {_OUT_CSV}  ({len(out_rows)}행, is_active=False {disabled_cnt}행)")
    # 소스별 통계 (병합 source 포함)
    from collections import Counter
    src_cnt = Counter(r["source"] for r in out_rows)
    for src, cnt in src_cnt.most_common():
        print(f"  source={src}: {cnt}행")
    type_cnt = Counter(r["relation_type"] for r in out_rows)
    for t, cnt in type_cnt.most_common():
        print(f"  relation_type={t}: {cnt}행")
    conf_cnt = Counter(r["confidence"] for r in out_rows)
    for c, cnt in sorted(conf_cnt.items()):
        print(f"  confidence={c}: {cnt}행")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()

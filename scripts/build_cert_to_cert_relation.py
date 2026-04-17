# File: build_cert_to_cert_relation.py
# Last Updated: 2026-04-18
# Content Hash: SHA256:TBD
# Role: cert_prerequisite.csv(NCS 체계) + parse_ir 텍스트 스캔 → cert_to_cert_relation.csv 생성
#
# 실행: python scripts/build_cert_to_cert_relation.py
#
# 출처 우선순위:
#   1. parse_ir/ JSONL 블록에서 선행/후행 관계 문장 추출 → reasoning_evidence 직접 기입
#   2. cert_prerequisite.csv (NCS 기능사→산업기사→기사 체계) → evidence="NCS 공식 자격 체계 기준"
#
# 컬럼: relation_id, from_cert_id, to_cert_id, relation_type, reasoning_evidence, source, is_active

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
_RELATION_TYPE_MAP = {
    "recommended_prior": "next_step",
    "prerequisite": "prerequisite",
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
                "relation_type":     _RELATION_TYPE_MAP.get(r.get("relation_kind", ""), "next_step"),
                "reasoning_evidence": "NCS 공식 자격 체계 기준",
                "source":            "cert_prerequisite",
            })
    return rows


def build():
    print("=== cert_to_cert_relation.csv 생성 ===")
    cert_name_map = _cert_name_map()
    print(f"cert_name_map: {len(cert_name_map)}개 이름 로드")

    # 1. parse_ir 추출
    ir_rows = _extract_parse_ir_evidence(cert_name_map)
    print(f"parse_ir 추출: {len(ir_rows)}건")

    # 2. NCS cert_prerequisite.csv
    prereq_rows = _load_prereq_rows()
    print(f"NCS 체계(cert_prerequisite): {len(prereq_rows)}건")

    # 3. 중복 제거 (from+to 쌍 기준) — parse_ir 우선
    seen: set[tuple] = set()
    merged: list[dict] = []
    for row in ir_rows + prereq_rows:
        key = (row["from_cert_id"], row["to_cert_id"])
        if key not in seen:
            seen.add(key)
            merged.append(row)

    # 4. relation_id 부여
    out_rows = []
    for idx, row in enumerate(merged, 1):
        rid = f"c2c_{idx:05d}"
        out_rows.append({
            "relation_id":        rid,
            "from_cert_id":       row["from_cert_id"],
            "to_cert_id":         row["to_cert_id"],
            "relation_type":      row["relation_type"],
            "reasoning_evidence": row["reasoning_evidence"],
            "source":             row["source"],
            "is_active":          "True",
        })

    # 5. 저장
    _OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["relation_id", "from_cert_id", "to_cert_id",
                  "relation_type", "reasoning_evidence", "source", "is_active"]
    with _OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"저장 완료: {_OUT_CSV}  ({len(out_rows)}행)")
    # 소스별 통계
    from collections import Counter
    src_cnt = Counter(r["source"].split(":")[0] for r in out_rows)
    for src, cnt in src_cnt.most_common():
        print(f"  {src}: {cnt}행")
    type_cnt = Counter(r["relation_type"] for r in out_rows)
    for t, cnt in type_cnt.most_common():
        print(f"  relation_type={t}: {cnt}행")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()

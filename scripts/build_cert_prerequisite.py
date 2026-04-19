# File: build_cert_prerequisite.py
# Last Updated: 2026-04-18
# Content Hash: SHA256:TBD
# Role: cert_master → cert_prerequisite.csv 생성 (cross-domain 이슈 해결 + 커버리지 보강)
#
# 생성 규칙 (MASTER_MERGE_PLAN §5 + §10.1 개선안):
#   1) 동일 domain_name_raw + 동일 subject_prefix (strict 매칭) 내 grade_tier 단계 연결
#   2) 동일 domain_name_raw 안에서 subject_prefix 포함관계(A ⊂ B)인 경우 같은 그룹으로 병합
#      (예: 토목 ⊂ 토목구조·토목시공·토목재료시험·토목제도·토목품질시험, 측량 ⊂ 측량및지형공간정보)
#      — union-find로 근접 subject 병합, cross-domain 연결은 여전히 금지
#   subject_prefix = cert_name에서 후행 grade 접미사(기능사/산업기사/기사/기술사/기능장) 제거.
#
# 실행: python scripts/build_cert_prerequisite.py

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

_ROOT = Path(__file__).parents[1]
_CERT_MASTER = _ROOT / "data/processed/master/cert_master.csv"
_OUT_CSV = _ROOT / "data/canonical/relations/cert_prerequisite.csv"

_GRADE_SUFFIX_RE = re.compile(r"(기능장|기술사|산업기사|기능사|기사)$")

# (prereq_tier, cert_tier, relation_kind) — prereq = 낮은 tier, cert = 높은 tier
_ALLOWED_PAIRS: list[tuple[str, str, str]] = [
    ("1_기능사",   "2_산업기사", "recommended_prior"),
    ("1_기능사",   "3_기사",     "recommended_prior"),
    ("2_산업기사", "3_기사",     "recommended_prior"),
    ("3_기사",     "4_기술사",   "prerequisite"),
    ("3_기사",     "5_기능장",   "recommended_prior"),
]

_FIELDS = [
    "relation_id",
    "cert_id",
    "prerequisite_cert_id",
    "relation_kind",
    "domain_name_raw",
    "subject_prefix",
    "is_active",
]


def _extract_subject_prefix(cert_name: str) -> str | None:
    m = _GRADE_SUFFIX_RE.search(cert_name)
    if not m or m.start() == 0:
        return None
    return cert_name[: m.start()]


def _union_find_groups(subjects: list[str]) -> dict[str, str]:
    """subject_prefix 간 포함관계를 union-find로 묶어 각 subject → 대표(root) 매핑 반환.
    동일 domain 내부에서만 호출한다.

    매칭 규칙 (둘 중 하나라도 만족하면 union):
      - prefix 포함: A.startswith(B) or B.startswith(A)        (예: 토목 ⊂ 토목구조, 측량 ⊂ 측량및지형공간정보)
      - suffix 포함: A.endswith(B) or B.endswith(A)            (예: 용접 ⊂ 특수용접·피복아크용접·가스텅스텐아크용접)

    길이 2 미만 subject 는 noise 방지 위해 결합 후보에서 제외."""
    parent = {s: s for s in subjects}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        # 더 짧은 subject 를 대표로 (공통 근원 키워드)
        if len(ra) <= len(rb):
            parent[rb] = ra
        else:
            parent[ra] = rb

    for i, a in enumerate(subjects):
        for b in subjects[i + 1:]:
            if len(a) < 2 or len(b) < 2:
                continue
            if a.startswith(b) or b.startswith(a) or a.endswith(b) or b.endswith(a):
                union(a, b)
    return {s: find(s) for s in subjects}


def build() -> None:
    with _CERT_MASTER.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # (domain_name_raw, subject_prefix) → tier → [cert_id, ...]
    raw: dict[tuple[str, str], dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    skipped_no_tier = 0
    skipped_no_domain = 0
    skipped_no_prefix = 0
    for r in rows:
        tier = r.get("cert_grade_tier", "").strip()
        if not tier:
            skipped_no_tier += 1
            continue
        domain = r.get("domain_name_raw", "").strip()
        if not domain:
            skipped_no_domain += 1
            continue
        prefix = _extract_subject_prefix(r["cert_name"].strip())
        if not prefix:
            skipped_no_prefix += 1
            continue
        raw[(domain, prefix)][tier].append(r["cert_id"])

    # domain 내부에서 subject_prefix 포함관계로 병합 → (domain, root_subject) 그룹
    by_domain: dict[str, list[str]] = defaultdict(list)
    for (domain, prefix) in raw.keys():
        by_domain[domain].append(prefix)

    # (domain, root_subject) → tier → [cert_id, ...]
    groups: dict[tuple[str, str], dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    # (domain, root_subject) → 포함된 원본 subject_prefix 집합 (기록용)
    group_members: dict[tuple[str, str], set[str]] = defaultdict(set)
    for domain, subjects in by_domain.items():
        root_of = _union_find_groups(subjects)
        for prefix in subjects:
            root = root_of[prefix]
            group_members[(domain, root)].add(prefix)
            for tier, cids in raw[(domain, prefix)].items():
                groups[(domain, root)][tier].extend(cids)

    out_rows: list[dict] = []
    idx = 1
    kind_cnt: dict[str, int] = defaultdict(int)
    domain_cnt: dict[str, int] = defaultdict(int)
    for (domain, root), tier_dict in sorted(groups.items()):
        # 기록용 subject_prefix: 그룹에 포함된 원본 subjects 정렬·| 로 결합
        members = sorted(group_members[(domain, root)])
        subject_label = root if len(members) == 1 else f"{root}*"
        for prereq_tier, cert_tier, kind in _ALLOWED_PAIRS:
            for prereq_cid in tier_dict.get(prereq_tier, []):
                for cert_cid in tier_dict.get(cert_tier, []):
                    if prereq_cid == cert_cid:
                        continue
                    out_rows.append(
                        {
                            "relation_id": f"prereq_{idx:05d}",
                            "cert_id": cert_cid,
                            "prerequisite_cert_id": prereq_cid,
                            "relation_kind": kind,
                            "domain_name_raw": domain,
                            "subject_prefix": subject_label,
                            "is_active": "True",
                        }
                    )
                    idx += 1
                    kind_cnt[kind] += 1
                    domain_cnt[domain] += 1

    _OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with _OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=_FIELDS)
        w.writeheader()
        w.writerows(out_rows)

    print(f"=== cert_prerequisite.csv 생성 완료 ===")
    print(f"cert_master 입력: {len(rows):,}행")
    print(f"  skip(grade_tier 없음): {skipped_no_tier:,}")
    print(f"  skip(domain_name_raw 없음): {skipped_no_domain:,}")
    print(f"  skip(subject_prefix 추출 실패): {skipped_no_prefix:,}")
    print(f"그룹 수: (domain × subject_prefix) = {len(groups):,}")
    print(f"출력: {_OUT_CSV.name} — {len(out_rows):,}행")
    print(f"relation_kind 분포:")
    for k, v in sorted(kind_cnt.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v:,}")
    print(f"상위 10개 domain_name_raw (연결 행 수):")
    for d, c in sorted(domain_cnt.items(), key=lambda x: -x[1])[:10]:
        print(f"  {d}: {c:,}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()

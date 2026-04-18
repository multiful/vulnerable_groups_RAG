# Content Hash: SHA256:879374e884f139f6acfa70265838c2da0b206f0608a4f4092ac668e44f7b3334
# Role: candidate JSONL 로드 + taxonomy 검증 + 필터·정렬 (추천 API)
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

from backend.canonical.candidate_row import CertificateCandidateRow, row_from_json_obj
from backend.canonical.taxonomy_labels import labels_from_taxonomy_file


def iter_jsonl_objects(path: Path) -> Iterator[dict[str, Any]]:
    if not path.is_file():
        return
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield obj


class TaxonomyViolation(ValueError):
    """row가 허용된 taxonomy 밖 라벨을 사용했을 때 build-time에 실패시키기 위한 예외."""


def load_validated_candidates(
    jsonl_path: Path,
    domain_labels: set[str],
    job_labels: set[str],
    strict: bool = False,
) -> list[CertificateCandidateRow]:
    """candidate JSONL을 로드하며 taxonomy ID 적합성을 검사한다.

    DATA_SCHEMA.md §9.1.1 참고 — 여기서 사용하는 허용 집합은
    **master CSV ID** 기준이다 (라벨 텍스트가 아니라 ID).

      - `domain_labels` ≔ `data/processed/master/domain_master.csv`의
        `domain_sub_label_id` 집합
      - `job_labels`    ≔ `data/processed/master/job_master.csv`의
        `job_role_id` 집합

    정책 (CLAUDE.md §7 "추천 결과에 taxonomy 밖 값이 나오면 오류로 간주"):

      strict=True  (build/CI용):
        - domain_labels/job_labels 중 하나라도 빈 set이면 즉시 TaxonomyViolation 발생.
        - taxonomy 밖 ID를 쓰는 row를 만나면 즉시 TaxonomyViolation 발생.

      strict=False (runtime fail-open, 기본값):
        - taxonomy set이 비었으면 검증 생략 (파일이 없는 개발/테스트 환경 대응).
        - taxonomy 밖 ID를 쓰는 row는 silent skip.
        - 빌드 단계의 게이트(`scripts/build_cert_candidates.py`)가 1차 방어선이며,
          이 함수는 2차 런타임 방어선이다.
    """
    if strict and (not domain_labels or not job_labels):
        raise TaxonomyViolation(
            "strict mode는 domain/job master ID 집합이 비어 있을 수 없음. "
            "master CSV 경로를 확인하라."
        )
    enforce_domains = bool(domain_labels)
    enforce_jobs = bool(job_labels)
    rows: list[CertificateCandidateRow] = []
    for obj in iter_jsonl_objects(jsonl_path):
        row = row_from_json_obj(obj)
        if row is None:
            continue
        if enforce_domains:
            bad_primary = row.primary_domain not in domain_labels
            bad_related = [d for d in row.related_domains if d not in domain_labels]
            if bad_primary or bad_related:
                if strict:
                    raise TaxonomyViolation(
                        f"candidate_id={row.candidate_id} domain taxonomy 위반: "
                        f"primary={row.primary_domain!r}, related 위반={bad_related}"
                    )
                continue
        if enforce_jobs and row.related_jobs:
            bad_jobs = [j for j in row.related_jobs if j not in job_labels]
            if bad_jobs:
                if strict:
                    raise TaxonomyViolation(
                        f"candidate_id={row.candidate_id} job taxonomy 위반: {bad_jobs}"
                    )
                continue
        rows.append(row)
    return rows


def risk_stage_matches(row: CertificateCandidateRow, risk_stage_id: str) -> bool:
    if not row.recommended_risk_stages:
        return True
    return risk_stage_id in row.recommended_risk_stages


def filter_and_rank(
    rows: list[CertificateCandidateRow],
    risk_stage_id: str,
    interested_domains: list[str] | None,
    interested_jobs: list[str] | None,
    limit: int,
) -> list[CertificateCandidateRow]:
    domains = interested_domains or []
    jobs = interested_jobs or []

    def domain_ok(r: CertificateCandidateRow) -> bool:
        if not domains:
            return True
        if r.primary_domain in domains:
            return True
        return any(d in domains for d in r.related_domains)

    def job_ok(r: CertificateCandidateRow) -> bool:
        if not jobs:
            return True
        if not r.related_jobs:
            return True
        return any(j in jobs for j in r.related_jobs)

    scored: list[tuple[int, CertificateCandidateRow]] = []
    for r in rows:
        if not risk_stage_matches(r, risk_stage_id):
            continue
        if not domain_ok(r):
            continue
        if not job_ok(r):
            continue
        ds = (
            len(set(domains) & set([r.primary_domain, *r.related_domains]))
            if domains
            else 0
        )
        if jobs and r.related_jobs:
            js = len(set(jobs) & set(r.related_jobs))
        elif not jobs:
            js = 1
        else:
            js = 0
        score = ds * 2 + js
        scored.append((score, r))

    scored.sort(key=lambda x: (-x[0], x[1].cert_name))
    return [r for _, r in scored[:limit]]


def to_api_candidate(row: CertificateCandidateRow) -> dict[str, Any]:
    return {
        "candidate_id": row.candidate_id,
        "cert_id": row.cert_id,
        "cert_name": row.cert_name,
        "primary_domain": row.primary_domain,
        "related_jobs": row.related_jobs,
        "related_domains": row.related_domains,
        "roadmap_stages": row.roadmap_stages,
        "summary": row.text_for_dense,
    }

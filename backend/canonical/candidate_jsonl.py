# Content Hash: SHA256:TBD
# Role: candidate JSONL 로드 + taxonomy 검증 + 필터·정렬 (추천 API용)
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
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield obj


def load_validated_candidates(
    jsonl_path: Path,
    domain_labels: set[str],
    job_labels: set[str],
) -> list[CertificateCandidateRow]:
    """taxonomy 집합이 비어 있으면 도메인/직무 라벨 검증은 생략(파일 누락 시 개발 완화)."""
    strict_domains = bool(domain_labels)
    strict_jobs = bool(job_labels)
    rows: list[CertificateCandidateRow] = []
    for obj in iter_jsonl_objects(jsonl_path):
        row = row_from_json_obj(obj)
        if row is None:
            continue
        if strict_domains:
            if row.primary_domain not in domain_labels:
                continue
            if any(d not in domain_labels for d in row.related_domains):
                continue
        if strict_jobs and row.related_jobs:
            if any(j not in job_labels for j in row.related_jobs):
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
        ds = len(set(domains) & set([r.primary_domain, *r.related_domains])) if domains else 0
        js = len(set(jobs) & set(r.related_jobs)) if jobs and r.related_jobs else (1 if not jobs else 0)
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

# File: recommendation_service.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: 추천 후보(JSONL canonical 대용) + evidence 위임
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from backend.app.core.config import Settings
from backend.app.schemas.envelope import err_envelope, ok_envelope
from backend.app.services import retrieval_service
from backend.canonical.candidate_jsonl import (
    filter_and_rank,
    load_validated_candidates,
    to_api_candidate,
)
from backend.canonical.taxonomy_labels import labels_from_taxonomy_file

_RISK_STAGE_ID = re.compile(r"^risk_stage_[1-5]$")


def _resolve_project_path(relative_or_abs: str) -> Path:
    p = Path(relative_or_abs)
    if p.is_absolute():
        return p
    return Path.cwd() / p


def recommendations(body: dict[str, Any], settings: Settings) -> dict[str, Any]:
    risk = body.get("risk_stage_id")
    if not risk:
        return err_envelope(
            "MISSING_REQUIRED_FIELD",
            "risk_stage_id는 필수입니다.",
            {"field": "risk_stage_id"},
        )
    risk_s = str(risk).strip()
    if not _RISK_STAGE_ID.match(risk_s):
        return err_envelope(
            "INVALID_INPUT",
            "risk_stage_id는 risk_stage_1 ~ risk_stage_5 형식이어야 합니다.",
            {"field": "risk_stage_id", "value": risk_s},
        )

    jobs_req = [str(x) for x in (body.get("interested_jobs") or []) if str(x).strip()]
    domains_req = [str(x) for x in (body.get("interested_domains") or []) if str(x).strip()]

    domain_path = _resolve_project_path(settings.taxonomy_domain_relative)
    job_path = _resolve_project_path(settings.taxonomy_job_relative)
    domain_labels = labels_from_taxonomy_file(domain_path)
    job_labels = labels_from_taxonomy_file(job_path)

    if domains_req and domain_labels:
        unknown = [d for d in domains_req if d not in domain_labels]
        if unknown:
            return err_envelope(
                "TAXONOMY_MAPPING_FAILED",
                "interested_domains에 허용되지 않은 라벨이 있습니다.",
                {"field": "interested_domains", "unknown": unknown},
            )

    if jobs_req and job_labels:
        unknown = [j for j in jobs_req if j not in job_labels]
        if unknown:
            return err_envelope(
                "TAXONOMY_MAPPING_FAILED",
                "interested_jobs에 허용되지 않은 라벨이 있습니다.",
                {"field": "interested_jobs", "unknown": unknown},
            )

    jsonl_path = _resolve_project_path(settings.candidates_jsonl_relative)
    rows = load_validated_candidates(jsonl_path, domain_labels, job_labels)
    picked = filter_and_rank(
        rows,
        risk_s,
        domains_req,
        jobs_req,
        settings.recommendation_max_results,
    )

    return ok_envelope(
        {
            "request_context": {
                "risk_stage_id": risk_s,
                "normalized_jobs": jobs_req,
                "normalized_domains": domains_req,
            },
            "candidates": [to_api_candidate(r) for r in picked],
        }
    )


def recommendations_evidence(body: dict[str, Any], settings: Settings) -> dict[str, Any]:
    return retrieval_service.search_evidence(body, settings)

# Content Hash: SHA256:ed064b94b0e09f8d2f91a5eb0f423b18e7ab2d0636dde9b915d52bb0bcaeeebf
# Role: DATA_SCHEMA certificate_candidate_row 최소 검증 (Pydantic)
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class CertificateCandidateRow(BaseModel):
    """`DATA_SCHEMA.md` §9.1 — API 응답으로보내기 전 저장소 행 검증."""

    model_config = {"extra": "ignore"}

    row_type: str = "certificate_candidate"
    candidate_id: str
    cert_id: str
    cert_name: str
    primary_domain: str
    related_domains: list[str]
    related_jobs: list[str] = Field(default_factory=list)
    recommended_risk_stages: list[str] = Field(default_factory=list)
    roadmap_stages: list[str] = Field(default_factory=list)
    text_for_dense: str
    aliases: list[str] | None = None
    issuer: str | None = None

    @field_validator("related_domains")
    @classmethod
    def at_least_one_domain(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("related_domains는 최소 1개 필요")
        return v


def row_from_json_obj(obj: dict[str, Any]) -> CertificateCandidateRow | None:
    try:
        return CertificateCandidateRow.model_validate(obj)
    except Exception:
        return None

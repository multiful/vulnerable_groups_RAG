# File: test_recommendations.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: POST /recommendations — JSONL 로더·taxonomy·필터 스모크
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import get_settings
from backend.app.main import app

client = TestClient(app)

_MIN_ROW = {
    "row_type": "certificate_candidate",
    "candidate_id": "cand_cert_013",
    "cert_id": "cert_013",
    "cert_name": "정보처리기사",
    "primary_domain": "데이터/AI",
    "related_domains": ["데이터/AI"],
    "related_jobs": ["데이터 분석"],
    "recommended_risk_stages": ["risk_stage_1"],
    "roadmap_stages": ["기초"],
    "text_for_dense": "요약 텍스트",
    "updated_at": "2026-04-03T00:00:00Z",
}


def test_recommendations_missing_risk_stage() -> None:
    r = client.post("/api/v1/recommendations", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is False
    assert body["error"]["code"] == "MISSING_REQUIRED_FIELD"


def test_recommendations_invalid_risk_stage() -> None:
    r = client.post(
        "/api/v1/recommendations",
        json={"risk_stage_id": "risk_stage_99"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_INPUT"


def test_recommendations_taxonomy_unknown_domain() -> None:
    r = client.post(
        "/api/v1/recommendations",
        json={
            "risk_stage_id": "risk_stage_1",
            "interested_domains": ["존재하지 않는 도메인 라벨"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is False
    assert body["error"]["code"] == "TAXONOMY_MAPPING_FAILED"


@pytest.fixture
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_recommendations_loads_jsonl(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    clear_settings_cache,
) -> None:
    p = tmp_path / "c.jsonl"
    p.write_text(json.dumps(_MIN_ROW, ensure_ascii=False) + "\n", encoding="utf-8")
    monkeypatch.setenv("CANDIDATES_JSONL_RELATIVE", str(p.resolve()))

    r = client.post(
        "/api/v1/recommendations",
        json={
            "risk_stage_id": "risk_stage_1",
            "interested_domains": ["데이터/AI"],
            "interested_jobs": ["데이터 분석"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert len(body["data"]["candidates"]) == 1
    assert body["data"]["candidates"][0]["cert_id"] == "cert_013"


def test_recommendations_empty_when_no_file(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    clear_settings_cache,
) -> None:
    missing = tmp_path / "none.jsonl"
    monkeypatch.setenv("CANDIDATES_JSONL_RELATIVE", str(missing.resolve()))

    r = client.post(
        "/api/v1/recommendations",
        json={"risk_stage_id": "risk_stage_1"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"]["candidates"] == []

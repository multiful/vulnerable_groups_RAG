# File: test_evidence.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: evidence API 계약 스모크 (Supabase 없이 cert_id 검증)
from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_evidence_missing_cert_id() -> None:
    r = client.post("/api/v1/recommendations/evidence", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is False
    assert body["error"]["code"] == "MISSING_REQUIRED_FIELD"

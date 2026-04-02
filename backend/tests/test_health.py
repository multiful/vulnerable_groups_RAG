# File: test_health.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: 헬스 엔드포인트 스모크 테스트
from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_ok() -> None:
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert body["error"] is None

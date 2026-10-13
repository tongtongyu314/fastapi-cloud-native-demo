from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "service" in data
    assert "version" in data
    assert "env" in data


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_info():
    resp = client.get("/info")
    assert resp.status_code == 200
    data = resp.json()
    assert "version" in data
    assert "env" in data
    assert "hostname" in data


def test_metrics():
    client.get("/health")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body

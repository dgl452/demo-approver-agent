from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
API_KEY = "test-api-key"


def test_health_returns_ok_with_bearer_api_key(monkeypatch) -> None:
    monkeypatch.setenv("API_KEY", API_KEY)
    response = client.get(
        "/api/health", headers={"Authorization": f"Bearer {API_KEY}"}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_rejects_missing_api_key(monkeypatch) -> None:
    monkeypatch.setenv("API_KEY", API_KEY)
    response = client.get("/api/health")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_health_rejects_invalid_api_key(monkeypatch) -> None:
    monkeypatch.setenv("API_KEY", API_KEY)
    response = client.get(
        "/api/health", headers={"Authorization": "Bearer wrong-key"}
    )

    assert response.status_code == 401


def test_health_fails_closed_when_api_key_is_unconfigured(monkeypatch) -> None:
    monkeypatch.delenv("API_KEY", raising=False)
    response = client.get(
        "/api/health", headers={"Authorization": f"Bearer {API_KEY}"}
    )

    assert response.status_code == 503

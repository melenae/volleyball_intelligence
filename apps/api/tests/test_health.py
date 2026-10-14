from fastapi.testclient import TestClient

from app.db.session import database_status
from app.main import app


def test_health_ok(monkeypatch) -> None:
    monkeypatch.setattr("app.api.routes.health.database_status", lambda: "ok")

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "volleyball-intelligence-api",
        "environment": "development",
        "database": "ok",
    }


def test_health_degraded_when_database_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("app.api.routes.health.database_status", lambda: "unavailable")

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "unavailable"


def test_database_status_reports_connection_failure(monkeypatch) -> None:
    class BrokenConnection:
        def __enter__(self) -> None:
            raise OSError("connection refused")

        def __exit__(self, *_args: object) -> bool:
            return False

    class BrokenEngine:
        def connect(self) -> BrokenConnection:
            return BrokenConnection()

    monkeypatch.setattr("app.db.session.engine", BrokenEngine())

    assert database_status() == "unavailable"


def test_cors_allows_only_configured_origin(monkeypatch) -> None:
    monkeypatch.setattr("app.api.routes.health.database_status", lambda: "ok")

    with TestClient(app) as client:
        allowed = client.get("/api/v1/health", headers={"Origin": "http://localhost:3000"})
        blocked = client.get("/api/v1/health", headers={"Origin": "https://example.com"})

    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-origin" not in blocked.headers


def test_openapi_lists_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/dashboard/summary" in paths
    assert "/api/v1/analytics/teams/{team_id}" in paths

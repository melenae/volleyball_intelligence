from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_db
from app.ingestion.demo.seed import seed_demo_league
from app.main import create_app

pytestmark = pytest.mark.postgres


@pytest.fixture
def api_client(db_session):
    seed_demo_league(db_session)

    application = create_app()

    def override_db():
        yield db_session

    application.dependency_overrides[get_db] = override_db
    with TestClient(application) as client:
        yield client
    application.dependency_overrides.clear()


def _demo_season_id(client: TestClient) -> UUID:
    response = client.get("/api/v1/seasons")
    assert response.status_code == 200
    return UUID(response.json()["items"][0]["id"])


def _team_id_by_slug(client: TestClient, slug: str) -> UUID:
    response = client.get("/api/v1/teams", params={"limit": 100})
    for item in response.json()["items"]:
        if item["slug"] == slug:
            return UUID(item["id"])
    raise AssertionError(f"team slug not found: {slug}")


def test_seasons_list_has_data_origin(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/seasons")
    body = response.json()
    assert response.status_code == 200
    assert body["data_origin"] == "demo"
    assert body["pagination"]["total"] >= 1


def test_teams_pagination(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/teams", params={"limit": 2, "offset": 0})
    body = response.json()
    assert response.status_code == 200
    assert len(body["items"]) == 2
    assert body["pagination"]["limit"] == 2


def test_team_not_found(api_client: TestClient) -> None:
    response = api_client.get(
        "/api/v1/teams/00000000-0000-0000-0000-000000000099",
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_player_not_found(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/players/00000000-0000-0000-0000-000000000099")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_match_not_found(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/matches/00000000-0000-0000-0000-000000000099")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_dashboard_unknown_season(api_client: TestClient) -> None:
    response = api_client.get(
        "/api/v1/dashboard/summary",
        params={"season_id": "00000000-0000-0000-0000-000000000099"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_team_analytics_unknown_season(api_client: TestClient) -> None:
    team_id = _team_id_by_slug(api_client, "severny-veter")
    response = api_client.get(
        f"/api/v1/analytics/teams/{team_id}",
        params={"season_id": "00000000-0000-0000-0000-000000000099"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_standings_null_win_percentage_for_team_without_valid_matches(
    api_client: TestClient,
) -> None:
    season_id = _demo_season_id(api_client)
    response = api_client.get("/api/v1/dashboard/summary", params={"season_id": str(season_id)})
    body = response.json()
    gorodskie = next(row for row in body["standings"] if row["team_slug"] == "gorodskie-barsy")
    assert gorodskie["played_matches"] == 0
    assert gorodskie["win_percentage"] is None


def test_team_analytics_on_demo_data(api_client: TestClient) -> None:
    season_id = _demo_season_id(api_client)
    team_id = _team_id_by_slug(api_client, "severny-veter")
    response = api_client.get(
        f"/api/v1/analytics/teams/{team_id}",
        params={"season_id": str(season_id)},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["data_origin"] == "demo"
    stats = body["statistics"]
    assert stats["played_matches"] == 1
    assert stats["wins"] == 1
    assert stats["losses"] == 0
    assert stats["win_percentage"] == 100.0


def test_invalid_completed_match_not_counted_in_standings(api_client: TestClient) -> None:
    season_id = _demo_season_id(api_client)
    team_id = _team_id_by_slug(api_client, "gorodskie-barsy")
    response = api_client.get(
        f"/api/v1/analytics/teams/{team_id}",
        params={"season_id": str(season_id)},
    )
    stats = response.json()["statistics"]
    assert stats["played_matches"] == 0
    assert stats["wins"] == 0
    assert stats["losses"] == 0


def test_dashboard_summary(api_client: TestClient) -> None:
    season_id = _demo_season_id(api_client)
    response = api_client.get("/api/v1/dashboard/summary", params={"season_id": str(season_id)})
    body = response.json()
    assert response.status_code == 200
    assert body["data_origin"] == "demo"
    assert body["matches_total"] == 3
    assert body["matches_valid_completed"] == 1
    assert body["teams_count"] == 4


def test_matches_filter_by_team(api_client: TestClient) -> None:
    season_id = _demo_season_id(api_client)
    team_id = _team_id_by_slug(api_client, "plyazhnye-koty")
    response = api_client.get(
        "/api/v1/matches",
        params={"season_id": str(season_id), "team_id": str(team_id)},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["pagination"]["total"] == 2


def test_match_detail_includes_sets(api_client: TestClient) -> None:
    season_id = _demo_season_id(api_client)
    matches = api_client.get("/api/v1/matches", params={"season_id": str(season_id), "limit": 1})
    match_id = matches.json()["items"][0]["id"]
    response = api_client.get(f"/api/v1/matches/{match_id}")
    body = response.json()
    assert response.status_code == 200
    assert body["data_origin"] == "demo"
    assert "set_results" in body


def test_player_analytics_without_invented_stats(api_client: TestClient) -> None:
    players = api_client.get("/api/v1/players", params={"limit": 1})
    player_id = players.json()["items"][0]["id"]
    response = api_client.get(f"/api/v1/analytics/players/{player_id}")
    body = response.json()
    assert response.status_code == 200
    assert body["data_origin"] == "demo"
    assert "rosters" in body
    assert "MatchEvent" in body["note"]

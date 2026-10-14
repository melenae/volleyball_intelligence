import uuid
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import League, Match, MatchStatus, Player, Season, SetResult, Team, TeamRoster

pytestmark = pytest.mark.postgres


def _base_league_season_teams(session: Session) -> tuple[Season, Team, Team]:
    league = League(name="Test League", slug=f"league-{uuid.uuid4().hex[:8]}")
    session.add(league)
    session.flush()
    season = Season(
        league_id=league.id,
        name="2025",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
    )
    home = Team(name="Home", slug=f"home-{uuid.uuid4().hex[:8]}")
    away = Team(name="Away", slug=f"away-{uuid.uuid4().hex[:8]}")
    session.add_all([season, home, away])
    session.flush()
    return season, home, away


def test_league_slug_must_be_unique(db_session: Session) -> None:
    db_session.add(League(name="A", slug="same-slug"))
    db_session.add(League(name="B", slug="same-slug"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_team_slug_must_be_unique(db_session: Session) -> None:
    db_session.add(Team(name="A", slug="team-slug"))
    db_session.add(Team(name="B", slug="team-slug"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_match_requires_different_home_and_away(db_session: Session) -> None:
    season, team, _away = _base_league_season_teams(db_session)
    db_session.add(
        Match(
            season_id=season.id,
            home_team_id=team.id,
            away_team_id=team.id,
            status=MatchStatus.scheduled,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_match_allows_null_venue(db_session: Session) -> None:
    season, home, away = _base_league_season_teams(db_session)
    match = Match(
        season_id=season.id,
        home_team_id=home.id,
        away_team_id=away.id,
        status=MatchStatus.scheduled,
        venue=None,
    )
    db_session.add(match)
    db_session.commit()
    assert match.venue is None


def test_set_number_unique_per_match(db_session: Session) -> None:
    season, home, away = _base_league_season_teams(db_session)
    match = Match(
        season_id=season.id,
        home_team_id=home.id,
        away_team_id=away.id,
        status=MatchStatus.completed,
    )
    db_session.add(match)
    db_session.flush()
    db_session.add_all(
        [
            SetResult(match_id=match.id, set_number=1, home_score=25, away_score=20),
            SetResult(match_id=match.id, set_number=1, home_score=25, away_score=22),
        ]
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_set_scores_cannot_be_negative_or_tied(db_session: Session) -> None:
    season, home, away = _base_league_season_teams(db_session)
    match = Match(
        season_id=season.id,
        home_team_id=home.id,
        away_team_id=away.id,
        status=MatchStatus.completed,
    )
    db_session.add(match)
    db_session.flush()

    db_session.add(SetResult(match_id=match.id, set_number=1, home_score=-1, away_score=20))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    db_session.add(SetResult(match_id=match.id, set_number=1, home_score=25, away_score=25))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_roster_unique_team_player_season(db_session: Session) -> None:
    season, home, away = _base_league_season_teams(db_session)
    player = Player(
        demo_slug=f"player-{uuid.uuid4().hex[:8]}",
        first_name="A",
        last_name="B",
        display_name="A B",
    )
    db_session.add(player)
    db_session.flush()
    db_session.add_all(
        [
            TeamRoster(team_id=home.id, player_id=player.id, season_id=season.id, jersey_number=1),
            TeamRoster(team_id=home.id, player_id=player.id, season_id=season.id, jersey_number=2),
        ]
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

"""Idempotent demo league seed. Run: python -m app.ingestion.demo.seed"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.ingestion.demo.fixtures import (
    DEMO_LEAGUE,
    DEMO_MATCHES,
    DEMO_PLAYERS,
    DEMO_ROSTERS,
    DEMO_SEASON,
    DEMO_TEAMS,
    DemoMatchFixture,
    DemoPlayerFixture,
)
from app.models import League, Match, MatchStatus, Player, Season, SetResult, Team, TeamRoster
from app.repositories.league import LeagueRepository
from app.repositories.match import MatchRepository
from app.repositories.player import PlayerRepository
from app.repositories.season import SeasonRepository
from app.repositories.team import TeamRepository

logger = logging.getLogger(__name__)


def _upsert_league(session: Session) -> League:
    repo = LeagueRepository(session)
    league = repo.get_by_slug(DEMO_LEAGUE.slug)
    if league is None:
        league = League(name=DEMO_LEAGUE.name, slug=DEMO_LEAGUE.slug)
        session.add(league)
        session.flush()
        return league
    league.name = DEMO_LEAGUE.name
    return league


def _upsert_season(session: Session, league_id: UUID) -> Season:
    repo = SeasonRepository(session)
    season = repo.get_by_league_and_name(league_id, DEMO_SEASON.name)
    if season is None:
        season = Season(
            league_id=league_id,
            name=DEMO_SEASON.name,
            start_date=DEMO_SEASON.start_date,
            end_date=DEMO_SEASON.end_date,
        )
        session.add(season)
        session.flush()
        return season
    season.start_date = DEMO_SEASON.start_date
    season.end_date = DEMO_SEASON.end_date
    return season


def _upsert_team(session: Session, fixture_name: str, fixture_slug: str) -> Team:
    repo = TeamRepository(session)
    team = repo.get_by_slug(fixture_slug)
    if team is None:
        team = Team(name=fixture_name, slug=fixture_slug)
        session.add(team)
        session.flush()
        return team
    team.name = fixture_name
    return team


def _upsert_player(session: Session, fixture: DemoPlayerFixture) -> Player:
    repo = PlayerRepository(session)
    player = repo.get_by_demo_slug(fixture.demo_slug)
    if player is None:
        player = Player(
            demo_slug=fixture.demo_slug,
            first_name=fixture.first_name,
            last_name=fixture.last_name,
            display_name=fixture.display_name,
            position=fixture.position,
        )
        session.add(player)
        session.flush()
        return player
    player.first_name = fixture.first_name
    player.last_name = fixture.last_name
    player.display_name = fixture.display_name
    player.position = fixture.position
    return player


def _upsert_roster(
    session: Session,
    *,
    team_id: UUID,
    player_id: UUID,
    season_id: UUID,
    jersey_number: int | None,
) -> None:
    existing = session.scalar(
        select(TeamRoster).where(
            TeamRoster.team_id == team_id,
            TeamRoster.player_id == player_id,
            TeamRoster.season_id == season_id,
        )
    )
    if existing is None:
        session.add(
            TeamRoster(
                team_id=team_id,
                player_id=player_id,
                season_id=season_id,
                jersey_number=jersey_number,
            )
        )
        return
    existing.jersey_number = jersey_number


def _upsert_match(
    session: Session,
    *,
    fixture: DemoMatchFixture,
    season_id: UUID,
    home_team_id: UUID,
    away_team_id: UUID,
) -> Match:
    repo = MatchRepository(session)
    match = repo.get_by_natural_key(
        season_id=season_id,
        scheduled_at=fixture.scheduled_at,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
    )
    status = MatchStatus(fixture.status)
    if match is None:
        match = Match(
            season_id=season_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            scheduled_at=fixture.scheduled_at,
            status=status,
            venue=fixture.venue,
        )
        session.add(match)
        session.flush()
    else:
        match.status = status
        match.venue = fixture.venue

    existing_sets = {
        row.set_number: row
        for row in session.scalars(select(SetResult).where(SetResult.match_id == match.id)).all()
    }
    for set_fixture in fixture.sets:
        row = existing_sets.get(set_fixture.set_number)
        if row is None:
            session.add(
                SetResult(
                    match_id=match.id,
                    set_number=set_fixture.set_number,
                    home_score=set_fixture.home_score,
                    away_score=set_fixture.away_score,
                )
            )
        else:
            row.home_score = set_fixture.home_score
            row.away_score = set_fixture.away_score
    return match


def seed_demo_league(session: Session) -> None:
    league = _upsert_league(session)
    season = _upsert_season(session, league.id)

    team_by_slug: dict[str, Team] = {}
    for team_fixture in DEMO_TEAMS:
        team_by_slug[team_fixture.slug] = _upsert_team(
            session,
            team_fixture.name,
            team_fixture.slug,
        )

    player_by_slug: dict[str, Player] = {}
    for player_fixture in DEMO_PLAYERS:
        player_by_slug[player_fixture.demo_slug] = _upsert_player(session, player_fixture)

    for roster_fixture in DEMO_ROSTERS:
        _upsert_roster(
            session,
            team_id=team_by_slug[roster_fixture.team_slug].id,
            player_id=player_by_slug[roster_fixture.player_demo_slug].id,
            season_id=season.id,
            jersey_number=roster_fixture.jersey_number,
        )

    for match_fixture in DEMO_MATCHES:
        _upsert_match(
            session,
            fixture=match_fixture,
            season_id=season.id,
            home_team_id=team_by_slug[match_fixture.home_team_slug].id,
            away_team_id=team_by_slug[match_fixture.away_team_slug].id,
        )

    session.commit()
    logger.info("Demo league seed completed (data_origin=demo, not AVL).")


def count_domain_rows(session: Session) -> dict[str, int]:
    return {
        "leagues": session.scalar(select(func.count()).select_from(League)) or 0,
        "seasons": session.scalar(select(func.count()).select_from(Season)) or 0,
        "teams": session.scalar(select(func.count()).select_from(Team)) or 0,
        "players": session.scalar(select(func.count()).select_from(Player)) or 0,
        "team_rosters": session.scalar(select(func.count()).select_from(TeamRoster)) or 0,
        "matches": session.scalar(select(func.count()).select_from(Match)) or 0,
        "set_results": session.scalar(select(func.count()).select_from(SetResult)) or 0,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    with SessionLocal() as session:
        seed_demo_league(session)
        counts = count_domain_rows(session)
        logger.info("Row counts: %s", counts)


if __name__ == "__main__":
    main()

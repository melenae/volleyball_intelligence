from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.http_utils import not_found
from app.repositories.season import SeasonRepository
from app.repositories.team import TeamRepository
from app.schemas.api_responses import (
    PaginatedTeamsResponse,
    TeamDetailResponse,
    TeamPlayersResponse,
    TeamRosterPlayerItem,
)
from app.schemas.common import PlayerRead, TeamRead
from app.schemas.pagination import PaginationMeta

router = APIRouter(prefix="/api/v1", tags=["teams"])


@router.get("/teams", response_model=PaginatedTeamsResponse)
def list_teams(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> PaginatedTeamsResponse:
    repo = TeamRepository(db)
    rows, total = repo.list_teams(limit=limit, offset=offset)
    return PaginatedTeamsResponse(
        items=[TeamRead.model_validate(row) for row in rows],
        pagination=PaginationMeta(limit=limit, offset=offset, total=total),
    )


@router.get("/teams/{team_id}", response_model=TeamDetailResponse)
def get_team(team_id: UUID, db: Session = Depends(get_db)) -> TeamDetailResponse:
    team = TeamRepository(db).get_by_id(team_id)
    if team is None:
        raise not_found("Команда не найдена.")
    return TeamDetailResponse(team=TeamRead.model_validate(team))


@router.get("/teams/{team_id}/players", response_model=TeamPlayersResponse)
def list_team_players(
    team_id: UUID,
    season_id: UUID = Query(..., description="Сезон состава"),
    db: Session = Depends(get_db),
) -> TeamPlayersResponse:
    teams = TeamRepository(db)
    seasons = SeasonRepository(db)
    if teams.get_by_id(team_id) is None:
        raise not_found("Команда не найдена.")
    if seasons.get_by_id(season_id) is None:
        raise not_found("Сезон не найден.")

    roster_rows = teams.list_roster_players(team_id, season_id)
    return TeamPlayersResponse(
        team_id=team_id,
        season_id=season_id,
        players=[
            TeamRosterPlayerItem(
                player=PlayerRead.model_validate(player),
                jersey_number=roster.jersey_number,
            )
            for roster, player in roster_rows
        ],
    )

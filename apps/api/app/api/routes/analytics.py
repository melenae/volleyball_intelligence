from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.http_utils import not_found
from app.repositories.player import PlayerRepository
from app.repositories.season import SeasonRepository
from app.repositories.team import TeamRepository
from app.schemas.api_responses import (
    PlayerAnalyticsResponse,
    PlayerRosterContext,
    TeamAnalyticsResponse,
    TeamMatchTimelineItem,
    TeamStatisticsPayload,
)
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/teams/{team_id}", response_model=TeamAnalyticsResponse)
def team_analytics(
    team_id: UUID,
    season_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> TeamAnalyticsResponse:
    if TeamRepository(db).get_by_id(team_id) is None:
        raise not_found("Команда не найдена.")
    if season_id is not None and SeasonRepository(db).get_by_id(season_id) is None:
        raise not_found("Сезон не найден.")

    stats = AnalyticsService(db).team_statistics(team_id, season_id)
    return TeamAnalyticsResponse(
        team_id=team_id,
        season_id=season_id,
        statistics=TeamStatisticsPayload(
            played_matches=stats.played_matches,
            wins=stats.wins,
            losses=stats.losses,
            sets_won=stats.sets_won,
            sets_lost=stats.sets_lost,
            points_for=stats.points_for,
            points_against=stats.points_against,
            win_percentage=stats.win_percentage,
            match_timeline=[
                TeamMatchTimelineItem(
                    match_id=item.match_id,
                    scheduled_at=item.scheduled_at,
                    opponent_team_id=item.opponent_team_id,
                    is_home=item.is_home,
                    result=item.result,
                    home_sets_won=item.home_sets_won,
                    away_sets_won=item.away_sets_won,
                )
                for item in stats.match_timeline
            ],
        ),
    )


@router.get("/players/{player_id}", response_model=PlayerAnalyticsResponse)
def player_analytics(
    player_id: UUID,
    season_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> PlayerAnalyticsResponse:
    players = PlayerRepository(db)
    if players.get_by_id(player_id) is None:
        raise not_found("Игрок не найден.")
    if season_id is not None and SeasonRepository(db).get_by_id(season_id) is None:
        raise not_found("Сезон не найден.")

    rosters = players.list_rosters_for_player(player_id, season_id=season_id)
    return PlayerAnalyticsResponse(
        player_id=player_id,
        season_id=season_id,
        rosters=[
            PlayerRosterContext(
                team_id=row.team_id,
                season_id=row.season_id,
                jersey_number=row.jersey_number,
            )
            for row in rosters
        ],
    )

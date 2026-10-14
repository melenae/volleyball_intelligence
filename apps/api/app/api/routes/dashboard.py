from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.http_utils import match_list_item, not_found
from app.schemas.api_responses import DashboardSummaryResponse, DashboardTeamStanding
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(
    season_id: UUID = Query(..., description="Сезон для сводки"),
    db: Session = Depends(get_db),
) -> DashboardSummaryResponse:
    service = DashboardService(db)
    payload = service.build_summary(season_id)
    if payload is None:
        raise not_found("Сезон не найден.")

    season = payload["season"]
    return DashboardSummaryResponse(
        season_id=season.id,
        season_name=season.name,
        teams_count=payload["teams_count"],
        matches_total=payload["matches_total"],
        matches_valid_completed=payload["matches_valid_completed"],
        standings=[
            DashboardTeamStanding(
                team_id=row["team_id"],
                team_name=row["team_name"],
                team_slug=row["team_slug"],
                played_matches=row["played_matches"],
                wins=row["wins"],
                losses=row["losses"],
                win_percentage=row["win_percentage"],
            )
            for row in payload["standings"]
        ],
        recent_matches=[match_list_item(match) for match in payload["recent_matches"]],
    )

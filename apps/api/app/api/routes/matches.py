from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.http_utils import (
    evaluate_match,
    match_list_item,
    match_read,
    not_found,
    winner_team_id,
)
from app.repositories.match import MatchRepository
from app.schemas.api_responses import (
    MatchDetailResponse,
    MatchSetResultItem,
    PaginatedMatchesResponse,
)
from app.schemas.pagination import PaginationMeta

router = APIRouter(prefix="/api/v1", tags=["matches"])


@router.get("/matches", response_model=PaginatedMatchesResponse)
def list_matches(
    season_id: UUID | None = Query(default=None),
    team_id: UUID | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> PaginatedMatchesResponse:
    repo = MatchRepository(db)
    rows, total = repo.list_matches(
        season_id=season_id,
        team_id=team_id,
        limit=limit,
        offset=offset,
    )
    return PaginatedMatchesResponse(
        items=[match_list_item(row) for row in rows],
        pagination=PaginationMeta(limit=limit, offset=offset, total=total),
    )


@router.get("/matches/{match_id}", response_model=MatchDetailResponse)
def get_match(match_id: UUID, db: Session = Depends(get_db)) -> MatchDetailResponse:
    match = MatchRepository(db).get_by_id(match_id)
    if match is None:
        raise not_found("Матч не найден.")
    evaluation = evaluate_match(match)
    return MatchDetailResponse(
        match=match_read(match),
        home_team=match_list_item(match).home_team,
        away_team=match_list_item(match).away_team,
        set_results=[
            MatchSetResultItem(
                set_number=row.set_number,
                home_score=row.home_score,
                away_score=row.away_score,
            )
            for row in sorted(match.set_results, key=lambda item: item.set_number)
        ],
        is_valid_completed_match=evaluation.is_valid_completed_match,
        winner_team_id=winner_team_id(match),
    )

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories.season import SeasonRepository
from app.schemas.api_responses import PaginatedSeasonsResponse
from app.schemas.common import SeasonRead
from app.schemas.pagination import PaginationMeta

router = APIRouter(prefix="/api/v1", tags=["seasons"])


@router.get("/seasons", response_model=PaginatedSeasonsResponse)
def list_seasons(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> PaginatedSeasonsResponse:
    repo = SeasonRepository(db)
    rows, total = repo.list_seasons(limit=limit, offset=offset)
    return PaginatedSeasonsResponse(
        items=[SeasonRead.model_validate(row) for row in rows],
        pagination=PaginationMeta(limit=limit, offset=offset, total=total),
    )

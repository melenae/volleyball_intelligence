from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.http_utils import not_found
from app.repositories.player import PlayerRepository
from app.schemas.api_responses import PaginatedPlayersResponse, PlayerDetailResponse
from app.schemas.common import PlayerRead
from app.schemas.pagination import PaginationMeta

router = APIRouter(prefix="/api/v1", tags=["players"])


@router.get("/players", response_model=PaginatedPlayersResponse)
def list_players(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> PaginatedPlayersResponse:
    repo = PlayerRepository(db)
    rows, total = repo.list_players(limit=limit, offset=offset)
    return PaginatedPlayersResponse(
        items=[PlayerRead.model_validate(row) for row in rows],
        pagination=PaginationMeta(limit=limit, offset=offset, total=total),
    )


@router.get("/players/{player_id}", response_model=PlayerDetailResponse)
def get_player(player_id: UUID, db: Session = Depends(get_db)) -> PlayerDetailResponse:
    player = PlayerRepository(db).get_by_id(player_id)
    if player is None:
        raise not_found("Игрок не найден.")
    return PlayerDetailResponse(player=PlayerRead.model_validate(player))

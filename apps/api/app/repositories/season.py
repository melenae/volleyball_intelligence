from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Season
from app.repositories.base import Repository


class SeasonRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, season_id: UUID) -> Season | None:
        return self.session.get(Season, season_id)

    def get_by_league_and_name(self, league_id: UUID, name: str) -> Season | None:
        return self.session.scalar(
            select(Season).where(Season.league_id == league_id, Season.name == name)
        )

    def list_seasons(self, *, limit: int, offset: int) -> tuple[list[Season], int]:
        base = select(Season).order_by(Season.start_date.desc(), Season.id)
        total = self.count(base)
        rows = self.session.scalars(base.limit(limit).offset(offset)).all()
        return list(rows), total

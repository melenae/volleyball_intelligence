from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Season
from app.repositories.base import Repository


class SeasonRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_league_and_name(self, league_id: UUID, name: str) -> Season | None:
        return self.session.scalar(
            select(Season).where(Season.league_id == league_id, Season.name == name)
        )

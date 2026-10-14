from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import League
from app.repositories.base import Repository


class LeagueRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_slug(self, slug: str) -> League | None:
        return self.session.scalar(select(League).where(League.slug == slug))

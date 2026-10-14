from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Team
from app.repositories.base import Repository


class TeamRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_slug(self, slug: str) -> Team | None:
        return self.session.scalar(select(Team).where(Team.slug == slug))

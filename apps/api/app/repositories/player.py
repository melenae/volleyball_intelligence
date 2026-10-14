from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Player
from app.repositories.base import Repository


class PlayerRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_demo_slug(self, demo_slug: str) -> Player | None:
        return self.session.scalar(select(Player).where(Player.demo_slug == demo_slug))

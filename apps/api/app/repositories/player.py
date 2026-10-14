from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Player, TeamRoster
from app.repositories.base import Repository


class PlayerRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, player_id: UUID) -> Player | None:
        return self.session.get(Player, player_id)

    def get_by_demo_slug(self, demo_slug: str) -> Player | None:
        return self.session.scalar(select(Player).where(Player.demo_slug == demo_slug))

    def list_players(self, *, limit: int, offset: int) -> tuple[list[Player], int]:
        base = select(Player).order_by(Player.last_name, Player.first_name, Player.id)
        total = self.count(base)
        rows = self.session.scalars(base.limit(limit).offset(offset)).all()
        return list(rows), total

    def list_rosters_for_player(
        self,
        player_id: UUID,
        *,
        season_id: UUID | None,
    ) -> list[TeamRoster]:
        stmt = select(TeamRoster).where(TeamRoster.player_id == player_id)
        if season_id is not None:
            stmt = stmt.where(TeamRoster.season_id == season_id)
        stmt = stmt.order_by(TeamRoster.season_id, TeamRoster.team_id)
        return list(self.session.scalars(stmt).all())

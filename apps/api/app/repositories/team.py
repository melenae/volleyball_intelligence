from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Player, Team, TeamRoster
from app.repositories.base import Repository


class TeamRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, team_id: UUID) -> Team | None:
        return self.session.get(Team, team_id)

    def get_by_slug(self, slug: str) -> Team | None:
        return self.session.scalar(select(Team).where(Team.slug == slug))

    def list_teams(self, *, limit: int, offset: int) -> tuple[list[Team], int]:
        base = select(Team).order_by(Team.name, Team.id)
        total = self.count(base)
        rows = self.session.scalars(base.limit(limit).offset(offset)).all()
        return list(rows), total

    def list_all(self) -> list[Team]:
        return list(self.session.scalars(select(Team).order_by(Team.name, Team.id)).all())

    def list_roster_players(
        self, team_id: UUID, season_id: UUID
    ) -> list[tuple[TeamRoster, Player]]:
        rows = self.session.execute(
            select(TeamRoster, Player)
            .join(Player, TeamRoster.player_id == Player.id)
            .where(TeamRoster.team_id == team_id, TeamRoster.season_id == season_id)
            .order_by(Player.last_name, Player.first_name, Player.id)
        ).all()
        return [(roster, player) for roster, player in rows]

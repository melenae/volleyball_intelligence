from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Match
from app.repositories.base import Repository


class MatchRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_natural_key(
        self,
        *,
        season_id: UUID,
        scheduled_at: datetime,
        home_team_id: UUID,
        away_team_id: UUID,
    ) -> Match | None:
        return self.session.scalar(
            select(Match).where(
                Match.season_id == season_id,
                Match.scheduled_at == scheduled_at,
                Match.home_team_id == home_team_id,
                Match.away_team_id == away_team_id,
            )
        )

    def get_with_sets(self, match_id: UUID) -> Match | None:
        return self.session.scalar(
            select(Match).where(Match.id == match_id).options(selectinload(Match.set_results))
        )

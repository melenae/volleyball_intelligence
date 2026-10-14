from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Match
from app.repositories.base import Repository


class MatchRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, match_id: UUID) -> Match | None:
        return self.session.scalar(
            select(Match)
            .where(Match.id == match_id)
            .options(
                selectinload(Match.set_results),
                selectinload(Match.home_team),
                selectinload(Match.away_team),
            )
        )

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

    def _list_base(
        self,
        *,
        season_id: UUID | None,
        team_id: UUID | None,
    ) -> select:
        stmt = select(Match).options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
        )
        if season_id is not None:
            stmt = stmt.where(Match.season_id == season_id)
        if team_id is not None:
            stmt = stmt.where(or_(Match.home_team_id == team_id, Match.away_team_id == team_id))
        return stmt.order_by(
            Match.scheduled_at.asc().nulls_last(),
            Match.id.asc(),
        )

    def list_matches(
        self,
        *,
        season_id: UUID | None,
        team_id: UUID | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Match], int]:
        base = self._list_base(season_id=season_id, team_id=team_id)
        total = self.count(base)
        rows = self.session.scalars(base.limit(limit).offset(offset)).all()
        return list(rows), total

    def list_matches_for_season_with_sets(self, season_id: UUID) -> list[Match]:
        stmt = (
            select(Match)
            .where(Match.season_id == season_id)
            .options(
                selectinload(Match.set_results),
                selectinload(Match.home_team),
                selectinload(Match.away_team),
            )
            .order_by(Match.scheduled_at.asc().nulls_last(), Match.id.asc())
        )
        return list(self.session.scalars(stmt).all())

    def list_matches_for_team(
        self,
        team_id: UUID,
        *,
        season_id: UUID | None,
    ) -> list[Match]:
        stmt = (
            select(Match)
            .where(or_(Match.home_team_id == team_id, Match.away_team_id == team_id))
            .options(selectinload(Match.set_results))
            .order_by(Match.scheduled_at.asc().nulls_last(), Match.id.asc())
        )
        if season_id is not None:
            stmt = stmt.where(Match.season_id == season_id)
        return list(self.session.scalars(stmt).all())

    def count_matches_in_season(self, season_id: UUID) -> int:
        return int(
            self.session.scalar(
                select(func.count()).select_from(Match).where(Match.season_id == season_id)
            )
            or 0
        )

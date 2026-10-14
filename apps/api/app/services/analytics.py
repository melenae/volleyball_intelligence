from uuid import UUID

from sqlalchemy.orm import Session

from app.analytics.team import compute_team_statistics
from app.analytics.types import TeamStatistics
from app.repositories.match import MatchRepository
from app.services.match_mapper import match_to_analytics


class AnalyticsService:
    def __init__(self, session: Session) -> None:
        self._matches = MatchRepository(session)

    def team_statistics(self, team_id: UUID, season_id: UUID | None) -> TeamStatistics:
        matches = self._matches.list_matches_for_team(team_id, season_id=season_id)
        analytics_rows = [match_to_analytics(match) for match in matches]
        return compute_team_statistics(team_id, analytics_rows)

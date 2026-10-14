from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.models.enums import MatchStatus
from app.services.match_result import SetScoreInput


@dataclass(frozen=True)
class MatchForAnalytics:
    match_id: UUID
    season_id: UUID
    scheduled_at: datetime | None
    home_team_id: UUID
    away_team_id: UUID
    status: MatchStatus
    sets: tuple[SetScoreInput, ...]


@dataclass(frozen=True)
class TeamMatchTimelineEntry:
    match_id: UUID
    scheduled_at: datetime | None
    opponent_team_id: UUID
    is_home: bool
    result: str
    home_sets_won: int
    away_sets_won: int


@dataclass(frozen=True)
class TeamStatistics:
    played_matches: int
    wins: int
    losses: int
    sets_won: int
    sets_lost: int
    points_for: int
    points_against: int
    win_percentage: float | None
    match_timeline: tuple[TeamMatchTimelineEntry, ...]

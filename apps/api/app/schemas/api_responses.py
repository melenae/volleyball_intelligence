from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import MatchRead, PlayerRead, SeasonRead, TeamRead
from app.schemas.pagination import PaginationMeta

DataOrigin = Literal["demo"]


class WithDataOrigin(BaseModel):
    data_origin: DataOrigin = "demo"


class PaginatedSeasonsResponse(WithDataOrigin):
    items: list[SeasonRead]
    pagination: PaginationMeta


class PaginatedTeamsResponse(WithDataOrigin):
    items: list[TeamRead]
    pagination: PaginationMeta


class PaginatedPlayersResponse(WithDataOrigin):
    items: list[PlayerRead]
    pagination: PaginationMeta


class TeamDetailResponse(WithDataOrigin):
    team: TeamRead


class PlayerDetailResponse(WithDataOrigin):
    player: PlayerRead


class TeamRosterPlayerItem(BaseModel):
    player: PlayerRead
    jersey_number: int | None


class TeamPlayersResponse(WithDataOrigin):
    team_id: UUID
    season_id: UUID
    players: list[TeamRosterPlayerItem]


class TeamMatchTimelineItem(BaseModel):
    match_id: UUID
    scheduled_at: datetime | None
    opponent_team_id: UUID
    is_home: bool
    result: Literal["win", "loss"]
    home_sets_won: int
    away_sets_won: int


class TeamStatisticsPayload(BaseModel):
    played_matches: int
    wins: int
    losses: int
    sets_won: int
    sets_lost: int
    points_for: int
    points_against: int
    win_percentage: float | None
    match_timeline: list[TeamMatchTimelineItem]


class TeamAnalyticsResponse(WithDataOrigin):
    team_id: UUID
    season_id: UUID | None = None
    statistics: TeamStatisticsPayload


class PlayerRosterContext(BaseModel):
    team_id: UUID
    season_id: UUID
    jersey_number: int | None


class PlayerAnalyticsResponse(WithDataOrigin):
    player_id: UUID
    season_id: UUID | None = None
    rosters: list[PlayerRosterContext]
    note: str = Field(default="Индивидуальная статистика матчей недоступна без событий MatchEvent.")


class MatchTeamSummary(BaseModel):
    id: UUID
    name: str
    slug: str


class MatchListItem(BaseModel):
    id: UUID
    season_id: UUID
    scheduled_at: datetime | None
    status: str
    venue: str | None
    home_team: MatchTeamSummary
    away_team: MatchTeamSummary


class PaginatedMatchesResponse(WithDataOrigin):
    items: list[MatchListItem]
    pagination: PaginationMeta


class MatchSetResultItem(BaseModel):
    set_number: int
    home_score: int
    away_score: int


class MatchDetailResponse(WithDataOrigin):
    match: MatchRead
    home_team: MatchTeamSummary
    away_team: MatchTeamSummary
    set_results: list[MatchSetResultItem]
    is_valid_completed_match: bool
    winner_team_id: UUID | None


class DashboardTeamStanding(BaseModel):
    team_id: UUID
    team_name: str
    team_slug: str
    played_matches: int
    wins: int
    losses: int
    win_percentage: float | None


class DashboardSummaryResponse(WithDataOrigin):
    season_id: UUID
    season_name: str
    teams_count: int
    matches_total: int
    matches_valid_completed: int
    standings: list[DashboardTeamStanding]
    recent_matches: list[MatchListItem]

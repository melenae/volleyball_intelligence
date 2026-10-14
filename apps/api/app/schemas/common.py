from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IdSchema(ORMModel):
    id: UUID


class LeagueRead(IdSchema):
    name: str
    slug: str
    created_at: datetime


class SeasonRead(IdSchema):
    league_id: UUID
    name: str
    start_date: date
    end_date: date


class TeamRead(IdSchema):
    name: str
    slug: str
    logo_url: str | None


class PlayerRead(IdSchema):
    demo_slug: str
    first_name: str
    last_name: str
    display_name: str
    position: str | None


class TeamRosterRead(IdSchema):
    team_id: UUID
    player_id: UUID
    season_id: UUID
    jersey_number: int | None
    active_from: date | None
    active_until: date | None


class SetResultRead(IdSchema):
    match_id: UUID
    set_number: int
    home_score: int
    away_score: int


class MatchRead(IdSchema):
    season_id: UUID
    home_team_id: UUID
    away_team_id: UUID
    scheduled_at: datetime | None
    status: str
    venue: str | None

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class LeaguePayloadV1(BaseModel):
    ref: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=120)


class SeasonPayloadV1(BaseModel):
    ref: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=120)
    start_date: date
    end_date: date
    league_ref: str = Field(min_length=1, max_length=120)

    @model_validator(mode="after")
    def end_not_before_start(self) -> "SeasonPayloadV1":
        if self.end_date < self.start_date:
            raise ValueError("end_date не может быть раньше start_date")
        return self


class TeamPayloadV1(BaseModel):
    ref: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=120)
    logo_url: str | None = Field(default=None, max_length=500)


class PlayerPayloadV1(BaseModel):
    ref: str = Field(min_length=1, max_length=120)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    display_name: str = Field(min_length=1, max_length=200)
    position: str | None = Field(default=None, max_length=50)


class RosterPayloadV1(BaseModel):
    team_ref: str = Field(min_length=1, max_length=120)
    player_ref: str = Field(min_length=1, max_length=120)
    season_ref: str = Field(min_length=1, max_length=120)
    jersey_number: int | None = None
    active_from: date | None = None
    active_until: date | None = None


class SetPayloadV1(BaseModel):
    set_number: int = Field(ge=1)
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)

    @model_validator(mode="after")
    def scores_not_tied(self) -> "SetPayloadV1":
        if self.home_score == self.away_score:
            raise ValueError("счёт сета не может быть ничейным")
        return self


class MatchPayloadV1(BaseModel):
    ref: str = Field(min_length=1, max_length=120)
    season_ref: str = Field(min_length=1, max_length=120)
    home_team_ref: str = Field(min_length=1, max_length=120)
    away_team_ref: str = Field(min_length=1, max_length=120)
    scheduled_at: datetime | None = None
    status: Literal["scheduled", "completed", "cancelled"]
    venue: str | None = Field(default=None, max_length=300)
    sets: list[SetPayloadV1] = Field(default_factory=list)

    @field_validator("venue", mode="before")
    @classmethod
    def empty_venue_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def teams_differ(self) -> "MatchPayloadV1":
        if self.home_team_ref == self.away_team_ref:
            raise ValueError("home_team_ref и away_team_ref должны различаться")
        return self

    @model_validator(mode="after")
    def sets_for_status(self) -> "MatchPayloadV1":
        if self.status in {"scheduled", "cancelled"} and self.sets:
            raise ValueError("для scheduled/cancelled список sets должен быть пустым")
        return self


class ImportBundleV1(BaseModel):
    schema_version: Literal[1]
    source_label: str = Field(min_length=1, max_length=200)
    league: LeaguePayloadV1
    seasons: list[SeasonPayloadV1]
    teams: list[TeamPayloadV1]
    players: list[PlayerPayloadV1]
    rosters: list[RosterPayloadV1] = Field(default_factory=list)
    matches: list[MatchPayloadV1] = Field(default_factory=list)

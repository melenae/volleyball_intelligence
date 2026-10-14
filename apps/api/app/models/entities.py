import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import MatchStatus


class League(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "leagues"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    seasons: Mapped[list["Season"]] = relationship(back_populates="league")


class Season(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "seasons"
    __table_args__ = (
        UniqueConstraint("league_id", "name", name="uq_seasons_league_name"),
        Index("ix_seasons_league_id", "league_id"),
    )

    league_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    league: Mapped["League"] = relationship(back_populates="seasons")
    matches: Mapped[list["Match"]] = relationship(back_populates="season")
    rosters: Mapped[list["TeamRoster"]] = relationship(back_populates="season")


class Team(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    home_matches: Mapped[list["Match"]] = relationship(
        back_populates="home_team",
        foreign_keys="Match.home_team_id",
    )
    away_matches: Mapped[list["Match"]] = relationship(
        back_populates="away_team",
        foreign_keys="Match.away_team_id",
    )
    rosters: Mapped[list["TeamRoster"]] = relationship(back_populates="team")


class Player(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "players"

    demo_slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str | None] = mapped_column(String(50), nullable=True)

    rosters: Mapped[list["TeamRoster"]] = relationship(back_populates="player")


class TeamRoster(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "team_rosters"
    __table_args__ = (
        UniqueConstraint(
            "team_id",
            "player_id",
            "season_id",
            name="uq_team_rosters_team_player_season",
        ),
        Index("ix_team_rosters_season_id", "season_id"),
        Index("ix_team_rosters_team_id", "team_id"),
        Index("ix_team_rosters_player_id", "player_id"),
    )

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
    )
    season_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
    )
    jersey_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    active_until: Mapped[date | None] = mapped_column(Date, nullable=True)

    team: Mapped["Team"] = relationship(back_populates="rosters")
    player: Mapped["Player"] = relationship(back_populates="rosters")
    season: Mapped["Season"] = relationship(back_populates="rosters")


class Match(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "matches"
    __table_args__ = (
        CheckConstraint(
            "home_team_id <> away_team_id",
            name="ck_matches_different_teams",
        ),
        Index("ix_matches_season_id", "season_id"),
        Index("ix_matches_home_team_id", "home_team_id"),
        Index("ix_matches_away_team_id", "away_team_id"),
        Index("ix_matches_season_scheduled", "season_id", "scheduled_at"),
    )

    season_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
    )
    home_team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
    )
    away_team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[MatchStatus] = mapped_column(
        Enum(
            MatchStatus,
            name="match_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    venue: Mapped[str | None] = mapped_column(String(300), nullable=True)

    season: Mapped["Season"] = relationship(back_populates="matches")
    home_team: Mapped["Team"] = relationship(
        back_populates="home_matches",
        foreign_keys=[home_team_id],
    )
    away_team: Mapped["Team"] = relationship(
        back_populates="away_matches",
        foreign_keys=[away_team_id],
    )
    set_results: Mapped[list["SetResult"]] = relationship(
        back_populates="match",
        order_by="SetResult.set_number",
    )


class SetResult(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "set_results"
    __table_args__ = (
        UniqueConstraint("match_id", "set_number", name="uq_set_results_match_set_number"),
        CheckConstraint("home_score >= 0", name="ck_set_results_home_score_non_negative"),
        CheckConstraint("away_score >= 0", name="ck_set_results_away_score_non_negative"),
        CheckConstraint("home_score <> away_score", name="ck_set_results_scores_not_tied"),
        Index("ix_set_results_match_id", "match_id"),
    )

    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    home_score: Mapped[int] = mapped_column(Integer, nullable=False)
    away_score: Mapped[int] = mapped_column(Integer, nullable=False)

    match: Mapped["Match"] = relationship(back_populates="set_results")

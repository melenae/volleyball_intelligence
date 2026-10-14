from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.constants import (
    ENTITY_LEAGUE,
    ENTITY_MATCH,
    ENTITY_PLAYER,
    ENTITY_ROSTER,
    ENTITY_SEASON,
    ENTITY_TEAM,
    IMPORT_SOURCE_FILE,
)
from app.ingestion.errors import IngestionFailedError, IngestionIssue
from app.ingestion.report import ValidationReport
from app.ingestion.schemas.file_v1 import ImportBundleV1
from app.ingestion.validate import validate_bundle_structure
from app.models import League, Match, MatchStatus, Player, Season, SetResult, Team, TeamRoster
from app.repositories.ingestion_external_key import IngestionExternalKeyRepository
from app.repositories.league import LeagueRepository
from app.repositories.match import MatchRepository
from app.repositories.player import PlayerRepository
from app.repositories.season import SeasonRepository
from app.repositories.team import TeamRepository


def roster_external_id(team_ref: str, player_ref: str, season_ref: str) -> str:
    return f"{team_ref}|{player_ref}|{season_ref}"


@dataclass
class _ApplyStats:
    create: dict[str, int] = field(default_factory=dict)
    skip: dict[str, int] = field(default_factory=dict)

    def bump_create(self, entity_type: str) -> None:
        self.create[entity_type] = self.create.get(entity_type, 0) + 1

    def bump_skip(self, entity_type: str) -> None:
        self.skip[entity_type] = self.skip.get(entity_type, 0) + 1


class StrictFileImporter:
    def __init__(self, session: Session, bundle: ImportBundleV1) -> None:
        self.session = session
        self.bundle = bundle
        self.source = IMPORT_SOURCE_FILE
        self.bundle_ref = bundle.source_label
        self.keys = IngestionExternalKeyRepository(session)
        self.stats = _ApplyStats()
        self.issues: list[IngestionIssue] = []

        self._league_id: UUID | None = None
        self._season_ids: dict[str, UUID] = {}
        self._team_ids: dict[str, UUID] = {}
        self._player_ids: dict[str, UUID] = {}

    def run(self) -> ValidationReport:
        structural = validate_bundle_structure(self.bundle)
        if structural:
            return self._report(valid=False, issues=structural)

        try:
            self._import_league()
            for season in self.bundle.seasons:
                self._import_season(season)
            for team in self.bundle.teams:
                self._import_team(team)
            for player in self.bundle.players:
                self._import_player(player)
            for roster in self.bundle.rosters:
                self._import_roster(roster)
            for match in self.bundle.matches:
                self._import_match(match)
        except IngestionFailedError as exc:
            self.issues.extend(exc.issues)
            return self._report(valid=False)

        if self.issues:
            return self._report(valid=False)
        return self._report(valid=True)

    def _report(self, valid: bool, issues: list[IngestionIssue] | None = None) -> ValidationReport:
        merged = self.issues + (issues or [])
        return ValidationReport(
            valid=valid and not merged,
            schema_version=self.bundle.schema_version,
            source_label=self.bundle.source_label,
            bundle_ref=self.bundle_ref,
            counts={
                "leagues": 1,
                "seasons": len(self.bundle.seasons),
                "teams": len(self.bundle.teams),
                "players": len(self.bundle.players),
                "rosters": len(self.bundle.rosters),
                "matches": len(self.bundle.matches),
            },
            issues=merged,
            would_create=self.stats.create,
            would_skip=self.stats.skip,
        )

    def _fail(self, issue: IngestionIssue) -> None:
        raise IngestionFailedError([issue])

    def _get_mapping(self, entity_type: str, external_id: str):
        return self.keys.get_mapping(
            source=self.source,
            entity_type=entity_type,
            external_id=external_id,
        )

    def _register(self, entity_type: str, external_id: str, internal_id: UUID) -> None:
        self.keys.register(
            source=self.source,
            entity_type=entity_type,
            external_id=external_id,
            internal_id=internal_id,
            bundle_ref=self.bundle_ref,
        )

    def _ensure_natural_key_free(
        self,
        *,
        entity_type: str,
        entity_ref: str,
        natural_label: str,
        existing_row: object | None,
        natural_field: str,
    ) -> None:
        mapping = self._get_mapping(entity_type, entity_ref)
        if existing_row is None:
            return
        existing_id = getattr(existing_row, "id")
        if mapping is None:
            self._fail(
                IngestionIssue(
                    code="slug_conflict",
                    message=(
                        f"{natural_label} уже существует в базе без привязки к ref «{entity_ref}»."
                    ),
                    entity_type=entity_type,
                    entity_ref=entity_ref,
                    field=natural_field,
                )
            )
        if mapping.internal_id != existing_id:
            self._fail(
                IngestionIssue(
                    code="ambiguous_match",
                    message=(
                        f"Неоднозначное сопоставление: ref «{entity_ref}» и существующий "
                        f"{natural_label} указывают на разные записи."
                    ),
                    entity_type=entity_type,
                    entity_ref=entity_ref,
                    field=natural_field,
                )
            )

    def _compare_or_fail(
        self,
        *,
        entity_type: str,
        entity_ref: str,
        field: str,
        expected: object,
        actual: object,
    ) -> None:
        if expected != actual:
            self._fail(
                IngestionIssue(
                    code="data_conflict",
                    message=(
                        f"Конфликт данных: поле «{field}» в базе ({actual!r}) "
                        f"не совпадает с файлом ({expected!r})."
                    ),
                    entity_type=entity_type,
                    entity_ref=entity_ref,
                    field=field,
                )
            )

    def _import_league(self) -> None:
        payload = self.bundle.league
        mapping = self._get_mapping(ENTITY_LEAGUE, payload.ref)
        repo = LeagueRepository(self.session)
        existing = repo.get_by_slug(payload.slug)
        self._ensure_natural_key_free(
            entity_type=ENTITY_LEAGUE,
            entity_ref=payload.ref,
            natural_label=f"лига со slug «{payload.slug}»",
            existing_row=existing,
            natural_field="slug",
        )
        if mapping:
            league = self.session.get(League, mapping.internal_id)
            if league is None:
                self._fail(
                    IngestionIssue(
                        code="broken_mapping",
                        message="Внешний ключ лиги указывает на отсутствующую запись.",
                        entity_type=ENTITY_LEAGUE,
                        entity_ref=payload.ref,
                    )
                )
            self._compare_or_fail(
                entity_type=ENTITY_LEAGUE,
                entity_ref=payload.ref,
                field="name",
                expected=payload.name,
                actual=league.name,
            )
            self._compare_or_fail(
                entity_type=ENTITY_LEAGUE,
                entity_ref=payload.ref,
                field="slug",
                expected=payload.slug,
                actual=league.slug,
            )
            self._league_id = league.id
            self.stats.bump_skip(ENTITY_LEAGUE)
            return

        if existing is not None:
            self._fail(
                IngestionIssue(
                    code="slug_conflict",
                    message=f"Лига со slug «{payload.slug}» уже существует.",
                    entity_type=ENTITY_LEAGUE,
                    entity_ref=payload.ref,
                    field="slug",
                )
            )

        league = League(name=payload.name, slug=payload.slug)
        self.session.add(league)
        self.session.flush()
        self._register(ENTITY_LEAGUE, payload.ref, league.id)
        self._league_id = league.id
        self.stats.bump_create(ENTITY_LEAGUE)

    def _import_season(self, payload) -> None:
        assert self._league_id is not None
        mapping = self._get_mapping(ENTITY_SEASON, payload.ref)
        repo = SeasonRepository(self.session)
        existing = repo.get_by_league_and_name(self._league_id, payload.name)
        if mapping:
            season = self.session.get(Season, mapping.internal_id)
            if season is None:
                self._fail(
                    IngestionIssue(
                        code="broken_mapping",
                        message="Внешний ключ сезона указывает на отсутствующую запись.",
                        entity_type=ENTITY_SEASON,
                        entity_ref=payload.ref,
                    )
                )
            self._compare_or_fail(
                entity_type=ENTITY_SEASON,
                entity_ref=payload.ref,
                field="name",
                expected=payload.name,
                actual=season.name,
            )
            self._compare_or_fail(
                entity_type=ENTITY_SEASON,
                entity_ref=payload.ref,
                field="start_date",
                expected=payload.start_date,
                actual=season.start_date,
            )
            self._compare_or_fail(
                entity_type=ENTITY_SEASON,
                entity_ref=payload.ref,
                field="end_date",
                expected=payload.end_date,
                actual=season.end_date,
            )
            self._season_ids[payload.ref] = season.id
            self.stats.bump_skip(ENTITY_SEASON)
            return

        if existing is not None:
            self._fail(
                IngestionIssue(
                    code="natural_key_conflict",
                    message=(
                        f"Сезон «{payload.name}» в этой лиге уже существует без ref "
                        f"«{payload.ref}»."
                    ),
                    entity_type=ENTITY_SEASON,
                    entity_ref=payload.ref,
                    field="name",
                )
            )

        season = Season(
            league_id=self._league_id,
            name=payload.name,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )
        self.session.add(season)
        self.session.flush()
        self._register(ENTITY_SEASON, payload.ref, season.id)
        self._season_ids[payload.ref] = season.id
        self.stats.bump_create(ENTITY_SEASON)

    def _import_team(self, payload) -> None:
        mapping = self._get_mapping(ENTITY_TEAM, payload.ref)
        repo = TeamRepository(self.session)
        existing = repo.get_by_slug(payload.slug)
        self._ensure_natural_key_free(
            entity_type=ENTITY_TEAM,
            entity_ref=payload.ref,
            natural_label=f"команда со slug «{payload.slug}»",
            existing_row=existing,
            natural_field="slug",
        )
        if mapping:
            team = self.session.get(Team, mapping.internal_id)
            if team is None:
                self._fail(
                    IngestionIssue(
                        code="broken_mapping",
                        message="Внешний ключ команды указывает на отсутствующую запись.",
                        entity_type=ENTITY_TEAM,
                        entity_ref=payload.ref,
                    )
                )
            self._compare_or_fail(
                entity_type=ENTITY_TEAM,
                entity_ref=payload.ref,
                field="name",
                expected=payload.name,
                actual=team.name,
            )
            self._compare_or_fail(
                entity_type=ENTITY_TEAM,
                entity_ref=payload.ref,
                field="slug",
                expected=payload.slug,
                actual=team.slug,
            )
            self._compare_or_fail(
                entity_type=ENTITY_TEAM,
                entity_ref=payload.ref,
                field="logo_url",
                expected=payload.logo_url,
                actual=team.logo_url,
            )
            self._team_ids[payload.ref] = team.id
            self.stats.bump_skip(ENTITY_TEAM)
            return

        if existing is not None:
            self._fail(
                IngestionIssue(
                    code="slug_conflict",
                    message=f"Команда со slug «{payload.slug}» уже существует.",
                    entity_type=ENTITY_TEAM,
                    entity_ref=payload.ref,
                    field="slug",
                )
            )

        team = Team(name=payload.name, slug=payload.slug, logo_url=payload.logo_url)
        self.session.add(team)
        self.session.flush()
        self._register(ENTITY_TEAM, payload.ref, team.id)
        self._team_ids[payload.ref] = team.id
        self.stats.bump_create(ENTITY_TEAM)

    def _import_player(self, payload) -> None:
        mapping = self._get_mapping(ENTITY_PLAYER, payload.ref)
        repo = PlayerRepository(self.session)
        existing = repo.get_by_demo_slug(payload.ref)
        self._ensure_natural_key_free(
            entity_type=ENTITY_PLAYER,
            entity_ref=payload.ref,
            natural_label=f"игрок с ключом «{payload.ref}»",
            existing_row=existing,
            natural_field="ref→demo_slug",
        )
        if mapping:
            player = self.session.get(Player, mapping.internal_id)
            if player is None:
                self._fail(
                    IngestionIssue(
                        code="broken_mapping",
                        message="Внешний ключ игрока указывает на отсутствующую запись.",
                        entity_type=ENTITY_PLAYER,
                        entity_ref=payload.ref,
                    )
                )
            for field_name in (
                "first_name",
                "last_name",
                "display_name",
                "position",
            ):
                self._compare_or_fail(
                    entity_type=ENTITY_PLAYER,
                    entity_ref=payload.ref,
                    field=field_name,
                    expected=getattr(payload, field_name),
                    actual=getattr(player, field_name),
                )
            self._compare_or_fail(
                entity_type=ENTITY_PLAYER,
                entity_ref=payload.ref,
                field="demo_slug",
                expected=payload.ref,
                actual=player.demo_slug,
            )
            self._player_ids[payload.ref] = player.id
            self.stats.bump_skip(ENTITY_PLAYER)
            return

        if existing is not None:
            self._fail(
                IngestionIssue(
                    code="slug_conflict",
                    message=f"Игрок с demo_slug «{payload.ref}» уже существует.",
                    entity_type=ENTITY_PLAYER,
                    entity_ref=payload.ref,
                    field="ref",
                )
            )

        player = Player(
            demo_slug=payload.ref,
            first_name=payload.first_name,
            last_name=payload.last_name,
            display_name=payload.display_name,
            position=payload.position,
        )
        self.session.add(player)
        self.session.flush()
        self._register(ENTITY_PLAYER, payload.ref, player.id)
        self._player_ids[payload.ref] = player.id
        self.stats.bump_create(ENTITY_PLAYER)

    def _import_roster(self, payload) -> None:
        external_id = roster_external_id(payload.team_ref, payload.player_ref, payload.season_ref)
        team_id = self._team_ids[payload.team_ref]
        player_id = self._player_ids[payload.player_ref]
        season_id = self._season_ids[payload.season_ref]
        mapping = self._get_mapping(ENTITY_ROSTER, external_id)
        existing = self.session.scalar(
            select(TeamRoster).where(
                TeamRoster.team_id == team_id,
                TeamRoster.player_id == player_id,
                TeamRoster.season_id == season_id,
            )
        )
        if mapping:
            roster = self.session.get(TeamRoster, mapping.internal_id)
            if roster is None:
                self._fail(
                    IngestionIssue(
                        code="broken_mapping",
                        message="Внешний ключ состава указывает на отсутствующую запись.",
                        entity_type=ENTITY_ROSTER,
                        entity_ref=external_id,
                    )
                )
            self._compare_roster(payload, roster, external_id)
            self.stats.bump_skip(ENTITY_ROSTER)
            return

        if existing is not None:
            self._fail(
                IngestionIssue(
                    code="natural_key_conflict",
                    message="Заявка уже существует без привязки к внешнему ключу файла.",
                    entity_type=ENTITY_ROSTER,
                    entity_ref=external_id,
                )
            )

        roster = TeamRoster(
            team_id=team_id,
            player_id=player_id,
            season_id=season_id,
            jersey_number=payload.jersey_number,
            active_from=payload.active_from,
            active_until=payload.active_until,
        )
        self.session.add(roster)
        self.session.flush()
        self._register(ENTITY_ROSTER, external_id, roster.id)
        self.stats.bump_create(ENTITY_ROSTER)

    def _compare_roster(self, payload, roster: TeamRoster, external_id: str) -> None:
        self._compare_or_fail(
            entity_type=ENTITY_ROSTER,
            entity_ref=external_id,
            field="jersey_number",
            expected=payload.jersey_number,
            actual=roster.jersey_number,
        )
        self._compare_or_fail(
            entity_type=ENTITY_ROSTER,
            entity_ref=external_id,
            field="active_from",
            expected=payload.active_from,
            actual=roster.active_from,
        )
        self._compare_or_fail(
            entity_type=ENTITY_ROSTER,
            entity_ref=external_id,
            field="active_until",
            expected=payload.active_until,
            actual=roster.active_until,
        )

    def _import_match(self, payload) -> None:
        season_id = self._season_ids[payload.season_ref]
        home_team_id = self._team_ids[payload.home_team_ref]
        away_team_id = self._team_ids[payload.away_team_ref]
        mapping = self._get_mapping(ENTITY_MATCH, payload.ref)
        match_repo = MatchRepository(self.session)

        if mapping:
            match = self.session.get(Match, mapping.internal_id)
            if match is None:
                self._fail(
                    IngestionIssue(
                        code="broken_mapping",
                        message="Внешний ключ матча указывает на отсутствующую запись.",
                        entity_type=ENTITY_MATCH,
                        entity_ref=payload.ref,
                    )
                )
            self._compare_match_fields(payload, match, season_id, home_team_id, away_team_id)
            self._compare_sets(payload, match)
            self.stats.bump_skip(ENTITY_MATCH)
            return

        if payload.scheduled_at is not None:
            existing = match_repo.get_by_natural_key(
                season_id=season_id,
                scheduled_at=payload.scheduled_at,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
            )
            if existing is not None:
                self._fail(
                    IngestionIssue(
                        code="natural_key_conflict",
                        message="Матч с тем же сезоном, датой и сторонами уже существует.",
                        entity_type=ENTITY_MATCH,
                        entity_ref=payload.ref,
                    )
                )

        match = Match(
            season_id=season_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            scheduled_at=payload.scheduled_at,
            status=MatchStatus(payload.status),
            venue=payload.venue,
        )
        self.session.add(match)
        self.session.flush()
        self._apply_sets(payload, match, is_new=True)
        self._register(ENTITY_MATCH, payload.ref, match.id)
        self.stats.bump_create(ENTITY_MATCH)

    def _compare_match_fields(
        self,
        payload,
        match: Match,
        season_id: UUID,
        home_team_id: UUID,
        away_team_id: UUID,
    ) -> None:
        self._compare_or_fail(
            entity_type=ENTITY_MATCH,
            entity_ref=payload.ref,
            field="season_id",
            expected=season_id,
            actual=match.season_id,
        )
        self._compare_or_fail(
            entity_type=ENTITY_MATCH,
            entity_ref=payload.ref,
            field="home_team_id",
            expected=home_team_id,
            actual=match.home_team_id,
        )
        self._compare_or_fail(
            entity_type=ENTITY_MATCH,
            entity_ref=payload.ref,
            field="away_team_id",
            expected=away_team_id,
            actual=match.away_team_id,
        )
        self._compare_or_fail(
            entity_type=ENTITY_MATCH,
            entity_ref=payload.ref,
            field="scheduled_at",
            expected=payload.scheduled_at,
            actual=match.scheduled_at,
        )
        self._compare_or_fail(
            entity_type=ENTITY_MATCH,
            entity_ref=payload.ref,
            field="status",
            expected=MatchStatus(payload.status),
            actual=match.status,
        )
        self._compare_or_fail(
            entity_type=ENTITY_MATCH,
            entity_ref=payload.ref,
            field="venue",
            expected=payload.venue,
            actual=match.venue,
        )

    def _compare_sets(self, payload, match: Match) -> None:
        existing = {
            row.set_number: (row.home_score, row.away_score)
            for row in self.session.scalars(
                select(SetResult).where(SetResult.match_id == match.id)
            ).all()
        }
        expected = {row.set_number: (row.home_score, row.away_score) for row in payload.sets}
        if existing != expected:
            self._fail(
                IngestionIssue(
                    code="data_conflict",
                    message="Счёт сетов в базе не совпадает с файлом.",
                    entity_type=ENTITY_MATCH,
                    entity_ref=payload.ref,
                    field="sets",
                )
            )

    def _apply_sets(self, payload, match: Match, *, is_new: bool) -> None:
        if not is_new:
            self._compare_sets(payload, match)
            return
        for set_row in sorted(payload.sets, key=lambda item: item.set_number):
            self.session.add(
                SetResult(
                    match_id=match.id,
                    set_number=set_row.set_number,
                    home_score=set_row.home_score,
                    away_score=set_row.away_score,
                )
            )
        self.session.flush()


def run_strict_import(session: Session, bundle: ImportBundleV1) -> ValidationReport:
    importer = StrictFileImporter(session, bundle)
    return importer.run()

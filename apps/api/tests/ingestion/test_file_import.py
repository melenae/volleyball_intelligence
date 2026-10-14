from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.ingestion.demo.seed import count_domain_rows, seed_demo_league
from app.ingestion.service import import_file, validate_import_file
from app.models import IngestionExternalKey, League, Match

pytestmark = pytest.mark.postgres

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
VALID_BUNDLE = FIXTURES / "import_bundle_valid.v1.json"


def test_validate_valid_structure() -> None:
    report = validate_import_file(VALID_BUNDLE)
    assert report.valid is True
    assert report.schema_version == 1
    assert report.counts["teams"] == 2


def test_validate_rejects_unknown_schema(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"schema_version": 99, "source_label": "x"}', encoding="utf-8")
    report = validate_import_file(path)
    assert report.valid is False
    assert any(issue.code == "unsupported_schema" for issue in report.issues)


def test_validate_unknown_team_ref(tmp_path: Path) -> None:
    path = tmp_path / "bad-ref.json"
    path.write_text(
        (
            '{"schema_version":1,"source_label":"bad",'
            '"league":{"ref":"lg","name":"L","slug":"slug-lg-bad"},'
            '"seasons":[{"ref":"sn","name":"S","start_date":"2099-01-01",'
            '"end_date":"2099-12-31","league_ref":"lg"}],'
            '"teams":[{"ref":"t1","name":"A","slug":"slug-t1-bad"}],'
            '"players":[],'
            '"rosters":[{"team_ref":"missing","player_ref":"p","season_ref":"sn"}],'
            '"matches":[]}'
        ),
        encoding="utf-8",
    )
    report = validate_import_file(path)
    assert report.valid is False
    assert any(issue.code == "unknown_reference" for issue in report.issues)


def test_validate_duplicate_ref(tmp_path: Path) -> None:
    path = tmp_path / "dup.json"
    path.write_text(
        """
{
  "schema_version": 1,
  "source_label": "dup",
  "league": {"ref": "lg", "name": "L", "slug": "slug-lg-dup"},
  "seasons": [],
  "teams": [
    {"ref": "same", "name": "A", "slug": "slug-a-dup"},
    {"ref": "same", "name": "B", "slug": "slug-b-dup"}
  ],
  "players": [],
  "matches": []
}
""".strip(),
        encoding="utf-8",
    )
    report = validate_import_file(path)
    assert report.valid is False
    assert any(issue.code == "duplicate_ref" for issue in report.issues)


def test_import_valid_bundle(db_session: Session) -> None:
    before = count_domain_rows(db_session)
    report = import_file(db_session, VALID_BUNDLE, dry_run=False)
    assert report.valid is True
    after = count_domain_rows(db_session)
    assert after["leagues"] == before["leagues"] + 1
    assert after["matches"] == before["matches"] + 1
    keys = db_session.scalar(select(func.count()).select_from(IngestionExternalKey)) or 0
    assert keys >= 6


def test_reimport_is_idempotent(db_session: Session) -> None:
    first = import_file(db_session, VALID_BUNDLE, dry_run=False)
    assert first.valid is True
    counts_after_first = count_domain_rows(db_session)
    second = import_file(db_session, VALID_BUNDLE, dry_run=False)
    assert second.valid is True
    assert count_domain_rows(db_session) == counts_after_first
    assert second.would_skip.get("team", 0) >= 2


def test_dry_run_does_not_persist(db_session: Session) -> None:
    before = count_domain_rows(db_session)
    report = import_file(db_session, VALID_BUNDLE, dry_run=True)
    assert report.valid is True
    db_session.expire_all()
    assert count_domain_rows(db_session) == before


def test_import_rolls_back_on_conflict(db_session: Session) -> None:
    import_file(db_session, VALID_BUNDLE, dry_run=False)
    counts = count_domain_rows(db_session)

    conflict_path = FIXTURES / "import_bundle_conflict.v1.json"
    report = import_file(db_session, conflict_path, dry_run=False)
    assert report.valid is False
    assert any(issue.code == "data_conflict" for issue in report.issues)
    assert count_domain_rows(db_session) == counts


def test_slug_conflict_with_demo_seed(db_session: Session) -> None:
    seed_demo_league(db_session)
    path = FIXTURES / "import_bundle_demo_slug_conflict.v1.json"
    report = import_file(db_session, path, dry_run=False)
    assert report.valid is False
    assert any(issue.code == "slug_conflict" for issue in report.issues)


def test_ambiguous_mapping_blocked(db_session: Session, tmp_path: Path) -> None:
    seed_demo_league(db_session)
    path = tmp_path / "ambiguous.json"
    path.write_text(
        (
            '{"schema_version":1,"source_label":"ambiguous-case",'
            '"league":{"ref":"new-lg","name":"X","slug":"brand-new-league-ambiguous"},'
            '"seasons":[{"ref":"sn","name":"S","start_date":"2098-01-01",'
            '"end_date":"2098-12-31","league_ref":"new-lg"}],'
            '"teams":[{"ref":"team-new-ref","name":"Северный ветер","slug":"severny-veter"}],'
            '"players":[],"matches":[]}'
        ),
        encoding="utf-8",
    )
    report = import_file(db_session, path, dry_run=False)
    assert report.valid is False
    assert any(issue.code in {"slug_conflict", "ambiguous_match"} for issue in report.issues)


def test_transaction_rollback_on_mid_bundle_error(db_session: Session) -> None:
    seed_demo_league(db_session)
    before = (
        db_session.scalar(
            select(func.count()).select_from(League).where(League.slug == "new-league-not-demo")
        )
        or 0
    )
    report = import_file(
        db_session,
        FIXTURES / "import_bundle_demo_slug_conflict.v1.json",
        dry_run=False,
    )
    assert report.valid is False
    db_session.expire_all()
    after = (
        db_session.scalar(
            select(func.count()).select_from(League).where(League.slug == "new-league-not-demo")
        )
        or 0
    )
    assert after == before == 0


def test_import_creates_match_with_sets(db_session: Session) -> None:
    report = import_file(db_session, VALID_BUNDLE, dry_run=False)
    assert report.valid is True
    match = db_session.scalar(
        select(Match).options(selectinload(Match.set_results)).where(Match.venue == "Зал импорта")
    )
    assert match is not None
    assert len(match.set_results) == 2

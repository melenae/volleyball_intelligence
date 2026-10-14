from pathlib import Path

from sqlalchemy.orm import Session

from app.ingestion.errors import IngestionFailedError
from app.ingestion.report import ValidationReport
from app.ingestion.schemas.file_v1 import ImportBundleV1
from app.ingestion.sources.file_json import JsonFileImportSource
from app.ingestion.validate import validate_bundle_structure
from app.ingestion.writer import run_strict_import


def parse_import_file(path: Path) -> ImportBundleV1:
    source = JsonFileImportSource(path)
    return source.load_bundle()


def validate_import_file(path: Path) -> ValidationReport:
    try:
        bundle = parse_import_file(path)
    except IngestionFailedError as exc:
        return ValidationReport(valid=False, issues=exc.issues)

    structural = validate_bundle_structure(bundle)
    if structural:
        return ValidationReport(
            valid=False,
            schema_version=bundle.schema_version,
            source_label=bundle.source_label,
            bundle_ref=bundle.source_label,
            counts={
                "leagues": 1,
                "seasons": len(bundle.seasons),
                "teams": len(bundle.teams),
                "players": len(bundle.players),
                "rosters": len(bundle.rosters),
                "matches": len(bundle.matches),
            },
            issues=structural,
        )

    return ValidationReport(
        valid=True,
        schema_version=bundle.schema_version,
        source_label=bundle.source_label,
        bundle_ref=bundle.source_label,
        counts={
            "leagues": 1,
            "seasons": len(bundle.seasons),
            "teams": len(bundle.teams),
            "players": len(bundle.players),
            "rosters": len(bundle.rosters),
            "matches": len(bundle.matches),
        },
        issues=[],
    )


def import_file(session: Session, path: Path, *, dry_run: bool = False) -> ValidationReport:
    bundle = parse_import_file(path)
    report = run_strict_import(session, bundle)
    if not report.valid:
        session.rollback()
        return report
    if dry_run:
        session.rollback()
        return report
    session.commit()
    return report

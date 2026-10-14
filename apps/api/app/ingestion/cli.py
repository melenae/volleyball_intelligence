"""CLI импорта: python -m app.ingestion.cli <command> ..."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.db.session import SessionLocal
from app.ingestion.constants import IMPORT_SOURCE_FILE
from app.ingestion.report import ValidationReport
from app.ingestion.service import import_file, validate_import_file
from app.repositories.ingestion_external_key import IngestionExternalKeyRepository


def _print_report(report: ValidationReport) -> None:
    if report.valid:
        print("Проверка пройдена.")
    else:
        print("Проверка не пройдена.")
    for issue in report.issues:
        parts = [issue.code, issue.message]
        if issue.entity_type:
            parts.append(f"({issue.entity_type}")
            if issue.entity_ref:
                parts.append(f" ref={issue.entity_ref}")
            parts.append(")")
        print("-", " ".join(parts))
    if report.would_create:
        print("Создать:", report.would_create)
    if report.would_skip:
        print("Пропустить (без изменений):", report.would_skip)


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.path)
    report = validate_import_file(path)
    if args.report:
        Path(args.report).write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    _print_report(report)
    return 0 if report.valid else 1


def cmd_report(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        print(f"Файл отчёта не найден: {path}", file=sys.stderr)
        return 1
    data = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    path = Path(args.path)
    with SessionLocal() as session:
        report = import_file(session, path, dry_run=args.dry_run)
    if args.report:
        Path(args.report).write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    _print_report(report)
    if args.dry_run and report.valid:
        print("(dry-run: изменения в базу не записаны)")
    elif report.valid:
        print("Импорт успешно завершён.")
    return 0 if report.valid else 1


def cmd_summary(args: argparse.Namespace) -> int:
    with SessionLocal() as session:
        repo = IngestionExternalKeyRepository(session)
        source = args.source or IMPORT_SOURCE_FILE
        bundles = repo.list_bundles(source=source)
        if args.bundle:
            counts = repo.count_by_bundle(args.bundle, source)
            print(f"Источник: {source}, пакет: {args.bundle}")
            print(json.dumps(counts, ensure_ascii=False, indent=2))
            return 0
        print(f"Источник: {source}")
        if not bundles:
            print("Импортированные пакеты не найдены.")
            return 0
        for bundle_ref in bundles:
            counts = repo.count_by_bundle(bundle_ref, source)
            print(f"\nПакет: {bundle_ref}")
            print(json.dumps(counts, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Импорт данных Volleyball Intelligence")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Проверить файл без записи в БД")
    validate.add_argument("path", help="Путь к JSON v1")
    validate.add_argument("--report", help="Сохранить JSON-отчёт")
    validate.set_defaults(func=cmd_validate)

    report = sub.add_parser("report", help="Показать сохранённый JSON-отчёт")
    report.add_argument("path", help="Путь к файлу отчёта")
    report.set_defaults(func=cmd_report)

    import_cmd = sub.add_parser("import", help="Импортировать валидный файл")
    import_cmd.add_argument("path", help="Путь к JSON v1")
    import_cmd.add_argument("--dry-run", action="store_true", help="Проверка с откатом транзакции")
    import_cmd.add_argument("--report", help="Сохранить JSON-отчёт")
    import_cmd.set_defaults(func=cmd_import)

    summary = sub.add_parser("summary", help="Сводка по ingestion_external_keys")
    summary.add_argument("--source", default=None, help="Код источника (по умолчанию file)")
    summary.add_argument("--bundle", default=None, help="Фильтр по source_label пакета")
    summary.set_defaults(func=cmd_summary)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    code = args.func(args)
    raise SystemExit(code)


if __name__ == "__main__":
    main()

import json
from pathlib import Path

from pydantic import ValidationError

from app.ingestion.constants import SUPPORTED_SCHEMA_VERSION
from app.ingestion.errors import IngestionFailedError, IngestionIssue
from app.ingestion.schemas.file_v1 import ImportBundleV1


class JsonFileImportSource:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load_bundle(self) -> ImportBundleV1:
        raw = self.path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise IngestionFailedError(
                [
                    IngestionIssue(
                        code="invalid_json",
                        message=f"Некорректный JSON: {exc.msg}",
                    )
                ]
            ) from exc
        if not isinstance(data, dict):
            raise IngestionFailedError(
                [
                    IngestionIssue(
                        code="invalid_structure",
                        message="Корень файла должен быть объектом JSON.",
                    )
                ]
            )
        version = data.get("schema_version")
        if version != SUPPORTED_SCHEMA_VERSION:
            raise IngestionFailedError(
                [
                    IngestionIssue(
                        code="unsupported_schema",
                        message=f"Неподдерживаемая schema_version: {version!r}",
                        field="schema_version",
                    )
                ]
            )
        try:
            return ImportBundleV1.model_validate(data)
        except ValidationError as exc:
            first = exc.errors()[0]
            loc = ".".join(str(part) for part in first.get("loc", ()))
            raise IngestionFailedError(
                [
                    IngestionIssue(
                        code="validation_error",
                        message=str(first.get("msg", "Ошибка валидации")),
                        field=loc or None,
                    )
                ]
            ) from exc

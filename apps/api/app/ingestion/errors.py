from dataclasses import dataclass


@dataclass(frozen=True)
class IngestionIssue:
    code: str
    message: str
    entity_type: str | None = None
    entity_ref: str | None = None
    field: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload: dict[str, str] = {"code": self.code, "message": self.message}
        if self.entity_type:
            payload["entity_type"] = self.entity_type
        if self.entity_ref:
            payload["entity_ref"] = self.entity_ref
        if self.field:
            payload["field"] = self.field
        return payload


class IngestionFailedError(Exception):
    def __init__(self, issues: list[IngestionIssue]) -> None:
        self.issues = issues
        super().__init__(issues[0].message if issues else "Import failed")

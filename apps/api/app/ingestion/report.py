from dataclasses import dataclass, field

from app.ingestion.errors import IngestionIssue


@dataclass
class ValidationReport:
    valid: bool
    schema_version: int | None = None
    source_label: str | None = None
    bundle_ref: str | None = None
    counts: dict[str, int] = field(default_factory=dict)
    issues: list[IngestionIssue] = field(default_factory=list)
    would_create: dict[str, int] = field(default_factory=dict)
    would_skip: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "schema_version": self.schema_version,
            "source_label": self.source_label,
            "bundle_ref": self.bundle_ref,
            "counts": self.counts,
            "would_create": self.would_create,
            "would_skip": self.would_skip,
            "issues": [issue.to_dict() for issue in self.issues],
        }

"""Documented stub for a future AVL ImportDataSource. Not wired to CLI or HTTP."""

from app.ingestion.schemas.file_v1 import ImportBundleV1


class AvlImportDataSourceNotConfiguredError(NotImplementedError):
    """Raised if code attempts to load AVL before a contract exists."""


class AvlImportDataSource:
    """Placeholder type for future implementation."""

    def load_bundle(self) -> ImportBundleV1:
        raise AvlImportDataSourceNotConfiguredError(
            "AVL adapter is not configured. See docs/ingestion/avl-adapter-placeholder.md."
        )

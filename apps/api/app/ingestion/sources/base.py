from typing import Protocol

from app.ingestion.schemas.file_v1 import ImportBundleV1


class ImportDataSource(Protocol):
    def load_bundle(self) -> ImportBundleV1:
        """Read and parse a versioned import bundle."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ingestion import IngestionExternalKey
from app.repositories.base import Repository


class IngestionExternalKeyRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_mapping(
        self,
        *,
        source: str,
        entity_type: str,
        external_id: str,
    ) -> IngestionExternalKey | None:
        return self.session.scalar(
            select(IngestionExternalKey).where(
                IngestionExternalKey.source == source,
                IngestionExternalKey.entity_type == entity_type,
                IngestionExternalKey.external_id == external_id,
            )
        )

    def register(
        self,
        *,
        source: str,
        entity_type: str,
        external_id: str,
        internal_id: UUID,
        bundle_ref: str | None,
    ) -> IngestionExternalKey:
        row = IngestionExternalKey(
            source=source,
            entity_type=entity_type,
            external_id=external_id,
            internal_id=internal_id,
            bundle_ref=bundle_ref,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def count_by_bundle(self, bundle_ref: str | None, source: str | None) -> dict[str, int]:
        stmt = select(
            IngestionExternalKey.entity_type,
            func.count(),
        ).group_by(IngestionExternalKey.entity_type)
        if bundle_ref is not None:
            stmt = stmt.where(IngestionExternalKey.bundle_ref == bundle_ref)
        if source is not None:
            stmt = stmt.where(IngestionExternalKey.source == source)
        rows = self.session.execute(stmt).all()
        return {entity_type: int(count) for entity_type, count in rows}

    def list_bundles(self, source: str | None = None) -> list[str]:
        stmt = select(IngestionExternalKey.bundle_ref).distinct()
        if source is not None:
            stmt = stmt.where(IngestionExternalKey.source == source)
        stmt = stmt.where(IngestionExternalKey.bundle_ref.is_not(None))
        return [row for row in self.session.scalars(stmt).all() if row]

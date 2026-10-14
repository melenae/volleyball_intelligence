import uuid

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class IngestionExternalKey(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ingestion_external_keys"
    __table_args__ = (
        UniqueConstraint(
            "source",
            "entity_type",
            "external_id",
            name="uq_ingestion_external_keys_source_entity_external",
        ),
        Index("ix_ingestion_external_keys_internal", "entity_type", "internal_id"),
        Index("ix_ingestion_external_keys_bundle_ref", "bundle_ref"),
    )

    source: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    external_id: Mapped[str] = mapped_column(String(200), nullable=False)
    internal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    bundle_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)

"""ingestion external keys

Revision ID: c4e8f1a92b3d
Revises: b8bb5fdc246b
Create Date: 2026-10-15 00:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4e8f1a92b3d"
down_revision: Union[str, Sequence[str], None] = "b8bb5fdc246b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ingestion_external_keys",
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("external_id", sa.String(length=200), nullable=False),
        sa.Column("internal_id", sa.UUID(), nullable=False),
        sa.Column("bundle_ref", sa.String(length=200), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source",
            "entity_type",
            "external_id",
            name="uq_ingestion_external_keys_source_entity_external",
        ),
    )
    op.create_index(
        "ix_ingestion_external_keys_internal",
        "ingestion_external_keys",
        ["entity_type", "internal_id"],
        unique=False,
    )
    op.create_index(
        "ix_ingestion_external_keys_bundle_ref",
        "ingestion_external_keys",
        ["bundle_ref"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ingestion_external_keys_bundle_ref", table_name="ingestion_external_keys")
    op.drop_index("ix_ingestion_external_keys_internal", table_name="ingestion_external_keys")
    op.drop_table("ingestion_external_keys")

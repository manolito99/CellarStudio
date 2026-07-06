"""add deleted_at column to barbers and clients (soft delete)

Revision ID: 008_soft_delete_barbers_clients
Revises: 007_add_service_deleted_at
Create Date: 2026-07-06

Note: the revision id must stay <= 32 chars (alembic_version.version_num is
VARCHAR(32)).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "008_soft_delete_barbers_clients"
down_revision: Union[str, None] = "007_add_service_deleted_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "barbers",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "clients",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("clients", "deleted_at")
    op.drop_column("barbers", "deleted_at")

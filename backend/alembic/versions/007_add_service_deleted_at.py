"""add deleted_at column to services (soft delete)

Revision ID: 007_add_service_deleted_at
Revises: 006_add_notifications
Create Date: 2026-07-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "007_add_service_deleted_at"
down_revision: Union[str, None] = "006_add_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "services",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("services", "deleted_at")

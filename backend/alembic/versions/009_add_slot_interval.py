"""add slot_interval_minutes to schedules and available_days

Revision ID: 009_add_slot_interval
Revises: 008_soft_delete_barbers_clients
Create Date: 2026-07-07

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "009_add_slot_interval"
down_revision: Union[str, None] = "008_soft_delete_barbers_clients"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "schedules",
        sa.Column(
            "slot_interval_minutes",
            sa.Integer(),
            server_default="60",
            nullable=False,
        ),
    )
    op.add_column(
        "available_days",
        sa.Column(
            "slot_interval_minutes",
            sa.Integer(),
            server_default="60",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("available_days", "slot_interval_minutes")
    op.drop_column("schedules", "slot_interval_minutes")

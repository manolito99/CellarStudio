"""add available_days table

Revision ID: 003_add_available_days
Revises: 002_add_reminder_sent
Create Date: 2026-02-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003_add_available_days"
down_revision: Union[str, None] = "002_add_reminder_sent"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "available_days",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "barber_id",
            sa.String(36),
            sa.ForeignKey("barbers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("available_days")

"""add email_reminder_sent column to appointments

Revision ID: 004_add_email_reminder_sent
Revises: 003_add_available_days
Create Date: 2026-03-25

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004_add_email_reminder_sent"
down_revision: Union[str, None] = "003_add_available_days"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "appointments",
        sa.Column(
            "email_reminder_sent",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("appointments", "email_reminder_sent")

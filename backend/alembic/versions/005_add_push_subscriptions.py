"""add push_subscriptions table and push_reminder_sent column

Revision ID: 005_add_push_subscriptions
Revises: 004_add_email_reminder_sent
Create Date: 2026-05-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_add_push_subscriptions"
down_revision: Union[str, None] = "004_add_email_reminder_sent"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("endpoint", sa.Text(), nullable=False, unique=True),
        sa.Column("p256dh_key", sa.Text(), nullable=False),
        sa.Column("auth_key", sa.Text(), nullable=False),
        sa.Column("client_phone", sa.String(50), nullable=False, index=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.add_column(
        "appointments",
        sa.Column(
            "push_reminder_sent",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("appointments", "push_reminder_sent")
    op.drop_table("push_subscriptions")

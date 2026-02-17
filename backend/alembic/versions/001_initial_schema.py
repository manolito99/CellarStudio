"""initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-02-17

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    # Clients
    op.create_table(
        "clients",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    # Services
    op.create_table(
        "services",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("sort_order", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    # Barbers
    op.create_table(
        "barbers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("sort_order", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    # Barber-Services association
    op.create_table(
        "barber_services",
        sa.Column(
            "barber_id",
            sa.String(36),
            sa.ForeignKey("barbers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "service_id",
            sa.String(36),
            sa.ForeignKey("services.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # Schedules
    op.create_table(
        "schedules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "barber_id",
            sa.String(36),
            sa.ForeignKey("barbers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
    )

    # Blocked Slots
    op.create_table(
        "blocked_slots",
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
        sa.Column("reason", sa.Text(), nullable=True),
    )

    # Appointments
    op.create_table(
        "appointments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "client_id",
            sa.String(36),
            sa.ForeignKey("clients.id"),
            nullable=False,
        ),
        sa.Column(
            "barber_id",
            sa.String(36),
            sa.ForeignKey("barbers.id"),
            nullable=False,
        ),
        sa.Column(
            "service_id",
            sa.String(36),
            sa.ForeignKey("services.id"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("appointments")
    op.drop_table("blocked_slots")
    op.drop_table("schedules")
    op.drop_table("barber_services")
    op.drop_table("barbers")
    op.drop_table("services")
    op.drop_table("clients")
    op.drop_table("users")

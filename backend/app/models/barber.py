import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

barber_services = Table(
    "barber_services",
    Base.metadata,
    Column("barber_id", String(36), ForeignKey("barbers.id", ondelete="CASCADE"), primary_key=True),
    Column("service_id", String(36), ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
)


class Barber(Base):
    __tablename__ = "barbers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", foreign_keys=[user_id])
    services = relationship("Service", secondary=barber_services, back_populates="barbers")
    schedules = relationship("Schedule", back_populates="barber", cascade="all, delete-orphan")
    blocked_slots = relationship("BlockedSlot", back_populates="barber", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="barber")

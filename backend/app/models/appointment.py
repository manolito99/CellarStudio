import uuid
from datetime import date as dt_date, time as dt_time, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clients.id"), nullable=False
    )
    barber_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("barbers.id"), nullable=False
    )
    service_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("services.id"), nullable=False
    )
    date: Mapped[dt_date] = mapped_column(Date, nullable=False)
    start_time: Mapped[dt_time] = mapped_column(Time, nullable=False)
    end_time: Mapped[dt_time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reminder_sent: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    email_reminder_sent: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    push_reminder_sent: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    client = relationship("Client", back_populates="appointments")
    barber = relationship("Barber", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")

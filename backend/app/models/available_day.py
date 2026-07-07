import uuid

from sqlalchemy import Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AvailableDay(Base):
    __tablename__ = "available_days"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    barber_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("barbers.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[str] = mapped_column(Date, nullable=False)
    start_time: Mapped[str] = mapped_column(Time, nullable=False)
    end_time: Mapped[str] = mapped_column(Time, nullable=False)
    # Minutes between consecutive bookable start times for this specific day.
    slot_interval_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=60, server_default="60"
    )

    barber = relationship("Barber", back_populates="available_days")

import uuid

from sqlalchemy import Date, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BlockedSlot(Base):
    __tablename__ = "blocked_slots"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    barber_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("barbers.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[str] = mapped_column(Date, nullable=False)
    start_time: Mapped[str] = mapped_column(Time, nullable=False)
    end_time: Mapped[str] = mapped_column(Time, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    barber = relationship("Barber", back_populates="blocked_slots")

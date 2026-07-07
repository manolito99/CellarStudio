import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field

# Bounds for the bookable-slot interval. The lower bound is the critical guard:
# a 0/negative interval would make the slot generator loop forever (public DoS).
MIN_SLOT_INTERVAL = 15
MAX_SLOT_INTERVAL = 120


class ScheduleEntry(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: dt.time
    end_time: dt.time
    slot_interval_minutes: int = Field(
        60, ge=MIN_SLOT_INTERVAL, le=MAX_SLOT_INTERVAL
    )


class ScheduleUpdate(BaseModel):
    schedules: list[ScheduleEntry]


class ScheduleResponse(BaseModel):
    id: str
    barber_id: str
    day_of_week: int
    start_time: dt.time
    end_time: dt.time
    slot_interval_minutes: int = 60

    model_config = {"from_attributes": True}


class BlockedSlotCreate(BaseModel):
    barber_id: str
    date: dt.date
    start_time: dt.time
    end_time: dt.time
    reason: Optional[str] = None


class BlockedSlotResponse(BaseModel):
    id: str
    barber_id: str
    date: dt.date
    start_time: dt.time
    end_time: dt.time
    reason: Optional[str] = None

    model_config = {"from_attributes": True}


class TimeSlot(BaseModel):
    start_time: dt.time
    end_time: dt.time
    available: bool = True


class AvailabilityResponse(BaseModel):
    barber_id: str
    date: dt.date
    slots: list[TimeSlot]


class AvailableDayCreate(BaseModel):
    barber_id: str
    date: dt.date
    start_time: dt.time
    end_time: dt.time
    slot_interval_minutes: int = Field(
        60, ge=MIN_SLOT_INTERVAL, le=MAX_SLOT_INTERVAL
    )


class AvailableDayResponse(BaseModel):
    id: str
    barber_id: str
    date: dt.date
    start_time: dt.time
    end_time: dt.time
    slot_interval_minutes: int = 60

    model_config = {"from_attributes": True}

import datetime as dt
from typing import Optional

from pydantic import BaseModel


class ScheduleEntry(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: dt.time
    end_time: dt.time


class ScheduleUpdate(BaseModel):
    schedules: list[ScheduleEntry]


class ScheduleResponse(BaseModel):
    id: str
    barber_id: str
    day_of_week: int
    start_time: dt.time
    end_time: dt.time

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

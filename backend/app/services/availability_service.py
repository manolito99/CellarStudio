"""Service to calculate available time slots for a barber on a given date."""

from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.blocked_slot import BlockedSlot
from app.models.schedule import Schedule
from app.models.service import Service
from app.schemas.schedule import AvailabilityResponse, TimeSlot


def get_availability(
    db: Session,
    barber_id: str,
    target_date: date,
    service_id: str,
) -> AvailabilityResponse:
    # Get service duration
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        return AvailabilityResponse(barber_id=barber_id, date=target_date, slots=[])

    duration = timedelta(minutes=service.duration_minutes)

    # Get schedule for this day of week (Monday=0, Sunday=6)
    day_of_week = target_date.weekday()
    schedule = (
        db.query(Schedule)
        .filter(Schedule.barber_id == barber_id, Schedule.day_of_week == day_of_week)
        .first()
    )

    if not schedule:
        return AvailabilityResponse(barber_id=barber_id, date=target_date, slots=[])

    # Generate all possible slots
    slots: list[TimeSlot] = []
    current = datetime.combine(target_date, schedule.start_time)
    end_of_day = datetime.combine(target_date, schedule.end_time)

    while current + duration <= end_of_day:
        slot_start = current.time()
        slot_end = (current + duration).time()
        slots.append(TimeSlot(start_time=slot_start, end_time=slot_end, available=True))
        current += timedelta(minutes=15)  # Step by 15 minutes

    # Get existing appointments for this barber on this date (not cancelled)
    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.barber_id == barber_id,
            Appointment.date == target_date,
            Appointment.status.notin_(["cancelled"]),
        )
        .all()
    )

    # Get blocked slots for this barber on this date
    blocked = (
        db.query(BlockedSlot)
        .filter(
            BlockedSlot.barber_id == barber_id,
            BlockedSlot.date == target_date,
        )
        .all()
    )

    # Mark overlapping slots as unavailable
    now = datetime.now(timezone.utc)
    today = now.date()

    for slot in slots:
        slot_start_dt = datetime.combine(target_date, slot.start_time)
        slot_end_dt = datetime.combine(target_date, slot.end_time)

        # Past slots
        if target_date == today and slot_start_dt.replace(tzinfo=timezone.utc) < now:
            slot.available = False
            continue

        # Check against appointments
        for appt in appointments:
            appt_start = datetime.combine(target_date, appt.start_time)
            appt_end = datetime.combine(target_date, appt.end_time)
            if slot_start_dt < appt_end and slot_end_dt > appt_start:
                slot.available = False
                break

        if not slot.available:
            continue

        # Check against blocked slots
        for block in blocked:
            block_start = datetime.combine(target_date, block.start_time)
            block_end = datetime.combine(target_date, block.end_time)
            if slot_start_dt < block_end and slot_end_dt > block_start:
                slot.available = False
                break

    return AvailabilityResponse(barber_id=barber_id, date=target_date, slots=slots)

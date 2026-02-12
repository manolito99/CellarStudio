from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.barber import Barber
from app.models.blocked_slot import BlockedSlot
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import (
    BlockedSlotCreate,
    BlockedSlotResponse,
    ScheduleResponse,
    ScheduleUpdate,
)

router = APIRouter(prefix="/api/admin", tags=["Admin - Schedules"])


@router.get("/barbers/{barber_id}/schedule", response_model=list[ScheduleResponse])
def get_barber_schedule(
    barber_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")

    return (
        db.query(Schedule)
        .filter(Schedule.barber_id == barber_id)
        .order_by(Schedule.day_of_week)
        .all()
    )


@router.put("/barbers/{barber_id}/schedule", response_model=list[ScheduleResponse])
def update_barber_schedule(
    barber_id: str,
    data: ScheduleUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")

    # Delete existing schedules
    db.query(Schedule).filter(Schedule.barber_id == barber_id).delete()

    # Create new schedules
    new_schedules = []
    for entry in data.schedules:
        schedule = Schedule(
            barber_id=barber_id,
            day_of_week=entry.day_of_week,
            start_time=entry.start_time,
            end_time=entry.end_time,
        )
        db.add(schedule)
        new_schedules.append(schedule)

    db.commit()
    for s in new_schedules:
        db.refresh(s)
    return new_schedules


@router.get("/blocked-slots", response_model=list[BlockedSlotResponse])
def list_blocked_slots(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    barber_id: str | None = None,
):
    query = db.query(BlockedSlot)
    if barber_id:
        query = query.filter(BlockedSlot.barber_id == barber_id)
    return query.order_by(BlockedSlot.date.desc()).all()


@router.post("/blocked-slots", response_model=BlockedSlotResponse, status_code=status.HTTP_201_CREATED)
def create_blocked_slot(
    data: BlockedSlotCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    slot = BlockedSlot(**data.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.delete("/blocked-slots/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blocked_slot(
    slot_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    slot = db.query(BlockedSlot).filter(BlockedSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Bloqueo no encontrado")
    db.delete(slot)
    db.commit()

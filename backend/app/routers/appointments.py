from datetime import date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_current_user, get_db
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.service import Service
from app.models.user import User
from app.schemas.appointment import (
    AppointmentAdminCreate,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentUpdate,
    StatusUpdate,
)

router = APIRouter(prefix="/api/admin/appointments", tags=["Admin - Appointments"])

VALID_STATUSES = {"pending", "confirmed", "completed", "cancelled", "noshow"}


def _get_appointment_query(db: Session):
    return db.query(Appointment).options(
        joinedload(Appointment.client),
        joinedload(Appointment.barber),
        joinedload(Appointment.service),
    )


@router.get("/", response_model=list[AppointmentListResponse])
def list_appointments(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    barber_id: str | None = None,
    service_id: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    date_from: date | None = None,
    date_to: date | None = None,
):
    query = _get_appointment_query(db)

    if barber_id:
        query = query.filter(Appointment.barber_id == barber_id)
    if service_id:
        query = query.filter(Appointment.service_id == service_id)
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    if date_from:
        query = query.filter(Appointment.date >= date_from)
    if date_to:
        query = query.filter(Appointment.date <= date_to)

    return query.order_by(Appointment.date.desc(), Appointment.start_time).all()


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    data: AppointmentAdminCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    service = db.query(Service).filter(Service.id == data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    client = db.query(Client).filter(Client.id == data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    end_dt = datetime.combine(data.date, data.start_time) + timedelta(minutes=service.duration_minutes)

    appointment = Appointment(
        client_id=data.client_id,
        barber_id=data.barber_id,
        service_id=data.service_id,
        date=data.date,
        start_time=data.start_time,
        end_time=end_dt.time(),
        status="confirmed",
        notes=data.notes,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    appointment = _get_appointment_query(db).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: str,
    data: AppointmentUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    update_data = data.model_dump(exclude_unset=True)

    if "start_time" in update_data and "service_id" not in update_data:
        service = db.query(Service).filter(Service.id == appointment.service_id).first()
        end_dt = datetime.combine(
            update_data.get("date", appointment.date),
            update_data["start_time"],
        ) + timedelta(minutes=service.duration_minutes)
        update_data["end_time"] = end_dt.time()

    if "status" in update_data and update_data["status"] not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Válidos: {VALID_STATUSES}")

    for key, value in update_data.items():
        setattr(appointment, key, value)

    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    db.delete(appointment)
    db.commit()


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_status(
    appointment_id: str,
    data: StatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Válidos: {VALID_STATUSES}")

    appointment = _get_appointment_query(db).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    appointment.status = data.status
    db.commit()
    db.refresh(appointment)
    return appointment

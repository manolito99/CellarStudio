from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db
from app.models.barber import Barber
from app.models.service import Service
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.schemas.barber import BarberResponse
from app.schemas.schedule import AvailabilityResponse
from app.schemas.service import ServiceResponse
from app.services.appointment_service import create_public_appointment
from app.services.availability_service import get_availability
from app.services.email_service import send_appointment_confirmation

router = APIRouter(prefix="/api/public", tags=["Public"])


@router.get("/services", response_model=list[ServiceResponse])
def list_services(db: Annotated[Session, Depends(get_db)]):
    return (
        db.query(Service)
        .filter(Service.is_active.is_(True))
        .order_by(Service.sort_order)
        .all()
    )


@router.get("/barbers", response_model=list[BarberResponse])
def list_barbers(db: Annotated[Session, Depends(get_db)]):
    return (
        db.query(Barber)
        .options(joinedload(Barber.services))
        .filter(Barber.is_active.is_(True))
        .order_by(Barber.sort_order)
        .all()
    )


@router.get("/availability", response_model=AvailabilityResponse)
def check_availability(
    barber_id: Annotated[str, Query()],
    date: Annotated[date, Query()],
    service_id: Annotated[str, Query()],
    db: Annotated[Session, Depends(get_db)],
):
    return get_availability(db, barber_id, date, service_id)


@router.post("/appointments", response_model=AppointmentResponse)
def create_appointment(
    data: AppointmentCreate,
    db: Annotated[Session, Depends(get_db)],
):
    appointment = create_public_appointment(db, data)
    # Refresh with relationships
    db.refresh(appointment)

    # Send confirmation email
    send_appointment_confirmation(
        client_name=appointment.client.name,
        client_email=appointment.client.email or "",
        barber_name=appointment.barber.name,
        service_name=appointment.service.name,
        date_str=appointment.date.strftime("%d/%m/%Y"),
        time_str=appointment.start_time.strftime("%H:%M"),
    )

    return appointment

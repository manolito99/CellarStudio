"""Service for appointment creation and management."""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.barber import Barber
from app.models.client import Client
from app.models.service import Service
from app.schemas.appointment import AppointmentCreate
from app.services.availability_service import get_availability


def create_public_appointment(db: Session, data: AppointmentCreate) -> Appointment:
    # Validate barber exists and is active
    barber = db.query(Barber).filter(Barber.id == data.barber_id, Barber.is_active.is_(True)).first()
    if not barber:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Barbero no encontrado")

    # Validate service exists and is active
    service = db.query(Service).filter(Service.id == data.service_id, Service.is_active.is_(True)).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")

    # Check availability
    availability = get_availability(db, data.barber_id, data.date, data.service_id)
    slot_available = any(
        s.start_time == data.start_time and s.available for s in availability.slots
    )
    if not slot_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El horario seleccionado no está disponible",
        )

    # Find or create client
    client = db.query(Client).filter(Client.phone == data.client_phone).first()
    if not client:
        client = Client(
            name=data.client_name,
            phone=data.client_phone,
            email=data.client_email,
        )
        db.add(client)
        db.flush()
    else:
        # Update name/email if provided
        client.name = data.client_name
        if data.client_email:
            client.email = data.client_email

    # Calculate end time
    end_dt = datetime.combine(data.date, data.start_time) + timedelta(minutes=service.duration_minutes)

    appointment = Appointment(
        client_id=client.id,
        barber_id=data.barber_id,
        service_id=data.service_id,
        date=data.date,
        start_time=data.start_time,
        end_time=end_dt.time(),
        status="pending",
        notes=data.notes,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment

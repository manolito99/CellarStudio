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
    barber = (
        db.query(Barber)
        .filter(Barber.id == data.barber_id, Barber.is_active.is_(True))
        .first()
    )
    if not barber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Barbero no encontrado"
        )

    # Validate service exists and is active
    service = (
        db.query(Service)
        .filter(Service.id == data.service_id, Service.is_active.is_(True))
        .first()
    )
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado"
        )

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
    end_dt = datetime.combine(data.date, data.start_time) + timedelta(
        minutes=service.duration_minutes
    )

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


def get_my_appointments(db: Session, phone: str, email: str) -> list[Appointment]:
    """Return future appointments for a client identified by phone + email."""
    from datetime import date
    from sqlalchemy.orm import joinedload

    client = (
        db.query(Client)
        .filter(
            Client.phone == phone,
            Client.email == email,
        )
        .first()
    )
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No encontramos ninguna cuenta con ese teléfono y correo",
        )

    today = date.today()
    appointments = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.client),
            joinedload(Appointment.barber),
            joinedload(Appointment.service),
        )
        .filter(
            Appointment.client_id == client.id,
            Appointment.date >= today,
            Appointment.status.notin_(["cancelled", "completed", "noshow"]),
        )
        .order_by(Appointment.date, Appointment.start_time)
        .all()
    )
    return appointments


def cancel_my_appointment(
    db: Session, appointment_id: str, phone: str, email: str
) -> Appointment:
    """Cancel an appointment after verifying ownership via phone + email."""
    from sqlalchemy.orm import joinedload as jl

    client = (
        db.query(Client).filter(Client.phone == phone, Client.email == email).first()
    )
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado"
        )

    appointment = (
        db.query(Appointment)
        .options(
            jl(Appointment.client), jl(Appointment.barber), jl(Appointment.service)
        )
        .filter(
            Appointment.id == appointment_id,
            Appointment.client_id == client.id,
        )
        .first()
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada"
        )
    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La cita ya está cancelada"
        )

    appointment.status = "cancelled"
    db.commit()
    db.refresh(appointment)
    return appointment


def modify_my_appointment(
    db: Session,
    appointment_id: str,
    phone: str,
    email: str,
    barber_id: str,
    service_id: str,
    new_date,
    new_start_time,
) -> Appointment:
    """Modify an appointment's date/time/barber/service after verifying ownership."""
    from sqlalchemy.orm import joinedload as jl

    client = (
        db.query(Client).filter(Client.phone == phone, Client.email == email).first()
    )
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado"
        )

    appointment = (
        db.query(Appointment)
        .options(
            jl(Appointment.client), jl(Appointment.barber), jl(Appointment.service)
        )
        .filter(
            Appointment.id == appointment_id,
            Appointment.client_id == client.id,
        )
        .first()
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada"
        )
    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar una cita cancelada",
        )

    # Validate barber and service exist
    barber = (
        db.query(Barber)
        .filter(Barber.id == barber_id, Barber.is_active.is_(True))
        .first()
    )
    if not barber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Barbero no encontrado"
        )

    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.is_active.is_(True))
        .first()
    )
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado"
        )

    # Temporarily mark current appointment as cancelled for availability check
    original_status = appointment.status
    appointment.status = "cancelled"
    db.flush()

    availability = get_availability(db, barber_id, new_date, service_id)
    slot_available = any(
        s.start_time == new_start_time and s.available for s in availability.slots
    )

    # Restore status if slot not available
    if not slot_available:
        appointment.status = original_status
        db.flush()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El horario seleccionado no está disponible",
        )

    # Calculate new end time
    end_dt = datetime.combine(new_date, new_start_time) + timedelta(
        minutes=service.duration_minutes
    )

    appointment.barber_id = barber_id
    appointment.service_id = service_id
    appointment.date = new_date
    appointment.start_time = new_start_time
    appointment.end_time = end_dt.time()
    appointment.status = original_status

    db.commit()
    db.refresh(appointment)
    return appointment

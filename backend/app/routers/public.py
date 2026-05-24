from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.dependencies import get_db
from app.models.barber import Barber
from app.models.notification import Notification
from app.models.push_subscription import PushSubscription
from app.models.service import Service
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    MyAppointmentsLookup,
    PublicAppointmentModify,
    PublicCancelRequest,
)
from app.schemas.barber import BarberResponse
from app.schemas.push import (
    NotificationResponse,
    PhoneLookup,
    PushSubscribeRequest,
    PushTestRequest,
)
from app.schemas.schedule import AvailabilityResponse
from app.schemas.service import ServiceResponse
from app.services.appointment_service import (
    cancel_my_appointment,
    create_public_appointment,
    get_my_appointments,
    modify_my_appointment,
)
from app.services.availability_service import get_availability
from app.services.email_service import (
    send_appointment_confirmation,
    send_appointment_modification,
)
from app.services.whatsapp_service import send_appointment_whatsapp

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


@router.get("/availability/dates")
def get_available_dates_range(
    barber_id: Annotated[str, Query()],
    service_id: Annotated[str, Query()],
    from_date: Annotated[date, Query(alias="from")],
    to_date: Annotated[date, Query(alias="to")],
    db: Annotated[Session, Depends(get_db)],
):
    """Return dates that have at least one available slot in the given range (max 90 days)."""
    # Cap range at 90 days to prevent abuse
    if (to_date - from_date).days > 90:
        to_date = from_date + timedelta(days=90)

    results = []
    current = from_date
    while current <= to_date:
        availability = get_availability(db, barber_id, current, service_id)
        available_slots = [s for s in availability.slots if s.available]
        if available_slots:
            results.append(
                {
                    "date": current.isoformat(),
                    "first_slot": str(available_slots[0].start_time)[:5],
                    "slots_count": len(available_slots),
                }
            )
        current += timedelta(days=1)

    return results


@router.post("/appointments", response_model=AppointmentResponse)
async def create_appointment(
    data: AppointmentCreate,
    db: Annotated[Session, Depends(get_db)],
):
    appointment = create_public_appointment(db, data)
    # Refresh with relationships
    db.refresh(appointment)

    date_str = appointment.date.strftime("%d/%m/%Y")
    time_str = appointment.start_time.strftime("%H:%M")

    # Send confirmation email with ICS attachment
    await send_appointment_confirmation(
        client_name=appointment.client.name,
        client_email=appointment.client.email or "",
        barber_name=appointment.barber.name,
        service_name=appointment.service.name,
        date_str=date_str,
        time_str=time_str,
        appointment_id=appointment.id,
        date_obj=appointment.date,
        start_time_obj=appointment.start_time,
        end_time_obj=appointment.end_time,
        duration_minutes=appointment.service.duration_minutes,
    )

    # Save notification for the client
    db.add(
        Notification(
            client_phone=appointment.client.phone or "",
            title="Reserva confirmada",
            body=(
                f"{appointment.service.name} el {date_str} a las {time_str}h "
                f"con {appointment.barber.name}"
            ),
            icon="booking",
        )
    )
    db.commit()

    # Send WhatsApp confirmation
    send_appointment_whatsapp(
        client_phone=appointment.client.phone or "",
        client_name=appointment.client.name,
        barber_name=appointment.barber.name,
        service_name=appointment.service.name,
        date_str=date_str,
        time_str=time_str,
    )

    return appointment


@router.post("/my-appointments/lookup", response_model=list[AppointmentResponse])
def lookup_my_appointments(
    data: MyAppointmentsLookup,
    db: Annotated[Session, Depends(get_db)],
):
    """Look up future appointments by phone + email."""
    return get_my_appointments(db, data.phone, data.email)


@router.patch(
    "/my-appointments/{appointment_id}/cancel", response_model=AppointmentResponse
)
def cancel_appointment_public(
    appointment_id: str,
    data: PublicCancelRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """Cancel an appointment. Ownership verified via phone + email."""
    return cancel_my_appointment(db, appointment_id, data.phone, data.email)


@router.put(
    "/my-appointments/{appointment_id}/modify", response_model=AppointmentResponse
)
async def modify_appointment_public(
    appointment_id: str,
    data: PublicAppointmentModify,
    db: Annotated[Session, Depends(get_db)],
):
    """Modify an appointment's date/time/barber/service. Ownership verified via phone + email."""
    appointment = modify_my_appointment(
        db,
        appointment_id,
        data.phone,
        data.email,
        data.barber_id,
        data.service_id,
        data.date,
        data.start_time,
    )

    # Send modification confirmation email
    if appointment.client and appointment.client.email and appointment.service:
        barber_name = appointment.barber.name if appointment.barber else ""
        await send_appointment_modification(
            client_name=appointment.client.name,
            client_email=appointment.client.email,
            barber_name=barber_name,
            service_name=appointment.service.name,
            date_str=appointment.date.strftime("%d/%m/%Y"),
            time_str=appointment.start_time.strftime("%H:%M"),
            appointment_id=appointment.id,
            date_obj=appointment.date,
            start_time_obj=appointment.start_time,
            end_time_obj=appointment.end_time,
            duration_minutes=appointment.service.duration_minutes,
        )

    return appointment


@router.get("/push/vapid-key")
def get_vapid_public_key():
    return {"public_key": settings.VAPID_PUBLIC_KEY}


@router.post("/push/subscribe")
def subscribe_push(
    data: PushSubscribeRequest,
    db: Annotated[Session, Depends(get_db)],
):
    existing = (
        db.query(PushSubscription)
        .filter(PushSubscription.endpoint == data.endpoint)
        .first()
    )
    if existing:
        existing.p256dh_key = data.p256dh_key
        existing.auth_key = data.auth_key
        existing.client_phone = data.client_phone
    else:
        db.add(
            PushSubscription(
                endpoint=data.endpoint,
                p256dh_key=data.p256dh_key,
                auth_key=data.auth_key,
                client_phone=data.client_phone,
            )
        )
    db.commit()
    return {"ok": True}


@router.post("/push/test")
def test_push(
    data: PushTestRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """Send a test push notification to verify the setup works."""
    from app.services.push_service import send_push_notification

    subscriptions = (
        db.query(PushSubscription)
        .filter(PushSubscription.client_phone == data.client_phone)
        .all()
    )
    if not subscriptions:
        return {"ok": False, "detail": "No subscriptions found"}

    sent = 0
    for sub in subscriptions:
        result = send_push_notification(
            subscription_info={
                "endpoint": sub.endpoint,
                "keys": {"p256dh": sub.p256dh_key, "auth": sub.auth_key},
            },
            title="Cellar Barber Studio",
            body="Recordatorio: Tu cita de Corte es hoy a las 16:00h con Maxi",
        )
        if result is True:
            sent += 1
        elif result is None:
            db.delete(sub)

    db.commit()
    return {"ok": sent > 0, "sent": sent}


@router.post("/notifications", response_model=list[NotificationResponse])
def list_notifications(
    data: PhoneLookup,
    db: Annotated[Session, Depends(get_db)],
):
    return (
        db.query(Notification)
        .filter(Notification.client_phone == data.phone)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )


@router.patch("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if notif:
        notif.read = True
        db.commit()
    return {"ok": True}


@router.patch("/notifications/read-all")
def mark_all_read(
    data: PhoneLookup,
    db: Annotated[Session, Depends(get_db)],
):
    db.query(Notification).filter(
        Notification.client_phone == data.phone,
        Notification.read.is_(False),
    ).update({"read": True})
    db.commit()
    return {"ok": True}


@router.get("/notifications/unread-count")
def unread_count(
    phone: Annotated[str, Query()],
    db: Annotated[Session, Depends(get_db)],
):
    count = (
        db.query(Notification)
        .filter(
            Notification.client_phone == phone,
            Notification.read.is_(False),
        )
        .count()
    )
    return {"count": count}

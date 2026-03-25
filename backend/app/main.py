import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

logger = logging.getLogger(__name__)


def send_appointment_reminders():
    """Check for upcoming appointments and send WhatsApp + email reminders."""
    import asyncio

    from app.database import SessionLocal
    from app.models.appointment import Appointment
    from app.services.whatsapp_service import send_reminder_whatsapp
    from app.services.email_service import send_appointment_reminder

    now = datetime.now(timezone.utc)

    db = SessionLocal()
    try:
        # ------------------------------------------------------------------
        # Pass 1 — WhatsApp reminder (2h before, configurable)
        # ------------------------------------------------------------------
        reminder_hours = settings.WHATSAPP_REMINDER_HOURS
        target_time = now + timedelta(hours=reminder_hours)

        whatsapp_appointments = (
            db.query(Appointment)
            .filter(
                Appointment.status.in_(["pending", "confirmed"]),
                Appointment.reminder_sent.is_(False),
                Appointment.date == target_time.date(),
            )
            .all()
        )

        for appt in whatsapp_appointments:
            appt_datetime = datetime.combine(
                appt.date, appt.start_time, tzinfo=timezone.utc
            )
            diff = abs((appt_datetime - target_time).total_seconds())
            # Window of 15 minutes (900 seconds)
            if diff <= 900:
                send_reminder_whatsapp(
                    client_phone=appt.client.phone or "",
                    client_name=appt.client.name,
                    barber_name=appt.barber.name,
                    service_name=appt.service.name,
                    date_str=appt.date.strftime("%d/%m/%Y"),
                    time_str=appt.start_time.strftime("%H:%M"),
                )
                appt.reminder_sent = True
                logger.info(f"WhatsApp reminder sent for appointment {appt.id}")

        # ------------------------------------------------------------------
        # Pass 2 — Email reminder (24h before)
        # Using a 23h lookahead so the 30-min scheduler always covers each
        # date in the window exactly once.
        # ------------------------------------------------------------------
        email_target_date = (now + timedelta(hours=23)).date()

        email_appointments = (
            db.query(Appointment)
            .filter(
                Appointment.status.in_(["pending", "confirmed"]),
                Appointment.email_reminder_sent.is_(False),
                Appointment.date == email_target_date,
            )
            .all()
        )

        for appt in email_appointments:
            if not appt.client.email:
                continue
            try:
                asyncio.run(
                    send_appointment_reminder(
                        client_name=appt.client.name,
                        client_email=appt.client.email,
                        barber_name=appt.barber.name,
                        service_name=appt.service.name,
                        date_str=appt.date.strftime("%d/%m/%Y"),
                        time_str=appt.start_time.strftime("%H:%M"),
                        appointment_id=appt.id,
                        date_obj=appt.date,
                        start_time_obj=appt.start_time,
                        end_time_obj=appt.end_time,
                        duration_minutes=appt.service.duration_minutes,
                    )
                )
                appt.email_reminder_sent = True
                logger.info(f"Email reminder sent for appointment {appt.id}")
            except Exception as e:
                logger.error(f"Email reminder failed for appointment {appt.id}: {e}")
                # Isolated failure — continue with remaining appointments

        db.commit()
    except Exception as e:
        logger.error(f"Error sending reminders: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed
    from app.database import Base, engine
    from app.models import (  # noqa: F401
        Appointment,
        Barber,
        BlockedSlot,
        Client,
        Schedule,
        Service,
        User,
    )

    Base.metadata.create_all(bind=engine)

    # Auto-seed on startup
    from app.seed import seed

    seed()

    # Start reminder scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_appointment_reminders, "interval", minutes=30)
    scheduler.start()
    logger.info("Reminder scheduler started (every 30 min)")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("Reminder scheduler stopped")


app = FastAPI(
    title="Cellar Barber Studio API",
    description="API para sistema de gestión de Cellar Barber Studio Barbería",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from app.routers.auth import router as auth_router  # noqa: E402
from app.routers.public import router as public_router  # noqa: E402
from app.routers.appointments import router as appointments_router  # noqa: E402
from app.routers.services import router as services_router  # noqa: E402
from app.routers.barbers import router as barbers_router  # noqa: E402
from app.routers.clients import router as clients_router  # noqa: E402
from app.routers.schedules import router as schedules_router  # noqa: E402
from app.routers.dashboard import router as dashboard_router  # noqa: E402

app.include_router(auth_router)
app.include_router(public_router)
app.include_router(appointments_router)
app.include_router(services_router)
app.include_router(barbers_router)
app.include_router(clients_router)
app.include_router(schedules_router)
app.include_router(dashboard_router)


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Cellar Barber Studio API"}

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

logger = logging.getLogger(__name__)


def send_appointment_reminders():
    """Check for upcoming appointments and send WhatsApp reminders."""
    from app.database import SessionLocal
    from app.models.appointment import Appointment
    from app.services.whatsapp_service import send_reminder_whatsapp

    now = datetime.now(timezone.utc)
    reminder_hours = settings.WHATSAPP_REMINDER_HOURS
    target_time = now + timedelta(hours=reminder_hours)

    db = SessionLocal()
    try:
        appointments = (
            db.query(Appointment)
            .filter(
                Appointment.status.in_(["pending", "confirmed"]),
                Appointment.reminder_sent.is_(False),
                Appointment.date == target_time.date(),
            )
            .all()
        )

        for appt in appointments:
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
                logger.info(f"Reminder sent for appointment {appt.id}")

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

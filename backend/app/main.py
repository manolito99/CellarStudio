from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: run Alembic migrations and seed
    import logging

    from alembic.config import Config
    from alembic import command
    from sqlalchemy import inspect, text

    from app.database import engine

    logger = logging.getLogger("cellarstudio.startup")

    # Clear connection pool inherited from parent process (uvicorn --workers fork)
    engine.dispose()

    try:
        with engine.connect() as conn:
            # Advisory lock prevents race conditions with multiple uvicorn workers
            conn.execute(text("SELECT pg_advisory_lock(1)"))
            try:
                alembic_cfg = Config("alembic.ini")
                inspector = inspect(conn)
                existing_tables = inspector.get_table_names()
                if existing_tables and "alembic_version" not in existing_tables:
                    command.stamp(alembic_cfg, "head")
                else:
                    command.upgrade(alembic_cfg, "head")
            finally:
                conn.execute(text("SELECT pg_advisory_unlock(1)"))
                conn.commit()
    except Exception as e:
        logger.warning(f"Alembic migration failed: {e}, falling back to create_all")
        from app.database import Base
        from app.models import (  # noqa: F401
            Appointment, Barber, BlockedSlot, Client, Schedule, Service, User,
        )
        Base.metadata.create_all(bind=engine)

    # Auto-seed on startup
    from app.seed import seed

    seed()

    yield
    # Shutdown


app = FastAPI(
    title="Cellar Studio API",
    description="API para sistema de gestión de Cellar Studio Barbería",
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
    return {"status": "ok", "service": "Cellar Studio API"}

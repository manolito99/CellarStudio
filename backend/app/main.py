from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: run Alembic migrations and seed
    from alembic.config import Config
    from alembic import command
    from sqlalchemy import inspect

    from app.database import engine

    alembic_cfg = Config("alembic.ini")

    # Auto-detect pre-existing DB without Alembic tracking
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    if existing_tables and "alembic_version" not in existing_tables:
        # DB has tables but no alembic_version — stamp as current
        command.stamp(alembic_cfg, "head")
    else:
        # Fresh DB or already tracked — run pending migrations
        command.upgrade(alembic_cfg, "head")

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

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Start all services (dev)
docker-compose up --build

# Start all services (prod)
docker-compose -f docker-compose.prod.yml up --build

# Backend only
docker-compose up backend

# Frontend only
docker-compose up frontend

# Run Alembic migration
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Capacitor mobile build
cd frontend && npm run mobile:build
```

No test framework is configured yet. There are no test files or test runners.

## Architecture

Monorepo with three services orchestrated via Docker Compose:

- **backend/** — FastAPI (Python 3.12) on port 8000
- **frontend/** — Vue 3 + Ionic 8 + Capacitor 6 on port 5173
- **nginx/** — Reverse proxy on port 8888 (dev) or 80 (prod), routes `/api` → backend, `/` → frontend

### Backend Structure (router → service → model)

- `app/main.py` — Lifespan creates tables + seeds DB on startup, registers all routers, CORS
- `app/models/` — SQLAlchemy 2.0 `mapped_column` style. Key models: User, Client, Barber, Service, Appointment, Schedule, BlockedSlot
- `app/routers/` — Auth (`/api/auth`), Public (`/api/public`), Admin CRUD (`/api/admin/*`), Dashboard
- `app/services/` — Business logic: auth_service (JWT), appointment_service (validation + find-or-create client by phone), availability_service (15-min interval slot calculation), email_service (async SMTP)
- `app/schemas/` — Pydantic v2 request/response models
- `app/dependencies.py` — `get_db` session and `get_current_user` JWT dependency
- `app/config.py` — Pydantic Settings loading from env vars
- `app/seed.py` — Seeds admin user, sample barbers/services/clients/appointments

### Frontend Structure

- `src/services/api.ts` — Axios instance with JWT interceptor (auto-refresh on 401)
- `src/services/{authApi,publicApi,adminApi}.ts` — API clients grouped by scope
- `src/stores/` — Pinia stores (auth, appointments, services)
- `src/composables/` — `useBooking` (5-step booking flow), `useAuth`, `usePlatform`
- `src/router/index.ts` — Public routes (`/`, `/booking`, `/confirmation`), admin routes with `meta.requiresAuth` guard
- `src/views/public/` — Landing, booking wizard, confirmation
- `src/views/admin/` — Dashboard, CRUD pages for appointments/services/barbers/clients/schedule/settings

### API Route Conventions

- **Public** (no auth): `/api/public/*` — services, barbers, availability, appointment creation
- **Auth**: `/api/auth/*` — login, refresh, me
- **Admin** (JWT required): `/api/admin/*` — full CRUD + dashboard stats
- **Health**: `/api/health`

## Key Technical Details

- **Auth**: JWT HS256 — access token (15 min) + refresh token (7 days), stored in localStorage
- **DB**: PostgreSQL 16, tables auto-created via `Base.metadata.create_all` (no migrations in versions/ yet)
- **Seed admin**: `admin@cellarstudio.com` / `admin123`
- **Availability algorithm**: 15-minute intervals, filters past times, booked appointments, and blocked slots
- **Brand colors**: `#000000` (primary), `#ffffff` (background) — Apple-inspired B&W palette defined in `tailwind.config.js`
- **Capacitor appId**: `com.cellarstudio.app`, webDir: `dist`
- **Schedule**: `day_of_week` uses 0=Monday through 6=Sunday

## Environment Variables

See `.env.example` for all variables. Key ones: `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET`, `SMTP_*` for email, `CORS_ORIGINS`.

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

# Run Alembic migration (apply all pending)
docker-compose exec backend alembic upgrade head

# Create new migration (autogenerate from model changes)
docker-compose exec backend alembic revision --autogenerate -m "description"

# Check current migration version
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history

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

- `app/main.py` — Lifespan runs `create_all` + seed on startup, starts WhatsApp reminder scheduler (every 30 min), registers all routers, CORS
- `app/models/` — SQLAlchemy 2.0 `mapped_column` style. Models: User, Client, Barber, Service, Appointment, Schedule, BlockedSlot, AvailableDay
- `app/routers/` — Auth (`/api/auth`), Public (`/api/public`), Admin CRUD (`/api/admin/*` via appointments, services, barbers, clients, schedules, dashboard routers)
- `app/services/` — Business logic: auth_service (JWT), appointment_service (validation + find-or-create client by phone), availability_service (15-min interval slot calculation), email_service (async SMTP), whatsapp_service (Twilio reminders)
- `app/schemas/` — Pydantic v2 request/response models
- `app/dependencies.py` — `get_db` session and `get_current_user` JWT dependency
- `app/config.py` — Pydantic Settings loading from env vars
- `app/seed.py` — Seeds admin user + barber Maxi + 3 services (Color, Haircut, Haircut & Beard) + sample clients/appointments. Only runs if DB is empty.

### Alembic Migrations

Fully implemented. 3 migrations applied in production (currently at `head`):

| Version | Description |
|---|---|
| `001_initial_schema` | Initial tables |
| `002_add_reminder_sent` | Add `reminder_sent` column to appointments |
| `003_add_available_days` | Add `available_days` table |

Schema changes must be done via Alembic migrations, **not** by modifying models alone.

### Frontend Structure

- `src/services/api.ts` — Axios instance with JWT interceptor (auto-refresh on 401)
- `src/services/{authApi,publicApi,adminApi}.ts` — API clients grouped by scope
- `src/stores/` — Pinia stores (auth, appointments, services)
- `src/composables/` — `useBooking` (5-step booking flow), `useAuth`, `usePlatform`
- `src/router/index.ts` — Public routes (`/`, `/booking`, `/confirmation`), admin routes with `meta.requiresAuth` guard
- `src/views/public/` — Landing, booking wizard, confirmation
- `src/views/admin/` — Dashboard, CRUD pages for appointments/services/barbers/clients/schedule/settings
- `src/components/public/ServicesGrid.vue` — Fetches services from API, `formatDuration()` handles display: 0 min → "Consultar duración", multiples of 60 → "Xh", otherwise "X min"

### API Route Conventions

- **Public** (no auth): `/api/public/*` — services, barbers, availability, appointment creation
- **Auth**: `/api/auth/*` — login, refresh, me
- **Admin** (JWT required): `/api/admin/*` — full CRUD + dashboard stats
- **Health**: `/api/health`

## Key Technical Details

- **Auth**: JWT HS256 — access token (15 min) + refresh token (7 days), stored in localStorage
- **DB**: PostgreSQL 16. Tables auto-created via `Base.metadata.create_all` on startup; schema changes managed via Alembic migrations (`alembic/versions/`)
- **Seed admin**: `admin@cellarstudio.com` / `admin123`
- **Seed services** (production): Color (0 min → Consultar duración), Haircut (60 min), Haircut & Beard (60 min)
- **WhatsApp reminders**: APScheduler runs every 30 min, sends Twilio WhatsApp reminder to clients with appointments in the next `WHATSAPP_REMINDER_HOURS` hours (only once per appointment via `reminder_sent` flag)
- **Availability algorithm**: 15-minute intervals, filters past times, booked appointments, and blocked slots
- **Brand colors**: `#000000` (primary), `#ffffff` (background) — Apple-inspired B&W palette defined in `tailwind.config.js`
- **Capacitor appId**: `com.cellarstudio.app`, webDir: `dist`
- **Schedule**: `day_of_week` uses 0=Monday through 6=Sunday

## Production & Deployment

- **Production URL**: https://cellarbarberstudio.com
- **Server**: Oracle Cloud Free Tier VM, `143.47.45.225`, user `ubuntu`, Ubuntu 20.04 ARM64
- **Docker on server**: Docker 28.1.1 + Docker Compose v2.35.1
- **App directory on VM**: `/home/ubuntu/CellarStudio`
- **CI/CD**: GitHub Actions (`.github/workflows/deploy.yml`) — auto-deploys on push to `main` via SSH
- **SSL**: Let's Encrypt via Certbot, auto-renews via cron daily at 3 AM
- **Domain DNS**: Cloudflare, A record `@` → `143.47.45.225` (DNS only, no proxy)
- **Production compose**: `docker-compose.prod.yml` — 3 services (db, backend, nginx) + certbot on-demand
- **Frontend in prod**: Built inside nginx Docker image via multi-stage build (`nginx/Dockerfile.prod`)
- **No separate frontend service in prod** — nginx serves the compiled Vue dist as static files
- **GitHub Secrets**: `SSH_HOST`, `SSH_USER`, `SSH_KEY`
- See `INFRASTRUCTURE.md` for detailed deployment docs, architecture diagrams, and troubleshooting

### SSH Access

SSH config alias `servidor-ubuntu` is defined in `~/.ssh/config`:

```
Host servidor-ubuntu
    HostName 143.47.45.225
    User ubuntu
    IdentityFile C:\Users\Nolo\Documents\oracle_config\llavelongas_minecraft_server_pay\ssh-key-2024-09-16.key
```

Connect with: `ssh servidor-ubuntu`

To run commands on the backend container in production:
```bash
ssh servidor-ubuntu "docker exec cellarstudio-backend-1 <command>"
# e.g. alembic upgrade head
ssh servidor-ubuntu "docker exec cellarstudio-backend-1 alembic upgrade head"
```

## Environment Variables

See `.env.example` for all variables. Key ones: `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET`, `SMTP_*` for email, `CORS_ORIGINS`, `WHATSAPP_REMINDER_HOURS`, `TWILIO_*` for WhatsApp.

# Cellar Studio

Plataforma de reservas online para barbería. Incluye landing page pública, sistema de booking paso a paso, panel de administración completo y soporte móvil con Capacitor.

## Tech Stack

**Backend:** FastAPI, SQLAlchemy 2.0, PostgreSQL 16, Alembic, JWT Auth

**Frontend:** Vue 3, Ionic 8, TailwindCSS 3, Pinia, Axios, Capacitor 6

**Infra:** Docker Compose, Nginx reverse proxy

## Arquitectura

```
├── backend/          # API REST (FastAPI) - puerto 8000
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── routers/      # Endpoints (auth, public, admin)
│   │   ├── schemas/      # Pydantic v2 request/response
│   │   ├── services/     # Business logic
│   │   └── utils/        # Helpers, security
│   └── alembic/          # DB migrations
├── frontend/         # SPA (Vue 3 + Ionic) - puerto 5173
│   └── src/
│       ├── views/        # Pages (public + admin)
│       ├── components/   # UI components
│       ├── composables/  # useBooking, useAuth, usePlatform
│       ├── stores/       # Pinia state management
│       └── services/     # API clients (axios)
├── nginx/            # Reverse proxy - puerto 8888 (dev) / 80 (prod)
├── docker-compose.yml
└── docker-compose.prod.yml
```

## Quick Start

### 1. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores (DB, JWT secrets, SMTP)
```

### 2. Levantar con Docker

```bash
# Desarrollo (con hot-reload)
docker-compose up --build

# Producción
docker-compose -f docker-compose.prod.yml up --build
```

### 3. Acceder

| Servicio        | URL                            |
|-----------------|--------------------------------|
| App (via Nginx) | http://localhost:8888          |
| Frontend direct | http://localhost:5173          |
| API             | http://localhost:8000/api      |
| API Docs        | http://localhost:8000/docs     |

### 4. Login admin

```
Email:    admin@cellarstudio.com
Password: admin123
```

## API Routes

| Scope   | Prefix         | Auth     | Descripción                          |
|---------|----------------|----------|--------------------------------------|
| Public  | `/api/public`  | No       | Servicios, barberos, disponibilidad, crear cita |
| Auth    | `/api/auth`    | No/JWT   | Login, refresh token, perfil         |
| Admin   | `/api/admin`   | JWT      | CRUD completo + dashboard stats      |
| Health  | `/api/health`  | No       | Healthcheck                          |

## Funcionalidades

**Público:**
- Landing page con secciones: hero, servicios, equipo, galería, ubicación
- Booking wizard de 5 pasos (servicio → barbero → fecha/hora → datos → confirmación)
- Cálculo de disponibilidad en intervalos de 15 minutos
- Exportación de cita a calendario (.ics)

**Admin:**
- Dashboard con estadísticas del día/semana/mes
- CRUD de citas, servicios, barberos, clientes
- Gestión de horarios por día de la semana
- Bloqueo de franjas horarias
- Configuración general

## Mobile

```bash
cd frontend
npm run mobile:build    # Build + Capacitor sync
npx cap open android    # Abrir en Android Studio
npx cap open ios        # Abrir en Xcode
```

**App ID:** `com.cellarstudio.app`

## Variables de Entorno

| Variable                         | Descripción                    |
|----------------------------------|--------------------------------|
| `POSTGRES_USER`                  | Usuario PostgreSQL             |
| `POSTGRES_PASSWORD`              | Password PostgreSQL            |
| `POSTGRES_DB`                    | Nombre de la base de datos     |
| `DATABASE_URL`                   | Connection string completo     |
| `SECRET_KEY`                     | Secret key de la app           |
| `JWT_SECRET`                     | Secret para firmar JWT tokens  |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`| Expiración access token (min)  |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS`  | Expiración refresh token (días)|
| `SMTP_HOST`                      | Servidor SMTP                  |
| `SMTP_PORT`                      | Puerto SMTP                    |
| `SMTP_USER`                      | Usuario SMTP                   |
| `SMTP_PASSWORD`                  | Password SMTP                  |
| `SMTP_FROM_NAME`                 | Nombre remitente emails        |
| `CORS_ORIGINS`                   | Orígenes permitidos (CORS)     |

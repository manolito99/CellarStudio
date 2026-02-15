# Infrastructure & Deployment Documentation

This document describes the complete infrastructure, deployment pipeline, and server configuration for Cellar Studio. It is intended as a reference for future development sessions, DevOps tasks, and onboarding.

---

## Table of Contents

1. [Overview](#overview)
2. [Environments](#environments)
3. [Server (Oracle Cloud)](#server-oracle-cloud)
4. [Docker Architecture](#docker-architecture)
5. [Nginx Configuration](#nginx-configuration)
6. [SSL / HTTPS (Let's Encrypt)](#ssl--https-lets-encrypt)
7. [CI/CD Pipeline (GitHub Actions)](#cicd-pipeline-github-actions)
8. [Environment Variables](#environment-variables)
9. [DNS & Domain](#dns--domain)
10. [File Map](#file-map)
11. [Common Operations](#common-operations)
12. [Troubleshooting](#troubleshooting)

---

## Overview

Cellar Studio is a barbershop booking platform deployed on an **Oracle Cloud Free Tier** VM. The application consists of three Docker services (PostgreSQL, FastAPI backend, Nginx) orchestrated via Docker Compose. A GitHub Actions workflow automatically deploys on every push to `main`.

**Production URL**: https://cellarbarberstudio.com
**Server IP**: `143.47.45.225`
**Repository**: https://github.com/manolito99/CellarStudio

### Production Architecture

```
Internet
   │
   ▼
┌─────────────────────────────────────────────────────────┐
│  Oracle Cloud VM (143.47.45.225) - Ubuntu 20.04 ARM64   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Docker Compose (docker-compose.prod.yml)       │    │
│  │                                                 │    │
│  │  ┌──────────┐   ┌──────────┐   ┌───────────┐   │    │
│  │  │  nginx   │──▶│ backend  │──▶│    db      │   │    │
│  │  │ :80/:443 │   │  :8000   │   │   :5432   │   │    │
│  │  │          │   │ (uvicorn │   │(postgres  │   │    │
│  │  │ static   │   │ 4 workers│   │ 16-alpine)│   │    │
│  │  │ files +  │   │  FastAPI)│   │           │   │    │
│  │  │ SSL +    │   └──────────┘   └───────────┘   │    │
│  │  │ reverse  │                                   │    │
│  │  │ proxy    │   ┌──────────┐                    │    │
│  │  │          │   │ certbot  │ (runs on demand)   │    │
│  │  └──────────┘   └──────────┘                    │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  Volumes:                                               │
│   - postgres_data  (DB persistence)                     │
│   - certbot_www    (ACME challenges)                    │
│   - certbot_certs  (SSL certificates)                   │
└─────────────────────────────────────────────────────────┘
```

### Request Flow

```
Client Request
   │
   ├── http://cellarbarberstudio.com/*
   │      → nginx :80 → 301 redirect to https://
   │
   ├── https://cellarbarberstudio.com/api/*
   │      → nginx :443 → proxy_pass → backend:8000 (FastAPI)
   │
   ├── https://cellarbarberstudio.com/docs
   │      → nginx :443 → proxy_pass → backend:8000 (Swagger UI)
   │
   ├── https://cellarbarberstudio.com/assets/*
   │      → nginx :443 → static files (Vue dist, 1 year cache)
   │
   └── https://cellarbarberstudio.com/* (any other route)
          → nginx :443 → try_files → /index.html (SPA fallback)
```

---

## Environments

### Development (local)

- **Compose file**: `docker-compose.yml`
- **Services**: db, backend (hot reload), frontend (Vite dev server), nginx
- **Ports**: `8888` (nginx), `8000` (backend direct), `5173` (frontend direct), `5433` (postgres)
- **Nginx**: `nginx/nginx.conf` — proxies to Vite dev server with HMR WebSocket support
- **Frontend**: runs `npm run dev` inside Docker, source code mounted as volume for hot reload
- **Backend**: runs `uvicorn --reload`, `backend/app/` mounted as volume

```bash
docker-compose up --build         # Start all services
docker-compose up backend         # Backend only
docker-compose up frontend        # Frontend only
```

### Production (Oracle Cloud)

- **Compose file**: `docker-compose.prod.yml`
- **Services**: db, backend (4 workers, no volumes), nginx (includes built frontend), certbot
- **Ports**: `80` (HTTP → redirect), `443` (HTTPS)
- **Nginx**: `nginx/nginx.prod.conf` — serves static files, SSL termination, reverse proxy
- **Frontend**: built at Docker image build time (multi-stage), served as static files by nginx
- **Backend**: `uvicorn` with 4 workers, no hot reload, no volume mounts
- **No `frontend` service** — the frontend is compiled into the nginx image

```bash
docker compose -f docker-compose.prod.yml up --build -d    # Deploy
docker compose -f docker-compose.prod.yml down              # Stop all
docker compose -f docker-compose.prod.yml logs -f           # View logs
docker compose -f docker-compose.prod.yml ps                # Check status
```

### Key Differences Between Environments

| Aspect | Development | Production |
|--------|------------|------------|
| Compose file | `docker-compose.yml` | `docker-compose.prod.yml` |
| Frontend | Vite dev server (container) | Static files in nginx (multi-stage build) |
| Backend | `--reload`, volume mounts | 4 workers, no volumes |
| Nginx config | `nginx/nginx.conf` | `nginx/nginx.prod.conf` |
| Nginx Dockerfile | `nginx/Dockerfile` | `nginx/Dockerfile.prod` |
| SSL | No | Yes (Let's Encrypt) |
| Ports | 8888, 8000, 5173, 5433 | 80, 443 |

---

## Server (Oracle Cloud)

### VM Details

| Property | Value |
|----------|-------|
| Provider | Oracle Cloud Infrastructure (OCI) |
| Tier | Always Free |
| IP | `143.47.45.225` |
| OS | Ubuntu 20.04 LTS (ARM64 / aarch64) |
| User | `ubuntu` |
| SSH Key Location (local) | `C:\Users\Nolo\Documents\oracle_config\llavelongas_minecraft_server_pay\ssh-key-2024-09-16.key` |
| App Directory | `/home/ubuntu/CellarStudio` |

### SSH Access

```bash
ssh -i "C:\Users\Nolo\Documents\oracle_config\llavelongas_minecraft_server_pay\ssh-key-2024-09-16.key" ubuntu@143.47.45.225
```

### Installed Software

- Docker CE + Docker Compose plugin (installed via `scripts/setup-server.sh`)
- Git
- User `ubuntu` is in the `docker` group (no sudo needed for docker commands)

### Firewall

Oracle Cloud VMs have **two layers of firewall**:

1. **iptables (VM-level)**: Configured by `scripts/setup-server.sh` — ports 80 and 443 are open
2. **Security List (OCI-level)**: Configured manually in the Oracle Cloud web console — ports 22, 80, and 443 have ingress rules allowing `0.0.0.0/0`

Both layers must allow traffic for a port to be accessible from the internet.

### Cron Jobs

```
0 3 * * * cd /home/ubuntu/CellarStudio && docker compose -f docker-compose.prod.yml run --rm certbot renew --quiet && docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

This runs daily at 3:00 AM to auto-renew the SSL certificate. Certbot only renews when the certificate is within 30 days of expiry.

---

## Docker Architecture

### Production: `docker-compose.prod.yml`

**4 services defined, 3 run permanently:**

#### `db` (PostgreSQL 16 Alpine)

- Image: `postgres:16-alpine`
- Volume: `postgres_data` persists database across restarts
- Healthcheck: `pg_isready` every 10s (backend waits for healthy status)
- No exposed ports (only accessible within Docker network)

#### `backend` (FastAPI / Python 3.12)

- Built from: `backend/Dockerfile`
- Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`
- Depends on: `db` (healthy)
- Reads env vars from `.env`
- No volume mounts in production (code is baked into the image)
- On startup: creates database tables + seeds initial data (admin user, sample barbers/services)

#### `nginx` (Nginx 1.27 Alpine + Vue frontend)

- Built from: `nginx/Dockerfile.prod` (multi-stage build, context = project root)
- Ports: `80:80` and `443:443`
- Volumes (read-only):
  - `certbot_www:/var/www/certbot` — ACME challenge files
  - `certbot_certs:/etc/letsencrypt` — SSL certificates
- Depends on: `backend`
- Contains the compiled Vue frontend as static files in `/usr/share/nginx/html`

#### `certbot` (Let's Encrypt client)

- Image: `certbot/certbot`
- Does NOT run permanently — it's an on-demand service
- Volumes (read-write):
  - `certbot_www:/var/www/certbot` — writes ACME challenge files
  - `certbot_certs:/etc/letsencrypt` — writes/reads certificates
- Used via: `docker compose run --rm certbot renew`

### Multi-Stage Build: `nginx/Dockerfile.prod`

This is the key production Dockerfile. It builds the frontend and packages it with nginx in a single image:

```dockerfile
# Stage 1: Build Vue frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build    # vue-tsc && vite build → outputs to /app/dist

# Stage 2: Nginx with static files + config
FROM nginx:1.27-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.prod.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /app/dist /usr/share/nginx/html
EXPOSE 80
```

**Important**: The build context is the **project root** (not `nginx/`), because it needs access to `frontend/` for the multi-stage build. This is why `docker-compose.prod.yml` sets `context: .` and `dockerfile: nginx/Dockerfile.prod`.

**Note**: There is no `package-lock.json` in the frontend. The Dockerfile uses `npm install` instead of `npm ci`. If a lock file is added in the future, switch to `npm ci` for deterministic builds.

### Docker Volumes

| Volume | Purpose | Persistence |
|--------|---------|-------------|
| `postgres_data` | PostgreSQL database files | Survives container restarts and rebuilds |
| `certbot_www` | ACME challenge files for domain verification | Shared between nginx (reads) and certbot (writes) |
| `certbot_certs` | SSL certificate files from Let's Encrypt | Shared between nginx (reads) and certbot (writes) |

---

## Nginx Configuration

### Development: `nginx/nginx.conf`

- Listens on port 80
- Proxies `/api`, `/docs`, `/openapi.json` → backend:8000
- Proxies `/ws` → frontend:5173 (Vite HMR WebSocket)
- Proxies everything else → frontend:5173 (Vite dev server)
- Includes WebSocket upgrade headers for HMR

### Production: `nginx/nginx.prod.conf`

Two server blocks:

**HTTP server (port 80)**:
- Serves Let's Encrypt ACME challenges at `/.well-known/acme-challenge/`
- Redirects all other traffic to HTTPS (301)

**HTTPS server (port 443)**:
- SSL with Let's Encrypt certificates
- TLS 1.2 and 1.3 only
- Serves static frontend files from `/usr/share/nginx/html`
- Proxies `/api` → backend:8000
- Proxies `/docs`, `/openapi.json` → backend:8000
- SPA fallback: `try_files $uri $uri/ /index.html`
- Gzip compression for text, JS, CSS, JSON, SVG, fonts
- 1-year cache headers for `/assets/` (Vite hashed filenames)
- Max upload size: 10MB

---

## SSL / HTTPS (Let's Encrypt)

### How It Works

1. **Certbot** obtains certificates via the **webroot** method
2. Nginx serves ACME challenge files from the `certbot_www` volume at `/.well-known/acme-challenge/`
3. Let's Encrypt verifies domain ownership by fetching these files
4. Certificates are stored in the `certbot_certs` volume at `/etc/letsencrypt/live/cellarbarberstudio.com/`
5. Nginx reads the certificates from this volume (mounted read-only)

### Certificate Details

| Property | Value |
|----------|-------|
| Domain | `cellarbarberstudio.com` |
| Provider | Let's Encrypt |
| Type | DV (Domain Validation) |
| Certificate path | `/etc/letsencrypt/live/cellarbarberstudio.com/fullchain.pem` |
| Private key path | `/etc/letsencrypt/live/cellarbarberstudio.com/privkey.pem` |
| Validity | 90 days (auto-renewed) |
| Auto-renewal | Cron job daily at 3:00 AM |

### Initial Setup (already done)

The script `scripts/init-ssl.sh` was used for the initial certificate setup. It:

1. Creates a dummy self-signed certificate (so nginx can start)
2. Starts nginx with the dummy cert
3. Removes the dummy cert
4. Requests a real certificate from Let's Encrypt via webroot challenge
5. Reloads nginx with the real certificate

This script only needs to run once. If certificates are lost (e.g., volumes deleted), run it again.

### Manual Renewal

```bash
cd /home/ubuntu/CellarStudio
docker compose -f docker-compose.prod.yml run --rm certbot renew
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

---

## CI/CD Pipeline (GitHub Actions)

### Workflow: `.github/workflows/deploy.yml`

**Trigger**: Every push to the `main` branch.

**What it does**:
1. SSHs into the Oracle Cloud VM using `appleboy/ssh-action`
2. Runs `git pull origin main` to fetch latest code
3. Runs `docker compose -f docker-compose.prod.yml up --build -d` to rebuild and restart services
4. Runs `docker image prune -f` to clean up old images

**Flow**:
```
Developer pushes to main
   │
   ▼
GitHub Actions triggered
   │
   ▼
SSH into 143.47.45.225 as ubuntu
   │
   ▼
git pull → docker compose up --build -d → docker image prune
   │
   ▼
Services rebuilt and running with new code
```

### GitHub Secrets (configured in repo Settings → Secrets → Actions)

| Secret | Value | Description |
|--------|-------|-------------|
| `SSH_HOST` | `143.47.45.225` | Oracle Cloud VM public IP |
| `SSH_USER` | `ubuntu` | SSH username |
| `SSH_KEY` | *(RSA private key content)* | Full contents of the SSH private key file |

### Important Notes

- The deploy rebuilds the **nginx** image on every push (which includes rebuilding the frontend). This takes ~1-2 minutes on the VM.
- The **backend** image is also rebuilt, but Docker caches layers so it's fast unless `requirements.txt` or source code changed.
- The **db** is never rebuilt (it uses a pre-built postgres image).
- Database data persists in a Docker volume — it is NOT lost on redeploy.
- If the deploy fails, the previous containers keep running (Docker Compose only replaces containers that build successfully).

---

## Environment Variables

### `.env.example` (committed to repo, safe defaults for development)

```env
# PostgreSQL
POSTGRES_USER=cellarstudio
POSTGRES_PASSWORD=cellarstudio_secret
POSTGRES_DB=cellarstudio_db

# Backend
DATABASE_URL=postgresql://cellarstudio:cellarstudio_secret@db:5432/cellarstudio_db
SECRET_KEY=super-secret-key-change-in-production
JWT_SECRET=jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# SMTP (email)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_NAME=Cellar Studio

# CORS
CORS_ORIGINS=http://localhost,http://localhost:5173,http://localhost:80

# Backend URL (for frontend)
BACKEND_URL=http://localhost/api
```

### Production `.env` (on the VM at `/home/ubuntu/CellarStudio/.env`, NOT in repo)

The production `.env` has:
- Strong, unique `POSTGRES_PASSWORD`, `SECRET_KEY`, `JWT_SECRET`
- `CORS_ORIGINS=https://cellarbarberstudio.com,http://cellarbarberstudio.com,http://143.47.45.225`
- `BACKEND_URL=https://cellarbarberstudio.com/api`
- SMTP credentials for actual email sending (if configured)

**The `.env` file is in `.gitignore` and never committed.**

---

## DNS & Domain

| Property | Value |
|----------|-------|
| Domain | `cellarbarberstudio.com` |
| Registrar | Cloudflare |
| DNS Provider | Cloudflare |
| DNS Record | `A` record, `@` → `143.47.45.225`, **DNS only** (grey cloud, no Cloudflare proxy) |

**Important**: The Cloudflare proxy (orange cloud) must be **OFF** for Let's Encrypt certificate renewal to work. If you enable Cloudflare proxy, you should use Cloudflare's own SSL instead of Let's Encrypt.

---

## File Map

### Infrastructure Files (created for deployment)

```
CellarStudio/
├── .github/
│   └── workflows/
│       └── deploy.yml              # GitHub Actions: SSH deploy on push to main
├── nginx/
│   ├── Dockerfile                  # Dev nginx (just copies nginx.conf)
│   ├── Dockerfile.prod             # Prod nginx (multi-stage: builds frontend + nginx)
│   ├── nginx.conf                  # Dev nginx config (proxies to Vite dev server)
│   └── nginx.prod.conf            # Prod nginx config (static files, SSL, reverse proxy)
├── scripts/
│   ├── setup-server.sh            # One-time VM setup (Docker, firewall, clone repo)
│   └── init-ssl.sh                # One-time SSL certificate initialization
├── docker-compose.yml             # Development compose (4 services, hot reload)
├── docker-compose.prod.yml        # Production compose (3 services + certbot)
├── .env.example                   # Template env vars (committed)
└── .env                           # Actual env vars (gitignored, exists only locally and on VM)
```

### Application Files (pre-existing)

```
CellarStudio/
├── backend/
│   ├── Dockerfile                 # Python 3.12-slim, installs requirements, runs uvicorn
│   ├── requirements.txt
│   └── app/
│       ├── main.py                # FastAPI app, lifespan, CORS, router registration
│       ├── config.py              # Pydantic Settings (reads env vars)
│       ├── dependencies.py        # get_db, get_current_user (JWT)
│       ├── seed.py                # Seeds admin user + sample data
│       ├── models/                # SQLAlchemy 2.0 models
│       ├── routers/               # API route handlers
│       ├── services/              # Business logic
│       └── schemas/               # Pydantic request/response models
├── frontend/
│   ├── Dockerfile                 # Dev: node:20-alpine, npm run dev
│   ├── package.json               # Vue 3 + Ionic 8 + Capacitor 6
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── services/              # API clients (axios with JWT interceptor)
│       ├── stores/                # Pinia stores
│       ├── composables/           # useBooking, useAuth, usePlatform
│       ├── router/                # Vue Router (public + admin routes)
│       ├── views/
│       │   ├── public/            # Landing, booking wizard, confirmation
│       │   └── admin/             # Dashboard, CRUD pages
│       └── components/
└── CLAUDE.md                      # Claude Code instructions
```

---

## Common Operations

### Deploy manually (bypass GitHub Actions)

```bash
ssh -i "<key-path>" ubuntu@143.47.45.225
cd ~/CellarStudio
git pull origin main
docker compose -f docker-compose.prod.yml up --build -d
```

### View logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f db
```

### Restart a specific service

```bash
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml restart nginx
```

### Access the database

```bash
docker compose -f docker-compose.prod.yml exec db psql -U cellarstudio -d cellarstudio_db
```

### Check SSL certificate expiry

```bash
docker compose -f docker-compose.prod.yml run --rm certbot certificates
```

### Force SSL renewal

```bash
docker compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Full rebuild (nuclear option)

```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up --build -d
```

**Warning**: `docker compose down -v` would delete ALL volumes including the database. Never use `-v` unless you want to wipe the DB.

### Update environment variables

```bash
nano ~/CellarStudio/.env
# Edit variables, then restart the affected service:
docker compose -f docker-compose.prod.yml up -d backend   # Recreates backend with new env
```

---

## Troubleshooting

### 502 Bad Gateway on `/api/*`

**Cause**: Nginx can't reach the backend. Usually happens when backend was recreated but nginx still has the old container IP cached.

**Fix**:
```bash
docker compose -f docker-compose.prod.yml restart nginx
```

### SSL certificate expired

**Fix**:
```bash
docker compose -f docker-compose.prod.yml run --rm certbot renew
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

If certificates are completely lost (volumes deleted), re-run the init script:
```bash
bash scripts/init-ssl.sh
```

### Port already in use

**Cause**: Orphaned Docker containers or processes holding the port.

**Fix**:
```bash
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker compose -f docker-compose.prod.yml up -d
```

### Frontend changes not showing

**Cause**: The frontend is built into the nginx Docker image. A `git pull` alone won't update it — you need to rebuild.

**Fix**: The deploy workflow already does `--build`, so just push to `main`. For manual:
```bash
docker compose -f docker-compose.prod.yml up --build -d nginx
```

### Cannot SSH to the VM

Check:
1. Correct key file path
2. Oracle Cloud Security List has port 22 open
3. VM is running (check Oracle Cloud console)

### Database lost after redeploy

This should NOT happen — `postgres_data` is a named Docker volume that persists across container restarts and rebuilds. Only `docker compose down -v` or `docker volume rm` would delete it.

### GitHub Actions deploy failing

Check:
1. GitHub Secrets are correctly set (`SSH_HOST`, `SSH_USER`, `SSH_KEY`)
2. The VM is reachable (SSH port 22 open)
3. The repo on the VM has no uncommitted local changes that would cause a merge conflict on `git pull`
4. View the workflow logs in GitHub → Actions tab

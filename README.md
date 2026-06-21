# Social Media Publisher Platform

Automated social media publishing for Facebook and TikTok via Playwright browser automation. Supports scheduled posts, multi-account cookie management, and a browser session farm.

## Architecture

```
┌────────────┐    ┌────────────────┐    ┌──────────────────┐
│  Vue 3 SPA │───▶│  FastAPI API   │───▶│  PostgreSQL DB   │
│ :5173      │    │  :8000         │    └──────────────────┘
└────────────┘    └───────┬────────┘    ┌──────────────────┐
                          │             │  Redis Cache +   │
                          ├────────────▶│  Celery Broker   │
                          │             └──────────────────┘
                          │             ┌──────────────────┐
                          └────────────▶│  Playwright Farm │
                                        │  (up to 100      │
                                        │   browser sessions)
                                        └──────────────────┘
Monitoring: Prometheus + Grafana + Loki
```

## Quick Start

### Prerequisites

- Docker 24+
- Docker Compose v2

### 1. Configure environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

- Set `JWT_SECRET` to a random 32+ char string
- Set `COOKIE_ENCRYPTION_KEY` to a base64-encoded 32-byte key:
  ```bash
  python -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
  ```
- Set `SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD`

### 2. Start all services

```bash
docker compose up -d
```

Services:
| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Grafana | http://localhost:3000 (admin/admin) |
| Prometheus | http://localhost:9090 |

### 3. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Seed admin user

```bash
docker compose exec api python scripts/seed_admin.py
```

### 5. Log in

Open http://localhost:5173 and sign in with the credentials from `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD`.

---

## Environment Variables

| Variable                | Required | Default                 | Description                            |
| ----------------------- | -------- | ----------------------- | -------------------------------------- |
| `DATABASE_URL`          | ✅       | —                       | PostgreSQL async URL                   |
| `REDIS_URL`             | ✅       | `redis://redis:6379/0`  | Redis connection                       |
| `JWT_SECRET`            | ✅       | —                       | JWT signing key (≥32 chars)            |
| `COOKIE_ENCRYPTION_KEY` | ✅       | —                       | Base64 AES-256 key (32 bytes)          |
| `ALLOWED_ORIGINS`       | —        | `http://localhost:5173` | CORS allowed origins (comma-separated) |
| `ENVIRONMENT`           | —        | `development`           | `development` or `production`          |
| `BROWSER_MAX_SESSIONS`  | —        | `100`                   | Max concurrent Playwright sessions     |
| `BROWSER_HEADLESS`      | —        | `true`                  | Run browsers headless                  |
| `SEED_ADMIN_EMAIL`      | —        | `admin@publisher.info`  | First admin email                      |
| `SEED_ADMIN_PASSWORD`   | —        | `Admin123!`             | First admin password                   |

---

## Development

### Backend (Python 3.12 / FastAPI)

```bash
cd backend
pip install -e ".[dev]"
cp .env.example .env   # edit DATABASE_URL to point to local Postgres
pytest
mypy .
```

### Frontend (Vue 3 / Vite)

```bash
cd frontend
npm install
npm run dev
npm run test:run
```

### Running tests

```bash
# Backend unit + integration tests
docker compose exec api pytest tests/ -v --cov=. --cov-fail-under=80

# Frontend unit tests
cd frontend && npm run test:run
```

---

## Key Workflows

### Add a new social account

1. Navigate to **Accounts → Add Account**
2. Select platform (Facebook or TikTok) and enter username
3. Click **Detail** → **Import Cookie**
4. Paste the JSON cookie array from browser DevTools (Application → Cookies → Copy all as JSON)
5. Click **Check Health** to verify the session is live

### Publish a post

1. Navigate to **Posts → New Post**
2. Select account, content type, and write caption
3. Leave schedule blank for immediate publish, or pick a date/time
4. Click **Create Post**

### Monitor publishing

- **Dashboard**: KPI overview — accounts, posts today, success rate
- **Sessions**: Live browser session status (auto-refresh 5s)
- **Grafana**: Deep metrics at http://localhost:3000

---

## Security

- Cookies stored AES-256-GCM encrypted — never logged or returned in API responses
- JWT access tokens expire in 15 minutes; refresh tokens in 7 days
- Rate limiting: 5 login attempts per 15 minutes per IP
- CORS restricted to `ALLOWED_ORIGINS`
- Security headers: X-Frame-Options, CSP, X-Content-Type-Options on all responses

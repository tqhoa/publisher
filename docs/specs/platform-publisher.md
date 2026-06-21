# Feature: Social Media Publisher Platform (Facebook + TikTok)

## Objective

Build an internal automation platform that manages 100+ social media accounts simultaneously, publishes images/videos to Facebook and TikTok via browser automation (Playwright), supports scheduled posting, and tracks publish status with monitoring.

## Target Users

Internal team operators who manage multiple social media accounts programmatically. No public signup — single-tenant, role-based access for team members.

## Layer

- [x] Full-stack (FastAPI + Vue 3)

---

## Core Features

| # | Feature | Acceptance Criteria |
|---|---------|---------------------|
| 1 | JWT Auth & RBAC | Login with email/password. Roles: `admin`, `operator`. JWT access (15m) + refresh (7d). All endpoints protected. |
| 2 | Account CRUD | Create/read/update/delete social accounts. Each account has platform (`facebook`/`tiktok`), username, status, and linked cookie. |
| 3 | Cookie Import & Encryption | Import cookies as JSON string. Encrypt at rest with AES-256. Expose `/health-check` per account to validate cookie is still alive. |
| 4 | Browser Farm | Pool of Playwright browser sessions. Each session mapped to one account. Support 100+ concurrent sessions. Session crash auto-recovery. |
| 5 | Facebook Publisher | Post text, image(s), video to Facebook page/profile using authenticated Playwright session. Track publish status. |
| 6 | TikTok Publisher | Upload video with caption + hashtags to TikTok via Playwright. Track upload + publish status. |
| 7 | Post Scheduler | Schedule posts for future datetime. Worker picks up due jobs and dispatches to browser farm. |
| 8 | Retry Engine | Failed posts auto-retry up to 3x with exponential backoff. Notify on permanent failure. |
| 9 | Monitoring Dashboard | Real-time view of browser sessions, account health, queue depth, publish success rate, error logs. |
| 10 | Audit Log | All actions (login, publish, cookie import, account change) logged with user + timestamp. |

## Out of Scope (v1)

- Instagram, YouTube, Twitter
- Comment/reaction management
- Analytics/insights pulling from platforms
- Proxy rotation management (assumed handled at infra level)
- Public API for third-party clients

---

## Technical Approach

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12) |
| Browser Automation | Playwright (async, Python) |
| Database | PostgreSQL (SQLAlchemy 2.0 async + Alembic) |
| Cache / Queue | Redis Streams |
| Task Workers | Celery + Redis |
| Frontend | Vue 3 + Vite + Pinia + TanStack Query |
| Deployment | Docker Compose (self-hosted) |
| Monitoring | Prometheus + Grafana + structlog → Loki |

---

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Vue 3 Dashboard                         │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP / WebSocket
┌─────────────────────────▼───────────────────────────────────┐
│                    FastAPI Gateway                           │
│  /api/v1/auth  /api/v1/accounts  /api/v1/posts              │
│  /api/v1/schedule  /api/v1/sessions  /api/v1/health         │
└──────┬─────────────────────────────────────────────┬────────┘
       │                                             │
┌──────▼──────┐                           ┌──────────▼────────┐
│  PostgreSQL  │                           │   Redis Streams   │
│  (accounts,  │                           │   (job queue)     │
│   posts,     │                           └──────────┬────────┘
│   audit_log) │                                      │
└─────────────┘                           ┌──────────▼────────┐
                                          │  Celery Workers   │
                                          │  (scheduler,      │
                                          │   retry engine)   │
                                          └──────────┬────────┘
                                                     │
                                          ┌──────────▼────────┐
                                          │   Browser Farm    │
                                          │  (Playwright Pool)│
                                          │  100+ sessions    │
                                          └───────────────────┘
```

---

### Backend (FastAPI)

#### New Endpoints

```
# Auth
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout

# Accounts
GET    /api/v1/accounts
POST   /api/v1/accounts
GET    /api/v1/accounts/{id}
PATCH  /api/v1/accounts/{id}
DELETE /api/v1/accounts/{id}
POST   /api/v1/accounts/{id}/cookie        # import/update cookie
GET    /api/v1/accounts/{id}/health        # check cookie alive

# Posts
GET    /api/v1/posts
POST   /api/v1/posts                       # create + optionally schedule
GET    /api/v1/posts/{id}
DELETE /api/v1/posts/{id}
POST   /api/v1/posts/{id}/publish-now      # immediate publish
POST   /api/v1/posts/{id}/retry

# Browser Sessions (read-only status)
GET    /api/v1/sessions
GET    /api/v1/sessions/{account_id}

# Monitoring
GET    /api/v1/health
GET    /metrics                            # Prometheus scrape endpoint
GET    /api/v1/audit-log
```

#### Database Models

```
users
  id, email, password_hash, role, created_at, updated_at

accounts
  id, platform (facebook|tiktok), username, status (active|inactive|banned)
  cookie_encrypted, cookie_updated_at, last_health_check_at, health_status
  created_by, created_at, updated_at

posts
  id, account_id, platform, content_type (text|image|video|mixed)
  caption, hashtags (jsonb), media_urls (jsonb)
  status (pending|queued|publishing|published|failed|cancelled)
  scheduled_at, published_at, error_message, retry_count
  created_by, created_at, updated_at

browser_sessions
  id, account_id, node_id, status (idle|busy|crashed|starting)
  started_at, last_activity_at

audit_logs
  id, user_id, action, resource_type, resource_id
  metadata (jsonb), ip_address, created_at
```

#### Services & Repositories

```
domain/services/
  auth_service.py          — login, token refresh, password hash
  account_service.py       — CRUD, cookie encrypt/decrypt
  post_service.py          — create, schedule, status update
  browser_session_service.py — acquire/release session, health

domain/repositories/
  account_repository.py
  post_repository.py
  browser_session_repository.py
  audit_log_repository.py

infrastructure/
  browser/
    playwright_pool.py     — session pool, acquire/release, crash recovery
    facebook_publisher.py  — Playwright automation for Facebook
    tiktok_publisher.py    — Playwright automation for TikTok
  queue/
    celery_app.py
    tasks/
      publish_task.py      — dispatch post to browser farm
      scheduler_task.py    — Celery Beat: scan for due posts
      health_check_task.py — periodic cookie health check
  cache/
    client.py              — Redis connection
  encryption/
    cookie_cipher.py       — AES-256-GCM encrypt/decrypt
```

---

### Browser Farm Design

```
PlαywrightPool
  ├── max_sessions: 100 (configurable)
  ├── session_map: { account_id → BrowserSession }
  ├── acquire(account_id) → BrowserSession  # warm or cold start
  ├── release(account_id)
  └── crash_recovery: auto-restart on exception

BrowserSession
  ├── browser: playwright.Browser
  ├── context: playwright.BrowserContext  # isolated with cookies loaded
  ├── page: playwright.Page
  └── status: idle | busy | crashed
```

Cookie flow:
1. Cookie imported → AES-256-GCM encrypted → stored in DB
2. `acquire(account_id)` → decrypt cookie → load into browser context
3. Session used for publish → released back to pool
4. Health check: navigate to platform → check login state

---

### Frontend (Vue 3)

**Pages:**
```
views/
  auth/LoginView.vue
  dashboard/DashboardView.vue        — overview stats
  accounts/
    AccountListView.vue
    AccountDetailView.vue
  posts/
    PostListView.vue
    PostCreateView.vue
    PostDetailView.vue
  sessions/SessionsView.vue          — browser farm live status
  monitoring/MonitoringView.vue      — Grafana embed or native charts
  audit/AuditLogView.vue
```

**State management:**
- `useAuthStore` — token, user, login/logout
- `useAccountStore` — account list, health status
- TanStack Query for all server state (posts, sessions, audit)

**Real-time updates:**
- WebSocket or SSE for live session status + publish progress

---

### Queue & Scheduling

```
Redis Streams:
  publisher:jobs          — immediate publish jobs
  publisher:scheduled     — due scheduled posts

Celery Beat tasks:
  every 30s: scan posts WHERE scheduled_at <= now AND status = 'pending'
             → enqueue to publisher:jobs

  every 5m:  cookie health check for all active accounts

Celery Workers:
  publish_task:
    1. acquire browser session for account
    2. dispatch to facebook_publisher or tiktok_publisher
    3. update post.status
    4. release session
    5. on failure: increment retry_count, schedule retry with backoff
```

---

### API Contract Examples

```
POST /api/v1/posts
Authorization: Bearer <token>

Request:
{
  "accountId": "uuid",
  "platform": "facebook",
  "contentType": "image",
  "caption": "Hello world!",
  "mediaUrls": ["s3://bucket/image.jpg"],
  "scheduledAt": "2026-06-21T10:00:00Z"   // null = publish now
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "queued",
    "scheduledAt": "2026-06-21T10:00:00Z"
  }
}

Errors: 400 (invalid), 401, 403, 404 (account not found), 422
```

```
GET /api/v1/sessions
Authorization: Bearer <token>

Response 200:
{
  "success": true,
  "data": [
    {
      "accountId": "uuid",
      "username": "@example",
      "platform": "facebook",
      "sessionStatus": "idle",
      "lastActivityAt": "2026-06-20T09:00:00Z"
    }
  ],
  "pagination": { "page": 1, "limit": 50, "total": 100, "totalPages": 2 }
}
```

---

## Security Constraints

- Cookies encrypted AES-256-GCM, key from `COOKIE_ENCRYPTION_KEY` env var — never stored in plaintext
- JWT signed with `JWT_SECRET` (RS256 preferred for prod)
- All endpoints require auth except `/api/v1/auth/login` and `/health`
- Rate limit login: 5 req/15min per IP
- Never log cookie values or decrypted credentials
- Browser sessions isolated via Playwright contexts (no cookie sharing)
- `CORS` locked to Vue frontend origin only

---

## Mandatory Standards

- Rules: `.claude/rules/` — all mandatory
- API format: `api-conventions.md`
- DB patterns: `database.md`
- Security: `security.md` — **CRITICAL** (cookie encryption never optional)
- Error handling: `error-handling.md`

---

## Testing Strategy

| Layer | Tool | Target |
|-------|------|--------|
| Unit | pytest | Services, encryption, publisher logic |
| Integration | pytest + httpx | All API endpoints |
| Browser automation | Playwright test mode | Facebook/TikTok publisher with mock pages |
| Component | Vitest + Vue Testing Library | Dashboard components |
| E2E | Playwright | Login → create post → publish flow |
| Coverage target | — | ≥ 80% |

---

## KPI / Acceptance Criteria

| Metric | Target |
|--------|--------|
| Facebook publish success rate | > 95% |
| Facebook publish time | < 60s/post |
| TikTok upload success rate | > 95% |
| TikTok upload time | < 120s/video |
| Concurrent browser sessions | 100+ |
| Browser crash rate | < 2% |
| Cookie health check interval | every 5 minutes |
| Job queue processing lag | < 5s for immediate posts |

---

## Boundaries

### Always Do
- Encrypt all cookies at rest
- Release browser session after every publish (success or failure)
- Log all publish attempts to audit_log
- Retry up to 3x on transient failures

### Ask First
- Adding new platform (Instagram, YouTube)
- Changing cookie encryption algorithm
- Scaling beyond single Docker Compose node (→ Kubernetes migration)

### Never Do
- Store cookies in plaintext anywhere (DB, logs, env vars)
- Share browser contexts between accounts
- Commit `.env` files
- Expose cookie values via API responses

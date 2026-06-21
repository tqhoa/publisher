# Plan: Social Media Publisher Platform

**Spec**: `docs/specs/platform-publisher.md`
**Layer**: Full-stack (FastAPI + Vue 3)
**Strategy**: Vertical slices — each task ships working functionality end-to-end

---

## Phase 1: Project Foundation

> Zero dependencies. Everything else builds on this.

- [x] **Task 1.1 — Project Scaffold**
  - Layer: Infrastructure
  - Objective: Runnable skeleton with all services wired in Docker Compose
  - Files:
    - `docker-compose.yml` — postgres, redis, api, worker, frontend, grafana, loki, prometheus
    - `backend/pyproject.toml` — FastAPI, SQLAlchemy, Alembic, Celery, Playwright, passlib, python-jose, cryptography, structlog, prometheus-client, slowapi, httpx, ruff, mypy
    - `backend/main.py` — FastAPI app with lifespan, CORS, middleware stubs
    - `backend/shared/config.py` — pydantic-settings (DATABASE_URL, REDIS_URL, JWT_SECRET, COOKIE_ENCRYPTION_KEY, etc.)
    - `backend/.env.example`
    - `frontend/` — `npm create vite@latest` with vue-ts template
    - `frontend/package.json` — pinia, @tanstack/vue-query, axios, vee-validate, zod, vue-router
  - Acceptance:
    - [ ] `docker compose up` starts all services without errors
    - [ ] `GET /health` → `{ "status": "ok" }`
    - [ ] Frontend serves at localhost:5173
  - Dependencies: none

- [x] **Task 1.2 — Shared Utilities**
  - Layer: Backend
  - Objective: Config, exceptions, logger, pagination helper available to all layers
  - Files:
    - `backend/shared/config.py` — all env vars with validation
    - `backend/shared/exceptions.py` — `AppError(message, status_code, code)`
    - `backend/shared/utils/logger.py` — structlog JSON config, bind service/env
    - `backend/shared/utils/pagination.py` — `PaginationParams`, `paginate(query, params)`
    - `backend/schemas/common.py` — `ApiResponse[T]`, `PaginatedResponse[T]`, `ErrorResponse`
    - `backend/main.py` — register `AppError`, `RequestValidationError`, `Exception` handlers
  - Acceptance:
    - [ ] `AppError("msg", 404, "NOT_FOUND")` raises and returns correct JSON envelope
    - [ ] Logger emits structured JSON with service/environment fields
    - [ ] `ApiResponse` and `PaginatedResponse` match spec contract
  - Dependencies: 1.1

- [x] **Task 1.3 — Database Models + Migrations**
  - Layer: Backend
  - Objective: All 5 tables created in Postgres via Alembic
  - Files:
    - `backend/infrastructure/database/models/user.py` — `UserModel`
    - `backend/infrastructure/database/models/account.py` — `AccountModel`
    - `backend/infrastructure/database/models/post.py` — `PostModel`
    - `backend/infrastructure/database/models/browser_session.py` — `BrowserSessionModel`
    - `backend/infrastructure/database/models/audit_log.py` — `AuditLogModel`
    - `backend/infrastructure/database/session.py` — async engine, `AsyncSessionLocal`, `get_db`
    - `backend/alembic/` — init + first migration
    - `backend/alembic.ini`
  - Acceptance:
    - [ ] `alembic upgrade head` creates all 5 tables cleanly
    - [ ] `alembic downgrade -1` rolls back cleanly
    - [ ] All FK constraints and indexes per spec
  - Dependencies: 1.1, 1.2

- [x] **Task 1.4 — Cookie Encryption Utility**
  - Layer: Backend
  - Objective: AES-256-GCM encrypt/decrypt; never cookie in plaintext
  - Files:
    - `backend/infrastructure/encryption/cookie_cipher.py`
      - `encrypt(plaintext: str) -> str` — base64(nonce + ciphertext + tag)
      - `decrypt(ciphertext: str) -> str`
      - key sourced from `settings.COOKIE_ENCRYPTION_KEY` (32 bytes)
    - `tests/unit/infrastructure/test_cookie_cipher.py`
  - Acceptance:
    - [ ] `decrypt(encrypt(data)) == data`
    - [ ] Different nonce per call (ciphertext not deterministic)
    - [ ] Key not 32 bytes → raises `ValueError` at import time
    - [ ] Unit tests pass
  - Dependencies: 1.2

- [x] **Task 1.5 — Redis Client + Audit Log Middleware**
  - Layer: Backend
  - Objective: Redis connection available; every API request auto-logged to audit_logs
  - Files:
    - `backend/infrastructure/cache/client.py` — `redis: Redis` singleton
    - `backend/domain/repositories/audit_log_repository.py`
    - `backend/api/middleware/audit.py` — `AuditMiddleware` (write to audit_logs on mutating requests)
    - `backend/api/middleware/logging.py` — `RequestLoggingMiddleware`
    - `backend/api/middleware/metrics.py` — `MetricsMiddleware` (Prometheus counters/histograms)
  - Acceptance:
    - [ ] `redis.ping()` succeeds in health check
    - [ ] POST/PATCH/DELETE requests write to `audit_logs`
    - [ ] `GET /metrics` returns Prometheus text
  - Dependencies: 1.2, 1.3

---

## Checkpoint: Phase 1 — Foundation Complete

- [ ] `docker compose up` → all containers healthy
- [ ] `GET /health` → 200
- [ ] `alembic upgrade head` → clean
- [ ] `GET /metrics` → Prometheus text
- [ ] `encrypt/decrypt` unit test passes
- [ ] No mypy errors: `mypy backend/`

---

## Phase 2: Authentication

> Gate everything. No auth = no access.

- [x] **Task 2.1 — Auth Service + User Seed**
  - Layer: Backend
  - Objective: Hash passwords, issue JWT tokens, validate tokens
  - Files:
    - `backend/shared/helpers/jwt.py` — `create_access_token`, `create_refresh_token`, `decode_token`
    - `backend/shared/helpers/hash.py` — `hash_password`, `verify_password` (bcrypt rounds=12)
    - `backend/domain/repositories/user_repository.py` — `find_by_email`, `find_by_id`
    - `backend/domain/services/auth_service.py` — `login`, `refresh`, `get_current_user`
    - `backend/scripts/seed_admin.py` — create first admin user via CLI
    - `tests/unit/services/test_auth_service.py`
  - Acceptance:
    - [ ] `python scripts/seed_admin.py` creates admin user
    - [ ] `hash_password` + `verify_password` round-trip works
    - [ ] `create_access_token` expires in 15m
    - [ ] `decode_token` raises on expired/invalid token
    - [ ] Unit tests pass
  - Dependencies: 1.3

- [x] **Task 2.2 — Auth Endpoints**
  - Layer: Backend
  - Objective: `POST /login`, `POST /refresh`, `POST /logout` fully working
  - Files:
    - `backend/schemas/auth.py` — `LoginRequest`, `LoginResponse`, `TokenRefreshRequest`
    - `backend/api/v1/auth.py` — router with 3 endpoints + rate limit on login
    - `backend/api/dependencies/auth.py` — `get_current_user`, `require_admin` FastAPI Depends
    - `backend/main.py` — include auth router
    - `tests/integration/routes/test_auth.py`
  - Acceptance:
    - [ ] `POST /api/v1/auth/login` valid creds → 200 with `accessToken` + `refreshToken`
    - [ ] `POST /api/v1/auth/login` wrong creds → 401
    - [ ] `POST /api/v1/auth/login` 6th attempt same IP → 429
    - [ ] `POST /api/v1/auth/refresh` valid refresh token → new `accessToken`
    - [ ] `POST /api/v1/auth/logout` invalidates refresh token
    - [ ] Integration tests pass
  - Dependencies: 2.1

---

## Checkpoint: Phase 2 — Auth Complete

- [ ] Login flow works end-to-end via curl
- [ ] Protected endpoint with no token → 401
- [ ] Refresh token flow → new access token
- [ ] Rate limit triggers on 6th login attempt
- [ ] Integration tests pass

---

## Phase 3: Account & Cookie Service

- [x] **Task 3.1 — Account CRUD (Backend)**
  - Layer: Backend
  - Objective: Full CRUD for social accounts behind auth
  - Files:
    - `backend/schemas/account.py` — `AccountCreate`, `AccountUpdate`, `AccountResponse`
    - `backend/domain/repositories/account_repository.py`
    - `backend/domain/services/account_service.py` — CRUD, status transitions
    - `backend/api/v1/accounts.py` — GET list, POST, GET by id, PATCH, DELETE
    - `tests/integration/routes/test_accounts.py`
  - Acceptance:
    - [ ] `GET /api/v1/accounts` paginated list (page, limit)
    - [ ] `POST /api/v1/accounts` creates account, returns 201
    - [ ] `PATCH /api/v1/accounts/{id}` partial update
    - [ ] `DELETE /api/v1/accounts/{id}` soft-delete (sets `status=inactive`)
    - [ ] Non-existent id → 404
    - [ ] No auth → 401
    - [ ] Integration tests pass
  - Dependencies: 2.2

- [x] **Task 3.2 — Cookie Import + Health Check**
  - Layer: Backend
  - Objective: Import cookies encrypted, verify live cookie health
  - Files:
    - `backend/schemas/account.py` — add `CookieImportRequest`
    - `backend/domain/services/account_service.py` — `import_cookie`, `check_health`
    - `backend/api/v1/accounts.py` — `POST /{id}/cookie`, `GET /{id}/health`
    - `backend/infrastructure/browser/health_checker.py` — Playwright headless nav to verify login state
    - `tests/integration/routes/test_account_cookie.py`
    - `tests/unit/services/test_account_service.py`
  - Acceptance:
    - [ ] `POST /{id}/cookie` with JSON cookie string → encrypted in DB, raw value never returned
    - [ ] `GET /{id}/health` launches Playwright, navigates to platform, returns `{ "healthy": true/false }`
    - [ ] Cookie value never appears in logs or API response
    - [ ] Unit tests for encrypt/decrypt round-trip
  - Dependencies: 3.1, 1.4

---

## Checkpoint: Phase 3 — Account & Cookie Complete

- [ ] Account CRUD all operations work
- [ ] Cookie import stores encrypted value only
- [ ] `/health` endpoint returns accurate status
- [ ] All integration tests pass
- [ ] mypy clean

---

## Phase 4: Browser Farm

- [x] **Task 4.1 — Playwright Session Pool**
  - Layer: Backend (Infrastructure)
  - Objective: AsyncIO pool managing up to 100 concurrent Playwright sessions
  - Files:
    - `backend/infrastructure/browser/playwright_pool.py`
      - `PlaywrightPool` (singleton, lifespan-managed)
      - `acquire(account_id) -> BrowserSession` — warm reuse or cold start
      - `release(account_id)` — mark idle
      - `_restart_session(account_id)` — crash recovery
      - `asyncio.Semaphore(max_sessions=100)`
    - `backend/infrastructure/browser/browser_session.py`
      - `BrowserSession(browser, context, page, status)`
    - `backend/main.py` — start/stop pool in lifespan
    - `tests/unit/infrastructure/test_playwright_pool.py`
  - Acceptance:
    - [ ] `acquire()` returns session with cookies loaded from account
    - [ ] `release()` marks session idle, not closed
    - [ ] Crashed session (page closed unexpectedly) auto-restarts
    - [ ] Concurrent `acquire()` calls respect semaphore (≤100)
    - [ ] Unit tests with mock Playwright
  - Dependencies: 3.2

- [x] **Task 4.2 — Session Service + DB Tracking**
  - Layer: Backend
  - Objective: Track session state in `browser_sessions` table; expose read API
  - Files:
    - `backend/domain/repositories/browser_session_repository.py`
    - `backend/domain/services/browser_session_service.py` — sync DB on acquire/release/crash
    - `backend/schemas/session.py` — `BrowserSessionResponse`
    - `backend/api/v1/sessions.py` — `GET /sessions`, `GET /sessions/{account_id}`
    - `backend/main.py` — include sessions router
    - `tests/integration/routes/test_sessions.py`
  - Acceptance:
    - [ ] `GET /api/v1/sessions` returns all sessions with status
    - [ ] Status updates (idle→busy→idle) reflected in DB within 1s
    - [ ] Crashed session shows `status=crashed` in API
    - [ ] Integration tests pass
  - Dependencies: 4.1

---

## Checkpoint: Phase 4 — Browser Farm Complete

- [ ] Pool starts with app, stops cleanly on shutdown
- [ ] 10 concurrent `acquire()` calls succeed without deadlock
- [ ] Crashed session recovers automatically
- [ ] `GET /sessions` returns live status
- [ ] mypy clean on infrastructure/browser/

---

## Phase 5: Facebook Publisher

- [x] **Task 5.1 — Post CRUD API**
  - Layer: Backend
  - Objective: Create, list, get, delete posts; no publish logic yet
  - Files:
    - `backend/schemas/post.py` — `PostCreate`, `PostResponse`, `PostListResponse`
    - `backend/domain/repositories/post_repository.py`
    - `backend/domain/services/post_service.py` — CRUD + status transitions
    - `backend/api/v1/posts.py` — full CRUD + `POST /{id}/publish-now` + `POST /{id}/retry`
    - `backend/main.py` — include posts router
    - `tests/integration/routes/test_posts.py`
  - Acceptance:
    - [ ] `POST /api/v1/posts` creates post, `status=pending`
    - [ ] `scheduledAt` provided → `status=pending`, future dispatch
    - [ ] `scheduledAt` null → immediately enqueued (`status=queued`)
    - [ ] `GET /api/v1/posts` paginated, filterable by `status`, `platform`, `accountId`
    - [ ] Integration tests pass
  - Dependencies: 3.1, 2.2

- [x] **Task 5.2 — Celery Infrastructure**
  - Layer: Backend
  - Objective: Celery app + worker running; publish task skeleton
  - Files:
    - `backend/infrastructure/queue/celery_app.py` — Celery app with Redis broker
    - `backend/infrastructure/queue/tasks/publish_task.py` — `publish_post.delay(post_id)` skeleton
    - `docker-compose.yml` — add `worker` service (`celery -A celery_app worker`)
  - Acceptance:
    - [ ] `celery -A celery_app worker` starts without error
    - [ ] `publish_post.delay("test")` enqueues and runs (no-op implementation)
    - [ ] Worker logs task received
  - Dependencies: 1.5, 5.1

- [x] **Task 5.3 — Facebook Playwright Automation**
  - Layer: Backend (Infrastructure)
  - Objective: `facebook_publisher.py` can post text/image/video via authenticated session
  - Files:
    - `backend/infrastructure/browser/facebook_publisher.py`
      - `post_text(page, caption) -> str` (returns post URL)
      - `post_image(page, caption, image_paths) -> str`
      - `post_video(page, caption, video_path) -> str`
    - `tests/unit/infrastructure/test_facebook_publisher.py` — mock Playwright page
  - Acceptance:
    - [ ] `post_text` navigates to Facebook, types caption, clicks Post, returns post URL
    - [ ] `post_image` attaches image file before posting
    - [ ] `post_video` handles upload progress wait (up to 60s)
    - [ ] On any Playwright error → raises `PublishError` with descriptive message
    - [ ] Unit tests with mocked page pass
  - Dependencies: 4.1

- [x] **Task 5.4 — Facebook Publish Task + Status Tracking**
  - Layer: Backend
  - Objective: End-to-end: enqueue → acquire session → publish → update status
  - Files:
    - `backend/infrastructure/queue/tasks/publish_task.py` — full implementation
      ```python
      @celery_app.task(bind=True, max_retries=3)
      async def publish_post(self, post_id: str):
          # 1. load post + account
          # 2. acquire session
          # 3. dispatch to facebook_publisher or tiktok_publisher
          # 4. update post.status = published / failed
          # 5. release session
          # 6. on exception: self.retry(countdown=60 * 2**self.request.retries)
      ```
    - `backend/domain/services/post_service.py` — `mark_publishing`, `mark_published`, `mark_failed`
    - `tests/integration/test_publish_flow.py` — mock browser farm
  - Acceptance:
    - [ ] `POST /api/v1/posts/{id}/publish-now` → status goes `queued→publishing→published`
    - [ ] Published post has `publishedAt` timestamp
    - [ ] Failed publish → `status=failed`, `errorMessage` populated
    - [ ] Session always released (even on exception)
    - [ ] Integration test with mocked Playwright passes
  - Dependencies: 5.2, 5.3, 4.2

---

## Checkpoint: Phase 5 — Facebook Publisher Complete

- [ ] Full flow: create post → publish-now → status=published
- [ ] Failed publish retries (mock 2 failures, 3rd success)
- [ ] Session released in all code paths
- [ ] `errorMessage` populated on failure
- [ ] Integration tests pass

---

## Phase 6: TikTok Publisher

- [x] **Task 6.1 — TikTok Playwright Automation**
  - Layer: Backend (Infrastructure)
  - Objective: `tiktok_publisher.py` uploads video with caption + hashtags
  - Files:
    - `backend/infrastructure/browser/tiktok_publisher.py`
      - `upload_video(page, caption, hashtags, video_path) -> str` (returns TikTok URL)
      - Handles TikTok upload UI: click Upload → file input → caption → hashtags → Post
      - Wait for processing completion (up to 120s)
    - `tests/unit/infrastructure/test_tiktok_publisher.py`
  - Acceptance:
    - [ ] `upload_video` completes full TikTok upload flow
    - [ ] Hashtags appended to caption correctly (`#tag1 #tag2`)
    - [ ] Upload progress wait handles slow connections (timeout 120s)
    - [ ] On failure → `PublishError`
    - [ ] Unit tests with mocked page pass
  - Dependencies: 4.1

- [x] **Task 6.2 — TikTok Publish Task**
  - Layer: Backend
  - Objective: TikTok posts go through same publish_task pipeline
  - Files:
    - `backend/infrastructure/queue/tasks/publish_task.py` — branch on `post.platform`
    - `tests/integration/test_tiktok_publish_flow.py`
  - Acceptance:
    - [ ] `POST /api/v1/posts` with `platform=tiktok` → dispatched to `tiktok_publisher`
    - [ ] Status tracking same as Facebook
    - [ ] `publishedAt` populated
  - Dependencies: 6.1, 5.4

---

## Checkpoint: Phase 6 — TikTok Publisher Complete

- [ ] TikTok post create → publish-now → status=published
- [ ] Hashtags formatted correctly
- [ ] Same retry/error handling as Facebook
- [ ] Tests pass

---

## Phase 7: Scheduler & Retry Engine

- [x] **Task 7.1 — Celery Beat Scheduler**
  - Layer: Backend
  - Objective: Scan due scheduled posts every 30s and enqueue them
  - Files:
    - `backend/infrastructure/queue/tasks/scheduler_task.py`
      - `@celery_app.on_after_configure.connect` sets up beat schedule
      - `enqueue_due_posts()` — `SELECT * FROM posts WHERE scheduled_at <= now AND status='pending'` → `publish_post.delay(post_id)`
    - `docker-compose.yml` — add `beat` service (`celery -A celery_app beat`)
    - `tests/unit/tasks/test_scheduler_task.py`
  - Acceptance:
    - [ ] Post with `scheduledAt = now+10s` → status=`queued` within 30s
    - [ ] Already-queued posts not double-enqueued
    - [ ] Beat service restarts without duplicate jobs
    - [ ] Unit test with frozen time passes
  - Dependencies: 5.4

- [x] **Task 7.2 — Cookie Health Check Task**
  - Layer: Backend
  - Objective: Every 5 minutes check all active account cookies; mark `health_status`
  - Files:
    - `backend/infrastructure/queue/tasks/health_check_task.py`
      - `check_all_cookies()` — iterate active accounts, call `health_checker.check(account_id)`
      - Update `accounts.health_status` + `last_health_check_at`
    - `tests/unit/tasks/test_health_check_task.py`
  - Acceptance:
    - [ ] Dead cookie → `health_status=unhealthy`, `active` account status unchanged (operator decides)
    - [ ] Healthy cookie → `health_status=healthy`
    - [ ] Task runs every 5 minutes per beat schedule
  - Dependencies: 3.2, 7.1

---

## Checkpoint: Phase 7 — Scheduler & Retry Complete

- [ ] Scheduled post auto-publishes at correct time (±30s)
- [ ] Cookie health check runs and updates DB
- [ ] Retry: 3 failures → `status=failed`, no more retries
- [ ] No duplicate enqueue on beat restart

---

## Phase 8: Frontend (Vue 3)

> Implement in order: shell → auth → accounts → posts → monitoring

- [x] **Task 8.1 — Frontend Shell: Router + Auth Store + API Client**
  - Layer: Frontend
  - Files:
    - `frontend/src/router/index.ts` — routes with `meta.requiresAuth`, `meta.guestOnly`
    - `frontend/src/router/guards/auth.guard.ts`
    - `frontend/src/stores/useAuthStore.ts` — `token`, `user`, `login()`, `logout()`
    - `frontend/src/api/index.ts` — axios instance, request interceptor (attach token), 401 handler
    - `frontend/src/api/endpoints/auth.api.ts`
    - `frontend/src/views/auth/LoginView.vue`
    - `tests/unit/stores/useAuthStore.test.ts`
  - Acceptance:
    - [ ] `LoginView` submits → calls `POST /api/v1/auth/login` → stores token → redirects to dashboard
    - [ ] Unauthenticated user redirected to `/login`
    - [ ] 401 response → auto-logout + redirect to `/login`
    - [ ] Token persisted in localStorage
    - [ ] Store unit tests pass
  - Dependencies: 2.2

- [x] **Task 8.2 — Account Management UI**
  - Layer: Frontend
  - Files:
    - `frontend/src/api/endpoints/accounts.api.ts`
    - `frontend/src/features/accounts/composables/useAccounts.ts` — TanStack Query
    - `frontend/src/views/accounts/AccountListView.vue` — table with status badges, health indicators
    - `frontend/src/views/accounts/AccountDetailView.vue` — cookie import form, health check button
    - `frontend/src/features/accounts/components/AccountForm.vue`
    - `frontend/src/features/accounts/components/CookieImportModal.vue`
    - `tests/unit/components/CookieImportModal.test.ts`
  - Acceptance:
    - [ ] Account list shows platform, username, status, health_status
    - [ ] Create account form validates required fields
    - [ ] Cookie import modal: paste JSON → submit → success toast
    - [ ] Health check button triggers `GET /{id}/health` → shows result
    - [ ] Delete shows confirmation dialog
  - Dependencies: 8.1, 3.2

- [x] **Task 8.3 — Post Management UI**
  - Layer: Frontend
  - Files:
    - `frontend/src/api/endpoints/posts.api.ts`
    - `frontend/src/features/posts/composables/usePosts.ts`
    - `frontend/src/views/posts/PostListView.vue` — filterable by status/platform
    - `frontend/src/views/posts/PostCreateView.vue` — select account, content type, media upload, schedule picker
    - `frontend/src/views/posts/PostDetailView.vue` — status timeline, retry button
    - `tests/unit/components/PostCreateView.test.ts`
  - Acceptance:
    - [ ] Create post: select account → fill caption → optional media URLs → optional schedule time → submit
    - [ ] Post list: filter by status, platform; shows status badge with color
    - [ ] Post detail: status history, `publishedAt`, `errorMessage`, retry button
    - [ ] Retry button only visible when `status=failed`
  - Dependencies: 8.1, 5.1

- [x] **Task 8.4 — Browser Sessions Live View**
  - Layer: Frontend
  - Files:
    - `frontend/src/api/endpoints/sessions.api.ts`
    - `frontend/src/features/sessions/composables/useSessions.ts` — poll every 5s
    - `frontend/src/views/sessions/SessionsView.vue` — live grid: account, platform, status, last activity
  - Acceptance:
    - [ ] Grid auto-refreshes every 5s without full reload
    - [ ] Status color: idle=green, busy=yellow, crashed=red
    - [ ] Shows total active / idle / crashed counts
  - Dependencies: 8.1, 4.2

- [x] **Task 8.5 — Dashboard Overview**
  - Layer: Frontend
  - Files:
    - `frontend/src/views/dashboard/DashboardView.vue`
      - KPI cards: total accounts, healthy accounts, posts today, success rate
      - Recent posts list (last 10)
      - Queue depth (poll `/api/v1/sessions` stats)
  - Acceptance:
    - [ ] Dashboard loads within 2s
    - [ ] KPI cards reflect real data
    - [ ] Auto-refreshes every 30s
  - Dependencies: 8.1, 8.2, 8.3

- [x] **Task 8.6 — Monitoring + Audit Log UI**
  - Layer: Frontend
  - Files:
    - `frontend/src/views/monitoring/MonitoringView.vue` — embed Grafana iframe or native Prometheus charts
    - `frontend/src/views/audit/AuditLogView.vue` — paginated table: timestamp, user, action, resource
    - `frontend/src/api/endpoints/audit.api.ts`
  - Acceptance:
    - [ ] Audit log shows last 100 actions, paginated
    - [ ] Monitoring view links to/embeds Grafana dashboard
    - [ ] Filterable by date range and action type
  - Dependencies: 8.1, 1.5

---

## Checkpoint: Phase 8 — Frontend Complete

- [ ] Full login → create account → import cookie → create post → publish-now flow works in browser
- [ ] Session live view updates without page refresh
- [ ] All form validations work (client-side + show server errors)
- [ ] No console errors on any page
- [ ] Vitest component tests pass

---

## Phase 9: Monitoring Infrastructure

- [x] **Task 9.1 — Grafana + Prometheus + Loki Setup**
  - Layer: Infrastructure
  - Files:
    - `monitoring/prometheus.yml` — scrape configs (FastAPI `/metrics`, node-exporter)
    - `monitoring/grafana/dashboards/publisher-overview.json` — RED metrics: request rate, error rate, P99 latency
    - `monitoring/grafana/dashboards/browser-farm.json` — session pool utilization, crash rate
    - `monitoring/grafana/dashboards/publish-jobs.json` — queue depth, success rate, retry rate
    - `monitoring/loki-config.yml`
    - `docker-compose.yml` — grafana, prometheus, loki, promtail services
  - Acceptance:
    - [ ] Grafana accessible at `localhost:3000`
    - [ ] Publisher Overview dashboard shows live request rate + error rate
    - [ ] Browser Farm dashboard shows session status counts
    - [ ] structlog output flows to Loki and queryable in Grafana
  - Dependencies: 1.5

- [x] **Task 9.2 — Alerting Rules**
  - Layer: Infrastructure
  - Files:
    - `monitoring/alerts.yml`
      - `ServiceDown` → critical
      - `HighErrorRate` (>5%) → warning
      - `HighLatency` (P99 > 1s) → warning
      - `BrowserCrashRate` (>2%) → warning
      - `PublishSuccessRateLow` (<95%) → critical
  - Acceptance:
    - [ ] Alert rules load in Prometheus without syntax errors
    - [ ] `PublishSuccessRateLow` fires when manually set metric below threshold
  - Dependencies: 9.1

---

## Checkpoint: Phase 9 — Monitoring Complete

- [ ] All 3 Grafana dashboards populated with live data
- [ ] Alerts load without errors
- [ ] Logs from FastAPI visible in Loki
- [ ] `browser_crash_rate` metric tracked

---

## Phase 10: Hardening & E2E Tests

- [x] **Task 10.1 — Security Hardening**
  - Audit all endpoints for missing auth
  - Verify cookie value never in any log line or API response
  - Confirm CORS allows only `ALLOWED_ORIGINS`
  - Helmet-equivalent headers (CSP, X-Frame-Options) via FastAPI middleware
  - `npm audit` on frontend, `pip-audit` on backend — zero high/critical
  - Files: `backend/api/middleware/security.py`

- [x] **Task 10.2 — Coverage Audit**
  - Run `pytest --cov=backend --cov-report=html --cov-fail-under=80`
  - Run `npx vitest run --coverage`
  - Fill gaps to reach ≥80% on both

- [x] **Task 10.3 — E2E Tests (Playwright)**
  - Files: `tests/e2e/`
    - `test_auth_flow.py` — login → protected page
    - `test_account_flow.py` — create account → import cookie → health check
    - `test_publish_flow.py` — create post → publish-now → verify status=published
    - `test_schedule_flow.py` — create scheduled post → wait → verify auto-publish

- [x] **Task 10.4 — Load Test: Browser Farm**
  - Spin up 50 mock accounts
  - Trigger 50 concurrent `publish_post` tasks
  - Verify all complete without deadlock
  - Verify crash rate < 2% under load
  - Files: `tests/load/test_browser_farm_load.py`

- [x] **Task 10.5 — README + Docker Compose Docs**
  - `README.md` with Quick Start, env var reference, architecture diagram
  - `docs/operations/runbook.md` — how to add accounts, recover crashed sessions, rotate encryption key

---

## Checkpoint: Phase 10 — Ship Ready

- [ ] Backend coverage ≥ 80%
- [ ] Frontend coverage ≥ 80%
- [ ] All E2E tests pass
- [ ] `npm audit` + `pip-audit` zero high/critical
- [ ] Cookie never appears in logs (grep test)
- [ ] 50 concurrent publishes complete without deadlock
- [ ] `docker compose up` from scratch → all healthy in < 60s
- [ ] README quick-start works end-to-end

---

## Task Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| 1 — Foundation | 1.1–1.5 | Docker, DB, config, encryption, middleware |
| 2 — Auth | 2.1–2.2 | JWT login, RBAC, rate limit |
| 3 — Accounts | 3.1–3.2 | CRUD, cookie import, health check |
| 4 — Browser Farm | 4.1–4.2 | Playwright pool, session tracking |
| 5 — Facebook | 5.1–5.4 | Post CRUD, Celery, Playwright automation, status |
| 6 — TikTok | 6.1–6.2 | Video upload, same pipeline |
| 7 — Scheduler | 7.1–7.2 | Beat scheduler, retry, health check tasks |
| 8 — Frontend | 8.1–8.6 | Full Vue 3 dashboard |
| 9 — Monitoring | 9.1–9.2 | Grafana, Prometheus, Loki, alerts |
| 10 — Hardening | 10.1–10.5 | Security, coverage, E2E, load test |

**Total: 25 tasks across 10 phases**

---

## Dependency Graph

```
1.1 → 1.2 → 1.3 → 1.4
               ↓
           2.1 → 2.2
               ↓
           3.1 → 3.2
               ↓         \
           4.1 → 4.2     1.5
               ↓           ↓
           5.1 → 5.2 → 5.3 → 5.4
                              ↓
                          6.1 → 6.2
                              ↓
                          7.1 → 7.2
                              ↓
                    8.1 → 8.2 → 8.3 → 8.4 → 8.5 → 8.6
                              ↓
                          9.1 → 9.2
                              ↓
                     10.1 → 10.2 → 10.3 → 10.4 → 10.5
```

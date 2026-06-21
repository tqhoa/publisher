# Operations Runbook

## Add a New Account

1. Log in as admin
2. **Accounts → Add Account** — choose platform + username
3. Get cookies from browser:
   - Log into Facebook/TikTok in Chrome
   - DevTools → Application → Cookies
   - Right-click → "Copy all as JSON" (use EditThisCookie extension for full JSON format)
4. **Account Detail → Import Cookie** — paste JSON array
5. Click **Check Health** — should show "Healthy"

If health check fails: the cookie has expired. Log in again in Chrome and re-import.

---

## Recover a Crashed Browser Session

Sessions crash when Playwright encounters an unrecoverable page error.

1. Navigate to **Sessions** — crashed sessions show in red
2. The pool automatically removes the crashed session from tracking
3. The next publish task for that account will create a fresh session
4. If an account is stuck in `crashed` state after 5 minutes:
   ```bash
   # Restart the API (which restarts the pool)
   docker compose restart api
   ```

---

## Rotate the Cookie Encryption Key

**Warning: Rotating the key invalidates all stored cookies.** All accounts must re-import their cookies after rotation.

1. Generate a new 32-byte key:
   ```bash
   python -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
   ```
2. Update `backend/.env`:
   ```
   COOKIE_ENCRYPTION_KEY=<new_key>
   ```
3. Restart the API:
   ```bash
   docker compose restart api
   ```
4. Re-import cookies for all accounts (old encrypted values are now unreadable)

---

## Rotate JWT Secret

1. Generate a new secret:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
2. Update `backend/.env`:
   ```
   JWT_SECRET=<new_secret>
   ```
3. Restart:
   ```bash
   docker compose restart api
   ```
4. **All active user sessions are invalidated.** Users must log in again.

---

## Scale Browser Farm

The default limit is 100 concurrent sessions (`BROWSER_MAX_SESSIONS=100`).

To increase:
1. Set `BROWSER_MAX_SESSIONS=200` in `backend/.env`
2. Ensure the container has sufficient memory (~150MB per session)
3. Restart: `docker compose restart api worker`

---

## Database Backup

```bash
docker compose exec db pg_dump -U publisher publisher > backup_$(date +%Y%m%d).sql
```

Restore:
```bash
cat backup_20260101.sql | docker compose exec -T db psql -U publisher publisher
```

---

## View Logs

```bash
# API logs
docker compose logs -f api

# Worker logs
docker compose logs -f worker

# All services
docker compose logs -f

# Structured logs in Grafana Loki
# Open http://localhost:3000 → Explore → select Loki datasource
# Query: {service="publisher"}
```

---

## Alerts

Alerts are defined in `monitoring/alerts.yml`:

| Alert | Severity | Condition |
|-------|----------|-----------|
| `ServiceDown` | critical | API unreachable for 1min |
| `HighErrorRate` | warning | HTTP 5xx > 5% for 5min |
| `HighLatency` | warning | P99 latency > 1s for 5min |
| `BrowserCrashRate` | warning | Session crash rate > 2% |
| `PublishSuccessRateLow` | critical | Success rate < 95% for 5min |

---

## Common Issues

### Posts stuck in `queued` state
- Worker is not running: `docker compose up -d worker`
- Check worker logs: `docker compose logs worker`

### Cookie health check always failing
- Cookie expired — re-import from browser
- Facebook/TikTok changed their login page — check Playwright selectors

### Celery beat not scheduling
- Beat service not running: `docker compose up -d beat`
- Check: `docker compose logs beat`

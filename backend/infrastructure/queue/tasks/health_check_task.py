import asyncio
from datetime import datetime, timezone

import structlog

from infrastructure.queue.celery_app import celery_app

logger = structlog.get_logger()


def _run(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="check_all_cookies")
def check_all_cookies() -> dict:  # type: ignore[type-arg]
    return _run(_check_all_cookies_async())


async def _check_all_cookies_async() -> dict:  # type: ignore[type-arg]
    from sqlalchemy import select
    from infrastructure.database.session import AsyncSessionLocal
    from infrastructure.database.models.account import AccountModel
    from infrastructure.encryption.cookie_cipher import decrypt
    from infrastructure.browser.playwright_pool import get_pool

    checked = 0
    healthy = 0

    try:
        pool = get_pool()
    except AssertionError:
        logger.warning("health_check_pool_not_ready")
        return {"checked": 0, "healthy": 0}

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AccountModel).where(
                AccountModel.status == "active",
                AccountModel.cookie_encrypted.is_not(None),
            )
        )
        accounts = list(result.scalars().all())

    for account in accounts:
        is_healthy = False
        try:
            if not account.cookie_encrypted:
                continue
            cookie_json = decrypt(account.cookie_encrypted)
            session = await pool.acquire(account.id, cookie_json)
            try:
                # Simple liveness check: navigate to platform home
                if account.platform == "facebook":
                    await session.page.goto("https://www.facebook.com", timeout=15_000)
                    is_healthy = "facebook.com" in session.page.url
                elif account.platform == "tiktok":
                    await session.page.goto("https://www.tiktok.com", timeout=15_000)
                    is_healthy = "tiktok.com" in session.page.url
            finally:
                await pool.release(account.id)
        except Exception as exc:
            logger.warning("health_check_failed", account_id=account.id, error=str(exc))

        checked += 1
        health_status = "healthy" if is_healthy else "unhealthy"
        if is_healthy:
            healthy += 1

        async with AsyncSessionLocal() as db:
            from sqlalchemy import select as sa_select
            result = await db.execute(
                sa_select(AccountModel).where(AccountModel.id == account.id)
            )
            acc = result.scalar_one_or_none()
            if acc:
                acc.health_status = health_status
                acc.last_health_check_at = datetime.now(timezone.utc)
            await db.commit()

    logger.info("health_check_complete", checked=checked, healthy=healthy)
    return {"checked": checked, "healthy": healthy}

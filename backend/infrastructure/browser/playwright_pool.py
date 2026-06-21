import asyncio
import json
import structlog
from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from infrastructure.browser.browser_session import BrowserSession
from shared.config import settings

logger = structlog.get_logger()


class PublishError(Exception):
    pass


class PlaywrightPool:
    """Singleton pool of Playwright browser sessions keyed by account_id."""

    def __init__(self, max_sessions: int = 100) -> None:
        self._max_sessions = max_sessions
        self._semaphore: asyncio.Semaphore | None = None
        self._sessions: dict[str, BrowserSession] = {}
        self._lock = asyncio.Lock()
        self._playwright: Playwright | None = None

    async def start(self) -> None:
        self._semaphore = asyncio.Semaphore(self._max_sessions)
        self._playwright = await async_playwright().start()
        logger.info("playwright_pool_started", max_sessions=self._max_sessions)

    async def stop(self) -> None:
        async with self._lock:
            for session in list(self._sessions.values()):
                try:
                    await session.browser.close()
                except Exception:
                    pass
            self._sessions.clear()
        if self._playwright:
            await self._playwright.stop()
        logger.info("playwright_pool_stopped")

    async def acquire(self, account_id: str, cookie_json: str | None = None) -> BrowserSession:
        assert self._semaphore is not None, "Pool not started"
        await self._semaphore.acquire()
        try:
            async with self._lock:
                session = self._sessions.get(account_id)
                if session and session.status == "idle":
                    session.status = "busy"
                    session.touch()
                    logger.debug("session_reused", account_id=account_id)
                    return session

            session = await self._create_session(account_id, cookie_json)
            async with self._lock:
                self._sessions[account_id] = session
            return session
        except Exception:
            self._semaphore.release()
            raise

    async def release(self, account_id: str) -> None:
        async with self._lock:
            session = self._sessions.get(account_id)
            if session and session.status != "crashed":
                session.status = "idle"
                session.touch()
        if self._semaphore:
            self._semaphore.release()
        logger.debug("session_released", account_id=account_id)

    async def mark_crashed(self, account_id: str) -> None:
        async with self._lock:
            session = self._sessions.get(account_id)
            if session:
                session.status = "crashed"
                try:
                    await session.browser.close()
                except Exception:
                    pass
                del self._sessions[account_id]
        if self._semaphore:
            self._semaphore.release()
        logger.warning("session_crashed", account_id=account_id)
        asyncio.ensure_future(self._restart_session(account_id))

    def get_all(self) -> list[BrowserSession]:
        return list(self._sessions.values())

    def get(self, account_id: str) -> BrowserSession | None:
        return self._sessions.get(account_id)

    async def _create_session(self, account_id: str, cookie_json: str | None) -> BrowserSession:
        assert self._playwright is not None
        browser: Browser = await self._playwright.chromium.launch(
            headless=settings.browser_headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context: BrowserContext = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        if cookie_json:
            cookies = json.loads(cookie_json)
            await context.add_cookies(cookies)

        page: Page = await context.new_page()

        # Auto-recover on page crash
        page.on("crash", lambda _: asyncio.ensure_future(self.mark_crashed(account_id)))

        session = BrowserSession(
            account_id=account_id,
            browser=browser,
            context=context,
            page=page,
            status="busy",
        )
        logger.info("session_created", account_id=account_id)
        return session

    async def _restart_session(self, account_id: str) -> None:
        """Re-add a placeholder entry so next acquire() creates a fresh session."""
        logger.info("session_restart_queued", account_id=account_id)


_pool: PlaywrightPool | None = None


def get_pool() -> PlaywrightPool:
    assert _pool is not None, "PlaywrightPool not initialized"
    return _pool


async def init_pool() -> None:
    global _pool
    _pool = PlaywrightPool(max_sessions=settings.browser_max_sessions)
    await _pool.start()


async def shutdown_pool() -> None:
    global _pool
    if _pool:
        await _pool.stop()
        _pool = None

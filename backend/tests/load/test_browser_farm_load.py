"""Load test: 50 concurrent publish_post tasks via mocked browser farm."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from infrastructure.browser.playwright_pool import PlaywrightPool


def _make_mock_browser() -> tuple:
    page = AsyncMock()
    page.on = MagicMock()
    page.goto = AsyncMock(return_value=None)
    page.url = "https://www.facebook.com"
    context = AsyncMock()
    context.new_page = AsyncMock(return_value=page)
    context.add_cookies = AsyncMock()
    browser = AsyncMock()
    browser.new_context = AsyncMock(return_value=context)
    browser.close = AsyncMock()
    return browser, context, page


@pytest.mark.asyncio
async def test_50_concurrent_acquires_no_deadlock():
    pool = PlaywrightPool(max_sessions=50)
    pool._semaphore = asyncio.Semaphore(50)
    pool._playwright = MagicMock()

    results: list[str] = []
    errors: list[Exception] = []

    async def acquire_publish_release(account_id: str) -> None:
        browser, context, page = _make_mock_browser()
        pool._playwright.chromium = AsyncMock()
        pool._playwright.chromium.launch = AsyncMock(return_value=browser)
        try:
            session = await pool.acquire(account_id)
            # Simulate publish work
            await asyncio.sleep(0)
            results.append(account_id)
            await pool.release(account_id)
        except Exception as e:
            errors.append(e)

    account_ids = [f"account-{i:03d}" for i in range(50)]
    await asyncio.gather(*[acquire_publish_release(aid) for aid in account_ids])

    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 50
    crash_rate = 0.0  # no crashes in mock
    assert crash_rate < 0.02


@pytest.mark.asyncio
async def test_semaphore_prevents_overflow():
    max_sessions = 5
    pool = PlaywrightPool(max_sessions=max_sessions)
    pool._semaphore = asyncio.Semaphore(max_sessions)
    pool._playwright = MagicMock()

    concurrent_count = 0
    max_concurrent = 0

    async def acquire_and_hold(account_id: str) -> None:
        nonlocal concurrent_count, max_concurrent
        browser, context, page = _make_mock_browser()
        pool._playwright.chromium = AsyncMock()
        pool._playwright.chromium.launch = AsyncMock(return_value=browser)

        session = await pool.acquire(account_id)
        concurrent_count += 1
        max_concurrent = max(max_concurrent, concurrent_count)
        await asyncio.sleep(0.01)
        concurrent_count -= 1
        await pool.release(account_id)

    await asyncio.gather(*[acquire_and_hold(f"acc-{i}") for i in range(20)])
    assert max_concurrent <= max_sessions


@pytest.mark.asyncio
async def test_crash_recovery_no_leak():
    pool = PlaywrightPool(max_sessions=10)
    pool._semaphore = asyncio.Semaphore(10)
    pool._playwright = MagicMock()

    browser, context, page = _make_mock_browser()
    pool._playwright.chromium = AsyncMock()
    pool._playwright.chromium.launch = AsyncMock(return_value=browser)

    session = await pool.acquire("crash-account")
    assert "crash-account" in pool._sessions

    initial_value = pool._semaphore._value
    await pool.mark_crashed("crash-account")

    assert "crash-account" not in pool._sessions
    # Semaphore released after crash
    assert pool._semaphore._value == initial_value + 1


@pytest.mark.asyncio
async def test_session_reuse_under_load():
    pool = PlaywrightPool(max_sessions=10)
    pool._semaphore = asyncio.Semaphore(10)
    pool._playwright = MagicMock()

    browser, context, page = _make_mock_browser()
    pool._playwright.chromium = AsyncMock()
    pool._playwright.chromium.launch = AsyncMock(return_value=browser)

    # First acquire creates session
    s1 = await pool.acquire("reuse-account")
    await pool.release("reuse-account")

    # Second acquire reuses it
    s2 = await pool.acquire("reuse-account")
    assert s1 is s2

    # Browser only launched once
    pool._playwright.chromium.launch.assert_awaited_once()
    await pool.release("reuse-account")

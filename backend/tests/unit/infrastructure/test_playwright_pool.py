import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from infrastructure.browser.playwright_pool import PlaywrightPool


def _make_mock_session(account_id: str):
    browser = AsyncMock()
    context = AsyncMock()
    page = AsyncMock()
    page.on = MagicMock()
    context.new_page = AsyncMock(return_value=page)
    context.add_cookies = AsyncMock()
    browser.new_context = AsyncMock(return_value=context)
    return browser, context, page


@pytest.fixture
def pool():
    return PlaywrightPool(max_sessions=5)


@pytest.fixture
async def started_pool(pool: PlaywrightPool):
    mock_browser, mock_context, mock_page = _make_mock_session("any")

    mock_chromium = AsyncMock()
    mock_chromium.launch = AsyncMock(return_value=mock_browser)
    mock_chromium.launch.side_effect = lambda **kw: _make_mock_session("x")[0]

    mock_playwright = MagicMock()
    mock_playwright.chromium = mock_chromium
    mock_playwright.stop = AsyncMock()

    with patch(
        "infrastructure.browser.playwright_pool.async_playwright",
    ) as mock_ap:
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_playwright)
        mock_cm.__aexit__ = AsyncMock(return_value=False)
        mock_ap.return_value = mock_cm
        # async_playwright() returns context manager
        mock_ap.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_ap.return_value.__aenter__ = AsyncMock(return_value=mock_playwright)

        pool._playwright = mock_playwright
        pool._semaphore = asyncio.Semaphore(5)
        yield pool, mock_playwright, mock_chromium


@pytest.mark.asyncio
async def test_acquire_creates_session(started_pool):
    pool, mock_playwright, mock_chromium = started_pool
    mock_browser, mock_context, mock_page = _make_mock_session("acc1")
    mock_chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.on = MagicMock()

    session = await pool.acquire("acc1")
    assert session.account_id == "acc1"
    assert session.status == "busy"


@pytest.mark.asyncio
async def test_release_marks_idle(started_pool):
    pool, mock_playwright, mock_chromium = started_pool
    mock_browser, mock_context, mock_page = _make_mock_session("acc2")
    mock_chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.on = MagicMock()

    session = await pool.acquire("acc2")
    assert session.status == "busy"

    await pool.release("acc2")
    assert session.status == "idle"


@pytest.mark.asyncio
async def test_acquire_reuses_idle_session(started_pool):
    pool, mock_playwright, mock_chromium = started_pool
    mock_browser, mock_context, mock_page = _make_mock_session("acc3")
    mock_chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.on = MagicMock()

    session1 = await pool.acquire("acc3")
    await pool.release("acc3")
    session2 = await pool.acquire("acc3")

    assert session1 is session2  # same object reused
    mock_chromium.launch.assert_awaited_once()  # only one browser created


@pytest.mark.asyncio
async def test_semaphore_limits_concurrent_sessions():
    pool = PlaywrightPool(max_sessions=2)
    pool._semaphore = asyncio.Semaphore(2)
    pool._playwright = MagicMock()

    results = []

    async def acquire_with_delay(acc: str) -> None:
        mock_browser, mock_context, mock_page = _make_mock_session(acc)
        pool._playwright.chromium = AsyncMock()
        pool._playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_page.on = MagicMock()
        await pool.acquire(acc)
        results.append(acc)

    await asyncio.gather(
        acquire_with_delay("a"),
        acquire_with_delay("b"),
    )
    assert len(results) == 2


@pytest.mark.asyncio
async def test_mark_crashed_removes_session(started_pool):
    pool, mock_playwright, mock_chromium = started_pool
    mock_browser, mock_context, mock_page = _make_mock_session("acc4")
    mock_chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.on = MagicMock()

    await pool.acquire("acc4")
    assert "acc4" in pool._sessions

    await pool.mark_crashed("acc4")
    assert "acc4" not in pool._sessions

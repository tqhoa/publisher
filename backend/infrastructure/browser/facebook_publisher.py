import asyncio

import structlog
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from infrastructure.browser.playwright_pool import PublishError

logger = structlog.get_logger()

_FB_HOME = "https://www.facebook.com"
_POST_BUTTON_SELECTORS = [
    '[aria-label="Create a post"]',
    '[data-pagelet="FeedComposer"] div[role="button"]',
    'div[aria-label="What\'s on your mind"]',
]
_PUBLISH_SELECTORS = [
    'div[aria-label="Post"][role="button"]',
    'button[type="submit"]',
]


async def post_text(page: Page, caption: str) -> str:
    """Post plain text to Facebook. Returns post URL."""
    try:
        await _open_composer(page)
        await _type_caption(page, caption)
        return await _submit_and_get_url(page)
    except PlaywrightTimeout as exc:
        raise PublishError(f"Facebook post_text timed out: {exc}") from exc
    except Exception as exc:
        raise PublishError(f"Facebook post_text failed: {exc}") from exc


async def post_image(page: Page, caption: str, image_paths: list[str]) -> str:
    """Post text + image(s) to Facebook. Returns post URL."""
    try:
        await _open_composer(page)
        await _attach_media(page, image_paths, media_type="photo")
        await _type_caption(page, caption)
        return await _submit_and_get_url(page)
    except PlaywrightTimeout as exc:
        raise PublishError(f"Facebook post_image timed out: {exc}") from exc
    except Exception as exc:
        raise PublishError(f"Facebook post_image failed: {exc}") from exc


async def post_video(page: Page, caption: str, video_path: str) -> str:
    """Post video to Facebook. Returns post URL. Waits up to 60s for upload."""
    try:
        await _open_composer(page)
        await _attach_media(page, [video_path], media_type="video")
        await _type_caption(page, caption)
        return await _submit_and_get_url(page, upload_timeout=60_000)
    except PlaywrightTimeout as exc:
        raise PublishError(f"Facebook post_video timed out: {exc}") from exc
    except Exception as exc:
        raise PublishError(f"Facebook post_video failed: {exc}") from exc


async def _open_composer(page: Page) -> None:
    await page.goto(_FB_HOME, wait_until="domcontentloaded", timeout=30_000)
    for selector in _POST_BUTTON_SELECTORS:
        btn = page.locator(selector).first
        if await btn.count() > 0:
            await btn.click()
            await page.wait_for_timeout(1000)
            return
    raise PublishError("Could not find Facebook post composer button")


async def _type_caption(page: Page, caption: str) -> None:
    composer_input = page.locator('[contenteditable="true"]').first
    await composer_input.wait_for(state="visible", timeout=10_000)
    await composer_input.click()
    await composer_input.fill(caption)


async def _attach_media(page: Page, file_paths: list[str], media_type: str) -> None:
    photo_video_btn = page.locator(
        '[aria-label="Photo/video"], [aria-label="Photo"], [aria-label="Add Photos/Videos"]'
    ).first
    if await photo_video_btn.count() > 0:
        await photo_video_btn.click()
        await page.wait_for_timeout(500)

    file_input = page.locator('input[type="file"]').first
    await file_input.set_input_files(file_paths)
    if media_type == "video":
        # Wait for video processing indicator to disappear
        await page.wait_for_function(
            "() => !document.querySelector('[data-visualcompletion=\"loading-state\"]')",
            timeout=60_000,
        )
    else:
        await page.wait_for_timeout(2000)


async def _submit_and_get_url(page: Page, upload_timeout: int = 10_000) -> str:
    for selector in _PUBLISH_SELECTORS:
        btn = page.locator(selector).first
        if await btn.count() > 0:
            await btn.click()
            break
    else:
        raise PublishError("Could not find Facebook Post submit button")

    # Wait for navigation back to feed or post permalink
    try:
        await page.wait_for_url(
            lambda url: "facebook.com" in url and "/posts/" in url,
            timeout=upload_timeout,
        )
        return page.url
    except PlaywrightTimeout:
        return _FB_HOME

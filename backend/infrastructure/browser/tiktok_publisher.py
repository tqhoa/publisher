import structlog
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from infrastructure.browser.playwright_pool import PublishError

logger = structlog.get_logger()

_TIKTOK_UPLOAD = "https://www.tiktok.com/creator-center/upload"


async def upload_video(
    page: Page,
    caption: str,
    hashtags: list[str],
    video_path: str,
) -> str:
    """Upload video to TikTok. Returns TikTok post URL."""
    try:
        await page.goto(_TIKTOK_UPLOAD, wait_until="domcontentloaded", timeout=30_000)
        await _upload_file(page, video_path)
        await _fill_caption(page, caption, hashtags)
        return await _submit(page)
    except PlaywrightTimeout as exc:
        raise PublishError(f"TikTok upload_video timed out: {exc}") from exc
    except PublishError:
        raise
    except Exception as exc:
        raise PublishError(f"TikTok upload_video failed: {exc}") from exc


async def _upload_file(page: Page, video_path: str) -> None:
    file_input = page.locator('input[type="file"][accept*="video"]').first
    await file_input.wait_for(state="attached", timeout=15_000)
    await file_input.set_input_files(video_path)

    # Wait for upload progress to complete (up to 120s)
    await page.wait_for_function(
        """() => {
            const progress = document.querySelector('[class*="upload-progress"], [class*="UploadProgress"]');
            return !progress || progress.style.display === 'none';
        }""",
        timeout=120_000,
    )
    logger.info("tiktok_upload_complete", video_path=video_path)


async def _fill_caption(page: Page, caption: str, hashtags: list[str]) -> None:
    hashtag_str = " ".join(f"#{tag.lstrip('#')}" for tag in hashtags) if hashtags else ""
    full_caption = f"{caption} {hashtag_str}".strip()

    caption_input = page.locator(
        '[class*="caption-input"], [class*="CaptionInput"], [contenteditable="true"]'
    ).first
    await caption_input.wait_for(state="visible", timeout=10_000)
    await caption_input.click()
    await caption_input.fill(full_caption)


async def _submit(page: Page) -> str:
    post_btn = page.locator(
        'button[class*="btn-post"], button[class*="BtnPost"], button:has-text("Post")'
    ).first
    await post_btn.wait_for(state="visible", timeout=10_000)
    await post_btn.click()

    try:
        await page.wait_for_url(
            lambda url: "tiktok.com" in url and "/video/" in url,
            timeout=30_000,
        )
        return page.url
    except PlaywrightTimeout:
        return _TIKTOK_UPLOAD

import asyncio

import structlog

from infrastructure.queue.celery_app import celery_app

logger = structlog.get_logger()


def _run(coro):  # type: ignore[no-untyped-def]
    """Run async coroutine from sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, name="publish_post")
def publish_post(self, post_id: str) -> dict:  # type: ignore[type-arg]
    return _run(_publish_post_async(self, post_id))


async def _publish_post_async(task, post_id: str) -> dict:  # type: ignore[type-arg]
    from infrastructure.database.session import AsyncSessionLocal
    from infrastructure.encryption.cookie_cipher import decrypt
    from infrastructure.browser.playwright_pool import get_pool, PublishError

    async with AsyncSessionLocal() as db:
        from domain.repositories.post_repository import PostRepository
        from domain.repositories.account_repository import AccountRepository

        post_repo = PostRepository(db)
        account_repo = AccountRepository(db)

        post = await post_repo.find_by_id(post_id)
        if not post:
            logger.error("publish_post_not_found", post_id=post_id)
            return {"post_id": post_id, "status": "not_found"}

        account = await account_repo.find_by_id(post.account_id)
        if not account or not account.cookie_encrypted:
            await post_repo.update(post, status="failed", error_message="Account cookie missing")
            await db.commit()
            return {"post_id": post_id, "status": "failed"}

        cookie_json = decrypt(account.cookie_encrypted)

        await post_repo.update(post, status="publishing")
        await db.commit()

    pool = get_pool()
    session = await pool.acquire(post.account_id, cookie_json)
    try:
        post_url = await _dispatch_publish(session.page, post, account)

        async with AsyncSessionLocal() as db:
            from domain.repositories.post_repository import PostRepository
            from datetime import datetime, timezone
            repo = PostRepository(db)
            p = await repo.find_by_id(post_id)
            if p:
                await repo.update(
                    p,
                    status="published",
                    published_at=datetime.now(timezone.utc),
                    error_message=None,
                )
            await db.commit()

        logger.info("publish_success", post_id=post_id, url=post_url)
        return {"post_id": post_id, "status": "published", "url": post_url}

    except Exception as exc:
        error_msg = str(exc)
        logger.error("publish_failed", post_id=post_id, error=error_msg)

        async with AsyncSessionLocal() as db:
            from domain.repositories.post_repository import PostRepository
            repo = PostRepository(db)
            p = await repo.find_by_id(post_id)
            if p:
                await repo.update(p, status="failed", error_message=error_msg)
            await db.commit()

        countdown = 60 * (2 ** task.request.retries)
        raise task.retry(exc=exc, countdown=countdown)

    finally:
        await pool.release(post.account_id)


async def _dispatch_publish(page, post, account) -> str:  # type: ignore[no-untyped-def]
    from infrastructure.browser.facebook_publisher import post_text, post_image, post_video
    from infrastructure.browser.tiktok_publisher import upload_video

    platform = post.platform
    caption = post.caption or ""
    hashtags = post.hashtags or []
    media_urls = post.media_urls or []

    if platform == "facebook":
        if post.content_type == "text":
            return await post_text(page, caption)
        elif post.content_type == "image":
            return await post_image(page, caption, media_urls)
        elif post.content_type in ("video", "mixed"):
            return await post_video(page, caption, media_urls[0] if media_urls else "")
        else:
            return await post_text(page, caption)

    elif platform == "tiktok":
        video_path = media_urls[0] if media_urls else ""
        return await upload_video(page, caption, hashtags, video_path)

    else:
        raise ValueError(f"Unsupported platform: {platform}")

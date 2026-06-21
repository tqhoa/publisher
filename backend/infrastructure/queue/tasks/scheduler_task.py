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


@celery_app.task(name="enqueue_due_posts")
def enqueue_due_posts() -> dict:  # type: ignore[type-arg]
    return _run(_enqueue_due_posts_async())


async def _enqueue_due_posts_async() -> dict:  # type: ignore[type-arg]
    from infrastructure.database.session import AsyncSessionLocal
    from domain.repositories.post_repository import PostRepository
    from infrastructure.queue.tasks.publish_task import publish_post

    now = datetime.now(timezone.utc)
    enqueued = 0

    async with AsyncSessionLocal() as db:
        repo = PostRepository(db)
        due_posts = await repo.find_due_scheduled(now)
        for post in due_posts:
            await repo.update(post, status="queued")
            publish_post.delay(post.id)
            enqueued += 1
        await db.commit()

    logger.info("scheduler_enqueued", count=enqueued)
    return {"enqueued": enqueued}


# Beat schedule registered in celery_app.py

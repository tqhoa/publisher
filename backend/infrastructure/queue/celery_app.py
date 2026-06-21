from celery import Celery
from shared.config import settings

celery_app = Celery(
    "publisher",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "infrastructure.queue.tasks.publish_task",
        "infrastructure.queue.tasks.scheduler_task",
        "infrastructure.queue.tasks.health_check_task",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "enqueue-due-posts-every-30s": {
            "task": "enqueue_due_posts",
            "schedule": 30.0,
        },
        "check-all-cookies-every-5min": {
            "task": "check_all_cookies",
            "schedule": 300.0,
        },
    },
)

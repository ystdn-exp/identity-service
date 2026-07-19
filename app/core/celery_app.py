from datetime import timedelta

from celery import Celery

from app.core.settings import settings

celery_app = Celery(
    "identity_service",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.modules.users.tasks.cleanup",
        "app.modules.users.tasks.email_verification",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "cleanup_unverified_users": {
            "task": "app.modules.users.tasks.cleanup.cleanup_unverified_users",
            "schedule": timedelta(days=1, hours=0, minutes=0, seconds=0),
        },
    },
)

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.core.celery_app import celery_app
from app.core.database.connection import SyncSessionLocal
from app.modules.users.models import User


@celery_app.task(name="app.modules.users.tasks.cleanup.cleanup_unverified_users")
def cleanup_unverified_users() -> int:
    """
    Delete users who have remained unverified (is_verified=False) for
    2 or more days since last_verified_at.
    """
    threshold = datetime.now(timezone.utc) - timedelta(days=2)

    with SyncSessionLocal() as db:
        result = db.execute(
            delete(User)
            .where(User.is_verified == False, User.last_verified_at <= threshold)
            .returning(User.id)
        )
        deleted_ids = result.scalars().all()
        db.commit()

    return len(deleted_ids)

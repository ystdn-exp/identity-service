import sentry_sdk

from app.core.settings import settings


def init_sentry():
    """
    Setup sentry monitoring.
    """
    sentry_sdk.init(dsn=settings.sentry_dsn, enable_tracing=True)

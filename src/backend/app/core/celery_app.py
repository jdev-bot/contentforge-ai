"""
Celery application configuration for background tasks.
"""
import logging
from celery import Celery
from celery.signals import task_failure, task_success
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "contentforge",
    broker=settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else "redis://localhost:6379/0",
    backend=settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else "redis://localhost:6379/0",
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Rate limiting
    task_rate_limit="10/m",  # Default: 10 tasks per minute
    # Retry configuration
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    # Result backend settings
    result_expires=3600,  # 1 hour
    # Queue configuration
    task_routes={
        "app.tasks.email.*": {"queue": "email"},
        "app.tasks.analytics.*": {"queue": "analytics"},
        "app.tasks.webhooks.*": {"queue": "webhooks"},
        "app.tasks.rss.*": {"queue": "rss"},
        "app.tasks.audience.*": {"queue": "analytics"},
        "app.tasks.trends.*": {"queue": "trends"},
    },
    # Beat schedule for periodic tasks
    beat_schedule={
        "weekly-digest": {
            "task": "app.tasks.email.send_weekly_digests",
            "schedule": 604800.0,  # Weekly
        },
        "process-scheduled-posts": {
            "task": "app.services.scheduler_service.process_scheduled_posts",
            "schedule": 60.0,  # Every minute
        },
        "retry-failed-posts": {
            "task": "app.services.scheduler_service.retry_failed_posts",
            "schedule": 300.0,  # Every 5 minutes
        },
        "fetch-rss-feeds-hourly": {
            "task": "app.tasks.rss.fetch_rss_feeds_task",
            "schedule": 3600.0,  # Every hour
        },
        "cleanup-old-rss-entries-daily": {
            "task": "app.tasks.rss.cleanup_old_rss_entries_task",
            "schedule": 86400.0,  # Every 24 hours
            "kwargs": {"days": 30},
        },
        "retry-failed-feeds-hourly": {
            "task": "app.tasks.rss.retry_failed_feeds_task",
            "schedule": 3600.0,  # Every hour
        },
        "calculate-growth-metrics-daily": {
            "task": "app.tasks.audience.calculate_growth_metrics",
            "schedule": 86400.0,  # Every 24 hours
        },
        "cleanup-old-audience-metrics-monthly": {
            "task": "app.tasks.audience.cleanup_old_audience_metrics",
            "schedule": 2592000.0,  # Every 30 days
            "kwargs": {"days": 365},
        },
        # Trending topics tasks
        "update-trending-topics-hourly": {
            "task": "app.tasks.trends.update_trending_topics_task",
            "schedule": 3600.0,  # Every hour
        },
        "cleanup-expired-trends-daily": {
            "task": "app.tasks.trends.cleanup_expired_trends_task",
            "schedule": 86400.0,  # Every 24 hours
        },
        "generate-trend-suggestions-hourly": {
            "task": "app.tasks.trends.generate_trend_content_suggestions_task",
            "schedule": 3600.0,  # Every hour
        },
        "notify-users-relevant-trends-daily": {
            "task": "app.tasks.trends.notify_users_of_relevant_trends_task",
            "schedule": 86400.0,  # Every 24 hours
        },
    },
)


@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, **kw):
    """Log task failures."""
    logger.error(f"Task {sender.name}[{task_id}] failed: {exception}")


@task_success.connect
def handle_task_success(sender=None, result=None, **kwargs):
    """Log task success."""
    logger.info(f"Task {sender.name} completed successfully")


def init_celery():
    """Initialize Celery with app context."""
    from app.main import app
    celery_app.conf.update(app.state.config if hasattr(app.state, 'config') else {})
    return celery_app

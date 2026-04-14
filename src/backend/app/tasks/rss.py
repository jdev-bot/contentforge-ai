"""
Celery tasks for RSS feed fetching and processing.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from app.core.celery_app import celery_app
from app.core.supabase import get_supabase_admin_client
from app.services.rss_service import rss_service

logger = logging.getLogger(__name__)


class RSSTaskError(Exception):
    """Custom exception for RSS task errors."""

    pass


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=1800,  # Max 30 minutes between retries
    retry_jitter=True,
    queue="rss",
)
def fetch_rss_feeds_task(self):
    """
    Fetch all active RSS feeds that are due for fetching.
    Runs every hour via Celery Beat schedule.
    """
    logger.info("Starting scheduled RSS feed fetch task")

    try:
        # Use async function via asyncio
        import asyncio

        result = asyncio.run(rss_service.fetch_all_active_feeds())

        total_feeds = result.get("total_feeds", 0)
        processed = result.get("processed", 0)

        logger.info(
            f"RSS fetch task completed: {processed}/{total_feeds} feeds processed"
        )

        return {
            "status": "success",
            "total_feeds": total_feeds,
            "processed": processed,
            "results": result.get("results", []),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"RSS fetch task failed: {e}")

        # Retry with exponential backoff
        try:
            self.retry(countdown=300 * (2**self.request.retries))
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for RSS fetch task")
            raise RSSTaskError(
                f"Failed to fetch RSS feeds after {self.max_retries} retries"
            )


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    queue="rss",
)
def fetch_single_feed_task(self, feed_id: str, user_id: str):
    """
    Fetch a single RSS feed.

    Args:
        feed_id: The RSS feed ID to fetch
        user_id: The user ID who owns the feed
    """
    logger.info(f"Fetching single RSS feed: {feed_id}")

    try:
        import asyncio

        result = asyncio.run(rss_service.fetch_feed(feed_id, user_id))

        logger.info(f"Feed {feed_id} fetch result: {result}")

        return {
            "status": "success" if result.get("success") else "failed",
            "feed_id": feed_id,
            "entries_fetched": result.get("entries_fetched", 0),
            "entries_new": result.get("entries_new", 0),
            "message": result.get("message", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to fetch feed {feed_id}: {e}")

        try:
            self.retry(countdown=60 * (2**self.request.retries))
        except MaxRetriesExceededError:
            raise RSSTaskError(f"Failed to fetch feed {feed_id} after retries")


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    queue="rss",
)
def process_rss_entry_task(
    self, entry_id: str, user_id: str, project_id: Optional[str] = None
):
    """
    Process a single RSS entry and create content from it.

    Args:
        entry_id: The RSS entry ID to process
        user_id: The user ID who owns the entry
        project_id: Optional project ID to associate with
    """
    logger.info(f"Processing RSS entry: {entry_id}")

    try:
        import asyncio

        result = asyncio.run(
            rss_service.import_entry(
                entry_id=entry_id, user_id=user_id, project_id=project_id
            )
        )

        logger.info(f"Entry {entry_id} processing result: {result}")

        return {
            "status": "success" if result.get("success") else "failed",
            "entry_id": entry_id,
            "content_id": result.get("content_id"),
            "message": result.get("message", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to process RSS entry {entry_id}: {e}")

        try:
            self.retry(countdown=60 * (2**self.request.retries))
        except MaxRetriesExceededError:
            raise RSSTaskError(f"Failed to process RSS entry {entry_id} after retries")


@celery_app.task(
    queue="rss",
)
def cleanup_old_rss_entries_task(days: int = 30):
    """
    Clean up old processed RSS entries to prevent table bloat.

    Args:
        days: Delete entries older than this many days (default: 30)
    """
    logger.info(f"Starting cleanup of RSS entries older than {days} days")

    try:
        supabase = get_supabase_admin_client()

        # Calculate cutoff date
        from datetime import timedelta

        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        # Delete old processed entries
        result = (
            supabase.table("rss_entries")
            .delete()
            .lt("created_at", cutoff_date)
            .eq("processed", True)
            .execute()
        )

        logger.info(f"Cleaned up old RSS entries: {result.count} deleted")

        return {
            "status": "success",
            "deleted_count": result.count or 0,
            "cutoff_date": cutoff_date,
        }

    except Exception as e:
        logger.error(f"Failed to cleanup old RSS entries: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


@celery_app.task(
    queue="rss",
)
def retry_failed_feeds_task():
    """
    Retry fetching feeds that are in error status.
    """
    logger.info("Starting retry of failed RSS feeds")

    try:
        supabase = get_supabase_admin_client()

        # Get feeds in error status
        feeds_result = (
            supabase.table("rss_feeds")
            .select("id, user_id")
            .eq("status", "error")
            .execute()
        )

        if not feeds_result.data:
            return {
                "status": "success",
                "feeds_to_retry": 0,
                "message": "No failed feeds to retry",
            }

        feeds = feeds_result.data
        retried = 0

        for feed in feeds:
            try:
                # Queue fetch task
                fetch_single_feed_task.delay(feed["id"], feed["user_id"])
                retried += 1
            except Exception as e:
                logger.error(f"Failed to queue retry for feed {feed['id']}: {e}")
                continue

        return {
            "status": "success",
            "feeds_to_retry": len(feeds),
            "retried": retried,
        }

    except Exception as e:
        logger.error(f"Failed to retry failed feeds: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


# Convenience function for Celery Beat scheduling
def schedule_rss_tasks(celery_app):
    """
    Add RSS tasks to Celery Beat schedule.
    Call this from celery_app.py to register the beat schedule.
    """
    celery_app.conf.beat_schedule.update(
        {
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
        }
    )

    # Add RSS queue if not already present
    if "rss" not in celery_app.conf.task_queues:
        from kombu import Queue

        celery_app.conf.task_queues = celery_app.conf.task_queues or []
        celery_app.conf.task_queues.append(Queue("rss", routing_key="rss.#"))

    # Add RSS task routes
    celery_app.conf.task_routes.update(
        {
            "app.tasks.rss.*": {"queue": "rss"},
        }
    )

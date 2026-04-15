"""
Scheduler service for automated content publishing.
Handles timezone-aware scheduling, retry logic, and Celery beat integration.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

import pytz
from celery import Task
from pydantic import BaseModel, ConfigDict

from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.core.supabase import get_supabase_admin_client, get_supabase_client

settings = get_settings()
logger = logging.getLogger(__name__)


class ScheduleRequest(BaseModel):
    """Request model for scheduling a post."""

    model_config = ConfigDict(from_attributes=True)
    content_id: str
    asset_id: Optional[str] = None
    platform: str
    scheduled_at: datetime
    asset_type: str = "post"
    settings: Dict[str, Any] = {}
    timezone: str = "UTC"


class ScheduleUpdateRequest(BaseModel):
    """Request model for updating a scheduled post."""

    model_config = ConfigDict(from_attributes=True)
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None


class ScheduledPostResponse(BaseModel):
    """Response model for scheduled post."""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: str
    user_id: str
    content_id: str
    asset_id: Optional[str] = None
    platform: str
    scheduled_at: datetime
    status: str
    asset_type: str
    settings: Dict[str, Any]
    content: Optional[str] = None
    retry_count: int
    max_retries: int
    timezone: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    external_id: Optional[str] = None
    published_url: Optional[str] = None


class SchedulerService:
    """Service for managing scheduled content publishing."""

    def __init__(self):
        self._supabase = None

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_admin_client()
        return self._supabase

    @supabase.setter
    def supabase(self, value):
        self._supabase = value

    def schedule_post(
        self, user_id: str, request: ScheduleRequest, content: Optional[str] = None
    ) -> ScheduledPostResponse:
        """Schedule a new post for automated publishing."""
        try:
            # Validate and convert scheduled time to UTC
            scheduled_at_utc = self._to_utc(request.scheduled_at, request.timezone)

            # Ensure scheduled time is in the future
            if scheduled_at_utc <= datetime.now(timezone.utc):
                raise ValueError("Scheduled time must be in the future")

            data = {
                "user_id": user_id,
                "content_id": request.content_id,
                "asset_id": request.asset_id,
                "platform": request.platform,
                "scheduled_at": scheduled_at_utc.isoformat(),
                "status": "pending",
                "asset_type": request.asset_type,
                "settings": request.settings,
                "content": content,
                "timezone": request.timezone,
                "retry_count": 0,
                "max_retries": 3,
            }

            result = self.supabase.table("scheduled_posts").insert(data).execute()

            if not result.data:
                raise RuntimeError("Failed to create scheduled post")

            return ScheduledPostResponse(**result.data[0])

        except Exception as e:
            logger.error(f"Failed to schedule post: {e}")
            raise

    def get_scheduled_posts(
        self,
        user_id: str,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ScheduledPostResponse]:
        """Get scheduled posts for a user with optional filtering."""
        try:
            query = (
                self.supabase.table("scheduled_posts")
                .select("*")
                .eq("user_id", user_id)
            )

            if status:
                query = query.eq("status", status)

            if platform:
                query = query.eq("platform", platform)

            query = query.order("scheduled_at", desc=True).limit(limit).offset(offset)
            result = query.execute()

            if result.data:
                if isinstance(result.data, list):
                    return [ScheduledPostResponse(**item) for item in result.data]
                else:
                    return [ScheduledPostResponse(**result.data)]
            return []

        except Exception as e:
            logger.error(f"Failed to get scheduled posts: {e}")
            raise

    def get_scheduled_post(
        self, user_id: str, post_id: str
    ) -> Optional[ScheduledPostResponse]:
        """Get a specific scheduled post."""
        try:
            result = (
                self.supabase.table("scheduled_posts")
                .select("*")
                .eq("id", post_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            # Handle both list and dict return types from Supabase
            if result.data:
                data = result.data[0] if isinstance(result.data, list) else result.data
                return ScheduledPostResponse(**data)
            return None

        except Exception as e:
            logger.error(f"Failed to get scheduled post: {e}")
            return None

    def update_scheduled_post(
        self, user_id: str, post_id: str, request: ScheduleUpdateRequest
    ) -> Optional[ScheduledPostResponse]:
        """Update a scheduled post."""
        try:
            # Get current post
            current = self.get_scheduled_post(user_id, post_id)
            if not current:
                return None

            # Cannot update already published or cancelled posts
            if current.status in ["published", "cancelled"]:
                raise ValueError(f"Cannot update post with status: {current.status}")

            update_data = {}

            if request.scheduled_at is not None:
                tz_name = request.timezone or current.timezone
                scheduled_at_utc = self._to_utc(request.scheduled_at, tz_name)

                if scheduled_at_utc <= datetime.now(timezone.utc):
                    raise ValueError("Scheduled time must be in the future")

                update_data["scheduled_at"] = scheduled_at_utc.isoformat()

            if request.status is not None:
                update_data["status"] = request.status

            if request.settings is not None:
                update_data["settings"] = request.settings

            if request.timezone is not None:
                update_data["timezone"] = request.timezone

            if not update_data:
                return current

            result = (
                self.supabase.table("scheduled_posts")
                .update(update_data)
                .eq("id", post_id)
                .eq("user_id", user_id)
                .execute()
            )

            return ScheduledPostResponse(**result.data[0]) if result.data else None

        except Exception as e:
            logger.error(f"Failed to update scheduled post: {e}")
            raise

    def cancel_scheduled_post(self, user_id: str, post_id: str) -> bool:
        """Cancel a scheduled post."""
        try:
            current = self.get_scheduled_post(user_id, post_id)
            if not current:
                return False

            # Cannot cancel already published posts
            if current.status == "published":
                raise ValueError("Cannot cancel already published post")

            result = (
                self.supabase.table("scheduled_posts")
                .update({"status": "cancelled"})
                .eq("id", post_id)
                .eq("user_id", user_id)
                .execute()
            )

            return bool(result.data)

        except Exception as e:
            logger.error(f"Failed to cancel scheduled post: {e}")
            raise

    def publish_now(
        self, user_id: str, post_id: str
    ) -> Optional[ScheduledPostResponse]:
        """Immediately publish a scheduled post."""
        try:
            current = self.get_scheduled_post(user_id, post_id)
            if not current:
                return None

            if current.status in ["published", "cancelled"]:
                raise ValueError(f"Cannot publish post with status: {current.status}")

            # Update to trigger immediate processing
            result = (
                self.supabase.table("scheduled_posts")
                .update(
                    {
                        "scheduled_at": datetime.now(timezone.utc).isoformat(),
                        "status": "pending",
                    }
                )
                .eq("id", post_id)
                .eq("user_id", user_id)
                .execute()
            )

            # Trigger immediate publish task
            if result.data:
                publish_scheduled_post.delay(post_id)
                return ScheduledPostResponse(**result.data[0])

            return None

        except Exception as e:
            logger.error(f"Failed to publish post now: {e}")
            raise

    def get_pending_posts_due(
        self, batch_size: int = 100
    ) -> List[ScheduledPostResponse]:
        """Get pending posts that are due for publishing."""
        try:
            now = datetime.now(timezone.utc).isoformat()

            result = (
                self.supabase.table("scheduled_posts")
                .select("*")
                .eq("status", "pending")
                .lte("scheduled_at", now)
                .limit(batch_size)
                .execute()
            )

            return (
                [ScheduledPostResponse(**item) for item in result.data]
                if result.data
                else []
            )

        except Exception as e:
            logger.error(f"Failed to get pending posts: {e}")
            return []

    def get_failed_posts_for_retry(
        self, batch_size: int = 50
    ) -> List[ScheduledPostResponse]:
        """Get failed posts eligible for retry."""
        try:
            result = (
                self.supabase.table("scheduled_posts")
                .select("*")
                .eq("status", "failed")
                .lt("retry_count", 3)
                .limit(batch_size)
                .execute()
            )

            return (
                [ScheduledPostResponse(**item) for item in result.data]
                if result.data
                else []
            )

        except Exception as e:
            logger.error(f"Failed to get retry posts: {e}")
            return []

    def _to_utc(self, dt: datetime, tz_name: str) -> datetime:
        """Convert datetime to UTC."""
        try:
            tz = pytz.timezone(tz_name)
            if dt.tzinfo is None:
                dt = tz.localize(dt)
            return dt.astimezone(pytz.UTC)
        except pytz.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone {tz_name}, defaulting to UTC")
            return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)

    def get_scheduler_stats(self, user_id: str) -> Dict[str, Any]:
        """Get scheduler statistics for a user."""
        try:
            # Count by status
            statuses = ["pending", "processing", "published", "failed", "cancelled"]
            stats = {}

            for status in statuses:
                result = (
                    self.supabase.table("scheduled_posts")
                    .select("id", count="exact")
                    .eq("user_id", user_id)
                    .eq("status", status)
                    .execute()
                )
                stats[status] = result.count if hasattr(result, "count") else 0

            # Get upcoming posts (next 24 hours)
            tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
            upcoming = (
                self.supabase.table("scheduled_posts")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("status", "pending")
                .lte("scheduled_at", tomorrow)
                .execute()
            )
            stats["upcoming_24h"] = upcoming.count if hasattr(upcoming, "count") else 0

            return stats

        except Exception as e:
            logger.error(f"Failed to get scheduler stats: {e}")
            return {}


# Create service instance
scheduler_service = SchedulerService()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def publish_scheduled_post(self: Task, post_id: str) -> Dict[str, Any]:
    """Celery task to publish a scheduled post."""
    try:
        supabase = get_supabase_admin_client()

        # Get post details
        result = (
            supabase.table("scheduled_posts")
            .select("*")
            .eq("id", post_id)
            .single()
            .execute()
        )

        if not result.data:
            logger.error(f"Scheduled post {post_id} not found")
            return {"status": "error", "message": "Post not found"}

        post = result.data

        # Check if already processed
        if post["status"] in ["published", "cancelled"]:
            return {"status": "skipped", "message": f"Post already {post['status']}"}

        # Mark as processing
        supabase.table("scheduled_posts").update({"status": "processing"}).eq(
            "id", post_id
        ).execute()

        # Here you would integrate with actual platform APIs
        # For now, we simulate successful publishing
        # TODO: Integrate with platform-specific distribution service

        # Simulate platform publishing
        platform = post["platform"]
        content = post.get("content", "")

        # Mock successful publish
        external_id = f"{platform}_{post_id[:8]}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        published_url = f"https://{platform}.com/post/{external_id}"

        # Update as published
        supabase.table("scheduled_posts").update(
            {
                "status": "published",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "external_id": external_id,
                "published_url": published_url,
                "error_message": None,
            }
        ).eq("id", post_id).execute()

        logger.info(f"Successfully published scheduled post {post_id} to {platform}")

        return {
            "status": "success",
            "post_id": post_id,
            "platform": platform,
            "external_id": external_id,
            "published_url": published_url,
        }

    except Exception as e:
        logger.error(f"Failed to publish scheduled post {post_id}: {e}")

        # Mark as failed with retry
        try:
            supabase = get_supabase_admin_client()
            current = (
                supabase.table("scheduled_posts")
                .select("retry_count")
                .eq("id", post_id)
                .single()
                .execute()
            )

            if current.data:
                new_retry_count = current.data["retry_count"] + 1
                update_data = {
                    "status": "failed",
                    "retry_count": new_retry_count,
                    "error_message": str(e)[:500],  # Limit error message length
                }
                supabase.table("scheduled_posts").update(update_data).eq(
                    "id", post_id
                ).execute()

                # Retry if under max retries
                if new_retry_count < 3:
                    logger.info(
                        f"Retrying post {post_id} (attempt {new_retry_count}/3)"
                    )
                    raise self.retry(
                        exc=e, countdown=60 * new_retry_count
                    )  # Exponential backoff

        except Exception as update_error:
            logger.error(f"Failed to update error status: {update_error}")

        return {"status": "error", "message": str(e)}


@celery_app.task
def process_scheduled_posts() -> Dict[str, Any]:
    """Celery beat task to process all due scheduled posts."""
    try:
        service = SchedulerService()
        due_posts = service.get_pending_posts_due(batch_size=100)

        if not due_posts:
            return {"status": "success", "processed": 0, "message": "No posts due"}

        # Queue publish tasks
        task_ids = []
        for post in due_posts:
            task = publish_scheduled_post.delay(post.id)
            task_ids.append({"post_id": post.id, "task_id": task.id})

        logger.info(f"Queued {len(task_ids)} scheduled posts for publishing")

        return {"status": "success", "processed": len(task_ids), "tasks": task_ids}

    except Exception as e:
        logger.error(f"Failed to process scheduled posts: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task
def retry_failed_posts() -> Dict[str, Any]:
    """Celery beat task to retry failed posts."""
    try:
        service = SchedulerService()
        failed_posts = service.get_failed_posts_for_retry(batch_size=50)

        if not failed_posts:
            return {
                "status": "success",
                "retried": 0,
                "message": "No failed posts to retry",
            }

        # Reset status to pending for retry
        task_ids = []
        for post in failed_posts:
            # Reset to pending
            service.supabase.table("scheduled_posts").update(
                {"status": "pending", "error_message": None}
            ).eq("id", post.id).execute()

            # Re-queue for immediate processing if due
            scheduled = post.scheduled_at
            if scheduled.tzinfo is None:
                scheduled = scheduled.replace(tzinfo=timezone.utc)
            if scheduled <= datetime.now(timezone.utc):
                task = publish_scheduled_post.delay(post.id)
                task_ids.append({"post_id": post.id, "task_id": task.id})

        logger.info(f"Queued {len(task_ids)} failed posts for retry")

        return {"status": "success", "retried": len(task_ids), "tasks": task_ids}

    except Exception as e:
        logger.error(f"Failed to retry posts: {e}")
        return {"status": "error", "message": str(e)}

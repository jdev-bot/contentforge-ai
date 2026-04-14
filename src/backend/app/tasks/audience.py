"""
Celery tasks for audience growth metrics.
"""
import logging
from celery import shared_task
from datetime import datetime, timedelta, timezone

from app.services.audience_service import audience_service
from app.core.supabase import get_supabase_admin_client

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def calculate_growth_metrics(self):
    """
    Calculate growth metrics for all users.
    
    This task should be run daily to compute growth snapshots
    for all active users.
    """
    logger.info("Starting daily growth metrics calculation")
    
    try:
        # Get all active users with audience metrics
        supabase = get_supabase_admin_client()
        
        # Get distinct user IDs from recent audience metrics
        result = supabase.table("audience_metrics")\
            .select("user_id")\
            .gte("recorded_at", (datetime.now(timezone.utc) - timedelta(days=30)).isoformat())\
            .execute()
        
        user_ids = list(set(row.get("user_id") for row in result.data or []))
        
        logger.info(f"Processing growth metrics for {len(user_ids)} users")
        
        processed = 0
        failed = 0
        
        for user_id in user_ids:
            try:
                # Calculate and store growth snapshot
                audience_service.calculate_growth_snapshot(user_id)
                processed += 1
                
                # Log progress every 10 users
                if processed % 10 == 0:
                    logger.info(f"Processed {processed}/{len(user_ids)} users")
                    
            except Exception as e:
                logger.error(f"Failed to calculate metrics for user {user_id}: {e}")
                failed += 1
        
        logger.info(f"Growth metrics calculation complete. Processed: {processed}, Failed: {failed}")
        return {
            "success": True,
            "processed": processed,
            "failed": failed,
            "total_users": len(user_ids)
        }
        
    except Exception as e:
        logger.error(f"Growth metrics calculation failed: {e}")
        # Retry with exponential backoff
        self.retry(countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def calculate_user_growth_metrics(self, user_id: str):
    """
    Calculate growth metrics for a specific user.
    
    Args:
        user_id: The user ID to calculate metrics for
    """
    logger.info(f"Calculating growth metrics for user {user_id}")
    
    try:
        snapshot = audience_service.calculate_growth_snapshot(user_id)
        logger.info(f"Successfully calculated metrics for user {user_id}")
        return {
            "success": True,
            "user_id": user_id,
            "snapshot": snapshot
        }
    except Exception as e:
        logger.error(f"Failed to calculate metrics for user {user_id}: {e}")
        self.retry(countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=2)
def process_platform_webhook(self, platform: str, payload: dict):
    """
    Process a webhook payload from a social platform.
    
    Args:
        platform: The social platform name
        payload: The webhook payload data
    """
    logger.info(f"Processing {platform} webhook: {payload}")
    
    try:
        user_id = payload.get("user_id")
        metric_type = payload.get("metric_type")
        value = payload.get("value")
        
        if not all([user_id, metric_type, value is not None]):
            raise ValueError("Missing required fields in webhook payload")
        
        recorded = audience_service.record_metric(
            user_id=user_id,
            platform=platform.lower(),
            metric_type=metric_type,
            value=value,
            period="daily"
        )
        
        logger.info(f"Recorded {platform} {metric_type} for user {user_id}")
        return {
            "success": True,
            "platform": platform,
            "recorded": recorded
        }
        
    except Exception as e:
        logger.error(f"Failed to process {platform} webhook: {e}")
        self.retry(countdown=30 * (2 ** self.request.retries))


@shared_task
def cleanup_old_audience_metrics(days: int = 365):
    """
    Clean up old audience metrics data.
    
    Args:
        days: Number of days to keep (older data is deleted)
    """
    logger.info(f"Cleaning up audience metrics older than {days} days")
    
    try:
        supabase = get_supabase_admin_client()
        
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        result = supabase.table("audience_metrics")\
            .delete()\
            .lt("recorded_at", cutoff_date)\
            .execute()
        
        deleted_count = len(result.data) if result.data else 0
        
        # Also clean up old snapshots (keep last 12 months)
        snapshot_cutoff = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
        supabase.table("growth_snapshots")\
            .delete()\
            .lt("recorded_at", snapshot_cutoff)\
            .execute()
        
        logger.info(f"Cleaned up {deleted_count} old metrics")
        return {
            "success": True,
            "deleted_metrics": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup old metrics: {e}")
        return {
            "success": False,
            "error": str(e)
        }

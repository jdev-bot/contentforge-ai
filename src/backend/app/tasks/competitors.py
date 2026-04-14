"""
Celery tasks for competitor analysis and updates.

Scheduled tasks:
- Daily competitor data fetching
- Weekly content gap analysis
"""
import asyncio
from datetime import datetime, timedelta, timezone
from celery import shared_task
from celery.utils.log import get_task_logger

from app.core.config import get_settings

logger = get_task_logger(__name__)
settings = get_settings()


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def fetch_competitor_data_task(self):
    """
    Fetch updated data for all tracked competitors.
    
    This task runs daily to refresh competitor content,
    engagement metrics, and follower counts.
    
    Should be scheduled via Celery beat to run daily.
    """
    try:
        logger.info("Starting competitor data fetch task")
        
        # Import here to avoid circular imports
        from app.services.competitor_service import competitor_service
        
        # Run the async update
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                competitor_service.fetch_all_competitor_data()
            )
        finally:
            loop.close()
        
        if result["success"]:
            logger.info(
                f"Competitor data fetch completed successfully. "
                f"Competitors updated: {result['competitors_updated']}, "
                f"New content items: {result['total_new_content']}"
            )
            return {
                "status": "success",
                "competitors_updated": result["competitors_updated"],
                "total_new_content": result["total_new_content"],
                "timestamp": result["timestamp"],
            }
        else:
            error_msg = result.get("error", "Unknown error")
            logger.error(f"Failed to fetch competitor data: {error_msg}")
            raise self.retry(exc=Exception(error_msg))
            
    except Exception as exc:
        logger.error(f"Error in fetch_competitor_data_task: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=600)
def analyze_content_gaps_task(self):
    """
    Analyze content gaps for all users with tracked competitors.
    
    This task runs weekly to identify:
    - Topics competitors are covering that user isn't
    - High-opportunity content gaps
    - Trending topics in competitor content
    
    Should be scheduled via Celery beat to run weekly.
    """
    try:
        logger.info("Starting content gap analysis task")
        
        from app.services.competitor_service import competitor_service
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                competitor_service.generate_gap_analysis_for_all_users()
            )
        finally:
            loop.close()
        
        if result["success"]:
            logger.info(
                f"Content gap analysis completed. "
                f"Users processed: {result['users_processed']}, "
                f"Gaps identified: {result['total_gaps_identified']}"
            )
            return {
                "status": "success",
                "users_processed": result["users_processed"],
                "gaps_identified": result["total_gaps_identified"],
                "timestamp": result["timestamp"],
            }
        else:
            error_msg = result.get("error", "Unknown error")
            logger.error(f"Failed to analyze content gaps: {error_msg}")
            raise self.retry(exc=Exception(error_msg))
            
    except Exception as exc:
        logger.error(f"Error in analyze_content_gaps_task: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def generate_competitor_insights_task(self):
    """
    Generate insights and recommendations based on competitor data.
    
    Pre-computes insights for:
    - Top performing content patterns
    - Engagement trends
    - Posting frequency analysis
    
    Runs daily.
    """
    try:
        logger.info("Starting competitor insights generation")
        
        from app.services.competitor_service import competitor_service
        from app.core.supabase import get_supabase_client
        
        supabase = get_supabase_client()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        insights_generated = 0
        
        try:
            # Get all active competitors
            result = supabase.table("competitors").select("*").eq("is_active", True).execute()
            competitors = result.data or []
            
            for competitor in competitors:
                try:
                    # Get recent content for analysis
                    content_result = supabase.table("competitor_content").select("*").eq(
                        "competitor_id", competitor["id"]
                    ).gte(
                        "published_at", (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
                    ).execute()
                    
                    if content_result.data:
                        # Calculate insights
                        avg_engagement = sum(c.get("engagement_score", 0) for c in content_result.data) / len(content_result.data)
                        best_performing = max(content_result.data, key=lambda x: x.get("engagement_score", 0))
                        
                        # Store insights (could add to a new table)
                        logger.info(
                            f"Competitor {competitor['name']}: "
                            f"Avg engagement: {avg_engagement:.0f}, "
                            f"Best post: {best_performing['engagement_score']}"
                        )
                        insights_generated += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to analyze competitor {competitor['id']}: {e}")
                    continue
                    
        finally:
            loop.close()
        
        logger.info(f"Generated insights for {insights_generated} competitors")
        return {
            "status": "success",
            "insights_generated": insights_generated,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error in generate_competitor_insights_task: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def notify_high_opportunity_gaps_task(self):
    """
    Notify users about high-opportunity content gaps.
    
    Identifies gaps with high opportunity scores and could notify
    users via email or in-app notifications.
    
    Runs weekly.
    """
    try:
        logger.info("Starting high-opportunity gap notifications")
        
        from app.core.supabase import get_supabase_client
        
        supabase = get_supabase_client()
        
        # Find high-opportunity gaps that haven't been addressed
        result = supabase.table("content_gaps").select("*").eq(
            "is_addressed", False
        ).gte(
            "opportunity_score", 70
        ).order(
            "opportunity_score", desc=True
        ).limit(100).execute()
        
        gaps = result.data or []
        
        # Group by user
        user_gaps = {}
        for gap in gaps:
            user_id = gap["user_id"]
            if user_id not in user_gaps:
                user_gaps[user_id] = []
            user_gaps[user_id].append(gap)
        
        notified_count = 0
        
        for user_id, gaps in user_gaps.items():
            if len(gaps) >= 3:  # Only notify if 3+ high-opportunity gaps
                logger.info(
                    f"User {user_id} has {len(gaps)} high-opportunity content gaps"
                )
                # Here you would send notification/email
                # For now, just log
                notified_count += 1
        
        logger.info(f"Identified {notified_count} users with high-opportunity gaps")
        return {
            "status": "success",
            "users_notified": notified_count,
            "total_gaps": len(gaps),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error in notify_high_opportunity_gaps_task: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def cleanup_old_competitor_content_task(self):
    """
    Clean up old competitor content data.
    
    Removes content older than 90 days to keep database size manageable.
    Retains summary statistics.
    
    Runs monthly.
    """
    try:
        logger.info("Starting old competitor content cleanup")
        
        from app.core.supabase import get_supabase_client
        
        supabase = get_supabase_client()
        
        # Delete content older than 90 days
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
        
        result = supabase.table("competitor_content").delete().lt(
            "published_at", cutoff_date
        ).execute()
        
        deleted_count = len(result.data) if result.data else 0
        
        logger.info(f"Cleaned up {deleted_count} old competitor content items")
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error in cleanup_old_competitor_content_task: {exc}")
        raise self.retry(exc=exc)


@shared_task
def competitor_health_check_task():
    """
    Check health of competitor tracking system.
    
    Reports on:
    - Number of active competitors
    - Last sync times
    - Data freshness
    
    Runs daily for monitoring.
    """
    try:
        from app.core.supabase import get_supabase_client
        
        supabase = get_supabase_client()
        
        # Get stats
        active_result = supabase.table("competitors").select("id", count="exact").eq(
            "is_active", True
        ).execute()
        active_count = active_result.count or 0
        
        # Get stale competitors (not synced in 48 hours)
        stale_cutoff = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        stale_result = supabase.table("competitors").select("id", count="exact").eq(
            "is_active", True
        ).lt(
            "last_synced_at", stale_cutoff
        ).execute()
        stale_count = stale_result.count or 0
        
        health_status = "healthy" if stale_count == 0 else "warning" if stale_count < 5 else "critical"
        
        logger.info(
            f"Competitor health check: {active_count} active, "
            f"{stale_count} stale, status: {health_status}"
        )
        
        return {
            "status": "success",
            "health_status": health_status,
            "active_competitors": active_count,
            "stale_competitors": stale_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error in competitor_health_check_task: {exc}")
        return {
            "status": "error",
            "error": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
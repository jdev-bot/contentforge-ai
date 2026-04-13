"""
Celery tasks for trending topics detection and updates.
"""
import asyncio
from datetime import datetime
from celery import shared_task
from celery.utils.log import get_task_logger

from app.core.config import get_settings

logger = get_task_logger(__name__)
settings = get_settings()


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def update_trending_topics_task(self):
    """
    Update trending topics from various sources.
    
    This task fetches trending data, analyzes it with AI,
    and updates the database with fresh trends.
    
    Should run hourly via Celery beat schedule.
    """
    try:
        logger.info("Starting trending topics update task")
        
        # Import here to avoid circular imports
        from app.services.trend_service import trend_service
        
        # Run the async update
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(trend_service.update_trending_topics())
        finally:
            loop.close()
        
        if result["success"]:
            logger.info(
                f"Trending topics updated successfully. "
                f"Analyzed: {result['trends_analyzed']}, "
                f"Saved: {result['trends_saved']}"
            )
            return {
                "status": "success",
                "trends_analyzed": result["trends_analyzed"],
                "trends_saved": result["trends_saved"],
                "timestamp": result["timestamp"],
            }
        else:
            logger.error(f"Failed to update trending topics: {result.get('error')}")
            raise self.retry(exc=Exception(result.get("error", "Unknown error")))
            
    except Exception as exc:
        logger.error(f"Error in update_trending_topics_task: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def cleanup_expired_trends_task(self):
    """
    Clean up expired trending topics from the database.
    
    Removes trends that have passed their expiration time.
    Runs daily.
    """
    try:
        logger.info("Starting cleanup of expired trends")
        
        from app.services.trend_service import trend_service
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            deleted_count = loop.run_until_complete(trend_service._cleanup_expired_trends())
        finally:
            loop.close()
        
        logger.info(f"Cleaned up {deleted_count} expired trends")
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error in cleanup_expired_trends_task: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def generate_trend_content_suggestions_task(self):
    """
    Generate content suggestions based on top trending topics.
    
    Pre-generates content ideas for the highest trending topics
    to improve user experience.
    """
    try:
        logger.info("Starting trend content suggestions generation")
        
        from app.services.trend_service import trend_service
        from app.core.supabase import get_supabase_client
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get top trending topics
            top_trends = loop.run_until_complete(
                trend_service.get_trending_topics(limit=5)
            )
            
            suggestions_created = 0
            platforms = ["twitter", "linkedin", "blog"]
            
            for trend in top_trends:
                for platform in platforms:
                    try:
                        content_data = loop.run_until_complete(
                            trend_service.generate_content_from_trend(
                                topic=trend["topic"],
                                category=trend.get("category", "general"),
                                platform=platform,
                                tone="professional"
                            )
                        )
                        suggestions_created += 1
                    except Exception as e:
                        logger.warning(f"Failed to generate suggestion for {trend['topic']} on {platform}: {e}")
                        continue
            
            logger.info(f"Generated {suggestions_created} content suggestions")
            
        finally:
            loop.close()
        
        return {
            "status": "success",
            "suggestions_created": suggestions_created,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error in generate_trend_content_suggestions_task: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def notify_users_of_relevant_trends_task(self):
    """
    Notify users about trends relevant to their interests.
    
    Finds users with tracked topics and notifies them of new relevant trends.
    """
    try:
        logger.info("Starting relevant trends notification")
        
        from app.services.trend_service import trend_service
        from app.core.supabase import get_supabase_client
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        notified_count = 0
        
        try:
            supabase = get_supabase_client()
            
            # Get all users with tracked topics
            users_result = supabase.table("user_topic_interests").select("user_id").execute()
            
            user_ids = set()
            for item in users_result.data or []:
                user_ids.add(item["user_id"])
            
            # For each user, find new relevant trends
            for user_id in user_ids:
                try:
                    relevant = loop.run_until_complete(
                        trend_service.get_relevant_topics_for_user(user_id=user_id, limit=3)
                    )
                    
                    # Filter for high-relevance new trends
                    new_relevant = [t for t in relevant if t.get("relevance_score", 0) > 0.7]
                    
                    if new_relevant:
                        # Here you could send notification/email
                        # For now, just log
                        logger.info(f"Found {len(new_relevant)} relevant trends for user {user_id}")
                        notified_count += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to process user {user_id}: {e}")
                    continue
            
        finally:
            loop.close()
        
        return {
            "status": "success",
            "users_notified": notified_count,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error in notify_users_of_relevant_trends_task: {exc}")
        raise self.retry(exc=exc)


@shared_task
def get_trending_insights_task():
    """
    Generate and cache trending insights.
    
    Pre-computes trending insights for faster API responses.
    """
    try:
        from app.services.trend_service import trend_service
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            insights = loop.run_until_complete(trend_service.get_trending_insights())
        finally:
            loop.close()
        
        logger.info(f"Trending insights generated: {insights}")
        return {
            "status": "success",
            "insights": insights,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error in get_trending_insights_task: {exc}")
        return {
            "status": "error",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        }

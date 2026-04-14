"""
Scheduler router for automated content publishing.
Provides endpoints for scheduling, managing, and monitoring scheduled posts.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status as http_status, Depends, Query
from pydantic import BaseModel, Field
from uuid import UUID

from app.core.rate_limit import rate_limit_dependency
from app.routers.auth import get_auth_user
from app.services.scheduler_service import (
    scheduler_service,
    ScheduleRequest,
    ScheduleUpdateRequest,
)

router = APIRouter()


# ============== Request/Response Models ==============

class ScheduledPostItem(BaseModel):
    """Individual scheduled post response."""
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


class CreateScheduleRequest(BaseModel):
    """Request model for creating a scheduled post."""
    content_id: str
    asset_id: Optional[str] = None
    platform: str = Field(..., description="Platform to publish to (twitter, linkedin, etc.)")
    scheduled_at: datetime = Field(..., description="When to publish (will be converted to UTC)")
    asset_type: str = Field(default="post", description="Type of asset: post, thread, article")
    settings: dict = Field(default_factory=dict, description="Platform-specific settings")
    timezone: str = Field(default="UTC", description="User's timezone for the scheduled_at time")
    content: Optional[str] = Field(default=None, description="Content to publish (caches from asset)")


class UpdateScheduleRequest(BaseModel):
    """Request model for updating a scheduled post."""
    scheduled_at: Optional[datetime] = Field(None, description="New scheduled time")
    status: Optional[str] = Field(None, description="New status (use carefully)")
    settings: Optional[dict] = Field(None, description="Updated platform settings")
    timezone: Optional[str] = Field(None, description="User's timezone")


class SchedulerStatsResponse(BaseModel):
    """Response model for scheduler statistics."""
    pending: int
    processing: int
    published: int
    failed: int
    cancelled: int
    upcoming_24h: int


class ScheduleListResponse(BaseModel):
    """Response model for list of scheduled posts."""
    items: List[ScheduledPostItem]
    total: int
    page: int
    limit: int


class PublishNowResponse(BaseModel):
    """Response model for publish now action."""
    message: str
    post: ScheduledPostItem
    task_queued: bool


# ============== API Endpoints ==============

@router.post("/schedule", response_model=ScheduledPostItem, status_code=http_status.HTTP_201_CREATED)
async def create_scheduled_post(
    request: CreateScheduleRequest,
    user=Depends(get_auth_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    Schedule a new post for automated publishing.
    
    The scheduled_at time will be interpreted in the provided timezone (default: UTC).
    Posts must be scheduled for a future time.
    """
    try:
        schedule_request = ScheduleRequest(
            content_id=request.content_id,
            asset_id=request.asset_id,
            platform=request.platform,
            scheduled_at=request.scheduled_at,
            asset_type=request.asset_type,
            settings=request.settings,
            timezone=request.timezone,
        )
        
        result = scheduler_service.schedule_post(
            user_id=str(user.id),
            request=schedule_request,
            content=request.content
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule post: {str(e)}"
        )


@router.get("/schedule", response_model=ScheduleListResponse)
async def list_scheduled_posts(
    status: Optional[str] = Query(None, description="Filter by status"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(50, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    user=Depends(get_auth_user)
):
    """
    List all scheduled posts for the authenticated user.
    
    Supports filtering by status and platform, with pagination.
    """
    try:
        posts = scheduler_service.get_scheduled_posts(
            user_id=str(user.id),
            status=status,
            platform=platform,
            limit=limit,
            offset=offset
        )
        
        return ScheduleListResponse(
            items=posts,
            total=len(posts),  # Note: In production, use a count query
            page=(offset // limit) + 1,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scheduled posts: {str(e)}"
        )


@router.get("/schedule/{post_id}", response_model=ScheduledPostItem)
async def get_scheduled_post(
    post_id: str,
    user=Depends(get_auth_user)
):
    """
    Get details of a specific scheduled post.
    """
    try:
        post = scheduler_service.get_scheduled_post(
            user_id=str(user.id),
            post_id=post_id
        )
        
        if not post:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Scheduled post not found"
            )
        
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduled post: {str(e)}"
        )


@router.put("/schedule/{post_id}", response_model=ScheduledPostItem)
async def update_scheduled_post(
    post_id: str,
    request: UpdateScheduleRequest,
    user=Depends(get_auth_user)
):
    """
    Update a scheduled post.
    
    Cannot update posts that are already published or cancelled.
    The scheduled_at time will be interpreted in the provided timezone.
    """
    try:
        update_request = ScheduleUpdateRequest(
            scheduled_at=request.scheduled_at,
            status=request.status,
            settings=request.settings,
            timezone=request.timezone
        )
        
        result = scheduler_service.update_scheduled_post(
            user_id=str(user.id),
            post_id=post_id,
            request=update_request
        )
        
        if not result:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Scheduled post not found"
            )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scheduled post: {str(e)}"
        )


@router.delete("/schedule/{post_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def cancel_scheduled_post(
    post_id: str,
    user=Depends(get_auth_user)
):
    """
    Cancel a scheduled post.
    
    Cancels the post by setting status to 'cancelled'.
    Cannot cancel posts that are already published.
    """
    try:
        success = scheduler_service.cancel_scheduled_post(
            user_id=str(user.id),
            post_id=post_id
        )
        
        if not success:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Scheduled post not found"
            )
        
        return None
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel scheduled post: {str(e)}"
        )


@router.post("/schedule/{post_id}/publish-now", response_model=PublishNowResponse)
async def publish_scheduled_post_now(
    post_id: str,
    user=Depends(get_auth_user)
):
    """
    Immediately publish a scheduled post.
    
    This triggers the publish task immediately, bypassing the scheduled time.
    Cannot publish posts that are already published or cancelled.
    """
    try:
        result = scheduler_service.publish_now(
            user_id=str(user.id),
            post_id=post_id
        )
        
        if not result:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Scheduled post not found"
            )
        
        return PublishNowResponse(
            message="Post queued for immediate publishing",
            post=result,
            task_queued=True
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish post: {str(e)}"
        )


@router.get("/schedule/stats", response_model=SchedulerStatsResponse)
async def get_scheduler_stats(
    user=Depends(get_auth_user)
):
    """
    Get scheduler statistics for the authenticated user.
    
    Returns counts by status and upcoming posts in the next 24 hours.
    """
    try:
        stats = scheduler_service.get_scheduler_stats(user_id=str(user.id))
        
        return SchedulerStatsResponse(
            pending=stats.get("pending", 0),
            processing=stats.get("processing", 0),
            published=stats.get("published", 0),
            failed=stats.get("failed", 0),
            cancelled=stats.get("cancelled", 0),
            upcoming_24h=stats.get("upcoming_24h", 0)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduler stats: {str(e)}"
        )


@router.get("/schedule/upcoming", response_model=ScheduleListResponse)
async def get_upcoming_scheduled_posts(
    hours: int = Query(24, ge=1, le=168, description="Hours ahead to look (max 7 days)"),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(get_auth_user)
):
    """
    Get upcoming scheduled posts for the next N hours.
    
    Default is next 24 hours. Maximum is 7 days (168 hours).
    """
    try:
        from datetime import timedelta
        
        now = datetime.now(timezone.utc)
        future = now + timedelta(hours=hours)
        
        # Get all pending posts
        all_posts = scheduler_service.get_scheduled_posts(
            user_id=str(user.id),
            status="pending",
            limit=100  # Get more to filter
        )
        
        # Filter to only those within the time window
        upcoming = [
            post for post in all_posts
            if post.scheduled_at <= future
        ][:limit]
        
        return ScheduleListResponse(
            items=upcoming,
            total=len(upcoming),
            page=1,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upcoming posts: {str(e)}"
        )


@router.post("/schedule/bulk", response_model=List[ScheduledPostItem], status_code=http_status.HTTP_201_CREATED)
async def bulk_create_scheduled_posts(
    requests: List[CreateScheduleRequest],
    user=Depends(get_auth_user)
):
    """
    Bulk schedule multiple posts at once.
    
    Useful for scheduling an entire content calendar.
    Returns all successfully scheduled posts.
    """
    results = []
    errors = []
    
    for i, request in enumerate(requests):
        try:
            schedule_request = ScheduleRequest(
                content_id=request.content_id,
                asset_id=request.asset_id,
                platform=request.platform,
                scheduled_at=request.scheduled_at,
                asset_type=request.asset_type,
                settings=request.settings,
                timezone=request.timezone,
            )
            
            result = scheduler_service.schedule_post(
                user_id=str(user.id),
                request=schedule_request,
                content=request.content
            )
            results.append(result)
            
        except Exception as e:
            errors.append({"index": i, "error": str(e)})
    
    if errors:
        # Log errors but still return successes
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Bulk schedule had {len(errors)} errors: {errors}")
    
    if not results and errors:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"All {len(requests)} scheduling attempts failed. Errors: {errors[:3]}"
        )
    
    return results

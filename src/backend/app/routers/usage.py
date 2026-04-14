"""
Usage tracking router for monitoring API consumption.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4, BaseModel

from app.core.rate_limit import UsageStats, get_usage_history, get_user_usage_stats
from app.routers.auth import get_auth_user

router = APIRouter()


class UsageStatsResponse(BaseModel):
    """Response model for current usage statistics."""

    monthly_usage_count: int
    monthly_usage_limit: int
    remaining: int
    percentage_used: float
    reset_at: Optional[datetime] = None
    subscription_tier: str = "free"


class UsageLogEntry(BaseModel):
    """Individual usage log entry."""

    id: UUID4
    user_id: UUID4
    event_type: str
    tokens_used: Optional[int] = None
    metadata: Optional[dict] = None
    created_at: datetime


class UsageHistoryResponse(BaseModel):
    """Response model for usage history."""

    total: int
    events: List[UsageLogEntry]


@router.get("/usage", response_model=UsageStatsResponse)
async def get_current_usage(user=Depends(get_auth_user)):
    """
    Get current user's usage statistics.

    Returns:
    - monthly_usage_count: Number of API calls made this month
    - monthly_usage_limit: Maximum allowed calls for the subscription tier
    - remaining: Remaining calls before limit
    - percentage_used: Percentage of quota consumed
    """
    try:
        stats = get_user_usage_stats(str(user.id))

        # Calculate percentage (handle unlimited -1)
        if stats.monthly_usage_limit == -1:
            percentage_used = 0
        elif stats.monthly_usage_limit > 0:
            percentage_used = (
                stats.monthly_usage_count / stats.monthly_usage_limit * 100
            )
        else:
            percentage_used = 0

        return UsageStatsResponse(
            monthly_usage_count=stats.monthly_usage_count,
            monthly_usage_limit=stats.monthly_usage_limit,
            remaining=stats.remaining,
            percentage_used=round(percentage_used, 2),
            reset_at=stats.reset_at,
            subscription_tier=stats.subscription_tier,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage statistics: {str(e)}",
        )


@router.get("/usage/history", response_model=UsageHistoryResponse)
async def get_usage_history_endpoint(limit: int = 100, user=Depends(get_auth_user)):
    """
    Get usage history for the current user.

    Args:
    - limit: Maximum number of events to return (default: 100)

    Returns usage log entries showing when and how API resources were consumed.
    """
    try:
        # Validate limit
        if limit < 1 or limit > 1000:
            limit = 100

        history = get_usage_history(str(user.id), limit=limit)

        events = [UsageLogEntry(**entry) for entry in history]

        return UsageHistoryResponse(
            total=len(events),
            events=events,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage history: {str(e)}",
        )


@router.get("/usage/summary")
async def get_usage_summary(user=Depends(get_auth_user)):
    """
    Get a summary of usage for the dashboard.

    Returns combined stats and recent activity.
    """
    try:
        stats = get_user_usage_stats(str(user.id))
        history = get_usage_history(str(user.id), limit=10)

        # Calculate percentage (handle unlimited)
        if stats.monthly_usage_limit == -1:
            percentage_used = 0
        elif stats.monthly_usage_limit > 0:
            percentage_used = (
                stats.monthly_usage_count / stats.monthly_usage_limit * 100
            )
        else:
            percentage_used = 0

        return {
            "stats": {
                "monthly_usage_count": stats.monthly_usage_count,
                "monthly_usage_limit": stats.monthly_usage_limit,
                "remaining": stats.remaining,
                "percentage_used": round(percentage_used, 2),
                "subscription_tier": stats.subscription_tier,
            },
            "recent_activity": [
                {
                    "event_type": entry.get("event_type"),
                    "tokens_used": entry.get("tokens_used"),
                    "created_at": entry.get("created_at"),
                }
                for entry in history
            ],
            "status": (
                "active"
                if stats.remaining > 0 or stats.remaining == -1
                else "limit_reached"
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage summary: {str(e)}",
        )

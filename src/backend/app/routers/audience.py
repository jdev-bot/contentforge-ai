"""
Audience Growth Metrics Router

API endpoints for tracking and analyzing audience growth across platforms.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from app.routers.auth import get_auth_user
from app.services.audience_service import audience_service

router = APIRouter()


# Pydantic Models
class AudienceMetricCreate(BaseModel):
    """Model for creating a new audience metric."""

    platform: str = Field(
        ..., description="Social media platform (twitter, linkedin, youtube, etc.)"
    )
    metric_type: str = Field(
        ...,
        description="Type of metric (followers, subscribers, engagement_rate, etc.)",
    )
    value: int = Field(..., ge=0, description="Metric value")
    period: str = Field(
        default="daily", description="Time period (daily, weekly, monthly)"
    )
    recorded_at: Optional[datetime] = Field(
        default=None, description="Timestamp for the metric"
    )


class AudienceMetricResponse(BaseModel):
    """Response model for audience metric."""

    id: str
    user_id: str
    platform: str
    metric_type: str
    value: int
    period: str
    recorded_at: datetime


class GrowthMetricsResponse(BaseModel):
    """Response model for growth metrics."""

    metrics: List[Dict[str, Any]]
    growth_rates: Dict[str, float]
    current_totals: Dict[str, int]
    platform: Optional[str]
    period_days: int


class PlatformMetricsResponse(BaseModel):
    """Response model for platform metrics."""

    platform: str
    current_followers: int
    growth_7d: int
    growth_30d: int


class HistoricalDataResponse(BaseModel):
    """Response model for historical data."""

    platform: Optional[str]
    metric_type: str
    days: int
    data: List[Dict[str, Any]]


class WebhookPayload(BaseModel):
    """Model for webhook payload from social platforms."""

    platform: str = Field(..., description="Platform name")
    metric_type: str = Field(..., description="Type of metric")
    value: int = Field(..., ge=0, description="Metric value")
    timestamp: Optional[datetime] = Field(default=None, description="Event timestamp")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional platform data"
    )


class WebhookResponse(BaseModel):
    """Response model for webhook."""

    success: bool
    message: str
    recorded_metric: Optional[Dict[str, Any]] = None


class GrowthInsight(BaseModel):
    """Model for growth insights."""

    summary: str
    key_finding: str
    recommendation: str


class AudienceInsightsResponse(BaseModel):
    """Response model for audience insights."""

    summary: Dict[str, Any]
    trends: Dict[str, Any]
    comparisons: Dict[str, Any]
    predictions: Dict[str, Any]
    platforms: List[Dict[str, Any]]
    ai_insights: Dict[str, str]
    recommendations: List[str]


# API Endpoints


@router.get(
    "/audience/growth",
    response_model=GrowthMetricsResponse,
    summary="Get audience growth metrics",
    description="Retrieve growth metrics including rates and current totals for the authenticated user.",
)
async def get_growth_metrics(
    platform: Optional[str] = Query(
        None, description="Filter by platform (e.g., twitter, linkedin)"
    ),
    days: int = Query(30, ge=7, le=365, description="Number of days to look back"),
    user=Depends(get_auth_user),
):
    """Get audience growth metrics for the authenticated user."""
    try:
        metrics = audience_service.get_growth_metrics(
            user_id=str(user.id), platform=platform, days=days
        )
        return GrowthMetricsResponse(**metrics)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve growth metrics: {str(e)}",
        )


@router.get(
    "/audience/platforms",
    response_model=List[PlatformMetricsResponse],
    summary="Get metrics by platform",
    description="Retrieve audience metrics grouped by social media platform.",
)
async def get_platforms_metrics(
    days: int = Query(30, ge=7, le=365, description="Number of days to look back"),
    user=Depends(get_auth_user),
):
    """Get audience metrics grouped by platform."""
    try:
        platforms = audience_service.get_platforms_metrics(
            user_id=str(user.id), days=days
        )
        return [PlatformMetricsResponse(**p) for p in platforms]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve platform metrics: {str(e)}",
        )


@router.get(
    "/audience/history",
    response_model=HistoricalDataResponse,
    summary="Get historical audience data",
    description="Retrieve historical audience metrics over time.",
)
async def get_historical_data(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    metric_type: str = Query("followers", description="Type of metric to retrieve"),
    days: int = Query(90, ge=7, le=365, description="Number of days to look back"),
    user=Depends(get_auth_user),
):
    """Get historical audience data for the authenticated user."""
    try:
        data = audience_service.get_historical_data(
            user_id=str(user.id), platform=platform, metric_type=metric_type, days=days
        )
        return HistoricalDataResponse(
            platform=platform, metric_type=metric_type, days=days, data=data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve historical data: {str(e)}",
        )


@router.post(
    "/audience/record",
    response_model=AudienceMetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record new audience metric",
    description="Record a new audience metric. Can be used manually or via webhook.",
)
async def record_metric(metric: AudienceMetricCreate, user=Depends(get_auth_user)):
    """Record a new audience metric for the authenticated user."""
    try:
        recorded = audience_service.record_metric(
            user_id=str(user.id),
            platform=metric.platform,
            metric_type=metric.metric_type,
            value=metric.value,
            period=metric.period,
            recorded_at=metric.recorded_at,
        )

        if not recorded:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record metric",
            )

        return AudienceMetricResponse(**recorded)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record metric: {str(e)}",
        )


@router.post(
    "/audience/webhook/{platform}",
    response_model=WebhookResponse,
    summary="Receive webhook from social platform",
    description="Webhook endpoint for receiving audience metrics from social media platforms.",
)
async def receive_webhook(platform: str, payload: WebhookPayload, request: Request):
    """Receive webhook from social media platforms.

    This endpoint accepts metrics from external platforms like Twitter, LinkedIn, etc.
    It validates the platform and records the metric.
    """
    try:
        # Validate platform
        valid_platforms = [
            "twitter",
            "linkedin",
            "youtube",
            "instagram",
            "tiktok",
            "facebook",
        ]
        if platform.lower() not in valid_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}",
            )

        # TODO: Implement webhook signature verification
        # This would require storing webhook secrets per user/platform

        # Extract user_id from webhook metadata or API key
        # For now, this would need to be mapped via external_id in metadata
        user_id = payload.metadata.get("user_id") if payload.metadata else None

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing user_id in webhook payload metadata",
            )

        recorded = audience_service.record_metric(
            user_id=user_id,
            platform=platform.lower(),
            metric_type=payload.metric_type,
            value=payload.value,
            recorded_at=payload.timestamp,
        )

        return WebhookResponse(
            success=True,
            message=f"Successfully recorded {payload.metric_type} metric for {platform}",
            recorded_metric=recorded,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}",
        )


@router.get(
    "/audience/insights",
    response_model=AudienceInsightsResponse,
    summary="Get AI-generated audience insights",
    description="Retrieve comprehensive audience insights including trends, predictions, and recommendations.",
)
async def get_insights(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    user=Depends(get_auth_user),
):
    """Get AI-generated audience insights for the authenticated user."""
    try:
        insights = audience_service.generate_insights(user_id=str(user.id), days=days)
        return AudienceInsightsResponse(**insights)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}",
        )


@router.post(
    "/audience/snapshot",
    response_model=Dict[str, Any],
    summary="Generate growth snapshot",
    description="Manually trigger calculation and storage of a growth snapshot.",
)
async def generate_snapshot(user=Depends(get_auth_user)):
    """Generate a new growth snapshot for the authenticated user."""
    try:
        snapshot = audience_service.calculate_growth_snapshot(user_id=str(user.id))
        return {
            "success": True,
            "message": "Growth snapshot created successfully",
            "snapshot": snapshot,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate snapshot: {str(e)}",
        )


@router.delete(
    "/audience/metrics/{metric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete audience metric",
    description="Delete a specific audience metric by ID.",
)
async def delete_metric(metric_id: UUID, user=Depends(get_auth_user)):
    """Delete an audience metric."""
    try:
        supabase = audience_service.supabase
        result = (
            supabase.table("audience_metrics")
            .delete()
            .eq("id", str(metric_id))
            .eq("user_id", str(user.id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found"
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete metric: {str(e)}",
        )

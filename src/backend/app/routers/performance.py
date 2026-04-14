"""
Performance Analytics router for content performance tracking and analysis.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.routers.auth import get_auth_user
from app.services.performance_service import performance_service

router = APIRouter()


# ------------------------------------------------------------------ #
#  Request / Response Models                                           #
# ------------------------------------------------------------------ #

class TrackEventRequest(BaseModel):
    """Request body for tracking a performance event."""
    content_id: UUID = Field(..., description="Content piece ID")
    event_type: str = Field(..., description="Event type: view, share, comment, conversion")
    value: int = Field(default=1, ge=1, description="Numeric value of the event")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class TrackEventResponse(BaseModel):
    """Response after tracking a performance event."""
    id: Optional[str] = None
    content_id: str
    event_type: str
    value: int
    metadata: Optional[Dict[str, Any]] = None
    message: str = "Event tracked successfully"


class OverviewResponse(BaseModel):
    """Response for overall performance summary."""
    total_views: int
    total_shares: int
    total_comments: int
    total_conversions: int
    total_content: int
    avg_views_per_content: float
    avg_conversions_per_content: float
    engagement_rate: float
    performance_score: int
    period_days: int


class ContentMetricsResponse(BaseModel):
    """Response for per-content performance metrics."""
    content_id: str
    title: str
    status: Optional[str] = None
    created_at: Optional[str] = None
    metrics: Dict[str, int]
    engagement_rate: float
    performance_score: int
    event_count: int
    daily_series: List[Dict[str, Any]]


class FunnelStage(BaseModel):
    """Single funnel stage."""
    name: str
    count: int


class FunnelResponse(BaseModel):
    """Response for funnel analysis."""
    stages: List[FunnelStage]
    conversion_rates: Dict[str, float]
    overall_conversion_rate: float
    period_days: int


class CohortEntry(BaseModel):
    """Single cohort bucket."""
    cohort: str
    content_count: int
    metrics: Dict[str, int]
    engagement_rate: float
    conversion_rate: float
    avg_views: float
    avg_conversions: float


class CohortResponse(BaseModel):
    """Response for cohort analysis."""
    cohorts: List[CohortEntry]
    cohort_size: str
    periods: int


class AttributionByType(BaseModel):
    """Attribution by content source type."""
    source_type: str
    conversions: int
    value: int
    content_count: int


class AttributionByPlatform(BaseModel):
    """Attribution by distribution platform."""
    platform: str
    conversions: int
    value: int


class TopConverter(BaseModel):
    """Top converting content piece."""
    content_id: str
    title: str
    source_type: str
    conversions: int
    value: int


class AttributionResponse(BaseModel):
    """Response for attribution data."""
    total_conversions: int
    total_value: int
    by_content: List[Dict[str, Any]]
    by_content_type: List[AttributionByType]
    by_platform: List[AttributionByPlatform]
    top_converters: List[TopConverter]
    period_days: int


class TrendDataPoint(BaseModel):
    """Single data point in a trend series."""
    period: str
    views: int = 0
    shares: int = 0
    comments: int = 0
    conversions: int = 0
    total_engagement: int = 0


class TrendsResponse(BaseModel):
    """Response for performance trends."""
    granularity: str
    period_days: int
    series: List[TrendDataPoint]
    total_events: int


# ------------------------------------------------------------------ #
#  Endpoints                                                           #
# ------------------------------------------------------------------ #

@router.post("/performance/track", response_model=TrackEventResponse)
async def track_performance_event(
    body: TrackEventRequest,
    user=Depends(get_auth_user),
):
    """
    Track a performance event for a content piece.

    Event types: view, share, comment, conversion.
    """
    try:
        result = await performance_service.track_event(
            user_id=user.id,
            content_id=body.content_id,
            event_type=body.event_type,
            value=body.value,
            metadata=body.metadata,
        )
        return TrackEventResponse(
            id=result.get("id"),
            content_id=result.get("content_id", str(body.content_id)),
            event_type=result.get("event_type", body.event_type),
            value=result.get("value", body.value),
            metadata=result.get("metadata", body.metadata),
            message="Event tracked successfully",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track event: {str(e)}",
        )


@router.get("/performance/overview", response_model=OverviewResponse)
async def get_performance_overview(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    user=Depends(get_auth_user),
):
    """
    Get overall performance summary across all content.

    Returns total engagement counts, averages, engagement rate, and performance score.
    """
    try:
        overview = await performance_service.get_overview(user_id=user.id, days=days)
        return OverviewResponse(**overview)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance overview: {str(e)}",
        )


@router.get("/performance/content/{content_id}", response_model=ContentMetricsResponse)
async def get_content_performance(
    content_id: UUID,
    user=Depends(get_auth_user),
):
    """
    Get detailed performance metrics for a specific content piece.

    Returns engagement counts, engagement rate, performance score, and daily time-series.
    """
    try:
        metrics = await performance_service.get_content_metrics(
            content_id=content_id, user_id=user.id,
        )
        if metrics is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found or does not belong to user",
            )
        return ContentMetricsResponse(**metrics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve content metrics: {str(e)}",
        )


@router.get("/performance/funnel", response_model=FunnelResponse)
async def get_performance_funnel(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    user=Depends(get_auth_user),
):
    """
    Get content funnel analysis: created → published → engaged → converted.

    Returns counts at each stage and conversion rates between stages.
    """
    try:
        funnel = await performance_service.get_funnel(user_id=user.id, days=days)
        return FunnelResponse(**funnel)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve funnel data: {str(e)}",
        )


@router.get("/performance/cohort", response_model=CohortResponse)
async def get_performance_cohort(
    cohort_size: str = Query(default="week", description="Cohort size: day, week, or month"),
    periods: int = Query(default=4, ge=1, le=12, description="Number of cohort periods"),
    user=Depends(get_auth_user),
):
    """
    Get cohort analysis: group content by publish date and compare performance.

    Cohort sizes: day, week, month.
    """
    if cohort_size not in ("day", "week", "month"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cohort_size must be one of: day, week, month",
        )

    try:
        cohort = await performance_service.get_cohort(
            user_id=user.id, cohort_size=cohort_size, periods=periods,
        )
        return CohortResponse(**cohort)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cohort data: {str(e)}",
        )


@router.get("/performance/attribution", response_model=AttributionResponse)
async def get_performance_attribution(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    user=Depends(get_auth_user),
):
    """
    Get attribution data: which content drives conversions.

    Returns conversion attribution by content, content type, platform,
    and top converting content pieces.
    """
    try:
        attribution = await performance_service.get_attribution(user_id=user.id, days=days)
        return AttributionResponse(**attribution)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve attribution data: {str(e)}",
        )


@router.get("/performance/trends", response_model=TrendsResponse)
async def get_performance_trends(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    granularity: str = Query(default="day", description="Time granularity: day, week, or month"),
    user=Depends(get_auth_user),
):
    """
    Get performance trends over time.

    Granularity: day, week, or month.
    """
    if granularity not in ("day", "week", "month"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="granularity must be one of: day, week, month",
        )

    try:
        trends = await performance_service.get_trends(
            user_id=user.id, days=days, granularity=granularity,
        )
        return TrendsResponse(**trends)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trends: {str(e)}",
        )
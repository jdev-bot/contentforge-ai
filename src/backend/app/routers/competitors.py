"""
Competitor Analysis Router for ContentForge AI.

Provides endpoints for:
- Adding/removing competitors
- Viewing competitor content
- Performance analysis
- Content gap identification
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.rate_limit import (
    UsageStats,
    check_and_increment_usage,
    enforce_subscription_limit,
)
from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.competitor_service import competitor_service

router = APIRouter()


# ============ Pydantic Models ============


class AddCompetitorRequest(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=255, description="Display name for the competitor"
    )
    platform: str = Field(
        ...,
        description="Platform: twitter, linkedin, instagram, youtube, tiktok, facebook, blog",
    )
    handle: str = Field(
        ..., min_length=1, max_length=255, description="Username/handle on the platform"
    )
    description: Optional[str] = Field(default=None, description="Optional description")
    profile_url: Optional[str] = Field(
        default=None, description="Optional direct profile URL"
    )


class CompetitorResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    platform: str
    handle: str
    follower_count: int
    description: Optional[str]
    profile_url: Optional[str]
    is_active: bool
    last_synced_at: Optional[datetime]
    created_at: datetime


class CompetitorContentResponse(BaseModel):
    id: UUID
    competitor_id: UUID
    external_id: str
    content: str
    content_type: str
    published_at: datetime
    url: Optional[str]
    likes: int
    shares: int
    comments: int
    views: int
    engagement_score: int
    sentiment: Optional[str]
    topics: List[str]
    keywords: List[str]
    analyzed_at: Optional[datetime]


class CompetitorAnalysisItem(BaseModel):
    id: UUID
    name: str
    platform: str
    handle: str
    follower_count: int
    content_last_30_days: int
    avg_engagement_rate: float
    last_synced: Optional[datetime]


class PerformanceInsight(BaseModel):
    type: str
    title: str
    description: str
    platform: Optional[str]
    recommendation: str


class PerformanceAnalysisResponse(BaseModel):
    competitor_count: int
    competitors: List[CompetitorAnalysisItem]
    aggregated_metrics: Dict[str, Any]
    platform_breakdown: Dict[str, Dict[str, Any]]
    insights: List[PerformanceInsight]


class ContentGapResponse(BaseModel):
    id: UUID
    user_id: UUID
    topic: str
    category: Optional[str]
    competitor_count: int
    user_has_content: bool
    user_content_count: int
    opportunity_score: int
    suggested_action: Optional[str]
    content_ideas: List[str]
    priority: str
    is_addressed: bool
    created_at: datetime


class TopicOverlapResponse(BaseModel):
    competitor_topic_count: int
    user_topic_count: int
    overlap_count: int
    overlap_percentage: float
    shared_topics: List[str]
    competitor_only_topics: List[str]
    user_only_topics: List[str]
    recommendation: str


class BenchmarkComparisonResponse(BaseModel):
    user_metrics: Dict[str, Any]
    competitor_avg: Dict[str, Any]
    comparison: Dict[str, Any]
    percentile: Dict[str, int]


class RefreshCompetitorResponse(BaseModel):
    success: bool
    competitor_id: UUID
    new_content_count: int
    total_content: int


class DeleteCompetitorResponse(BaseModel):
    success: bool
    message: str


class ContentGapAnalysisResponse(BaseModel):
    gaps_analyzed: int
    gaps_stored: int
    gaps: List[ContentGapResponse]


# ============ API Endpoints ============


@router.post(
    "/competitors",
    response_model=CompetitorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_competitor(
    request: AddCompetitorRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """
    Add a new competitor to track.

    Creates a competitor entry and fetches initial mock content.
    """
    check_and_increment_usage(str(user.id))

    # Validate platform
    valid_platforms = [
        "twitter",
        "linkedin",
        "instagram",
        "youtube",
        "tiktok",
        "facebook",
        "blog",
        "newsletter",
        "other",
    ]
    if request.platform not in valid_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}",
        )

    try:
        competitor = await competitor_service.add_competitor(
            user_id=str(user.id),
            name=request.name,
            platform=request.platform,
            handle=request.handle,
            description=request.description,
            profile_url=request.profile_url,
        )

        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create competitor",
            )

        return CompetitorResponse(**competitor)

    except Exception as e:
        # Check for duplicate constraint violation
        if (
            "unique_competitor_per_user" in str(e).lower()
            or "duplicate" in str(e).lower()
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"You are already tracking this competitor ({request.platform}/{request.handle})",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add competitor: {str(e)}",
        )


@router.get("/competitors", response_model=List[CompetitorResponse])
async def list_competitors(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    user=Depends(get_auth_user),
):
    """
    List all tracked competitors for the user.

    Optionally filter by platform.
    """
    try:
        competitors = await competitor_service.get_competitors(
            user_id=str(user.id), platform=platform
        )
        return [CompetitorResponse(**comp) for comp in competitors]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch competitors: {str(e)}",
        )


@router.delete("/competitors/{competitor_id}", response_model=DeleteCompetitorResponse)
async def remove_competitor(competitor_id: UUID, user=Depends(get_auth_user)):
    """
    Remove a competitor from tracking.

    Performs a soft delete (sets is_active=false).
    """
    try:
        success = await competitor_service.remove_competitor(
            competitor_id=str(competitor_id), user_id=str(user.id)
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found"
            )

        return DeleteCompetitorResponse(
            success=True, message="Competitor removed from tracking"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove competitor: {str(e)}",
        )


@router.get(
    "/competitors/{competitor_id}/content",
    response_model=List[CompetitorContentResponse],
)
async def get_competitor_content(
    competitor_id: UUID,
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    user=Depends(get_auth_user),
):
    """
    Get content for a specific competitor.

    Returns the competitor's posts sorted by published date (newest first).
    """
    try:
        content = await competitor_service.get_competitor_content(
            competitor_id=str(competitor_id),
            user_id=str(user.id),
            limit=limit,
            offset=offset,
        )

        return [CompetitorContentResponse(**item) for item in content]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch competitor content: {str(e)}",
        )


@router.get("/competitors/analysis", response_model=PerformanceAnalysisResponse)
async def get_performance_analysis(
    user=Depends(get_auth_user), _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Get comprehensive performance analysis of all tracked competitors.

    Includes engagement metrics, activity levels, and actionable insights.
    """
    check_and_increment_usage(str(user.id))

    try:
        analysis = await competitor_service.get_performance_analysis(str(user.id))

        if analysis.get("competitor_count") == 0:
            return PerformanceAnalysisResponse(
                competitor_count=0,
                competitors=[],
                aggregated_metrics={},
                platform_breakdown={},
                insights=[],
            )

        return PerformanceAnalysisResponse(**analysis)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch performance analysis: {str(e)}",
        )


@router.get("/competitors/gaps", response_model=List[ContentGapResponse])
async def get_content_gaps(
    min_opportunity: int = Query(
        0, ge=0, le=100, description="Minimum opportunity score filter"
    ),
    user=Depends(get_auth_user),
):
    """
    Get identified content gaps.

    Returns topics that competitors are covering but you might be missing.
    """
    try:
        gaps = await competitor_service.get_content_gaps(
            user_id=str(user.id), min_opportunity=min_opportunity
        )
        return [ContentGapResponse(**gap) for gap in gaps]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch content gaps: {str(e)}",
        )


@router.post("/competitors/gaps/analyze", response_model=ContentGapAnalysisResponse)
async def analyze_content_gaps(
    user=Depends(get_auth_user), _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Run content gap analysis.

    Analyzes competitor content and identifies opportunities.
    """
    check_and_increment_usage(str(user.id))

    try:
        result = await competitor_service.identify_content_gaps(str(user.id))
        return ContentGapAnalysisResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze content gaps: {str(e)}",
        )


@router.get("/competitors/topics/overlap", response_model=TopicOverlapResponse)
async def get_topic_overlap(
    user=Depends(get_auth_user), _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Get topic overlap analysis between user and competitors.

    Shows shared topics, unique topics, and overlap percentage.
    """
    check_and_increment_usage(str(user.id))

    try:
        overlap = await competitor_service.analyze_topic_overlap(str(user.id))
        return TopicOverlapResponse(**overlap)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze topic overlap: {str(e)}",
        )


@router.get("/competitors/benchmark", response_model=BenchmarkComparisonResponse)
async def get_benchmark_comparison(
    user=Depends(get_auth_user), _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Get benchmark comparison against competitors.

    Compares your metrics to competitor averages and calculates percentiles.
    """
    check_and_increment_usage(str(user.id))

    try:
        benchmark = await competitor_service.get_benchmark_comparison(str(user.id))
        return BenchmarkComparisonResponse(**benchmark)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch benchmark: {str(e)}",
        )


@router.post(
    "/competitors/{competitor_id}/refresh", response_model=RefreshCompetitorResponse
)
async def refresh_competitor_data(
    competitor_id: UUID,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """
    Refresh data for a specific competitor.

    Fetches new content and updates metrics.
    """
    check_and_increment_usage(str(user.id))

    try:
        result = await competitor_service.refresh_competitor_data(
            competitor_id=str(competitor_id), user_id=str(user.id)
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Competitor not found"),
            )

        return RefreshCompetitorResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh competitor data: {str(e)}",
        )


@router.get("/competitors/{competitor_id}", response_model=CompetitorResponse)
async def get_competitor_details(competitor_id: UUID, user=Depends(get_auth_user)):
    """
    Get detailed information about a specific competitor.
    """
    try:
        competitor = await competitor_service.get_competitor_by_id(
            competitor_id=str(competitor_id), user_id=str(user.id)
        )

        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found"
            )

        return CompetitorResponse(**competitor)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch competitor details: {str(e)}",
        )


@router.get("/competitors/platforms/list", response_model=List[str])
async def get_supported_platforms():
    """
    Get list of supported competitor platforms.
    """
    return [
        "twitter",
        "linkedin",
        "instagram",
        "youtube",
        "tiktok",
        "facebook",
        "blog",
        "newsletter",
        "other",
    ]

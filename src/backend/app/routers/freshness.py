"""
Content Freshness Scoring API Router.

Provides endpoints for:
- Analyzing individual content freshness
- Getting freshness scores
- Listing stale content
- Bulk analyzing user content
- Dashboard statistics
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.freshness_service import freshness_service

logger = logging.getLogger(__name__)

router = APIRouter()


class FreshnessFactorsResponse(BaseModel):
    """Freshness scoring factors breakdown."""

    age_factor: float
    engagement_factor: float
    trend_factor: float
    age_points: int
    engagement_points: int
    trend_points: int


class FreshnessScoreResponse(BaseModel):
    """Response model for freshness score."""

    id: UUID
    content_id: UUID
    user_id: UUID
    freshness_score: int = Field(..., ge=0, le=100)
    age_days: int
    status: str
    last_analyzed_at: datetime
    factors: FreshnessFactorsResponse
    recommendations: List[str]
    created_at: datetime
    updated_at: datetime


class FreshnessAnalyzeRequest(BaseModel):
    """Request model for analyzing content freshness."""

    force_reanalyze: bool = Field(
        default=False, description="Force reanalysis even if recently analyzed"
    )


class FreshnessAnalyzeResponse(BaseModel):
    """Response model for analyze endpoint."""

    content_id: UUID
    freshness_score: int
    age_days: int
    status: str
    factors: FreshnessFactorsResponse
    recommendations: List[str]
    message: str


class StaleContentItem(BaseModel):
    """Stale content item with freshness info."""

    content_id: UUID
    title: str
    freshness_score: int
    age_days: int
    status: str
    recommendations: List[str]
    created_at: datetime


class StaleContentListResponse(BaseModel):
    """Response model for stale content list."""

    items: List[StaleContentItem]
    total: int
    page: int
    page_size: int


class BulkAnalyzeResponse(BaseModel):
    """Response model for bulk analyze."""

    total_analyzed: int
    freshness_scores: List[Dict[str, Any]]
    summary: Dict[str, int]


class FreshnessDashboardStats(BaseModel):
    """Dashboard statistics for content freshness."""

    total_content: int
    analyzed_content: int
    pending_analysis: int
    average_freshness_score: float
    fresh_count: int  # score >= 80
    good_count: int  # 60 <= score < 80
    aging_count: int  # 40 <= score < 60
    stale_count: int  # 20 <= score < 40
    outdated_count: int  # score < 20
    needs_refresh_count: int  # score < 50
    avg_age_days: float


class FreshnessDashboardResponse(BaseModel):
    """Response model for freshness dashboard."""

    stats: FreshnessDashboardStats
    recent_analyses: List[FreshnessScoreResponse]
    oldest_content: List[StaleContentItem]
    recommendations_summary: Dict[str, int]


@router.post("/freshness/analyze/{content_id}", response_model=FreshnessAnalyzeResponse)
async def analyze_content_freshness(
    content_id: UUID,
    request: FreshnessAnalyzeRequest = FreshnessAnalyzeRequest(),
    user=Depends(get_auth_user),
):
    """
    Analyze content freshness and store the score.

    - **content_id**: UUID of the content to analyze
    - **force_reanalyze**: If true, reanalyze even if recently analyzed

    Returns freshness score, factors breakdown, and recommendations.
    """
    supabase = get_supabase_client()

    try:
        # Get the content
        result = (
            supabase.table("content")
            .select("*")
            .eq("id", str(content_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            )

        content = result.data

        # Check if already analyzed recently (unless force_reanalyze)
        if not request.force_reanalyze:
            existing = (
                supabase.table("content_freshness_scores")
                .select("*")
                .eq("content_id", str(content_id))
                .eq("user_id", str(user.id))
                .execute()
            )
            if existing.data:
                last_analyzed = existing.data[0].get("last_analyzed_at")
                if last_analyzed:
                    last_analyzed_dt = datetime.fromisoformat(
                        last_analyzed.replace("Z", "+00:00")
                    )
                    if datetime.now(
                        last_analyzed_dt.tzinfo
                    ) - last_analyzed_dt < timedelta(hours=24):
                        # Return existing analysis
                        score_data = existing.data[0]
                        return FreshnessAnalyzeResponse(
                            content_id=content_id,
                            freshness_score=score_data["freshness_score"],
                            age_days=score_data["age_days"],
                            status=freshness_service.get_freshness_status(
                                score_data["freshness_score"]
                            ),
                            factors=FreshnessFactorsResponse(**score_data["factors"]),
                            recommendations=score_data["recommendations"],
                            message="Using cached analysis (within 24 hours)",
                        )

        # Perform freshness analysis
        analysis = freshness_service.analyze_content(content)
        status_label = freshness_service.get_freshness_status(
            analysis["freshness_score"]
        )

        # Upsert freshness score record
        freshness_data = {
            "content_id": str(content_id),
            "user_id": str(user.id),
            "freshness_score": analysis["freshness_score"],
            "age_days": analysis["age_days"],
            "last_analyzed_at": datetime.now().isoformat(),
            "factors": analysis["factors"],
            "recommendations": analysis["recommendations"],
        }

        supabase.table("content_freshness_scores").upsert(
            freshness_data, on_conflict="content_id,user_id"
        ).execute()

        return FreshnessAnalyzeResponse(
            content_id=content_id,
            freshness_score=analysis["freshness_score"],
            age_days=analysis["age_days"],
            status=status_label,
            factors=FreshnessFactorsResponse(**analysis["factors"]),
            recommendations=analysis["recommendations"],
            message="Freshness analysis completed",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze freshness: {str(e)}",
        )


@router.get("/freshness/stale", response_model=StaleContentListResponse)
async def list_stale_content(
    threshold: int = Query(
        default=50,
        ge=0,
        le=100,
        description="Freshness score threshold (content below this score is considered stale)",
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user=Depends(get_auth_user),
):
    """
    List stale content (freshness score below threshold).

    - **threshold**: Score threshold (default: 50)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)

    Returns paginated list of stale content with freshness info.
    """
    supabase = get_supabase_client()

    try:
        # Get stale freshness scores
        offset = (page - 1) * page_size
        result = (
            supabase.table("content_freshness_scores")
            .select("*, content!inner(title, created_at)")
            .eq("user_id", str(user.id))
            .lt("freshness_score", threshold)
            .order("freshness_score")
            .range(offset, offset + page_size - 1)
            .execute()
        )

        items = []
        for score_data in result.data:
            content_info = score_data.get("content", {})
            status_label = freshness_service.get_freshness_status(
                score_data["freshness_score"]
            )

            items.append(
                StaleContentItem(
                    content_id=score_data["content_id"],
                    title=content_info.get("title", "Untitled"),
                    freshness_score=score_data["freshness_score"],
                    age_days=score_data["age_days"],
                    status=status_label,
                    recommendations=score_data["recommendations"],
                    created_at=content_info.get("created_at", score_data["created_at"]),
                )
            )

        # Get total count
        count_result = (
            supabase.table("content_freshness_scores")
            .select("count", count="exact")
            .eq("user_id", str(user.id))
            .lt("freshness_score", threshold)
            .execute()
        )
        total = count_result.count or len(items)

        return StaleContentListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/freshness/bulk-analyze", response_model=BulkAnalyzeResponse)
async def bulk_analyze_content(
    content_ids: Optional[List[UUID]] = None, user=Depends(get_auth_user)
):
    """
    Analyze freshness for multiple content items.

    - **content_ids**: Optional list of specific content IDs to analyze. If not provided, analyzes all user content.

    Returns summary of analysis results.
    """
    supabase = get_supabase_client()

    try:
        # Get content to analyze
        if content_ids:
            # Analyze specific content IDs
            content_query = (
                supabase.table("content")
                .select("*")
                .eq("user_id", str(user.id))
                .in_("id", [str(cid) for cid in content_ids])
            )
        else:
            # Analyze all user content
            content_query = (
                supabase.table("content").select("*").eq("user_id", str(user.id))
            )

        content_result = content_query.execute()

        if not content_result.data:
            return BulkAnalyzeResponse(
                total_analyzed=0,
                freshness_scores=[],
                summary={},
            )

        freshness_scores = []
        summary = {
            "fresh": 0,
            "good": 0,
            "aging": 0,
            "stale": 0,
            "outdated": 0,
        }

        # Analyze each content item and collect upsert data
        upsert_batch = []
        for content in content_result.data:
            try:
                analysis = freshness_service.analyze_content(content)
                status_label = freshness_service.get_freshness_status(
                    analysis["freshness_score"]
                )

                # Collect freshness data for batch upsert
                freshness_data = {
                    "content_id": content["id"],
                    "user_id": str(user.id),
                    "freshness_score": analysis["freshness_score"],
                    "age_days": analysis["age_days"],
                    "last_analyzed_at": datetime.now().isoformat(),
                    "factors": analysis["factors"],
                    "recommendations": analysis["recommendations"],
                }
                upsert_batch.append(freshness_data)

                freshness_scores.append(
                    {
                        "content_id": content["id"],
                        "title": content.get("title", "Untitled"),
                        "freshness_score": analysis["freshness_score"],
                        "status": status_label,
                    }
                )

                # Update summary
                summary[status_label] = summary.get(status_label, 0) + 1

            except Exception as e:
                # Log error but continue with other content
                logger.error(f"Error analyzing content {content.get('id')}: {e}")
                continue

        # Batch upsert all freshness scores at once
        if upsert_batch:
            supabase.table("content_freshness_scores").upsert(
                upsert_batch, on_conflict="content_id,user_id"
            ).execute()

        return BulkAnalyzeResponse(
            total_analyzed=len(freshness_scores),
            freshness_scores=freshness_scores,
            summary=summary,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk analysis failed: {str(e)}",
        )


@router.get("/freshness/dashboard", response_model=FreshnessDashboardResponse)
async def get_freshness_dashboard(user=Depends(get_auth_user)):
    """
    Get freshness statistics dashboard.

    Returns comprehensive freshness stats for the user's content.
    """
    supabase = get_supabase_client()

    try:
        # Get all content count
        content_result = (
            supabase.table("content")
            .select("count", count="exact")
            .eq("user_id", str(user.id))
            .execute()
        )
        total_content = content_result.count or 0

        # Get all freshness scores
        scores_result = (
            supabase.table("content_freshness_scores")
            .select("*")
            .eq("user_id", str(user.id))
            .execute()
        )

        analyzed_content = len(scores_result.data)
        pending_analysis = total_content - analyzed_content

        if analyzed_content == 0:
            return FreshnessDashboardResponse(
                stats=FreshnessDashboardStats(
                    total_content=total_content,
                    analyzed_content=0,
                    pending_analysis=total_content,
                    average_freshness_score=0.0,
                    fresh_count=0,
                    good_count=0,
                    aging_count=0,
                    stale_count=0,
                    outdated_count=0,
                    needs_refresh_count=0,
                    avg_age_days=0.0,
                ),
                recent_analyses=[],
                oldest_content=[],
                recommendations_summary={},
            )

        # Calculate statistics
        scores = [s["freshness_score"] for s in scores_result.data]
        ages = [s["age_days"] for s in scores_result.data]

        average_score = sum(scores) / len(scores) if scores else 0
        avg_age = sum(ages) / len(ages) if ages else 0

        fresh_count = sum(1 for s in scores if s >= 80)
        good_count = sum(1 for s in scores if 60 <= s < 80)
        aging_count = sum(1 for s in scores if 40 <= s < 60)
        stale_count = sum(1 for s in scores if 20 <= s < 40)
        outdated_count = sum(1 for s in scores if s < 20)
        needs_refresh = sum(1 for s in scores if s < 50)

        # Get recent analyses (last 5)
        recent_result = (
            supabase.table("content_freshness_scores")
            .select("*")
            .eq("user_id", str(user.id))
            .order("last_analyzed_at", desc=True)
            .limit(5)
            .execute()
        )

        recent_analyses = []
        for score_data in recent_result.data:
            status_label = freshness_service.get_freshness_status(
                score_data["freshness_score"]
            )
            recent_analyses.append(
                FreshnessScoreResponse(
                    id=score_data["id"],
                    content_id=score_data["content_id"],
                    user_id=score_data["user_id"],
                    freshness_score=score_data["freshness_score"],
                    age_days=score_data["age_days"],
                    status=status_label,
                    last_analyzed_at=score_data["last_analyzed_at"],
                    factors=FreshnessFactorsResponse(**score_data["factors"]),
                    recommendations=score_data["recommendations"],
                    created_at=score_data["created_at"],
                    updated_at=score_data["updated_at"],
                )
            )

        # Get oldest/stalest content (top 5 by age)
        oldest_result = (
            supabase.table("content_freshness_scores")
            .select("*, content!inner(title, created_at)")
            .eq("user_id", str(user.id))
            .order("age_days", desc=True)
            .limit(5)
            .execute()
        )

        oldest_content = []
        for score_data in oldest_result.data:
            content_info = score_data.get("content", {})
            status_label = freshness_service.get_freshness_status(
                score_data["freshness_score"]
            )
            oldest_content.append(
                StaleContentItem(
                    content_id=score_data["content_id"],
                    title=content_info.get("title", "Untitled"),
                    freshness_score=score_data["freshness_score"],
                    age_days=score_data["age_days"],
                    status=status_label,
                    recommendations=score_data["recommendations"],
                    created_at=content_info.get("created_at", score_data["created_at"]),
                )
            )

        # Calculate recommendations summary
        recommendations_summary = {}
        for score_data in scores_result.data:
            for rec in score_data.get("recommendations", []):
                recommendations_summary[rec] = recommendations_summary.get(rec, 0) + 1

        return FreshnessDashboardResponse(
            stats=FreshnessDashboardStats(
                total_content=total_content,
                analyzed_content=analyzed_content,
                pending_analysis=pending_analysis,
                average_freshness_score=round(average_score, 1),
                fresh_count=fresh_count,
                good_count=good_count,
                aging_count=aging_count,
                stale_count=stale_count,
                outdated_count=outdated_count,
                needs_refresh_count=needs_refresh,
                avg_age_days=round(avg_age, 1),
            ),
            recent_analyses=recent_analyses,
            oldest_content=oldest_content,
            recommendations_summary=recommendations_summary,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/freshness/{content_id}", response_model=FreshnessScoreResponse)
async def get_freshness_score(content_id: UUID, user=Depends(get_auth_user)):
    """
    Get freshness score for specific content.

    - **content_id**: UUID of the content

    Returns stored freshness score or 404 if not analyzed yet.
    """
    supabase = get_supabase_client()

    try:
        result = (
            supabase.table("content_freshness_scores")
            .select("*")
            .eq("content_id", str(content_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Freshness score not found. Use POST /freshness/analyze/{content_id} to analyze.",
            )

        score_data = result.data
        status_label = freshness_service.get_freshness_status(
            score_data["freshness_score"]
        )

        return FreshnessScoreResponse(
            id=score_data["id"],
            content_id=score_data["content_id"],
            user_id=score_data["user_id"],
            freshness_score=score_data["freshness_score"],
            age_days=score_data["age_days"],
            status=status_label,
            last_analyzed_at=score_data["last_analyzed_at"],
            factors=FreshnessFactorsResponse(**score_data["factors"]),
            recommendations=score_data["recommendations"],
            created_at=score_data["created_at"],
            updated_at=score_data["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

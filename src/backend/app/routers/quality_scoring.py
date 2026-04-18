"""
Content Quality Scoring API Router.

Endpoints:
- POST   /api/v1/quality-scoring/analyze              — Analyze content quality
- GET    /api/v1/quality-scoring/content/{content_id}  — Get quality score for existing content
- GET    /api/v1/quality-scoring/history/{content_id}  — Get quality score history
- POST   /api/v1/quality-scoring/batch                 — Batch analyze multiple items
- GET    /api/v1/quality-scoring/suggestions/{content_id} — Get improvement suggestions
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from pydantic import BaseModel, Field

from app.core.rate_limit import (
    UsageStats,
    check_and_increment_usage,
    enforce_subscription_limit,
)
from app.core.supabase import get_supabase_client, get_supabase_admin_client
from app.routers.auth import get_auth_user
from app.services.quality_service import quality_service

router = APIRouter()


# ---------- Request / Response models ---------- #


class QualityAnalyzeRequest(BaseModel):
    """Request body for quality analysis of raw text."""

    text: str = Field(..., min_length=10, description="Content text to analyze")
    brand_voice: Optional[Dict[str, Any]] = Field(
        default=None, description="Brand voice reference for brand consistency scoring"
    )


class QualityBatchItem(BaseModel):
    """Single item in a batch analysis request."""

    content_id: UUID
    text: str = Field(..., min_length=10)
    brand_voice: Optional[Dict[str, Any]] = None


class QualityBatchRequest(BaseModel):
    """Batch quality analysis request."""

    items: List[QualityBatchItem] = Field(..., min_length=1, max_length=50)


class QualityScoreResponse(BaseModel):
    """Response model for a quality score."""

    id: Optional[UUID] = None
    content_id: Optional[UUID] = None
    overall_score: int = Field(..., ge=0, le=100)
    readability: int = Field(..., ge=0, le=100)
    seo: int = Field(..., ge=0, le=100)
    engagement: int = Field(..., ge=0, le=100)
    grammar: int = Field(..., ge=0, le=100)
    brand: int = Field(..., ge=0, le=100)
    suggestions: List[str] = []
    created_at: Optional[datetime] = None


class QualityHistoryResponse(BaseModel):
    """Response for quality score history."""

    content_id: UUID
    history: List[QualityScoreResponse]


class QualitySuggestionsResponse(BaseModel):
    """Response for improvement suggestions."""

    content_id: UUID
    suggestions: List[str]


# ---------- Endpoints ---------- #


@router.post("/quality-scoring/analyze", response_model=QualityScoreResponse)
async def analyze_quality(
    request: QualityAnalyzeRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Analyze content quality and return multi-dimensional scores."""
    check_and_increment_usage(str(user.id))

    try:
        scores = await quality_service.analyze_quality(
            text=request.text,
            brand_voice=request.brand_voice,
        )
        return QualityScoreResponse(
            overall_score=scores["overall_score"],
            readability=scores["readability"],
            seo=scores["seo"],
            engagement=scores["engagement"],
            grammar=scores["grammar"],
            brand=scores["brand"],
            suggestions=scores.get("suggestions", []),
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality analysis failed: {str(e)}",
        )


@router.get("/quality-scoring/content/{content_id}", response_model=QualityScoreResponse)
async def get_content_quality(
    content_id: UUID,
    user=Depends(get_auth_user),
):
    """Get the latest quality score for existing content."""
    try:
        score = await quality_service.get_score(content_id=content_id, user_id=user.id)
        if score is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="No quality score found for this content",
            )
        return QualityScoreResponse(**score)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/quality-scoring/history/{content_id}", response_model=QualityHistoryResponse)
async def get_quality_history(
    content_id: UUID,
    limit: int = 50,
    user=Depends(get_auth_user),
):
    """Get quality score history over time for a content item."""
    try:
        history = await quality_service.get_history(
            content_id=content_id,
            user_id=user.id,
            limit=limit,
        )
        return QualityHistoryResponse(
            content_id=content_id,
            history=[QualityScoreResponse(**h) for h in history],
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/quality-scoring/batch", response_model=List[QualityScoreResponse])
async def batch_analyze_quality(
    request: QualityBatchRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Batch analyze multiple content items."""
    check_and_increment_usage(str(user.id))

    try:
        items = [item.model_dump() for item in request.items]
        results = await quality_service.batch_analyze(items=items, user_id=user.id)
        return [QualityScoreResponse(**r) for r in results]
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}",
        )


@router.get(
    "/quality-scoring/suggestions/{content_id}", response_model=QualitySuggestionsResponse
)
async def get_quality_suggestions(
    content_id: UUID,
    user=Depends(get_auth_user),
):
    """Get improvement suggestions for a content item."""
    try:
        suggestions = await quality_service.get_suggestions(
            content_id=content_id,
            user_id=user.id,
        )
        return QualitySuggestionsResponse(
            content_id=content_id,
            suggestions=suggestions,
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/quality-scoring/{content_id}", response_model=QualityScoreResponse)
async def get_quality_score_by_id(
    content_id: UUID,
    user=Depends(get_auth_user),
):
    """Get quality score for content by ID (frontend-friendly alias).

    Alias for GET /quality-scoring/content/{content_id}.
    """
    return await get_content_quality(content_id=content_id, user=user)


@router.post("/quality-scoring/{content_id}/analyze", response_model=QualityScoreResponse)
async def analyze_quality_by_id(
    content_id: UUID,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Analyze quality score by content ID (frontend-friendly alias).

    Fetches the content text from the database, then analyzes it.
    """
    check_and_increment_usage(str(user.id))
    supabase = get_supabase_admin_client()
    try:
        result = (
            supabase.table("content")
            .select("body, title")
            .eq("id", str(content_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            )
        text = result.data.get("body", "") or result.data.get("title", "")
        if not text:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Content has no text to analyze",
            )
        request = QualityAnalyzeRequest(text=text)
        return await analyze_quality(request=request, user=user, _=_)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/quality-scoring/{content_id}/history", response_model=QualityHistoryResponse)
async def get_quality_history_by_id(
    content_id: UUID,
    days: int = Query(default=30, ge=1, le=365),
    user=Depends(get_auth_user),
):
    """Get quality score history by content ID (frontend-friendly alias).

    Alias for GET /quality-scoring/history/{content_id}.
    Converts days parameter to limit.
    """
    return await get_quality_history(content_id=content_id, limit=days, user=user)

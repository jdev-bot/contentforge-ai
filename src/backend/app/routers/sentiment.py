"""
Sentiment Analysis API Router.

Endpoints:
- POST   /api/v1/sentiment/analyze              — Analyze sentiment of text
- GET    /api/v1/sentiment/content/{content_id}  — Get sentiment for existing content
- POST   /api/v1/sentiment/batch                — Batch analyze sentiment
- GET    /api/v1/sentiment/trends/{content_id}   — Get sentiment trends over time
- GET    /api/v1/sentiment/distribution          — Get sentiment distribution across all content
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.rate_limit import (
    UsageStats,
    check_and_increment_usage,
    enforce_subscription_limit,
)
from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.sentiment_service import sentiment_service

router = APIRouter()


# ---------- Request / Response models ---------- #


class SentimentAnalyzeRequest(BaseModel):
    """Request body for sentiment analysis of raw text."""

    text: str = Field(..., min_length=5, description="Text to analyze for sentiment")


class SentimentBatchItem(BaseModel):
    """Single item in a batch sentiment analysis."""

    content_id: UUID
    text: str = Field(..., min_length=5)


class SentimentBatchRequest(BaseModel):
    """Batch sentiment analysis request."""

    items: List[SentimentBatchItem] = Field(..., min_length=1, max_length=50)


class EmotionScores(BaseModel):
    """Emotion detection scores 0-1."""

    joy: float = Field(..., ge=0.0, le=1.0)
    anger: float = Field(..., ge=0.0, le=1.0)
    sadness: float = Field(..., ge=0.0, le=1.0)
    fear: float = Field(..., ge=0.0, le=1.0)
    surprise: float = Field(..., ge=0.0, le=1.0)
    disgust: float = Field(..., ge=0.0, le=1.0)


class AspectSentiment(BaseModel):
    """Aspect-based sentiment for a section/paragraph."""

    section: str
    sentiment: str
    score: float = Field(..., ge=-1.0, le=1.0)


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis."""

    id: Optional[UUID] = None
    content_id: Optional[UUID] = None
    sentiment: str = Field(..., description="positive, negative, neutral, or mixed")
    score: float = Field(
        ..., ge=-1.0, le=1.0, description="Sentiment score -1.0 to +1.0"
    )
    emotions: EmotionScores
    aspects: List[AspectSentiment] = []
    tone: str = Field(
        ..., description="formal, casual, urgent, persuasive, or informative"
    )
    created_at: Optional[datetime] = None


class SentimentTrendsResponse(BaseModel):
    """Response for sentiment trends."""

    content_id: UUID
    trends: List[SentimentResponse]


class SentimentDistributionResponse(BaseModel):
    """Response for sentiment distribution."""

    total_analyses: int
    distribution: Dict[str, int]
    percentages: Dict[str, float]


# ---------- Endpoints ---------- #


@router.post("/sentiment/analyze", response_model=SentimentResponse)
async def analyze_sentiment(
    request: SentimentAnalyzeRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Analyze sentiment of text and return multi-level results."""
    check_and_increment_usage(str(user.id))

    try:
        analysis = await sentiment_service.analyze_sentiment(text=request.text)
        emotions = EmotionScores(**analysis["emotions"])
        aspects = [AspectSentiment(**a) for a in analysis.get("aspects", [])]
        return SentimentResponse(
            sentiment=analysis["sentiment"],
            score=analysis["score"],
            emotions=emotions,
            aspects=aspects,
            tone=analysis["tone"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sentiment analysis failed: {str(e)}",
        )


@router.get("/sentiment/content/{content_id}", response_model=SentimentResponse)
async def get_content_sentiment(
    content_id: UUID,
    user=Depends(get_auth_user),
):
    """Get sentiment analysis for existing content."""
    try:
        analysis = await sentiment_service.get_analysis(
            content_id=content_id,
            user_id=user.id,
        )
        if analysis is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sentiment analysis found for this content",
            )
        emotions = EmotionScores(**analysis["emotions"])
        aspects = [AspectSentiment(**a) for a in analysis.get("aspects", [])]
        return SentimentResponse(
            **{k: v for k, v in analysis.items() if k != "emotions" and k != "aspects"},
            emotions=emotions,
            aspects=aspects,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/sentiment/batch", response_model=List[SentimentResponse])
async def batch_analyze_sentiment(
    request: SentimentBatchRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Batch analyze sentiment for multiple content items."""
    check_and_increment_usage(str(user.id))

    try:
        items = [item.model_dump() for item in request.items]
        results = await sentiment_service.batch_analyze(items=items, user_id=user.id)
        response = []
        for r in results:
            emotions = EmotionScores(**r["emotions"])
            aspects = [AspectSentiment(**a) for a in r.get("aspects", [])]
            resp = SentimentResponse(
                id=r.get("id"),
                content_id=r.get("content_id"),
                sentiment=r["sentiment"],
                score=r["score"],
                emotions=emotions,
                aspects=aspects,
                tone=r["tone"],
                created_at=r.get("created_at"),
            )
            response.append(resp)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch sentiment analysis failed: {str(e)}",
        )


@router.get("/sentiment/trends/{content_id}", response_model=SentimentTrendsResponse)
async def get_sentiment_trends(
    content_id: UUID,
    limit: int = 50,
    user=Depends(get_auth_user),
):
    """Get sentiment trends over time for a content item."""
    try:
        trends = await sentiment_service.get_trends(
            content_id=content_id,
            user_id=user.id,
            limit=limit,
        )
        trend_responses = []
        for t in trends:
            emotions = EmotionScores(**t["emotions"])
            aspects = [AspectSentiment(**a) for a in t.get("aspects", [])]
            trend_responses.append(
                SentimentResponse(
                    id=t.get("id"),
                    content_id=t.get("content_id"),
                    sentiment=t["sentiment"],
                    score=t["score"],
                    emotions=emotions,
                    aspects=aspects,
                    tone=t["tone"],
                    created_at=t.get("created_at"),
                )
            )
        return SentimentTrendsResponse(content_id=content_id, trends=trend_responses)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/sentiment/distribution", response_model=SentimentDistributionResponse)
async def get_sentiment_distribution(
    user=Depends(get_auth_user),
):
    """Get sentiment distribution across all user content."""
    try:
        result = await sentiment_service.get_distribution(user_id=user.id)
        return SentimentDistributionResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

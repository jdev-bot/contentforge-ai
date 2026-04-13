"""
Trending topics router for ContentForge AI.
Provides endpoints for discovering and leveraging trending topics.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.core.rate_limit import check_and_increment_usage, enforce_subscription_limit, UsageStats
from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.trend_service import trend_service

router = APIRouter()


# ============ Pydantic Models ============

class TrendingTopicResponse(BaseModel):
    id: UUID
    topic: str
    category: Optional[str] = None
    trend_score: Optional[float] = None
    mention_count: Optional[int] = None
    velocity: Optional[float] = None
    source: Optional[str] = None
    discovered_at: datetime
    expires_at: Optional[datetime] = None
    related_keywords: Optional[List[str]] = None
    sample_content: Optional[List[Dict[str, str]]] = None


class TrendingTopicWithRelevance(TrendingTopicResponse):
    relevance_score: float


class TrendCategoryResponse(BaseModel):
    category: str
    topics: List[TrendingTopicResponse]
    topic_count: int


class TrackTopicRequest(BaseModel):
    topic_id: UUID = Field(..., description="ID of the trending topic to track")
    relevance_score: Optional[float] = Field(default=0.0, ge=0, le=1)


class TrackTopicResponse(BaseModel):
    success: bool
    message: str


class GenerateContentRequest(BaseModel):
    topic: str = Field(..., min_length=2, description="The trending topic")
    category: Optional[str] = Field(default=None, description="Topic category")
    platform: str = Field(default="twitter", description="Platform: twitter, linkedin, blog, newsletter, instagram, tiktok")
    tone: str = Field(default="professional", description="Content tone: professional, casual, witty, formal, friendly")


class GeneratedContentResponse(BaseModel):
    topic: str
    platform: str
    headline: str
    content: str
    angles: List[str]
    hashtags: List[str]
    cta: str
    saved_suggestion_id: Optional[UUID] = None


class TrendVelocityResponse(BaseModel):
    id: UUID
    topic: str
    velocity: float
    category: Optional[str] = None


class TrendInsightsResponse(BaseModel):
    total_trends: int
    top_category: Optional[str] = None
    avg_velocity: float
    highest_velocity_topic: Optional[str] = None
    category_distribution: Optional[Dict[str, int]] = None


class RefreshTrendsResponse(BaseModel):
    success: bool
    trends_analyzed: int
    trends_saved: int
    timestamp: datetime


# ============ API Endpoints ============

@router.get("/trends", response_model=List[TrendingTopicResponse])
async def list_trending_topics(
    category: Optional[str] = Query(None, description="Filter by category (tech, business, entertainment, etc.)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    min_score: float = Query(0.0, ge=0, le=100, description="Minimum trend score"),
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    List current trending topics.
    
    Returns trending topics sorted by trend score, optionally filtered by category.
    """
    check_and_increment_usage(str(user.id))
    
    try:
        trends = await trend_service.get_trending_topics(
            category=category,
            limit=limit,
            min_score=min_score
        )
        
        return [TrendingTopicResponse(**trend) for trend in trends]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trending topics: {str(e)}"
        )


@router.get("/trends/relevant", response_model=List[TrendingTopicWithRelevance])
async def get_relevant_trends(
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Get trending topics relevant to the user's content history.
    
    Analyzes user's existing content to find matching trending topics.
    """
    check_and_increment_usage(str(user.id))
    
    try:
        trends = await trend_service.get_relevant_topics_for_user(
            user_id=str(user.id),
            limit=limit
        )
        
        return [TrendingTopicWithRelevance(**trend) for trend in trends]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch relevant trends: {str(e)}"
        )


@router.get("/trends/categories", response_model=List[TrendCategoryResponse])
async def get_trends_by_category(
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Get trending topics grouped by category.
    
    Organizes trends into categories for easier browsing.
    """
    check_and_increment_usage(str(user.id))
    
    try:
        topics_by_category = await trend_service.get_topics_by_category()
        
        result = []
        for category, topics in topics_by_category.items():
            result.append(TrendCategoryResponse(
                category=category or "uncategorized",
                topics=[TrendingTopicResponse(**t) for t in topics[:10]],  # Top 10 per category
                topic_count=len(topics)
            ))
        
        # Sort by topic count
        result.sort(key=lambda x: x.topic_count, reverse=True)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trends by category: {str(e)}"
        )


@router.post("/trends/track", response_model=TrackTopicResponse)
async def track_topic(
    request: TrackTopicRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Track a trending topic for the user.
    
    Adds the topic to user's tracked interests for personalized recommendations.
    """
    check_and_increment_usage(str(user.id))
    
    try:
        success = await trend_service.track_topic_for_user(
            user_id=str(user.id),
            topic_id=str(request.topic_id),
            relevance_score=request.relevance_score
        )
        
        if success:
            return TrackTopicResponse(
                success=True,
                message="Topic is now being tracked for you"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to track topic"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track topic: {str(e)}"
        )


@router.get("/trends/tracked", response_model=List[Dict[str, Any]])
async def get_tracked_topics(
    user=Depends(get_auth_user)
):
    """
    Get all topics currently tracked by the user.
    """
    try:
        tracked = await trend_service.get_user_tracked_topics(str(user.id))
        return tracked
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tracked topics: {str(e)}"
        )


@router.delete("/trends/tracked/{topic_id}")
async def untrack_topic(
    topic_id: UUID,
    user=Depends(get_auth_user)
):
    """
    Stop tracking a specific topic.
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("user_topic_interests").delete().eq("user_id", str(user.id)).eq("topic_id", str(topic_id)).execute()
        
        return {"success": True, "message": "Topic removed from tracking"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove tracked topic: {str(e)}"
        )


@router.post("/trends/generate-content", response_model=GeneratedContentResponse)
async def generate_content_from_trend(
    request: GenerateContentRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Generate content based on a trending topic.
    
    Creates AI-powered content optimized for the specified platform.
    """
    check_and_increment_usage(str(user.id))
    
    try:
        # Generate content using trend service
        content_data = await trend_service.generate_content_from_trend(
            topic=request.topic,
            category=request.category or "general",
            platform=request.platform,
            tone=request.tone
        )
        
        # Try to find the topic ID for reference
        topic_id = None
        try:
            supabase = get_supabase_client()
            topic_result = supabase.table("trending_topics").select("id").eq("topic", request.topic).execute()
            if topic_result.data:
                topic_id = topic_result.data[0]["id"]
        except:
            pass
        
        # Save the suggestion
        saved_id = None
        if topic_id:
            try:
                suggestion_data = {
                    "topic_id": topic_id,
                    "user_id": str(user.id),
                    "platform": request.platform,
                    "suggested_content": content_data.get("content", ""),
                    "tokens_used": len(content_data.get("content", "").split()) * 2,  # Rough estimate
                }
                result = supabase.table("trend_content_suggestions").insert(suggestion_data).execute()
                if result.data:
                    saved_id = result.data[0]["id"]
            except Exception as e:
                print(f"Failed to save suggestion: {e}")
        
        return GeneratedContentResponse(
            topic=content_data["topic"],
            platform=content_data["platform"],
            headline=content_data["headline"],
            content=content_data["content"],
            angles=content_data["angles"],
            hashtags=content_data["hashtags"],
            cta=content_data["cta"],
            saved_suggestion_id=saved_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {str(e)}"
        )


@router.get("/trends/velocity", response_model=List[TrendVelocityResponse])
async def get_velocity_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Get the fastest-growing trending topics by velocity.
    
    Velocity represents the rate of growth (mentions per hour).
    """
    check_and_increment_usage(str(user.id))
    
    try:
        trends = await trend_service.get_velocity_leaderboard(limit=limit)
        return [TrendVelocityResponse(**t) for t in trends]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch velocity leaderboard: {str(e)}"
        )


@router.get("/trends/insights", response_model=TrendInsightsResponse)
async def get_trending_insights(
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Get overall insights about current trending topics.
    
    Returns aggregated statistics about trends including top categories and velocity metrics.
    """
    check_and_increment_usage(str(user.id))
    
    try:
        insights = await trend_service.get_trending_insights()
        return TrendInsightsResponse(**insights)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trending insights: {str(e)}"
        )


@router.post("/trends/refresh", response_model=RefreshTrendsResponse)
async def refresh_trending_topics(
    user=Depends(get_auth_user)
):
    """
    Manually refresh trending topics (admin only).
    
    Triggers a fresh fetch and analysis of trending topics.
    """
    # Check if user is admin (simplified check)
    try:
        supabase = get_supabase_client()
        user_result = supabase.table("user_profiles").select("role").eq("id", str(user.id)).single().execute()
        
        is_admin = user_result.data and user_result.data.get("role") == "admin"
        
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can manually refresh trending topics"
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can manually refresh trending topics"
        )
    
    try:
        result = await trend_service.update_trending_topics()
        
        if result["success"]:
            return RefreshTrendsResponse(
                success=True,
                trends_analyzed=result["trends_analyzed"],
                trends_saved=result["trends_saved"],
                timestamp=result["timestamp"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to refresh trends: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh trends: {str(e)}"
        )


@router.get("/trends/search")
async def search_trends(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    user=Depends(get_auth_user)
):
    """
    Search trending topics by keyword.
    """
    try:
        supabase = get_supabase_client()
        
        # Search in topic name, category, and related keywords
        result = supabase.table("trending_topics").select("*").ilike("topic", f"%{q}%").order("trend_score", desc=True).limit(limit).execute()
        
        if len(result.data or []) < limit:
            # Also search in related keywords
            category_result = supabase.table("trending_topics").select("*").ilike("category", f"%{q}%").order("trend_score", desc=True).limit(limit).execute()
            existing_ids = {t["id"] for t in result.data or []}
            for item in category_result.data or []:
                if item["id"] not in existing_ids:
                    result.data.append(item)
        
        return {
            "query": q,
            "results": result.data or [],
            "total": len(result.data or [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search trends: {str(e)}"
        )


@router.get("/trends/{topic_id}", response_model=TrendingTopicResponse)
async def get_trend_details(
    topic_id: UUID,
    user=Depends(get_auth_user)
):
    """
    Get detailed information about a specific trending topic.
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("trending_topics").select("*").eq("id", str(topic_id)).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trend not found"
            )
        
        return TrendingTopicResponse(**result.data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trend details: {str(e)}"
        )

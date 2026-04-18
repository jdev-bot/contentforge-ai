"""
Auto-Suggestions router for ContentForge AI.
Provides endpoints for AI-powered topic suggestions, posting time optimization,
and content improvement recommendations.
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
from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.suggestion_service import suggestion_service

router = APIRouter()


# ============ Pydantic Models ============


class TopicSuggestion(BaseModel):
    title: str
    description: str
    recommended_platform: str
    rationale: str
    keywords: List[str]


class PostingTimeSuggestion(BaseModel):
    day: str
    time_window: str
    platform: str
    expected_engagement: str
    reasoning: str


class ContentImprovementSuggestion(BaseModel):
    category: str
    current_state: str
    suggested_improvement: str
    priority: str
    example: str


class SaveSuggestionsRequest(BaseModel):
    suggestion_type: str = Field(
        ..., description="Type: topics, posting_times, content_improvements"
    )
    suggestions: List[Dict[str, Any]] = Field(
        ..., description="List of suggestions to save"
    )
    metadata: Optional[Dict[str, Any]] = None


class SaveSuggestionsResponse(BaseModel):
    id: UUID
    user_id: UUID
    suggestion_type: str
    suggestions: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class GenerateAllSuggestionsResponse(BaseModel):
    topics: List[Dict[str, Any]]
    posting_times: List[Dict[str, Any]]
    content_improvements: List[Dict[str, Any]]
    generated_at: str


# ============ Topic Suggestions ============


@router.get("/suggestions/topics", response_model=List[Dict[str, Any]])
async def get_topic_suggestions(
    limit: int = Query(
        5, ge=1, le=20, description="Number of topic suggestions to generate"
    ),
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """
    Get AI-generated topic suggestions based on user's content history and performance data.

    Analyzes past content patterns, engagement metrics, and trending topics
    to suggest new content topics the user should write about.
    """
    check_and_increment_usage(str(user.id))

    try:
        suggestions = await suggestion_service.suggest_topics(
            user_id=str(user.id),
            limit=limit,
        )
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate topic suggestions: {str(e)}",
        )


# ============ Posting Time Suggestions ============


@router.get("/suggestions/posting-times", response_model=List[Dict[str, Any]])
async def get_posting_time_suggestions(
    platform: Optional[str] = Query(
        None,
        description="Filter by platform: twitter, linkedin, blog, newsletter, instagram, tiktok",
    ),
    limit: int = Query(
        5, ge=1, le=10, description="Number of time suggestions to generate"
    ),
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """
    Get AI-generated optimal posting time suggestions based on audience engagement patterns.

    Analyzes when the user's audience is most active and engaged to
    recommend the best times to publish content.
    """
    check_and_increment_usage(str(user.id))

    try:
        suggestions = await suggestion_service.suggest_posting_times(
            user_id=str(user.id),
            platform=platform,
            limit=limit,
        )
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate posting time suggestions: {str(e)}",
        )


# ============ Content Improvement Suggestions ============


@router.get("/suggestions/improvements", response_model=List[Dict[str, Any]])
async def get_content_improvement_suggestions(
    content_id: Optional[str] = Query(
        None,
        description="Specific content ID to analyze (if omitted, analyzes recent content)",
    ),
    limit: int = Query(5, ge=1, le=10, description="Number of improvement suggestions"),
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """
    Get AI-generated content improvement suggestions.

    Analyzes tone, structure, keywords, readability, and engagement potential
    to provide actionable improvement recommendations.
    """
    check_and_increment_usage(str(user.id))

    try:
        suggestions = await suggestion_service.suggest_content_improvements(
            user_id=str(user.id),
            content_id=content_id,
            limit=limit,
        )
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate improvement suggestions: {str(e)}",
        )


# ============ Generate All Suggestions ============


@router.post("/suggestions/generate-all", response_model=GenerateAllSuggestionsResponse)
async def generate_all_suggestions(
    user=Depends(get_auth_user), _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Generate all types of suggestions at once (topics, posting times, improvements).

    This is a convenience endpoint that triggers all suggestion generation
    and saves the results for later retrieval.
    """
    check_and_increment_usage(str(user.id))

    try:
        result = await suggestion_service.generate_all_suggestions(
            user_id=str(user.id),
        )
        return GenerateAllSuggestionsResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate all suggestions: {str(e)}",
        )


# ============ Save Suggestions ============


@router.post("/suggestions/save", response_model=SaveSuggestionsResponse)
async def save_suggestions(
    request: SaveSuggestionsRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """
    Save generated suggestions for later retrieval.

    Persists suggestion data to Supabase so users can reference
    their past suggestions.
    """
    check_and_increment_usage(str(user.id))

    try:
        result = await suggestion_service.save_suggestions(
            user_id=str(user.id),
            suggestion_type=request.suggestion_type,
            suggestions=request.suggestions,
            metadata=request.metadata,
        )

        if not result:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save suggestions",
            )

        return SaveSuggestionsResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save suggestions: {str(e)}",
        )


# ============ List Saved Suggestions ============


@router.get("/suggestions/saved", response_model=List[Dict[str, Any]])
async def list_saved_suggestions(
    suggestion_type: Optional[str] = Query(
        None, description="Filter by type: topics, posting_times, content_improvements"
    ),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    user=Depends(get_auth_user),
):
    """
    List previously saved suggestions for the user.

    Returns saved suggestion records, optionally filtered by type.
    """
    try:
        suggestions = await suggestion_service.get_saved_suggestions(
            user_id=str(user.id),
            suggestion_type=suggestion_type,
            limit=limit,
        )
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list saved suggestions: {str(e)}",
        )


# ============ Delete Saved Suggestion ============


@router.delete("/suggestions/saved/{suggestion_id}")
async def delete_saved_suggestion(suggestion_id: UUID, user=Depends(get_auth_user)):
    """
    Delete a saved suggestion record.
    """
    try:
        success = await suggestion_service.delete_suggestion(
            user_id=str(user.id),
            suggestion_id=str(suggestion_id),
        )

        if not success:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found or could not be deleted",
            )

        return {"success": True, "message": "Suggestion deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete suggestion: {str(e)}",
        )

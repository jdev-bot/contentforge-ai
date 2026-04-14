"""
Smart Categorization router for ContentForge AI.
Provides endpoints for AI-powered content categorization, auto-tagging,
and content clustering.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.rate_limit import (UsageStats, check_and_increment_usage,
                                 enforce_subscription_limit)
from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.categorization_service import categorization_service

router = APIRouter()


# ============ Pydantic Models ============

class CategorizeRequest(BaseModel):
    content_id: UUID = Field(..., description="ID of the content item to categorize")


class CategorizeResponse(BaseModel):
    id: Optional[UUID] = None
    content_id: UUID
    category: str
    industry: str
    format: str
    sub_topics: List[str] = []
    relevance_score: int = 0
    target_audience: str = "General audience"
    tone: str = "professional"


class BatchCategorizeRequest(BaseModel):
    content_ids: Optional[List[str]] = Field(default=None, description="Specific content IDs to categorize (omit for uncategorized)")
    uncategorized_only: bool = Field(default=True, description="Only categorize content without categories")
    limit: int = Field(default=50, ge=1, le=100, description="Max content items to process")


class BatchCategorizeResponse(BaseModel):
    total: int
    categorized: int
    results: List[Dict[str, Any]]


class AutoTagRequest(BaseModel):
    content_id: UUID = Field(..., description="ID of the content item to tag")
    max_tags: int = Field(default=10, ge=1, le=30, description="Maximum number of tags to generate")


class AutoTagResponse(BaseModel):
    id: Optional[UUID] = None
    content_id: UUID
    tags: List[str] = []
    primary_keywords: List[str] = []
    secondary_keywords: List[str] = []
    long_tail_keywords: List[str] = []
    entity_tags: List[str] = []
    sentiment: str = "neutral"


class BatchAutoTagRequest(BaseModel):
    content_ids: Optional[List[str]] = Field(default=None, description="Specific content IDs to tag (omit for untagged)")
    untagged_only: bool = Field(default=True, description="Only tag content without tags")
    max_tags: int = Field(default=10, ge=1, le=30, description="Maximum number of tags per content")
    limit: int = Field(default=50, ge=1, le=100, description="Max content items to process")


class ClusterRequest(BaseModel):
    cluster_count: Optional[int] = Field(default=None, ge=2, le=20, description="Number of clusters (auto-determined if omitted)")


class ClusterResponse(BaseModel):
    clusters: List[Dict[str, Any]] = []
    total_content: int = 0
    num_clusters: int = 0
    generated_at: Optional[str] = None


class UpdateCategorizationRequest(BaseModel):
    category: Optional[str] = None
    industry: Optional[str] = None
    format: Optional[str] = None
    sub_topics: Optional[List[str]] = None
    relevance_score: Optional[int] = Field(default=None, ge=0, le=100)
    target_audience: Optional[str] = None
    tone: Optional[str] = None


# ============ Categorize Single Content ============

@router.post("/categorization/categorize", response_model=Dict[str, Any])
async def categorize_content(
    request: CategorizeRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Auto-categorize a single content item.
    
    Uses AI to analyze content and assign topic category, industry vertical,
    content format, sub-topics, and tone classification.
    """
    check_and_increment_usage(str(user.id))

    try:
        result = await categorization_service.categorize_content(
            content_id=str(request.content_id),
            user_id=str(user.id),
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to categorize content: {str(e)}"
        )


# ============ Batch Categorize ============

@router.post("/categorization/batch-categorize", response_model=BatchCategorizeResponse)
async def batch_categorize_content(
    request: BatchCategorizeRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Batch categorize multiple content items.
    
    Processes uncategorized content or specific content IDs.
    Limited to 20 items per batch for AI rate limiting.
    """
    check_and_increment_usage(str(user.id))

    try:
        result = await categorization_service.batch_categorize(
            user_id=str(user.id),
            content_ids=request.content_ids,
            uncategorized_only=request.uncategorized_only,
            limit=request.limit,
        )
        return BatchCategorizeResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch categorize: {str(e)}"
        )


# ============ Auto-Tag Single Content ============

@router.post("/categorization/auto-tag", response_model=Dict[str, Any])
async def auto_tag_content(
    request: AutoTagRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Auto-tag a single content item with AI-generated keywords.
    
    Generates primary keywords, secondary keywords, long-tail keywords,
    entity tags, and sentiment classification.
    """
    check_and_increment_usage(str(user.id))

    try:
        result = await categorization_service.auto_tag_content(
            content_id=str(request.content_id),
            user_id=str(user.id),
            max_tags=request.max_tags,
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-tag content: {str(e)}"
        )


# ============ Batch Auto-Tag ============

@router.post("/categorization/batch-auto-tag", response_model=Dict[str, Any])
async def batch_auto_tag_content(
    request: BatchAutoTagRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Batch auto-tag multiple content items.
    
    Processes untagged content or specific content IDs.
    Limited to 20 items per batch for AI rate limiting.
    """
    check_and_increment_usage(str(user.id))

    try:
        result = await categorization_service.batch_auto_tag(
            user_id=str(user.id),
            content_ids=request.content_ids,
            untagged_only=request.untagged_only,
            max_tags=request.max_tags,
            limit=request.limit,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch auto-tag: {str(e)}"
        )


# ============ Content Clustering ============

@router.post("/categorization/cluster", response_model=ClusterResponse)
async def cluster_content(
    request: ClusterRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Cluster user's content into thematic groups.
    
    Uses AI to analyze content patterns and organize items into
    meaningful clusters with descriptions, keywords, and suggested categories.
    """
    check_and_increment_usage(str(user.id))

    try:
        result = await categorization_service.cluster_content(
            user_id=str(user.id),
            cluster_count=request.cluster_count,
        )
        return ClusterResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cluster content: {str(e)}"
        )


# ============ Get Categorization for Content ============

@router.get("/categorization/content/{content_id}", response_model=Dict[str, Any])
async def get_content_categorization(
    content_id: UUID,
    user=Depends(get_auth_user)
):
    """
    Retrieve the categorization record for a specific content item.
    """
    try:
        result = await categorization_service.get_content_categorization(
            content_id=str(content_id),
            user_id=str(user.id),
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categorization not found for this content"
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get categorization: {str(e)}"
        )


# ============ Get Tags for Content ============

@router.get("/categorization/content/{content_id}/tags", response_model=Dict[str, Any])
async def get_content_tags(
    content_id: UUID,
    user=Depends(get_auth_user)
):
    """
    Retrieve the tag record for a specific content item.
    """
    try:
        result = await categorization_service.get_content_tags(
            content_id=str(content_id),
            user_id=str(user.id),
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tags not found for this content"
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content tags: {str(e)}"
        )


# ============ Update Categorization ============

@router.patch("/categorization/{categorization_id}", response_model=Dict[str, Any])
async def update_categorization(
    categorization_id: UUID,
    request: UpdateCategorizationRequest,
    user=Depends(get_auth_user)
):
    """
    Update a categorization record (e.g., user overrides of AI categorization).
    
    Only provided fields will be updated.
    """
    try:
        updates = request.dict(exclude_none=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )

        result = await categorization_service.update_categorization(
            categorization_id=str(categorization_id),
            user_id=str(user.id),
            updates=updates,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categorization not found or update failed"
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update categorization: {str(e)}"
        )


# ============ Delete Categorization ============

@router.delete("/categorization/{categorization_id}")
async def delete_categorization(
    categorization_id: UUID,
    user=Depends(get_auth_user)
):
    """
    Delete a categorization record.
    """
    try:
        success = await categorization_service.delete_categorization(
            categorization_id=str(categorization_id),
            user_id=str(user.id),
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categorization not found or could not be deleted"
            )

        return {"success": True, "message": "Categorization deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete categorization: {str(e)}"
        )


# ============ List Categorizations ============

@router.get("/categorization/list", response_model=List[Dict[str, Any]])
async def list_categorizations(
    category: Optional[str] = Query(None, description="Filter by category"),
    industry: Optional[str] = Query(None, description="Filter by industry vertical"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    user=Depends(get_auth_user)
):
    """
    List all categorizations for the user with optional filters.
    """
    try:
        categorizations = await categorization_service.list_categorizations(
            user_id=str(user.id),
            category=category,
            industry=industry,
            limit=limit,
        )
        return categorizations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list categorizations: {str(e)}"
        )
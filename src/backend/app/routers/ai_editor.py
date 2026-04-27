"""
AI Content Editor router for smart content editing, rewriting, expansion, and optimization.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from pydantic import BaseModel, Field, validator

from app.core.rate_limit import (
    UsageStats,
    check_and_increment_usage,
    enforce_subscription_limit,
)
from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.routers.auth import get_auth_user
from app.services.ai_service import ai_service
from app.core.byok_dependency import ensure_byok_context

router = APIRouter(dependencies=[Depends(ensure_byok_context)])


class RewriteRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Content to rewrite")
    tone: str = Field(
        default="professional",
        description="casual, professional, witty, formal, friendly, authoritative, enthusiastic, empathetic",
    )
    style: str = Field(
        default="neutral",
        description="neutral, persuasive, informative, storytelling, concise, descriptive",
    )

    @validator("tone")
    def validate_tone(cls, v):
        valid_tones = [
            "casual",
            "professional",
            "witty",
            "formal",
            "friendly",
            "authoritative",
            "enthusiastic",
            "empathetic",
        ]
        if v not in valid_tones:
            raise ValueError(f"tone must be one of {valid_tones}")
        return v

    @validator("style")
    def validate_style(cls, v):
        valid_styles = [
            "neutral",
            "persuasive",
            "informative",
            "storytelling",
            "concise",
            "descriptive",
        ]
        if v not in valid_styles:
            raise ValueError(f"style must be one of {valid_styles}")
        return v


class ExpandRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Content to expand")
    target_length: int = Field(
        default=2, ge=2, le=5, description="Length multiplier (2x, 3x, 4x, 5x)"
    )
    focus_areas: List[str] = Field(
        default=[], description="Specific areas to focus expansion on"
    )


class CondenseRequest(BaseModel):
    content: str = Field(..., min_length=20, description="Content to condense")
    target_percentage: int = Field(
        default=50, ge=20, le=80, description="Target percentage of original length"
    )
    preserve_key_points: bool = Field(
        default=True, description="Whether to preserve key points"
    )


class OptimizeRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Content to optimize")
    platform: str = Field(
        ..., description="twitter, linkedin, blog, newsletter, instagram, tiktok"
    )
    include_hashtags: bool = Field(
        default=True, description="Include hashtags in optimized content"
    )
    include_cta: bool = Field(default=True, description="Include call-to-action")

    @validator("platform")
    def validate_platform(cls, v):
        valid_platforms = [
            "twitter",
            "linkedin",
            "blog",
            "newsletter",
            "instagram",
            "tiktok",
        ]
        if v not in valid_platforms:
            raise ValueError(f"platform must be one of {valid_platforms}")
        return v


class RewriteResponse(BaseModel):
    id: str
    operation: str = "rewrite"
    original_content: str
    rewritten_content: str
    tone: str
    style: str
    tokens_used: int
    created_at: datetime


class ExpandResponse(BaseModel):
    id: str
    operation: str = "expand"
    original_content: str
    expanded_content: str
    target_length: int
    actual_expansion_ratio: float
    tokens_used: int
    created_at: datetime


class CondenseResponse(BaseModel):
    id: str
    operation: str = "condense"
    original_content: str
    condensed_content: str
    target_percentage: int
    actual_reduction_percentage: float
    tokens_used: int
    created_at: datetime


class OptimizeResponse(BaseModel):
    id: str
    operation: str = "optimize"
    original_content: str
    optimized_content: str
    platform: str
    character_count: int
    word_count: int
    tokens_used: int
    created_at: datetime


class EditorHistoryItem(BaseModel):
    id: str
    content_id: Optional[str]
    operation: str
    original_preview: str
    result_preview: str
    tokens_used: int
    created_at: datetime


@router.post("/ai/edit/rewrite", response_model=RewriteResponse)
async def rewrite_content(
    request: RewriteRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Rewrite content with different tone and style."""
    usage_stats = check_and_increment_usage(str(user.id))

    try:
        rewritten_text, tokens_used = await ai_service.rewrite_content(
            content=request.content,
            tone=request.tone,
            style=request.style,
        )

        response = RewriteResponse(
            id=str(uuid4()),
            operation="rewrite",
            original_content=request.content,
            rewritten_content=rewritten_text,
            tone=request.tone,
            style=request.style,
            tokens_used=tokens_used,
            created_at=datetime.now(timezone.utc),
        )

        return response

    except HTTPException:

        raise

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rewrite content: {str(e)}",
        )


@router.post("/ai/edit/expand", response_model=ExpandResponse)
async def expand_content(
    request: ExpandRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Expand content with more detail and depth."""
    usage_stats = check_and_increment_usage(str(user.id))

    try:
        expanded_text, tokens_used = await ai_service.expand_content(
            content=request.content,
            target_length=request.target_length,
            focus_areas=request.focus_areas,
        )

        # Calculate actual expansion ratio
        original_words = len(request.content.split())
        expanded_words = len(expanded_text.split())
        actual_ratio = expanded_words / original_words if original_words > 0 else 1.0

        response = ExpandResponse(
            id=str(uuid4()),
            operation="expand",
            original_content=request.content,
            expanded_content=expanded_text,
            target_length=request.target_length,
            actual_expansion_ratio=round(actual_ratio, 2),
            tokens_used=tokens_used,
            created_at=datetime.now(timezone.utc),
        )

        return response

    except HTTPException:

        raise

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to expand content: {str(e)}",
        )


@router.post("/ai/edit/condense", response_model=CondenseResponse)
async def condense_content(
    request: CondenseRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Condense content to be shorter while preserving key points."""
    usage_stats = check_and_increment_usage(str(user.id))

    try:
        condensed_text, tokens_used = await ai_service.condense_content(
            content=request.content,
            target_percentage=request.target_percentage,
            preserve_key_points=request.preserve_key_points,
        )

        # Calculate actual reduction percentage
        original_words = len(request.content.split())
        condensed_words = len(condensed_text.split())
        reduction_pct = (
            ((original_words - condensed_words) / original_words * 100)
            if original_words > 0
            else 0
        )

        response = CondenseResponse(
            id=str(uuid4()),
            operation="condense",
            original_content=request.content,
            condensed_content=condensed_text,
            target_percentage=request.target_percentage,
            actual_reduction_percentage=round(reduction_pct, 1),
            tokens_used=tokens_used,
            created_at=datetime.now(timezone.utc),
        )

        return response

    except HTTPException:

        raise

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to condense content: {str(e)}",
        )


@router.post("/ai/edit/optimize", response_model=OptimizeResponse)
async def optimize_content(
    request: OptimizeRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Optimize content for a specific platform."""
    usage_stats = check_and_increment_usage(str(user.id))

    try:
        result = await ai_service.optimize_content(
            content=request.content,
            platform=request.platform,
            include_hashtags=request.include_hashtags,
            include_cta=request.include_cta,
        )

        response = OptimizeResponse(
            id=str(uuid4()),
            operation="optimize",
            original_content=request.content,
            optimized_content=result["optimized_content"],
            platform=request.platform,
            character_count=result["character_count"],
            word_count=result["word_count"],
            tokens_used=result["estimated_tokens"],
            created_at=datetime.now(timezone.utc),
        )

        return response

    except HTTPException:

        raise

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize content: {str(e)}",
        )


@router.get("/ai/edit/history", response_model=List[EditorHistoryItem])
async def get_editor_history(
    limit: int = 50, operation: Optional[str] = None, user=Depends(get_auth_user)
):
    """Get history of AI editor operations."""
    supabase = get_supabase_admin_client()

    try:
        query = (
            supabase.table("ai_editor_history")
            .select("*")
            .eq("user_id", str(user.id))
            .order("created_at", desc=True)
            .limit(limit)
        )

        if operation:
            query = query.eq("operation", operation)

        result = query.execute()

        return [
            EditorHistoryItem(
                id=item["id"],
                content_id=item.get("content_id"),
                operation=item["operation"],
                original_preview=item["original_preview"],
                result_preview=item["result_preview"],
                tokens_used=item["tokens_used"],
                created_at=item["created_at"],
            )
            for item in result.data
        ]

    except HTTPException:

        raise

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch editor history: {str(e)}",
        )

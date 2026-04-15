"""
AI Content Suggestions router for content improvement, SEO optimization, and tone adjustment.
"""

import logging
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

logger = logging.getLogger(__name__)
from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.routers.auth import get_auth_user
from app.services.groq_service import groq_service

router = APIRouter()


class ContentImprovementRequest(BaseModel):
    content_id: UUID
    suggestion_type: str = Field(
        ..., description="Type: readability, engagement, clarity, grammar"
    )


class SEOOptimizationRequest(BaseModel):
    content_id: UUID
    keywords: Optional[List[str]] = None
    target_audience: Optional[str] = None


class ToneAdjustmentRequest(BaseModel):
    content_id: UUID
    tone: str = Field(
        ...,
        description="Options: professional, casual, humorous, formal, friendly, authoritative",
    )


class AIImprovementSuggestion(BaseModel):
    id: UUID
    content_id: UUID
    user_id: UUID
    suggestion_type: str
    original_text: str
    improved_text: str
    explanation: str
    confidence_score: Optional[float] = None
    applied: bool = False
    created_at: datetime


class SEOAnalysisResult(BaseModel):
    id: UUID
    content_id: UUID
    user_id: UUID
    seo_score: int = Field(..., ge=0, le=100)
    keyword_density: Dict[str, float]
    readability_score: int = Field(..., ge=0, le=100)
    suggestions: List[str]
    meta_title_suggestion: Optional[str] = None
    meta_description_suggestion: Optional[str] = None
    heading_structure_suggestions: List[str]
    created_at: datetime


class ToneAdjustmentResult(BaseModel):
    id: UUID
    content_id: UUID
    user_id: UUID
    original_tone: str
    target_tone: str
    adjusted_text: str
    tone_characteristics: Dict[str, Any]
    created_at: datetime


# ===== Smart Content Editor Models =====


class RewriteRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Content to rewrite")
    tone: str = Field(
        default="professional",
        description="casual, professional, witty, formal, friendly, authoritative, enthusiastic, empathetic",
    )
    style: str = Field(
        default="engaging",
        description="engaging, concise, descriptive, persuasive, storytelling, technical",
    )


class ExpandRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Content to expand")
    target_length: int = Field(
        default=500, ge=100, le=2000, description="Target word count"
    )


class CondenseRequest(BaseModel):
    content: str = Field(..., min_length=20, description="Content to condense")
    percentage: int = Field(
        default=50, ge=10, le=80, description="Reduction percentage"
    )


class OptimizeRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Content to optimize")
    platform: str = Field(
        ...,
        description="twitter, linkedin, blog, newsletter, instagram, tiktok, facebook, youtube",
    )


class RewriteResult(BaseModel):
    content: str
    tokens_used: int


class ExpandResult(BaseModel):
    content: str
    tokens_used: int
    original_length: int
    new_length: int


class CondenseResult(BaseModel):
    content: str
    tokens_used: int
    reduction_percentage: float


class OptimizeResult(BaseModel):
    content: str
    tokens_used: int
    platform: str
    optimizations_applied: List[str]


@router.post("/ai-suggestions/improve", response_model=AIImprovementSuggestion)
async def get_content_improvements(
    request: ContentImprovementRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Get AI suggestions to improve content quality."""
    usage_stats = check_and_increment_usage(str(user.id))

    supabase = get_supabase_admin_client()

    try:
        # Get the content
        content_result = (
            supabase.table("content")
            .select("*")
            .eq("id", str(request.content_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not content_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            )

        content = content_result.data
        original_text = content.get("original_text") or content.get("title", "")

        if not original_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No content text available for analysis",
            )

        # Generate improvement suggestions based on type
        system_prompts = {
            "readability": "You are an expert editor focused on improving readability. Suggest improvements for sentence structure, paragraph length, and flow. Keep the meaning intact but make it easier to read.",
            "engagement": "You are a content engagement expert. Suggest improvements to make the content more engaging, add hooks, improve transitions, and increase reader interest.",
            "clarity": "You are a clarity specialist. Suggest improvements to make the message clearer, remove ambiguity, and ensure the key points stand out.",
            "grammar": "You are a grammar and style expert. Fix grammar errors, improve word choice, and polish the writing while maintaining the original voice.",
        }

        system_prompt = system_prompts.get(
            request.suggestion_type, system_prompts["readability"]
        )

        prompt = f"""Analyze this content and provide an improved version:

Original Content:
{original_text}

Provide your response in this exact format:
IMPROVED_TEXT:
[Your improved version here]

EXPLANATION:
[Explain what you changed and why, 2-3 sentences]

CONFIDENCE:
[Score from 0.0 to 1.0]"""

        result = await groq_service.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=2000,
        )

        # Parse the result
        improved_text = ""
        explanation = ""
        confidence_score = 0.8

        if "IMPROVED_TEXT:" in result:
            parts = result.split("EXPLANATION:")
            if len(parts) > 1:
                improved_text = parts[0].replace("IMPROVED_TEXT:", "").strip()
                remaining = parts[1]

                if "CONFIDENCE:" in remaining:
                    exp_conf = remaining.split("CONFIDENCE:")
                    explanation = exp_conf[0].strip()
                    try:
                        confidence_score = float(exp_conf[1].strip()[:3])
                    except Exception:
                        confidence_score = 0.8
                else:
                    explanation = remaining.strip()
        else:
            # Fallback - use the whole response as improved text
            improved_text = result.strip()
            explanation = f"Content improved for {request.suggestion_type}"

        # Save suggestion to database
        suggestion_data = {
            "content_id": str(request.content_id),
            "user_id": str(user.id),
            "suggestion_type": request.suggestion_type,
            "original_text": original_text,
            "improved_text": improved_text,
            "explanation": explanation,
            "confidence_score": confidence_score,
            "applied": False,
        }

        result = supabase.table("ai_suggestions").insert(suggestion_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save suggestion",
            )

        return AIImprovementSuggestion(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/ai-suggestions/seo", response_model=SEOAnalysisResult)
async def get_seo_optimization(
    request: SEOOptimizationRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Get SEO optimization suggestions for content."""
    usage_stats = check_and_increment_usage(str(user.id))

    supabase = get_supabase_admin_client()

    try:
        # Get the content
        content_result = (
            supabase.table("content")
            .select("*")
            .eq("id", str(request.content_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not content_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            )

        content = content_result.data
        original_text = content.get("original_text") or content.get("title", "")

        if not original_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No content text available for SEO analysis",
            )

        keywords_str = (
            ", ".join(request.keywords) if request.keywords else "auto-detect"
        )
        target_audience = request.target_audience or "general"

        prompt = f"""Analyze this content for SEO and provide detailed optimization suggestions:

Content:
{original_text}

Target Keywords: {keywords_str}
Target Audience: {target_audience}

Provide your analysis in this exact format:
SEO_SCORE: [0-100]
READABILITY_SCORE: [0-100]

KEYWORD_DENSITY:
- keyword1: 2.5%
- keyword2: 1.8%

SUGGESTIONS:
1. [First SEO suggestion]
2. [Second SEO suggestion]

META_TITLE_SUGGESTION: [Suggested meta title, 50-60 chars]

META_DESCRIPTION_SUGGESTION: [Suggested meta description, 150-160 chars]

HEADING_STRUCTURE:
1. [Suggestion for H1/H2 structure]
2. [Another heading suggestion]"""

        system_prompt = """You are an SEO expert with deep knowledge of search engine optimization, keyword research, and content optimization. Provide actionable SEO advice."""

        result = await groq_service.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4,
            max_tokens=2500,
        )

        # Parse the result
        seo_score = 70
        readability_score = 75
        keyword_density = {}
        suggestions = []
        meta_title = None
        meta_description = None
        heading_suggestions = []

        try:
            if "SEO_SCORE:" in result:
                score_line = [l for l in result.split("\n") if "SEO_SCORE:" in l][0]
                seo_score = int("".join(filter(str.isdigit, score_line)))

            if "READABILITY_SCORE:" in result:
                score_line = [
                    l for l in result.split("\n") if "READABILITY_SCORE:" in l
                ][0]
                readability_score = int("".join(filter(str.isdigit, score_line)))

            if "KEYWORD_DENSITY:" in result:
                kd_section = result.split("KEYWORD_DENSITY:")[1].split("SUGGESTIONS:")[
                    0
                ]
                for line in kd_section.split("\n"):
                    if ":" in line and "-" in line:
                        parts = line.replace("-", "").strip().split(":")
                        if len(parts) == 2:
                            keyword_density[parts[0].strip()] = float(
                                parts[1].replace("%", "").strip()
                            )

            if "SUGGESTIONS:" in result:
                sug_section = result.split("SUGGESTIONS:")[1].split(
                    "META_TITLE_SUGGESTION:"
                )[0]
                for line in sug_section.split("\n"):
                    if line.strip() and (
                        line.strip()[0].isdigit() or line.strip().startswith("-")
                    ):
                        suggestions.append(
                            line.replace("-", "")
                            .replace("1.", "")
                            .replace("2.", "")
                            .replace("3.", "")
                            .strip()
                        )

            if "META_TITLE_SUGGESTION:" in result:
                mt_section = result.split("META_TITLE_SUGGESTION:")[1].split(
                    "META_DESCRIPTION_SUGGESTION:"
                )[0]
                meta_title = mt_section.strip()[:60]

            if "META_DESCRIPTION_SUGGESTION:" in result:
                md_section = result.split("META_DESCRIPTION_SUGGESTION:")[1].split(
                    "HEADING_STRUCTURE:"
                )[0]
                meta_description = md_section.strip()[:160]

            if "HEADING_STRUCTURE:" in result:
                hs_section = result.split("HEADING_STRUCTURE:")[1]
                for line in hs_section.split("\n"):
                    if line.strip() and (
                        line.strip()[0].isdigit() or line.strip().startswith("-")
                    ):
                        heading_suggestions.append(
                            line.replace("-", "")
                            .replace("1.", "")
                            .replace("2.", "")
                            .strip()
                        )

        except Exception as parse_error:
            logger.error(f"Parse error: {parse_error}")
            # Use defaults if parsing fails
            pass

        # Ensure we have reasonable defaults
        if not suggestions:
            suggestions = [
                "Add more relevant keywords throughout the content",
                "Include internal links to related content",
                "Optimize images with alt tags",
            ]

        if not heading_suggestions:
            heading_suggestions = [
                "Use H1 for the main title",
                "Break content into sections with H2 headings",
            ]

        if not keyword_density:
            keyword_density = {"primary_keyword": 2.0, "secondary_keyword": 1.5}

        # Save analysis to database
        analysis_data = {
            "content_id": str(request.content_id),
            "user_id": str(user.id),
            "seo_score": max(0, min(100, seo_score)),
            "keyword_density": keyword_density,
            "readability_score": max(0, min(100, readability_score)),
            "suggestions": suggestions,
            "meta_title_suggestion": meta_title,
            "meta_description_suggestion": meta_description,
            "heading_structure_suggestions": heading_suggestions,
        }

        result = supabase.table("seo_analyses").insert(analysis_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save SEO analysis",
            )

        return SEOAnalysisResult(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/ai-suggestions/tone", response_model=ToneAdjustmentResult)
async def adjust_content_tone(
    request: ToneAdjustmentRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Adjust content tone to match target style."""
    usage_stats = check_and_increment_usage(str(user.id))

    supabase = get_supabase_admin_client()

    try:
        # Get the content
        content_result = (
            supabase.table("content")
            .select("*")
            .eq("id", str(request.content_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not content_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            )

        content = content_result.data
        original_text = content.get("original_text") or content.get("title", "")

        if not original_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No content text available for tone adjustment",
            )

        # Analyze current tone first
        analysis_prompt = f"""Analyze the tone of this content in one word:

{original_text}

Respond with just the tone descriptor (e.g., formal, casual, professional, humorous)."""

        original_tone = await groq_service.generate_content(
            prompt=analysis_prompt,
            temperature=0.3,
            max_tokens=50,
        )
        original_tone = (
            original_tone.strip().lower().split()[0]
            if original_tone.strip()
            else "neutral"
        )

        # Generate tone-adjusted version
        tone_prompts = {
            "professional": "Rewrite this content in a professional, business-appropriate tone. Use clear, concise language. Avoid slang and casual expressions. Be authoritative yet approachable.",
            "casual": "Rewrite this content in a casual, conversational tone. Use everyday language. Be friendly and relatable. Use contractions and a relaxed style.",
            "humorous": "Rewrite this content with humor and wit. Add playful elements. Use clever wordplay where appropriate. Keep it light and entertaining while delivering the message.",
            "formal": "Rewrite this content in a formal, academic tone. Use sophisticated vocabulary. Avoid contractions. Maintain objectivity and professionalism.",
            "friendly": "Rewrite this content in a warm, friendly tone. Be welcoming and supportive. Use inclusive language. Make the reader feel like you're having a conversation with a friend.",
            "authoritative": "Rewrite this content with authority and confidence. Be decisive and clear. Use strong, confident statements. Position the content as expert advice.",
        }

        system_prompt = tone_prompts.get(request.tone, tone_prompts["professional"])

        prompt = f"""Rewrite this content with the specified tone:

Original Content:
{original_text}

Provide:
1. The rewritten content in the new tone
2. Three key characteristics of this tone that were applied"""

        result = await groq_service.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.6,
            max_tokens=2000,
        )

        adjusted_text = result.strip()

        # Determine tone characteristics
        tone_characteristics = {
            "tone_applied": request.tone,
            "vocabulary_level": (
                "elevated"
                if request.tone in ["formal", "professional", "authoritative"]
                else "conversational"
            ),
            "sentence_structure": (
                "complex" if request.tone in ["formal", "professional"] else "varied"
            ),
            "emotional_quality": (
                "neutral"
                if request.tone == "formal"
                else "warm" if request.tone == "friendly" else "confident"
            ),
        }

        # Save to database
        tone_data = {
            "content_id": str(request.content_id),
            "user_id": str(user.id),
            "original_tone": original_tone,
            "target_tone": request.tone,
            "adjusted_text": adjusted_text,
            "tone_characteristics": tone_characteristics,
        }

        result = supabase.table("tone_adjustments").insert(tone_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save tone adjustment",
            )

        return ToneAdjustmentResult(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/ai-suggestions/{content_id}", response_model=List[AIImprovementSuggestion]
)
async def list_suggestions(
    content_id: UUID, suggestion_type: Optional[str] = None, user=Depends(get_auth_user)
):
    """List all AI suggestions for a content item."""
    supabase = get_supabase_admin_client()

    try:
        query = (
            supabase.table("ai_suggestions")
            .select("*")
            .eq("content_id", str(content_id))
            .eq("user_id", str(user.id))
        )

        if suggestion_type:
            query = query.eq("suggestion_type", suggestion_type)

        query = query.order("created_at", desc=True)
        result = query.execute()

        return [AIImprovementSuggestion(**s) for s in result.data]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.patch(
    "/ai-suggestions/{suggestion_id}/apply", response_model=AIImprovementSuggestion
)
async def apply_suggestion(suggestion_id: UUID, user=Depends(get_auth_user)):
    """Mark a suggestion as applied and update the content."""
    supabase = get_supabase_admin_client()

    try:
        # Get the suggestion
        suggestion_result = (
            supabase.table("ai_suggestions")
            .select("*")
            .eq("id", str(suggestion_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not suggestion_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found",
            )

        suggestion = suggestion_result.data

        # Update the suggestion as applied
        update_result = (
            supabase.table("ai_suggestions")
            .update({"applied": True})
            .eq("id", str(suggestion_id))
            .execute()
        )

        # Update the content with the improved text
        supabase.table("content").update(
            {"original_text": suggestion["improved_text"], "updated_at": "now()"}
        ).eq("id", suggestion["content_id"]).execute()

        return AIImprovementSuggestion(**update_result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/ai-suggestions/{content_id}/seo", response_model=List[SEOAnalysisResult])
async def list_seo_analyses(content_id: UUID, user=Depends(get_auth_user)):
    """List all SEO analyses for a content item."""
    supabase = get_supabase_admin_client()

    try:
        result = (
            supabase.table("seo_analyses")
            .select("*")
            .eq("content_id", str(content_id))
            .eq("user_id", str(user.id))
            .order("created_at", desc=True)
            .execute()
        )

        return [SEOAnalysisResult(**a) for a in result.data]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/ai-suggestions/{content_id}/tone", response_model=List[ToneAdjustmentResult]
)
async def list_tone_adjustments(content_id: UUID, user=Depends(get_auth_user)):
    """List all tone adjustments for a content item."""
    supabase = get_supabase_admin_client()

    try:
        result = (
            supabase.table("tone_adjustments")
            .select("*")
            .eq("content_id", str(content_id))
            .eq("user_id", str(user.id))
            .order("created_at", desc=True)
            .execute()
        )

        return [ToneAdjustmentResult(**t) for t in result.data]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ===== Smart Content Editor Endpoints =====


@router.post("/ai-suggestions/rewrite", response_model=RewriteResult)
async def rewrite_content_endpoint(
    request: RewriteRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Rewrite content with different tone and style."""
    check_and_increment_usage(str(user.id))

    try:
        rewritten_text, tokens_used = await groq_service.rewrite_content(
            content=request.content,
            tone=request.tone,
            style=request.style,
        )

        return RewriteResult(
            content=rewritten_text,
            tokens_used=tokens_used,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rewrite content: {str(e)}",
        )


@router.post("/ai-suggestions/expand", response_model=ExpandResult)
async def expand_content_endpoint(
    request: ExpandRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Expand content to target length."""
    check_and_increment_usage(str(user.id))

    try:
        expanded_text, tokens_used = await groq_service.expand_content(
            content=request.content,
            target_length=request.target_length,
            focus_areas=[],
        )

        original_words = len(request.content.split())
        expanded_words = len(expanded_text.split())

        return ExpandResult(
            content=expanded_text,
            tokens_used=tokens_used,
            original_length=original_words,
            new_length=expanded_words,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to expand content: {str(e)}",
        )


@router.post("/ai-suggestions/condense", response_model=CondenseResult)
async def condense_content_endpoint(
    request: CondenseRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Condense content by percentage."""
    check_and_increment_usage(str(user.id))

    try:
        condensed_text, tokens_used = await groq_service.condense_content(
            content=request.content,
            target_percentage=request.percentage,
            preserve_key_points=True,
        )

        original_words = len(request.content.split())
        condensed_words = len(condensed_text.split())
        reduction_pct = (
            ((original_words - condensed_words) / original_words * 100)
            if original_words > 0
            else 0
        )

        return CondenseResult(
            content=condensed_text,
            tokens_used=tokens_used,
            reduction_percentage=round(reduction_pct, 1),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to condense content: {str(e)}",
        )


@router.post("/ai-suggestions/optimize", response_model=OptimizeResult)
async def optimize_content_endpoint(
    request: OptimizeRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Optimize content for specific platform."""
    check_and_increment_usage(str(user.id))

    try:
        result = await groq_service.optimize_content(
            content=request.content,
            platform=request.platform,
            include_hashtags=True,
            include_cta=True,
        )

        return OptimizeResult(
            content=result["optimized_content"],
            tokens_used=result["estimated_tokens"],
            platform=request.platform,
            optimizations_applied=result.get(
                "optimizations_applied", ["platform_formatting"]
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize content: {str(e)}",
        )

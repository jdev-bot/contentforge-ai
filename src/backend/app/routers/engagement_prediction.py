"""
Engagement Prediction router — AI-powered content performance prediction.

Provides endpoints for predicting content engagement metrics based on
content analysis. Uses a rule-based scoring engine by default, with
optional GROQ-powered AI enhancement when API key is available.
"""

import logging
import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from pydantic import BaseModel, Field

from app.core.rate_limit import (
    check_and_increment_usage,
    enforce_subscription_limit,
    rate_limit_dependency,
)
from app.core.supabase import get_supabase_admin_client
from app.routers.auth import get_auth_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/engagement-prediction", tags=["engagement-prediction"])


# ============== Models ==============


class PredictionRequest(BaseModel):
    """Request model for engagement prediction."""

    content: str = Field(..., min_length=1, max_length=10000, description="Content text to analyze")
    platform: str = Field(
        default="twitter",
        description="Target platform: twitter, linkedin, facebook, instagram",
    )
    content_id: Optional[str] = Field(None, description="Optional content ID for history tracking")
    use_ai: bool = Field(default=False, description="Use GROQ AI for enhanced prediction")


class FactorScores(BaseModel):
    """Individual factor scores."""

    readability: int = Field(..., ge=0, le=100)
    emotional_impact: int = Field(..., ge=0, le=100)
    hashtag_usage: int = Field(..., ge=0, le=100)
    optimal_length: int = Field(..., ge=0, le=100)
    call_to_action: int = Field(..., ge=0, le=100)


class PredictedEngagement(BaseModel):
    """Predicted engagement metrics."""

    likes: int
    comments: int
    shares: int
    impressions: int


class PredictionResponse(BaseModel):
    """Full prediction response."""

    score: int = Field(..., ge=0, le=100, description="Overall engagement score")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level")
    factors: FactorScores
    suggestions: List[str]
    predicted_engagement: PredictedEngagement
    best_posting_time: str
    platform: str
    content_length: int
    analyzed_at: datetime


class PredictionHistoryItem(BaseModel):
    """Historical prediction record."""

    id: str
    user_id: str
    content_id: Optional[str]
    platform: str
    score: int
    content_preview: str
    created_at: datetime


class PredictionHistoryResponse(BaseModel):
    """Paginated prediction history."""

    items: List[PredictionHistoryItem]
    total: int
    page: int
    limit: int


# ============== Rule-Based Scoring Engine ==============


# Emotional/power words by category
EMOTIONAL_WORDS = {
    "positive": [
        "amazing", "incredible", "exciting", "thrilling", "fantastic",
        "outstanding", "brilliant", "remarkable", "extraordinary", "inspiring",
        "powerful", "transform", "breakthrough", "revolutionary", "stunning",
        "unbelievable", "mind-blowing", "game-changing", "epic", "legendary",
    ],
    "urgency": [
        "now", "today", "urgent", "limited", "deadline", "hurry",
        "don't miss", "last chance", "act now", "before it's too late",
        "exclusive", "only", "closing", "final", "today only",
    ],
    "curiosity": [
        "secret", "hidden", "discover", "reveal", "uncover", "surprising",
        "shocking", "unexpected", "little-known", "untold", "mystery",
        "why", "how", "what if", "truth", "real reason",
    ],
}

CTA_PATTERNS = [
    r"\b(click|tap|check|try|start|join|subscribe|follow|share|comment|like|read|learn|get|download|sign up)\b",
    r"\b(let me know|tell me|drop a|share your|what do you think|what's your|agree\?)\b",
    r"\?{1,}\s*$",  # ending question mark
]

PLATFORM_CONFIG = {
    "twitter": {
        "optimal_length_range": (70, 200),
        "max_length": 280,
        "hashtag_ideal": (1, 3),
        "base_engagement": {"likes": 50, "comments": 5, "shares": 8, "impressions": 800},
        "best_times": ["09:00", "12:00", "17:00"],
    },
    "linkedin": {
        "optimal_length_range": (150, 600),
        "max_length": 3000,
        "hashtag_ideal": (3, 5),
        "base_engagement": {"likes": 80, "comments": 12, "shares": 15, "impressions": 1500},
        "best_times": ["08:00", "10:00", "12:00"],
    },
    "facebook": {
        "optimal_length_range": (80, 300),
        "max_length": 63206,
        "hashtag_ideal": (1, 2),
        "base_engagement": {"likes": 60, "comments": 8, "shares": 10, "impressions": 1000},
        "best_times": ["09:00", "13:00", "16:00"],
    },
    "instagram": {
        "optimal_length_range": (50, 150),
        "max_length": 2200,
        "hashtag_ideal": (5, 15),
        "base_engagement": {"likes": 120, "comments": 10, "shares": 5, "impressions": 2000},
        "best_times": ["07:00", "12:00", "19:00"],
    },
}


def _count_hashtags(text: str) -> int:
    """Count hashtag occurrences in text."""
    return len(re.findall(r"#\w+", text))


def _score_readability(text: str) -> int:
    """Score readability based on sentence length, word complexity, structure."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return 30

    # Average sentence length (ideal: 10-20 words)
    avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
    if 10 <= avg_len <= 20:
        len_score = 100
    elif 8 <= avg_len <= 25:
        len_score = 70
    else:
        len_score = max(20, 100 - abs(avg_len - 15) * 5)

    # Short first sentence bonus (hook)
    first_len = len(sentences[0].split())
    hook_bonus = 20 if first_len <= 12 else 0

    # Paragraph structure (line breaks help)
    line_breaks = text.count("\n")
    structure_bonus = min(15, line_breaks * 5)

    # Avoid all caps (shouting)
    caps_ratio = sum(1 for w in text.split() if w.isupper() and len(w) > 2) / max(len(text.split()), 1)
    caps_penalty = int(caps_ratio * 30)

    return max(0, min(100, int(len_score * 0.5 + hook_bonus + structure_bonus - caps_penalty)))


def _score_emotional_impact(text: str) -> int:
    """Score based on emotional/power words and sentence variety."""
    text_lower = text.lower()

    # Count emotional words
    emotional_count = 0
    for category, words in EMOTIONAL_WORDS.items():
        for word in words:
            if word in text_lower:
                emotional_count += 1

    # Base score from emotional word density
    word_count = len(text.split())
    density = emotional_count / max(word_count, 1)
    if density >= 0.05:
        base_score = 90
    elif density >= 0.03:
        base_score = 75
    elif density >= 0.01:
        base_score = 60
    else:
        base_score = 35

    # Exclamation marks (moderate is good, excessive is bad)
    excl_count = text.count("!")
    if excl_count == 0:
        excl_bonus = 0
    elif 1 <= excl_count <= 2:
        excl_bonus = 10
    else:
        excl_bonus = -10

    # Questions (engagement driver)
    question_count = text.count("?")
    question_bonus = min(15, question_count * 5)

    # Emoji presence
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    emoji_count = len(emoji_pattern.findall(text))
    emoji_bonus = min(10, emoji_count * 3)

    return max(0, min(100, base_score + excl_bonus + question_bonus + emoji_bonus))


def _score_hashtag_usage(text: str, platform: str) -> int:
    """Score hashtag usage based on platform-specific best practices."""
    count = _count_hashtags(text)
    config = PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG["twitter"])
    ideal_min, ideal_max = config["hashtag_ideal"]

    if ideal_min <= count <= ideal_max:
        return 95
    elif count == 0:
        return 20
    elif count < ideal_min:
        # Too few
        return max(30, 95 - (ideal_min - count) * 15)
    else:
        # Too many
        return max(20, 95 - (count - ideal_max) * 10)


def _score_optimal_length(text: str, platform: str) -> int:
    """Score based on content length vs platform optimal range."""
    char_len = len(text)
    config = PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG["twitter"])
    opt_min, opt_max = config["optimal_length_range"]
    max_len = config["max_length"]

    if opt_min <= char_len <= opt_max:
        return 100
    elif char_len < opt_min:
        # Too short — gradient down
        ratio = char_len / max(opt_min, 1)
        return max(20, int(ratio * 100))
    elif char_len <= opt_max * 1.5:
        # Slightly too long
        over_ratio = (char_len - opt_max) / max(opt_max, 1)
        return max(40, int(100 - over_ratio * 60))
    elif char_len > max_len:
        return 10
    else:
        return 30


def _score_call_to_action(text: str) -> int:
    """Score based on presence of calls-to-action."""
    text_lower = text.lower()
    cta_count = 0

    for pattern in CTA_PATTERNS:
        cta_count += len(re.findall(pattern, text_lower))

    if cta_count >= 3:
        return 95
    elif cta_count == 2:
        return 80
    elif cta_count == 1:
        return 60
    else:
        return 15


def _generate_suggestions(
    text: str, platform: str, factors: FactorScores
) -> List[str]:
    """Generate improvement suggestions based on factor scores."""
    suggestions = []

    if factors.hashtag_usage < 60:
        ideal = PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG["twitter"])["hashtag_ideal"]
        count = _count_hashtags(text)
        if count == 0:
            suggestions.append(
                f"Add {ideal[1]} relevant hashtags to increase discoverability"
            )
        elif count < ideal[0]:
            suggestions.append(
                f"Add {ideal[0] - count} more hashtags for better reach on {platform}"
            )
        else:
            suggestions.append("Reduce hashtag count — too many can look spammy")

    if factors.call_to_action < 50:
        suggestions.append(
            "Include a clear call-to-action to boost engagement (e.g., 'What do you think?', 'Try it now')"
        )

    if factors.optimal_length < 60:
        config = PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG["twitter"])
        opt_min, opt_max = config["optimal_length_range"]
        if len(text) < opt_min:
            suggestions.append(
                f"Expand your content — {platform} posts perform best at {opt_min}-{opt_max} characters"
            )
        else:
            suggestions.append(
                f"Shorten your content — {platform} posts perform best at {opt_min}-{opt_max} characters"
            )

    if factors.emotional_impact < 50:
        suggestions.append(
            "Use more engaging language — try power words like 'discover', 'transform', 'breakthrough'"
        )

    if factors.readability < 60:
        suggestions.append(
            "Improve readability with shorter sentences and line breaks"
        )

    # Best time suggestion
    config = PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG["twitter"])
    best_time = config["best_times"][0]
    suggestions.append(
        f"Consider posting around {best_time} for maximum reach on {platform}"
    )

    # Positive feedback if score is high
    if factors.readability >= 80:
        suggestions.append("Your content structure is strong — good readability!")

    if factors.emotional_impact >= 80:
        suggestions.append("Great emotional hook — your content grabs attention!")

    return suggestions[:6]  # Cap at 6 suggestions


def _predict_engagement_metrics(
    score: int, platform: str
) -> PredictedEngagement:
    """Calculate predicted engagement based on score and platform baselines."""
    config = PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG["twitter"])
    base = config["base_engagement"]

    # Scale by score (0-100 → 0.1-2.5x multiplier)
    multiplier = 0.1 + (score / 100) * 2.4

    return PredictedEngagement(
        likes=max(1, int(base["likes"] * multiplier)),
        comments=max(0, int(base["comments"] * multiplier)),
        shares=max(0, int(base["shares"] * multiplier)),
        impressions=max(10, int(base["impressions"] * multiplier)),
    )


def _get_best_posting_time(platform: str) -> str:
    """Get the best posting time for the platform."""
    config = PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG["twitter"])
    hour = config["best_times"][0]
    return f"{hour} EST"


def analyze_content(content: str, platform: str) -> PredictionResponse:
    """
    Analyze content and return engagement prediction.

    Uses rule-based scoring engine. Works without any AI API key.
    """
    # Calculate individual factor scores
    readability = _score_readability(content)
    emotional_impact = _score_emotional_impact(content)
    hashtag_usage = _score_hashtag_usage(content, platform)
    optimal_length = _score_optimal_length(content, platform)
    call_to_action = _score_call_to_action(content)

    factors = FactorScores(
        readability=readability,
        emotional_impact=emotional_impact,
        hashtag_usage=hashtag_usage,
        optimal_length=optimal_length,
        call_to_action=call_to_action,
    )

    # Weighted overall score
    weights = {
        "readability": 0.20,
        "emotional_impact": 0.25,
        "hashtag_usage": 0.15,
        "optimal_length": 0.20,
        "call_to_action": 0.20,
    }

    overall_score = sum(
        getattr(factors, k) * v for k, v in weights.items()
    )
    overall_score = max(0, min(100, int(overall_score)))

    # Confidence based on content length (longer = more data = more confident)
    word_count = len(content.split())
    if word_count >= 20:
        confidence = min(0.90, 0.60 + word_count * 0.005)
    elif word_count >= 5:
        confidence = 0.40 + word_count * 0.01
    else:
        confidence = 0.25

    suggestions = _generate_suggestions(content, platform, factors)
    predicted_engagement = _predict_engagement_metrics(overall_score, platform)
    best_time = _get_best_posting_time(platform)

    return PredictionResponse(
        score=overall_score,
        confidence=round(confidence, 2),
        factors=factors,
        suggestions=suggestions,
        predicted_engagement=predicted_engagement,
        best_posting_time=best_time,
        platform=platform,
        content_length=len(content),
        analyzed_at=datetime.now(timezone.utc),
    )


# ============== Endpoints ==============


@router.post("/analyze", response_model=PredictionResponse)
async def predict_engagement(
    request: PredictionRequest,
    user=Depends(get_auth_user),
    _: None = Depends(rate_limit_dependency),
):
    """
    Analyze content and predict engagement metrics.

    Uses a rule-based scoring engine that evaluates readability,
    emotional impact, hashtag usage, content length, and call-to-action
    presence. Optionally uses GROQ AI for enhanced analysis.
    """
    try:
        # Check usage limits
        await check_and_increment_usage(str(user.id), "engagement_prediction")

        platform = request.platform.lower()
        if platform not in PLATFORM_CONFIG:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}. Supported: {list(PLATFORM_CONFIG.keys())}",
            )

        # Try AI-enhanced prediction if requested and GROQ key is available
        if request.use_ai:
            try:
                from app.services.groq_service import groq_service

                ai_result = await groq_service.generate_content(
                    prompt=f"""Analyze this social media content for {platform} and return JSON:
{{
  "score": <0-100 overall engagement prediction>,
  "confidence": <0-1 confidence level>,
  "readability": <0-100>,
  "emotional_impact": <0-100>,
  "hashtag_usage": <0-100>,
  "optimal_length": <0-100>,
  "call_to_action": <0-100>,
  "suggestions": ["<suggestion1>", "<suggestion2>", ...],
  "predicted_likes": <number>,
  "predicted_comments": <number>,
  "predicted_shares": <number>,
  "predicted_impressions": <number>,
  "best_posting_time": "<HH:MM timezone>"
}}

Content to analyze:
{request.content}""",
                    system_prompt="You are a social media engagement analyst. Return only valid JSON, no other text.",
                    temperature=0.3,
                    max_tokens=1000,
                )

                import json

                # Parse AI response
                ai_data = json.loads(ai_result.strip())
                return PredictionResponse(
                    score=ai_data.get("score", 50),
                    confidence=ai_data.get("confidence", 0.5),
                    factors=FactorScores(
                        readability=ai_data.get("readability", 50),
                        emotional_impact=ai_data.get("emotional_impact", 50),
                        hashtag_usage=ai_data.get("hashtag_usage", 50),
                        optimal_length=ai_data.get("optimal_length", 50),
                        call_to_action=ai_data.get("call_to_action", 50),
                    ),
                    suggestions=ai_data.get("suggestions", []),
                    predicted_engagement=PredictedEngagement(
                        likes=ai_data.get("predicted_likes", 50),
                        comments=ai_data.get("predicted_comments", 5),
                        shares=ai_data.get("predicted_shares", 5),
                        impressions=ai_data.get("predicted_impressions", 500),
                    ),
                    best_posting_time=ai_data.get("best_posting_time", "09:00 EST"),
                    platform=platform,
                    content_length=len(request.content),
                    analyzed_at=datetime.now(timezone.utc),
                )

            except Exception as ai_err:
                logger.warning(f"AI prediction failed, falling back to rule-based: {ai_err}")
                # Fall through to rule-based

        # Rule-based prediction (always works, no AI key needed)
        result = analyze_content(request.content, platform)

        # Save to history
        try:
            supabase = get_supabase_admin_client()
            supabase.table("engagement_predictions").insert({
                "user_id": str(user.id),
                "content_id": request.content_id,
                "platform": platform,
                "score": result.score,
                "content_preview": request.content[:200],
                "factors": result.factors.model_dump(),
                "predicted_engagement": result.predicted_engagement.model_dump(),
                "suggestions": result.suggestions,
            }).execute()
        except Exception as save_err:
            logger.warning(f"Failed to save prediction history: {save_err}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Engagement prediction failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@router.get("/history", response_model=PredictionHistoryResponse)
async def get_prediction_history(
    limit: int = 20,
    offset: int = 0,
    user=Depends(get_auth_user),
):
    """
    Get user's prediction history.
    """
    try:
        supabase = get_supabase_admin_client()
        user_id = str(user.id)

        # Get total count
        count_result = (
            supabase.table("engagement_predictions")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .execute()
        )
        total = count_result.count or 0

        # Get items
        result = (
            supabase.table("engagement_predictions")
            .select("id, user_id, content_id, platform, score, content_preview, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .offset(offset)
            .execute()
        )

        items = [
            PredictionHistoryItem(
                id=str(item["id"]),
                user_id=item["user_id"],
                content_id=item.get("content_id"),
                platform=item["platform"],
                score=item["score"],
                content_preview=item["content_preview"],
                created_at=item["created_at"],
            )
            for item in (result.data or [])
        ]

        return PredictionHistoryResponse(
            items=items,
            total=total,
            page=(offset // limit) + 1,
            limit=limit,
        )

    except Exception as e:
        logger.error(f"Failed to get prediction history: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/platform-config")
async def get_platform_config(
    user=Depends(get_auth_user),
):
    """
    Get platform-specific configuration for engagement prediction.
    Returns optimal lengths, hashtag counts, best posting times per platform.
    """
    return {
        "platforms": {
            name: {
                "optimal_length_range": config["optimal_length_range"],
                "max_length": config["max_length"],
                "hashtag_ideal": config["hashtag_ideal"],
                "best_times": config["best_times"],
                "base_engagement": config["base_engagement"],
            }
            for name, config in PLATFORM_CONFIG.items()
        }
    }
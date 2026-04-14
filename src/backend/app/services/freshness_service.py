"""
Content Freshness Scoring Service.

This service analyzes content freshness based on:
- Age (0-40 points): Newer content scores higher
- Engagement (0-40 points): Based on mock/implied metrics
- Trend relevance (0-20 points): Keywords still trending
"""

import random
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.supabase import get_supabase_client


class FreshnessFactors:
    """Freshness scoring factors with weights."""

    AGE_MAX_POINTS = 40
    ENGAGEMENT_MAX_POINTS = 40
    TREND_MAX_POINTS = 20

    # Age thresholds (days)
    AGE_FRESH = 7  # 0-7 days: full points
    AGE_RECENT = 30  # 8-30 days: high points
    AGE_MODERATE = 90  # 31-90 days: moderate points
    AGE_STALE = 180  # 91-180 days: low points

    # Engagement thresholds (mock metrics)
    ENGAGEMENT_HIGH = 100  # 100+ interactions: full points
    ENGAGEMENT_GOOD = 50  # 50-99 interactions: high points
    ENGAGEMENT_MODERATE = 20  # 20-49 interactions: moderate points

    # Trending keywords (mock - in production this would come from an API)
    TRENDING_KEYWORDS = [
        "ai",
        "artificial intelligence",
        "machine learning",
        "ml",
        "automation",
        "workflow",
        "productivity",
        "content",
        "marketing",
        "social media",
        "growth",
        "analytics",
        "data",
        "insights",
        "trends",
        "2026",
        "strategy",
    ]


class FreshnessService:
    """Service for analyzing and scoring content freshness."""

    def __init__(self):
        self.factors = FreshnessFactors()

    def calculate_age_score(self, age_days: int) -> int:
        """
        Calculate age score (0-40 points).

        Newer content gets higher scores:
        - 0-7 days: 40 points
        - 8-30 days: 35 points
        - 31-90 days: 25 points
        - 91-180 days: 15 points
        - 180+ days: 5 points
        """
        if age_days <= self.factors.AGE_FRESH:
            return self.factors.AGE_MAX_POINTS
        elif age_days <= self.factors.AGE_RECENT:
            return int(self.factors.AGE_MAX_POINTS * 0.875)  # 35
        elif age_days <= self.factors.AGE_MODERATE:
            return int(self.factors.AGE_MAX_POINTS * 0.625)  # 25
        elif age_days <= self.factors.AGE_STALE:
            return int(self.factors.AGE_MAX_POINTS * 0.375)  # 15
        else:
            return 5

    def calculate_engagement_score(self, content: Dict[str, Any]) -> int:
        """
        Calculate engagement score (0-40 points).

        In production, this would use actual engagement metrics.
        For now, we derive implied engagement from content quality signals.
        """
        score = 0
        original_text = content.get("original_text", "") or ""
        word_count = content.get("word_count", 0) or 0

        # Word count as a quality signal (more comprehensive content)
        if word_count > 1000:
            score += 15
        elif word_count > 500:
            score += 10
        elif word_count > 100:
            score += 5

        # Content has source URL (indicates original source)
        if content.get("source_url"):
            score += 5

        # Content status is completed
        if content.get("status") == "completed":
            score += 5

        # Has generated assets (indicates usage)
        score += min(15, self._count_generated_assets(str(content.get("id", ""))) * 3)

        return min(score, self.factors.ENGAGEMENT_MAX_POINTS)

    def _count_generated_assets(self, content_id: str) -> int:
        """Count generated assets for content (used as engagement signal)."""
        if not content_id:
            return 0

        try:
            supabase = get_supabase_client()
            result = (
                supabase.table("generated_assets")
                .select("count", count="exact")
                .eq("content_id", content_id)
                .execute()
            )
            return result.count or 0
        except Exception:
            return 0

    def calculate_trend_score(self, content: Dict[str, Any]) -> int:
        """
        Calculate trend relevance score (0-20 points).

        Analyzes content for trending keywords.
        """
        original_text = (content.get("original_text", "") or "").lower()
        title = (content.get("title", "") or "").lower()

        combined_text = f"{title} {original_text}"

        # Count trending keywords
        trending_matches = sum(
            1
            for keyword in self.factors.TRENDING_KEYWORDS
            if keyword.lower() in combined_text
        )

        # Score based on keyword matches
        if trending_matches >= 5:
            return self.factors.TREND_MAX_POINTS
        elif trending_matches >= 3:
            return int(self.factors.TREND_MAX_POINTS * 0.75)  # 15
        elif trending_matches >= 1:
            return int(self.factors.TREND_MAX_POINTS * 0.5)  # 10
        else:
            return 5  # Base score for any content

    def generate_recommendations(
        self,
        age_days: int,
        age_score: int,
        engagement_score: int,
        trend_score: int,
        content: Dict[str, Any],
    ) -> List[str]:
        """
        Generate improvement recommendations based on scores.

        Recommendations:
        - "Update statistics" if data is old
        - "Add recent examples" if examples are dated
        - "Refresh headline" if CTR declined (low engagement)
        - "Add trending keywords" if relevance dropped
        """
        recommendations = []

        # Age-based recommendations
        if age_days > self.factors.AGE_MODERATE:
            recommendations.append("Update statistics")
        if age_days > self.factors.AGE_STALE:
            recommendations.append("Add recent examples")

        # Engagement-based recommendations
        if engagement_score < 20:
            recommendations.append("Refresh headline")
            recommendations.append("Add compelling call-to-action")

        # Trend-based recommendations
        if trend_score < 10:
            recommendations.append("Add trending keywords")
        if trend_score < 15:
            recommendations.append("Update to current industry trends")

        # Content-specific recommendations
        word_count = content.get("word_count", 0) or 0
        if word_count < 300:
            recommendations.append("Expand content depth")

        # General freshness recommendations
        if age_days > self.factors.AGE_RECENT:
            recommendations.append("Review and update content")

        return recommendations[:5]  # Return top 5 recommendations

    def analyze_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete freshness analysis on content.

        Returns a dictionary with:
        - freshness_score: Overall score (0-100)
        - age_days: Age in days
        - factors: Breakdown of scoring factors
        - recommendations: List of improvement suggestions
        """
        # Calculate age
        created_at = content.get("created_at")
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            age_days = (datetime.now(created_at.tzinfo) - created_at).days
        else:
            age_days = 0

        # Calculate individual scores
        age_score = self.calculate_age_score(age_days)
        engagement_score = self.calculate_engagement_score(content)
        trend_score = self.calculate_trend_score(content)

        # Calculate total score
        freshness_score = age_score + engagement_score + trend_score

        # Generate recommendations
        recommendations = self.generate_recommendations(
            age_days, age_score, engagement_score, trend_score, content
        )

        # Normalize factors to sum to 1.0
        total_raw = age_score + engagement_score + trend_score
        if total_raw > 0:
            factors = {
                "age_factor": round(age_score / total_raw, 2),
                "engagement_factor": round(engagement_score / total_raw, 2),
                "trend_factor": round(trend_score / total_raw, 2),
                "age_points": age_score,
                "engagement_points": engagement_score,
                "trend_points": trend_score,
            }
        else:
            factors = {
                "age_factor": 0,
                "engagement_factor": 0,
                "trend_factor": 0,
                "age_points": 0,
                "engagement_points": 0,
                "trend_points": 0,
            }

        return {
            "freshness_score": freshness_score,
            "age_days": age_days,
            "factors": factors,
            "recommendations": recommendations,
        }

    def get_freshness_status(self, score: int) -> str:
        """Get human-readable freshness status."""
        if score >= 80:
            return "fresh"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "aging"
        elif score >= 20:
            return "stale"
        else:
            return "outdated"

    def should_refresh(self, score: int, age_days: int) -> bool:
        """Determine if content should be refreshed."""
        return score < 50 or age_days > 90


# Singleton instance
freshness_service = FreshnessService()

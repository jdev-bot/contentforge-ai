"""
Content Quality Scoring Service.

Multi-dimensional quality analysis using Groq AI:
- Readability (Flesch-Kincaid, Gunning Fog)
- SEO optimization (keyword density, heading structure, meta quality)
- Engagement potential (hook strength, CTAs, emotional appeal)
- Grammar & style (sentence variety, passive voice, clarity)
- Brand consistency (tone matching, vocabulary alignment)
"""

import json
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.cache import cache
from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.services.groq_service import groq_service

logger = logging.getLogger(__name__)

# Weights for composite score
DIMENSION_WEIGHTS = {
    "readability": 0.25,
    "seo": 0.20,
    "engagement": 0.25,
    "grammar": 0.15,
    "brand": 0.15,
}

CACHE_PREFIX = "quality"
CACHE_TTL_SECONDS = 1800  # 30 min


class QualityService:
    """Service for multi-dimensional content quality scoring."""

    def __init__(self):
        self._supabase = None

    @property
    def supabase(self):
        """Lazy Supabase client init."""
        if self._supabase is None:
            self._supabase = get_supabase_admin_client()
        return self._supabase

    # ------------------------------------------------------------------ #
    #  AI-powered scoring                                                  #
    # ------------------------------------------------------------------ #

    async def analyze_quality(
        self, text: str, brand_voice: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze content quality across five dimensions using Groq AI.

        Returns a dict with keys:
            overall_score, readability, seo, engagement, grammar, brand,
            suggestions (list of strings)
        """
        brand_instruction = ""
        if brand_voice:
            brand_instruction = f"\n\nBrand voice reference: {json.dumps(brand_voice)}"

        system_prompt = (
            "You are a senior content quality auditor. "
            "Score the provided text on five dimensions, each 0-100.\n"
            "Dimensions:\n"
            "1. READABILITY – Flesch-Kincaid ease, Gunning Fog, sentence/paragraph length.\n"
            "2. SEO – keyword density, heading structure, meta-readiness.\n"
            "3. ENGAGEMENT – hook strength, CTAs, emotional appeal.\n"
            "4. GRAMMAR – sentence variety, passive-voice ratio, clarity.\n"
            "5. BRAND – tone consistency, vocabulary alignment with brand voice."
            f"{brand_instruction}\n\n"
            "Respond ONLY with valid JSON in this exact schema (no markdown fences):\n"
            '{"readability": <int 0-100>, "seo": <int 0-100>, '
            '"engagement": <int 0-100>, "grammar": <int 0-100>, '
            '"brand": <int 0-100>, '
            '"suggestions": ["<suggestion1>", "<suggestion2>", ...]}'
        )

        prompt = f"Analyze the quality of this content:\n\n{text}"

        raw = await groq_service.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1200,
        )

        # Strip possible markdown fences
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Groq returned non-JSON quality response, using defaults")
            parsed = {
                "readability": 50,
                "seo": 50,
                "engagement": 50,
                "grammar": 50,
                "brand": 50,
                "suggestions": ["Could not parse AI response; please retry."],
            }

        # Clamp each dimension to 0-100
        for key in ("readability", "seo", "engagement", "grammar", "brand"):
            parsed[key] = max(0, min(100, int(parsed.get(key, 50))))

        if not isinstance(parsed.get("suggestions"), list):
            parsed["suggestions"] = ["No suggestions returned."]

        overall = self._compute_overall(parsed)
        parsed["overall_score"] = overall
        return parsed

    def _compute_overall(self, scores: Dict[str, Any]) -> int:
        """Weighted composite 0-100."""
        total = sum(
            scores.get(dim, 0) * weight for dim, weight in DIMENSION_WEIGHTS.items()
        )
        return max(0, min(100, round(total)))

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #

    async def store_score(
        self,
        content_id: UUID,
        user_id: UUID,
        scores: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Persist a quality score row in Supabase."""
        row = {
            "content_id": str(content_id),
            "user_id": str(user_id),
            "overall_score": scores["overall_score"],
            "readability": scores["readability"],
            "seo": scores["seo"],
            "engagement": scores["engagement"],
            "grammar": scores["grammar"],
            "brand": scores["brand"],
            "suggestions": scores.get("suggestions", []),
        }

        result = self.supabase.table("quality_scores").insert(row).execute()
        # Invalidate cache
        cache.delete(str(content_id), prefix=CACHE_PREFIX)
        cache.delete(f"history:{content_id}", prefix=CACHE_PREFIX)
        return result.data[0] if result.data else row

    async def get_score(
        self, content_id: UUID, user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Fetch the latest quality score for a content item (with cache)."""
        cached = cache.get(str(content_id), prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        result = (
            self.supabase.table("quality_scores")
            .select("*")
            .eq("content_id", str(content_id))
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if not result.data:
            return None

        row = result.data[0]
        cache.set(str(content_id), row, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return row

    async def get_history(
        self,
        content_id: UUID,
        user_id: UUID,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Fetch quality score history for a content item."""
        cached = cache.get(f"history:{content_id}", prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        result = (
            self.supabase.table("quality_scores")
            .select("*")
            .eq("content_id", str(content_id))
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        rows = result.data or []
        cache.set(
            f"history:{content_id}", rows, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX
        )
        return rows

    async def get_suggestions(self, content_id: UUID, user_id: UUID) -> List[str]:
        """Return improvement suggestions from the most recent score."""
        score = await self.get_score(content_id, user_id)
        if score is None:
            return []
        return score.get("suggestions", [])

    async def batch_analyze(
        self,
        items: List[Dict[str, Any]],
        user_id: UUID,
    ) -> List[Dict[str, Any]]:
        """
        Analyze a batch of content items.

        Each item dict must have at least 'content_id' and 'text'.
        Brand voice is optional: 'brand_voice'.
        """
        results = []
        for item in items:
            content_id = item["content_id"]
            text = item["text"]
            brand_voice = item.get("brand_voice")

            scores = await self.analyze_quality(text, brand_voice=brand_voice)
            stored = await self.store_score(
                content_id=content_id,
                user_id=user_id,
                scores=scores,
            )
            results.append(stored)
        return results


# Singleton
quality_service = QualityService()

"""
Sentiment Analysis Service.

Multi-level sentiment analysis using Groq AI:
- Overall sentiment: positive, negative, neutral, mixed
- Sentiment score: -1.0 to +1.0 continuous scale
- Emotion detection: joy, anger, sadness, fear, surprise, disgust
- Aspect-based sentiment: per-section/paragraph analysis
- Tone detection: formal, casual, urgent, persuasive, informative
"""

import json
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.cache import cache
from app.core.supabase import get_supabase_client
from app.services.groq_service import groq_service

logger = logging.getLogger(__name__)

CACHE_PREFIX = "sentiment"
CACHE_TTL_SECONDS = 3600  # 1 hour


class SentimentService:
    """Service for multi-level sentiment analysis."""

    def __init__(self):
        self._supabase = None

    @property
    def supabase(self):
        """Lazy Supabase client init."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    # ------------------------------------------------------------------ #
    #  AI-powered analysis                                                 #
    # ------------------------------------------------------------------ #

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Perform multi-level sentiment analysis on text using Groq AI.

        Returns dict with keys:
            sentiment, score, emotions, aspects, tone
        """
        system_prompt = (
            "You are an expert sentiment analyst. Analyze the provided text and return "
            "ONLY valid JSON (no markdown fences) matching this schema:\n"
            "{\n"
            '  "sentiment": "<positive|negative|neutral|mixed>",\n'
            '  "score": <float between -1.0 and 1.0>,\n'
            '  "emotions": {\n'
            '    "joy": <float 0-1>,\n'
            '    "anger": <float 0-1>,\n'
            '    "sadness": <float 0-1>,\n'
            '    "fear": <float 0-1>,\n'
            '    "surprise": <float 0-1>,\n'
            '    "disgust": <float 0-1>\n'
            "  },\n"
            '  "aspects": [\n'
            "    {\n"
            '      "section": "<brief quote or summary>",\n'
            '      "sentiment": "<positive|negative|neutral|mixed>",\n'
            '      "score": <float -1.0 to 1.0>\n'
            "    }\n"
            "  ],\n"
            '  "tone": "<formal|casual|urgent|persuasive|informative>"\n'
            "}"
        )

        prompt = f"Analyze the sentiment of this text:\n\n{text}"

        raw = await groq_service.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=2000,
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
            logger.warning("Groq returned non-JSON sentiment response, using defaults")
            parsed = {
                "sentiment": "neutral",
                "score": 0.0,
                "emotions": {
                    "joy": 0.0,
                    "anger": 0.0,
                    "sadness": 0.0,
                    "fear": 0.0,
                    "surprise": 0.0,
                    "disgust": 0.0,
                },
                "aspects": [],
                "tone": "informative",
            }

        # Normalise / clamp values
        valid_sentiments = {"positive", "negative", "neutral", "mixed"}
        parsed["sentiment"] = parsed.get("sentiment", "neutral")
        if parsed["sentiment"] not in valid_sentiments:
            parsed["sentiment"] = "neutral"

        parsed["score"] = max(-1.0, min(1.0, float(parsed.get("score", 0.0))))

        emotions = parsed.get("emotions", {})
        for emo in ("joy", "anger", "sadness", "fear", "surprise", "disgust"):
            emotions[emo] = max(0.0, min(1.0, float(emotions.get(emo, 0.0))))
        parsed["emotions"] = emotions

        aspects = parsed.get("aspects", [])
        if not isinstance(aspects, list):
            aspects = []
        for aspect in aspects:
            if not isinstance(aspect, dict):
                continue
            aspect["sentiment"] = aspect.get("sentiment", "neutral")
            if aspect["sentiment"] not in valid_sentiments:
                aspect["sentiment"] = "neutral"
            aspect["score"] = max(-1.0, min(1.0, float(aspect.get("score", 0.0))))
        parsed["aspects"] = aspects

        valid_tones = {"formal", "casual", "urgent", "persuasive", "informative"}
        parsed["tone"] = parsed.get("tone", "informative")
        if parsed["tone"] not in valid_tones:
            parsed["tone"] = "informative"

        return parsed

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #

    async def store_analysis(
        self,
        content_id: UUID,
        user_id: UUID,
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Persist a sentiment analysis row in Supabase."""
        row = {
            "content_id": str(content_id),
            "user_id": str(user_id),
            "sentiment": analysis["sentiment"],
            "score": analysis["score"],
            "emotions": analysis["emotions"],
            "aspects": analysis["aspects"],
            "tone": analysis["tone"],
        }

        result = self.supabase.table("sentiment_analyses").insert(row).execute()
        # Invalidate caches
        cache.delete(str(content_id), prefix=CACHE_PREFIX)
        cache.delete(f"trends:{content_id}", prefix=CACHE_PREFIX)
        return result.data[0] if result.data else row

    async def get_analysis(
        self,
        content_id: UUID,
        user_id: UUID,
    ) -> Optional[Dict[str, Any]]:
        """Fetch the latest sentiment analysis for a content item (with cache)."""
        cached = cache.get(str(content_id), prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        result = (
            self.supabase.table("sentiment_analyses")
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

    async def get_trends(
        self,
        content_id: UUID,
        user_id: UUID,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get sentiment trend history for a content item."""
        cached = cache.get(f"trends:{content_id}", prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        result = (
            self.supabase.table("sentiment_analyses")
            .select("*")
            .eq("content_id", str(content_id))
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        rows = result.data or []
        cache.set(
            f"trends:{content_id}", rows, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX
        )
        return rows

    async def get_distribution(self, user_id: UUID) -> Dict[str, Any]:
        """Get sentiment distribution across all user content."""
        result = (
            self.supabase.table("sentiment_analyses")
            .select("sentiment")
            .eq("user_id", str(user_id))
            .execute()
        )

        rows = result.data or []
        distribution = {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0}
        for row in rows:
            s = row.get("sentiment", "neutral")
            if s in distribution:
                distribution[s] += 1

        total = sum(distribution.values())
        percentages = {}
        if total > 0:
            percentages = {
                k: round(v / total * 100, 1) for k, v in distribution.items()
            }

        return {
            "total_analyses": total,
            "distribution": distribution,
            "percentages": percentages,
        }

    async def batch_analyze(
        self,
        items: List[Dict[str, Any]],
        user_id: UUID,
    ) -> List[Dict[str, Any]]:
        """
        Batch analyze multiple content items.

        Each item dict must have 'content_id' and 'text'.
        """
        results = []
        for item in items:
            content_id = item["content_id"]
            text = item["text"]

            analysis = await self.analyze_sentiment(text)
            stored = await self.store_analysis(
                content_id=content_id,
                user_id=user_id,
                analysis=analysis,
            )
            results.append(stored)
        return results


# Singleton
sentiment_service = SentimentService()

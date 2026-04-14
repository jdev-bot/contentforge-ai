"""
Tests for Sentiment Analysis API and Service.

Covers:
- SentimentService analysis logic
- API endpoints
- Caching behaviour
- Batch operations
- Distribution endpoint
"""

import pytest
import json
from datetime import datetime
from uuid import uuid4, UUID
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from app.services.sentiment_service import SentimentService, sentiment_service

# =========================================================================== #
#  Service unit tests                                                          #
# =========================================================================== #


class TestSentimentServiceAnalyze:
    """Tests for the AI-powered sentiment analysis method."""

    @pytest.mark.asyncio
    async def test_analyze_returns_required_keys(self):
        """Result should contain all expected keys."""
        mock_ai_response = json.dumps(
            {
                "sentiment": "positive",
                "score": 0.75,
                "emotions": {
                    "joy": 0.8,
                    "anger": 0.1,
                    "sadness": 0.05,
                    "fear": 0.02,
                    "surprise": 0.5,
                    "disgust": 0.01,
                },
                "aspects": [
                    {"section": "intro", "sentiment": "positive", "score": 0.8}
                ],
                "tone": "informative",
            }
        )

        svc = SentimentService()
        svc._supabase = MagicMock()
        with patch("app.services.sentiment_service.groq_service") as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value=mock_ai_response)
            result = await svc.analyze_sentiment("Great product, I love it!")

        assert result["sentiment"] in {"positive", "negative", "neutral", "mixed"}
        assert -1.0 <= result["score"] <= 1.0
        assert "emotions" in result
        assert "tone" in result
        assert isinstance(result["aspects"], list)

    @pytest.mark.asyncio
    async def test_analyze_handles_bad_json(self):
        """Non-JSON response should fall back to defaults."""
        svc = SentimentService()
        svc._supabase = MagicMock()
        with patch("app.services.sentiment_service.groq_service") as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value="Not JSON")
            result = await svc.analyze_sentiment("Some text")

        assert result["sentiment"] == "neutral"
        assert result["score"] == 0.0

    @pytest.mark.asyncio
    async def test_analyze_clamps_sentiment_score(self):
        """Score should be clamped to [-1.0, 1.0]."""
        mock_ai_response = json.dumps(
            {
                "sentiment": "positive",
                "score": 1.5,  # over limit
                "emotions": {
                    "joy": 0.5,
                    "anger": 0.5,
                    "sadness": 0.5,
                    "fear": 0.5,
                    "surprise": 0.5,
                    "disgust": 0.5,
                },
                "aspects": [],
                "tone": "informative",
            }
        )

        svc = SentimentService()
        svc._supabase = MagicMock()
        with patch("app.services.sentiment_service.groq_service") as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value=mock_ai_response)
            result = await svc.analyze_sentiment("Test")

        assert result["score"] == 1.0  # Clamped

    @pytest.mark.asyncio
    async def test_analyze_normalizes_invalid_sentiment(self):
        """Invalid sentiment values should default to neutral."""
        mock_ai_response = json.dumps(
            {
                "sentiment": "excited",  # invalid
                "score": 0.5,
                "emotions": {
                    "joy": 0.9,
                    "anger": 0.0,
                    "sadness": 0.0,
                    "fear": 0.0,
                    "surprise": 0.3,
                    "disgust": 0.0,
                },
                "aspects": [],
                "tone": "casual",
            }
        )

        svc = SentimentService()
        svc._supabase = MagicMock()
        with patch("app.services.sentiment_service.groq_service") as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value=mock_ai_response)
            result = await svc.analyze_sentiment("Excited text")

        assert result["sentiment"] == "neutral"

    @pytest.mark.asyncio
    async def test_analyze_normalizes_invalid_tone(self):
        """Invalid tone values should default to informative."""
        mock_ai_response = json.dumps(
            {
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
                "tone": "sarcastic",  # invalid
            }
        )

        svc = SentimentService()
        svc._supabase = MagicMock()
        with patch("app.services.sentiment_service.groq_service") as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value=mock_ai_response)
            result = await svc.analyze_sentiment("Some text")

        assert result["tone"] == "informative"

    @pytest.mark.asyncio
    async def test_analyze_clamps_emotions(self):
        """Emotion scores should be clamped to [0, 1]."""
        mock_ai_response = json.dumps(
            {
                "sentiment": "positive",
                "score": 0.5,
                "emotions": {
                    "joy": 1.5,
                    "anger": -0.2,
                    "sadness": 0.3,
                    "fear": 0.1,
                    "surprise": 0.8,
                    "disgust": 0.0,
                },
                "aspects": [],
                "tone": "formal",
            }
        )

        svc = SentimentService()
        svc._supabase = MagicMock()
        with patch("app.services.sentiment_service.groq_service") as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value=mock_ai_response)
            result = await svc.analyze_sentiment("Test")

        assert result["emotions"]["joy"] == 1.0  # clamped from 1.5
        assert result["emotions"]["anger"] == 0.0  # clamped from -0.2

    @pytest.mark.asyncio
    async def test_analyze_strips_markdown_fences(self):
        """Groq may wrap JSON in markdown fences."""
        raw = '```json\n{"sentiment": "negative", "score": -0.6, "emotions": {"joy": 0.05, "anger": 0.7, "sadness": 0.4, "fear": 0.2, "surprise": 0.1, "disgust": 0.3}, "aspects": [{"section": "complaint", "sentiment": "negative", "score": -0.8}], "tone": "urgent"}\n```'
        svc = SentimentService()
        svc._supabase = MagicMock()
        with patch("app.services.sentiment_service.groq_service") as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value=raw)
            result = await svc.analyze_sentiment("I hate this product")

        assert result["sentiment"] == "negative"
        assert result["score"] == -0.6

    @pytest.mark.asyncio
    async def test_analyze_aspect_sentiment_normalization(self):
        """Aspect sentiment values should be normalized."""
        mock_ai_response = json.dumps(
            {
                "sentiment": "mixed",
                "score": 0.2,
                "emotions": {
                    "joy": 0.4,
                    "anger": 0.3,
                    "sadness": 0.1,
                    "fear": 0.0,
                    "surprise": 0.2,
                    "disgust": 0.1,
                },
                "aspects": [
                    {"section": "good part", "sentiment": "positive", "score": 0.7},
                    {"section": "bad part", "sentiment": "negative", "score": -0.5},
                ],
                "tone": "persuasive",
            }
        )

        svc = SentimentService()
        svc._supabase = MagicMock()
        with patch("app.services.sentiment_service.groq_service") as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value=mock_ai_response)
            result = await svc.analyze_sentiment("Mixed text")

        assert len(result["aspects"]) == 2
        assert result["aspects"][0]["sentiment"] == "positive"
        assert result["aspects"][1]["sentiment"] == "negative"


class TestSentimentServicePersistence:
    """Tests for store/get/trends/distribution."""

    @pytest.mark.asyncio
    async def test_store_analysis_calls_supabase(self):
        """store_analysis should insert a row."""
        svc = SentimentService()
        mock_sb = MagicMock()
        mock_sb.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": str(uuid4())}
        ]
        analysis = {
            "sentiment": "positive",
            "score": 0.7,
            "emotions": {
                "joy": 0.8,
                "anger": 0.1,
                "sadness": 0.05,
                "fear": 0.02,
                "surprise": 0.5,
                "disgust": 0.01,
            },
            "aspects": [],
            "tone": "informative",
        }
        with patch.object(svc, "_supabase", mock_sb):
            with patch("app.services.sentiment_service.cache") as mock_cache:
                result = await svc.store_analysis(
                    content_id=uuid4(),
                    user_id=uuid4(),
                    analysis=analysis,
                )
        assert result is not None
        mock_sb.table.assert_called_with("sentiment_analyses")

    @pytest.mark.asyncio
    async def test_get_analysis_returns_none_when_empty(self):
        """get_analysis returns None when no rows exist."""
        svc = SentimentService()
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = (
            []
        )
        with patch.object(svc, "_supabase", mock_sb):
            with patch("app.services.sentiment_service.cache") as mock_cache:
                mock_cache.get = Mock(return_value=None)
                result = await svc.get_analysis(uuid4(), uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_analysis_uses_cache(self):
        """get_analysis should return cached data when available."""
        svc = SentimentService()
        cached = {"id": str(uuid4()), "sentiment": "neutral", "score": 0.0}
        with patch("app.services.sentiment_service.cache") as mock_cache:
            mock_cache.get = Mock(return_value=cached)
            result = await svc.get_analysis(uuid4(), uuid4())
        assert result == cached

    @pytest.mark.asyncio
    async def test_get_trends_returns_list(self):
        """get_trends should return a list of analysis rows."""
        svc = SentimentService()
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
            {"id": str(uuid4()), "score": 0.7},
            {"id": str(uuid4()), "score": 0.3},
        ]
        with patch.object(svc, "_supabase", mock_sb):
            with patch("app.services.sentiment_service.cache") as mock_cache:
                mock_cache.get = Mock(return_value=None)
                result = await svc.get_trends(uuid4(), uuid4())
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_distribution_counts_sentiments(self):
        """get_distribution should return counts and percentages."""
        svc = SentimentService()
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"sentiment": "positive"},
            {"sentiment": "positive"},
            {"sentiment": "negative"},
            {"sentiment": "neutral"},
        ]
        with patch.object(svc, "_supabase", mock_sb):
            result = await svc.get_distribution(uuid4())

        assert result["total_analyses"] == 4
        assert result["distribution"]["positive"] == 2
        assert result["distribution"]["negative"] == 1
        assert result["distribution"]["neutral"] == 1
        assert result["percentages"]["positive"] == 50.0

    @pytest.mark.asyncio
    async def test_get_distribution_empty(self):
        """get_distribution with no data returns zeros."""
        svc = SentimentService()
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.data = (
            []
        )
        with patch.object(svc, "_supabase", mock_sb):
            result = await svc.get_distribution(uuid4())

        assert result["total_analyses"] == 0
        assert result["distribution"]["positive"] == 0
        assert result["percentages"] == {}


class TestSentimentServiceBatch:
    """Tests for batch sentiment analysis."""

    @pytest.mark.asyncio
    async def test_batch_analyze_processes_all_items(self):
        """batch_analyze should analyze and store each item."""
        svc = SentimentService()
        mock_analysis = {
            "sentiment": "positive",
            "score": 0.7,
            "emotions": {
                "joy": 0.8,
                "anger": 0.1,
                "sadness": 0.05,
                "fear": 0.02,
                "surprise": 0.5,
                "disgust": 0.01,
            },
            "aspects": [],
            "tone": "informative",
        }
        with patch.object(
            svc, "analyze_sentiment", new_callable=AsyncMock, return_value=mock_analysis
        ):
            with patch.object(
                svc,
                "store_analysis",
                new_callable=AsyncMock,
                return_value={"id": str(uuid4())},
            ):
                items = [
                    {"content_id": uuid4(), "text": "Great stuff"},
                    {"content_id": uuid4(), "text": "Not so great"},
                ]
                result = await svc.batch_analyze(items, user_id=uuid4())
        assert len(result) == 2


class TestSentimentServiceSingleton:
    """Tests for module-level singleton."""

    def test_singleton_exists(self):
        """Module-level sentiment_service instance exists."""
        assert isinstance(sentiment_service, SentimentService)

    def test_lazy_supabase_init(self):
        """Supabase client is None before first access."""
        svc = SentimentService()
        assert svc._supabase is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

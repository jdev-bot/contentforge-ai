"""
Tests for Content Quality Scoring API and Service.

Covers:
- QualityService scoring logic
- API endpoints
- Caching behaviour
- Batch operations
"""

import pytest
import json
from datetime import datetime
from uuid import uuid4, UUID
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from app.services.quality_service import (
    QualityService,
    quality_service,
    DIMENSION_WEIGHTS,
)

# =========================================================================== #
#  Service unit tests                                                          #
# =========================================================================== #


class TestQualityServiceComputeOverall:
    """Tests for the weighted composite score computation."""

    def test_all_perfect_scores(self):
        """All 100s should yield overall 100."""
        svc = QualityService()
        scores = {
            "readability": 100,
            "seo": 100,
            "engagement": 100,
            "grammar": 100,
            "brand": 100,
        }
        assert svc._compute_overall(scores) == 100

    def test_all_zero_scores(self):
        """All 0s should yield overall 0."""
        svc = QualityService()
        scores = {"readability": 0, "seo": 0, "engagement": 0, "grammar": 0, "brand": 0}
        assert svc._compute_overall(scores) == 0

    def test_mixed_scores_weighted(self):
        """Overall should be weighted sum of dimensions."""
        svc = QualityService()
        scores = {
            "readability": 80,
            "seo": 60,
            "engagement": 70,
            "grammar": 90,
            "brand": 50,
        }
        expected = round(80 * 0.25 + 60 * 0.20 + 70 * 0.25 + 90 * 0.15 + 50 * 0.15)
        assert svc._compute_overall(scores) == expected

    def test_score_clamped_to_100(self):
        """Overall is clamped at 100 even with inflated inputs."""
        svc = QualityService()
        scores = {
            "readability": 200,
            "seo": 200,
            "engagement": 200,
            "grammar": 200,
            "brand": 200,
        }
        assert svc._compute_overall(scores) == 100

    def test_dimension_weights_sum_to_one(self):
        """Dimension weights must sum to 1.0."""
        total = sum(DIMENSION_WEIGHTS.values())
        assert abs(total - 1.0) < 0.001

    def test_five_dimensions_present(self):
        """Exactly five dimensions with weights."""
        assert len(DIMENSION_WEIGHTS) == 5
        for dim in ("readability", "seo", "engagement", "grammar", "brand"):
            assert dim in DIMENSION_WEIGHTS


class TestQualityServiceAnalyzeQuality:
    """Tests for the AI-powered quality analysis method."""

    @pytest.mark.asyncio
    async def test_analyze_returns_required_keys(self):
        """Result should contain all expected keys."""
        mock_ai_response = json.dumps(
            {
                "readability": 75,
                "seo": 60,
                "engagement": 80,
                "grammar": 90,
                "brand": 70,
                "suggestions": ["Improve keyword density", "Add more CTAs"],
            }
        )

        svc = QualityService()
        svc._supabase = MagicMock()
        with patch("app.services.quality_service.ai_service") as mock_ai:
            mock_ai.generate_content = AsyncMock(return_value=mock_ai_response)
            result = await svc.analyze_quality("Some test content here.")

        assert "overall_score" in result
        assert "readability" in result
        assert "seo" in result
        assert "engagement" in result
        assert "grammar" in result
        assert "brand" in result
        assert "suggestions" in result

    @pytest.mark.asyncio
    async def test_analyze_handles_bad_json(self):
        """Non-JSON response should fall back to defaults."""
        svc = QualityService()
        svc._supabase = MagicMock()
        with patch("app.services.quality_service.ai_service") as mock_ai:
            mock_ai.generate_content = AsyncMock(
                return_value="This is not JSON at all"
            )
            result = await svc.analyze_quality("Some test content here.")

        assert result["overall_score"] is not None
        assert 0 <= result["overall_score"] <= 100
        assert isinstance(result["suggestions"], list)

    @pytest.mark.asyncio
    async def test_analyze_scores_clamped_0_100(self):
        """All dimension scores should be clamped to 0-100."""
        mock_ai_response = json.dumps(
            {
                "readability": -10,
                "seo": 150,
                "engagement": 80,
                "grammar": 90,
                "brand": 70,
                "suggestions": [],
            }
        )

        svc = QualityService()
        svc._supabase = MagicMock()
        with patch("app.services.quality_service.ai_service") as mock_ai:
            mock_ai.generate_content = AsyncMock(return_value=mock_ai_response)
            result = await svc.analyze_quality("Test content.")

        assert result["readability"] == 0
        assert result["seo"] == 100
        assert 0 <= result["overall_score"] <= 100

    @pytest.mark.asyncio
    async def test_analyze_with_brand_voice(self):
        """Brand voice parameter should be passed through to the prompt."""
        mock_ai_response = json.dumps(
            {
                "readability": 70,
                "seo": 60,
                "engagement": 80,
                "grammar": 85,
                "brand": 90,
                "suggestions": [],
            }
        )

        brand_voice = {"tone": "professional", "vocabulary": "elevated"}
        svc = QualityService()
        svc._supabase = MagicMock()
        with patch("app.services.quality_service.ai_service") as mock_ai:
            mock_ai.generate_content = AsyncMock(return_value=mock_ai_response)
            result = await svc.analyze_quality("Test content.", brand_voice=brand_voice)

        assert result["brand"] == 90

    @pytest.mark.asyncio
    async def test_analyze_strips_markdown_fences(self):
        """Groq may return JSON inside ```json ... ``` fences."""
        raw = '```json\n{"readability": 70, "seo": 60, "engagement": 65, "grammar": 80, "brand": 75, "suggestions": ["Fix typo"]}\n```'
        svc = QualityService()
        svc._supabase = MagicMock()
        with patch("app.services.quality_service.ai_service") as mock_ai:
            mock_ai.generate_content = AsyncMock(return_value=raw)
            result = await svc.analyze_quality("Test content.")

        assert result["readability"] == 70


class TestQualityServicePersistence:
    """Tests for store/get/history/suggestions."""

    @pytest.mark.asyncio
    async def test_store_score_calls_supabase(self):
        """store_score should insert a row and return data."""
        svc = QualityService()
        mock_sb = MagicMock()
        mock_sb.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": str(uuid4())}
        ]
        with patch.object(svc, "_supabase", mock_sb):
            with patch("app.services.quality_service.cache") as mock_cache:
                result = await svc.store_score(
                    content_id=uuid4(),
                    user_id=uuid4(),
                    scores={
                        "overall_score": 80,
                        "readability": 80,
                        "seo": 70,
                        "engagement": 85,
                        "grammar": 90,
                        "brand": 75,
                        "suggestions": ["Improve SEO"],
                    },
                )
        assert result is not None
        mock_sb.table.assert_called_with("quality_scores")

    @pytest.mark.asyncio
    async def test_get_score_returns_none_when_empty(self):
        """get_score returns None when no rows exist."""
        svc = QualityService()
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = (
            []
        )
        with patch.object(svc, "_supabase", mock_sb):
            with patch("app.services.quality_service.cache") as mock_cache:
                mock_cache.get = Mock(return_value=None)
                result = await svc.get_score(uuid4(), uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_score_uses_cache(self):
        """get_score should return cached data when available."""
        svc = QualityService()
        cached_data = {"id": str(uuid4()), "overall_score": 85}
        with patch("app.services.quality_service.cache") as mock_cache:
            mock_cache.get = Mock(return_value=cached_data)
            result = await svc.get_score(uuid4(), uuid4())
        assert result == cached_data

    @pytest.mark.asyncio
    async def test_get_history_returns_list(self):
        """get_history should return a list of score rows."""
        svc = QualityService()
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
            {"id": str(uuid4()), "overall_score": 80},
            {"id": str(uuid4()), "overall_score": 75},
        ]
        with patch.object(svc, "_supabase", mock_sb):
            with patch("app.services.quality_service.cache") as mock_cache:
                mock_cache.get = Mock(return_value=None)
                result = await svc.get_history(uuid4(), uuid4())
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_suggestions_returns_list(self):
        """get_suggestions returns suggestions from latest score."""
        svc = QualityService()
        suggestions = ["Fix grammar", "Add CTA"]
        with patch.object(svc, "get_score", new_callable=AsyncMock) as mock_gs:
            mock_gs.return_value = {"suggestions": suggestions}
            result = await svc.get_suggestions(uuid4(), uuid4())
        assert result == suggestions

    @pytest.mark.asyncio
    async def test_get_suggestions_empty_when_no_score(self):
        """get_suggestions returns empty list when no score exists."""
        svc = QualityService()
        with patch.object(svc, "get_score", new_callable=AsyncMock) as mock_gs:
            mock_gs.return_value = None
            result = await svc.get_suggestions(uuid4(), uuid4())
        assert result == []


class TestQualityServiceBatch:
    """Tests for batch analysis."""

    @pytest.mark.asyncio
    async def test_batch_analyze_processes_all_items(self):
        """batch_analyze should process and store each item."""
        svc = QualityService()
        mock_scores = {
            "overall_score": 80,
            "readability": 80,
            "seo": 70,
            "engagement": 85,
            "grammar": 90,
            "brand": 75,
            "suggestions": [],
        }
        with patch.object(
            svc, "analyze_quality", new_callable=AsyncMock, return_value=mock_scores
        ):
            with patch.object(
                svc,
                "store_score",
                new_callable=AsyncMock,
                return_value={"id": str(uuid_id())},
            ):
                items = [
                    {"content_id": uuid_id(), "text": "Content 1"},
                    {"content_id": uuid_id(), "text": "Content 2"},
                ]
                result = await svc.batch_analyze(items, user_id=uuid4())
        assert len(result) == 2


class TestQualityServiceSingleton:
    """Tests for the module-level singleton."""

    def test_singleton_exists(self):
        """Module-level quality_service instance exists."""
        assert isinstance(quality_service, QualityService)

    def test_lazy_supabase_init(self):
        """Supabase client is None before first access."""
        svc = QualityService()
        assert svc._supabase is None


# Helper to avoid typo
def uuid_id():
    return uuid4()


# =========================================================================== #
#  API endpoint tests                                                          #
# =========================================================================== #


class TestQualityScoringAPI:
    """Tests for Quality Scoring API endpoints via TestClient."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.mock_user = Mock()
        self.mock_user.id = uuid4()

    def test_analyze_endpoint_success(self):
        """POST /quality/analyze returns scores."""
        from app.routers.quality_scoring import analyze_quality

        with patch("app.routers.quality_scoring.quality_service") as mock_svc:
            mock_svc.analyze_quality = AsyncMock(
                return_value={
                    "overall_score": 82,
                    "readability": 80,
                    "seo": 70,
                    "engagement": 85,
                    "grammar": 90,
                    "brand": 75,
                    "suggestions": ["Improve SEO keywords"],
                }
            )
            with patch("app.routers.quality_scoring.check_and_increment_usage"):
                import asyncio

                result = asyncio.get_event_loop().run_until_complete(
                    analyze_quality(
                        request=Mock(text="Test content", brand_voice=None),
                        user=self.mock_user,
                        _=Mock(),
                    )
                )
        assert result.overall_score == 82

    def test_content_endpoint_not_found(self):
        """GET /quality/content/{id} raises 404 when no score exists."""
        from app.routers.quality_scoring import get_content_quality

        with patch("app.routers.quality_scoring.quality_service") as mock_svc:
            mock_svc.get_score = AsyncMock(return_value=None)
            import asyncio

            with pytest.raises(Exception):  # HTTPException
                asyncio.get_event_loop().run_until_complete(
                    get_content_quality(content_id=uuid4(), user=self.mock_user)
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

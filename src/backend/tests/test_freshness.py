"""
Tests for Content Freshness Scoring API.

Covers:
- FreshnessService scoring algorithm
- API endpoints
- Dashboard statistics
- Bulk operations
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import Mock, patch, MagicMock

from app.services.freshness_service import FreshnessService, FreshnessFactors, freshness_service


class TestFreshnessFactors:
    """Tests for FreshnessFactors constants."""
    
    def test_age_constants(self):
        """Test age threshold constants."""
        assert FreshnessFactors.AGE_MAX_POINTS == 40
        assert FreshnessFactors.AGE_FRESH == 7
        assert FreshnessFactors.AGE_RECENT == 30
        assert FreshnessFactors.AGE_MODERATE == 90
        assert FreshnessFactors.AGE_STALE == 180
    
    def test_engagement_constants(self):
        """Test engagement threshold constants."""
        assert FreshnessFactors.ENGAGEMENT_MAX_POINTS == 40
        assert FreshnessFactors.ENGAGEMENT_HIGH == 100
        assert FreshnessFactors.ENGAGEMENT_GOOD == 50
        assert FreshnessFactors.ENGAGEMENT_MODERATE == 20
    
    def test_trend_constants(self):
        """Test trend threshold constants."""
        assert FreshnessFactors.TREND_MAX_POINTS == 20
        assert len(FreshnessFactors.TRENDING_KEYWORDS) > 0


class TestFreshnessServiceAgeScore:
    """Tests for age score calculation."""
    
    def test_fresh_content_score(self):
        """Content 0-7 days old gets maximum age score."""
        service = FreshnessService()
        assert service.calculate_age_score(0) == 40
        assert service.calculate_age_score(7) == 40
        assert service.calculate_age_score(3) == 40
    
    def test_recent_content_score(self):
        """Content 8-30 days old gets high age score."""
        service = FreshnessService()
        assert service.calculate_age_score(8) == 35
        assert service.calculate_age_score(30) == 35
        assert service.calculate_age_score(15) == 35
    
    def test_moderate_content_score(self):
        """Content 31-90 days old gets moderate age score."""
        service = FreshnessService()
        assert service.calculate_age_score(31) == 25
        assert service.calculate_age_score(90) == 25
        assert service.calculate_age_score(60) == 25
    
    def test_stale_content_score(self):
        """Content 91-180 days old gets low age score."""
        service = FreshnessService()
        assert service.calculate_age_score(91) == 15
        assert service.calculate_age_score(180) == 15
        assert service.calculate_age_score(120) == 15
    
    def test_very_old_content_score(self):
        """Content 180+ days old gets minimum age score."""
        service = FreshnessService()
        assert service.calculate_age_score(181) == 5
        assert service.calculate_age_score(365) == 5
        assert service.calculate_age_score(1000) == 5


class TestFreshnessServiceEngagementScore:
    """Tests for engagement score calculation."""
    
    def test_engagement_word_count_high(self):
        """High word count adds engagement points."""
        service = FreshnessService()
        content = {"original_text": "x " * 1500, "word_count": 1500}
        score = service.calculate_engagement_score(content)
        assert score >= 15  # At least word count points
    
    def test_engagement_word_count_medium(self):
        """Medium word count adds moderate engagement points."""
        service = FreshnessService()
        content = {"original_text": "x " * 600, "word_count": 600}
        score = service.calculate_engagement_score(content)
        assert score >= 10  # At least word count points for 500+
    
    def test_engagement_word_count_low(self):
        """Low word count adds minimal engagement points."""
        service = FreshnessService()
        content = {"original_text": "x " * 50, "word_count": 50}
        score = service.calculate_engagement_score(content)
        assert score >= 0
    
    def test_engagement_source_url_bonus(self):
        """Content with source URL gets bonus points."""
        service = FreshnessService()
        content = {"original_text": "x " * 500, "word_count": 500, "source_url": "https://example.com"}
        score_with_url = service.calculate_engagement_score(content)
        
        content_no_url = {"original_text": "x " * 500, "word_count": 500}
        score_without_url = service.calculate_engagement_score(content_no_url)
        
        assert score_with_url > score_without_url
    
    def test_engagement_completed_status_bonus(self):
        """Content with completed status gets bonus points."""
        service = FreshnessService()
        content = {"original_text": "x " * 500, "word_count": 500, "status": "completed"}
        score_completed = service.calculate_engagement_score(content)
        
        content_pending = {"original_text": "x " * 500, "word_count": 500, "status": "pending"}
        score_pending = service.calculate_engagement_score(content_pending)
        
        assert score_completed > score_pending
    
    def test_engagement_max_points_cap(self):
        """Engagement score is capped at maximum points."""
        service = FreshnessService()
        content = {
            "original_text": "x " * 2000,
            "word_count": 2000,
            "source_url": "https://example.com",
            "status": "completed"
        }
        score = service.calculate_engagement_score(content)
        assert score <= FreshnessFactors.ENGAGEMENT_MAX_POINTS


class TestFreshnessServiceTrendScore:
    """Tests for trend score calculation."""
    
    def test_many_trending_keywords(self):
        """Content with many trending keywords gets high score."""
        service = FreshnessService()
        content = {
            "original_text": "ai machine learning automation workflow productivity content marketing",
            "title": "AI and ML for Content Marketing"
        }
        score = service.calculate_trend_score(content)
        assert score == 20  # Max points for 5+ keywords
    
    def test_some_trending_keywords(self):
        """Content with some trending keywords gets moderate score."""
        service = FreshnessService()
        content = {
            "original_text": "ai automation workflow",
            "title": "AI Automation"
        }
        score = service.calculate_trend_score(content)
        assert score == 15  # 3-4 keywords
    
    def test_few_trending_keywords(self):
        """Content with few trending keywords gets low-moderate score."""
        service = FreshnessService()
        content = {
            "original_text": "ai",
            "title": "AI"
        }
        score = service.calculate_trend_score(content)
        assert score == 10  # 1-2 keywords
    
    def test_no_trending_keywords(self):
        """Content with no trending keywords gets base score."""
        service = FreshnessService()
        content = {
            "original_text": "hello world foo bar baz",
            "title": "Random Thoughts"
        }
        score = service.calculate_trend_score(content)
        assert score == 5  # Base score
    
    def test_trend_score_case_insensitive(self):
        """Trending keyword matching is case insensitive."""
        service = FreshnessService()
        content = {
            "original_text": "AI MACHINE LEARNING",
            "title": "AI"
        }
        score_upper = service.calculate_trend_score(content)
        
        content_lower = {
            "original_text": "ai machine learning",
            "title": "ai"
        }
        score_lower = service.calculate_trend_score(content_lower)
        
        assert score_upper == score_lower


class TestFreshnessServiceRecommendations:
    """Tests for recommendation generation."""
    
    def test_old_content_recommendations(self):
        """Old content gets update recommendations."""
        service = FreshnessService()
        content = {"original_text": "test", "word_count": 100}
        
        recommendations = service.generate_recommendations(
            age_days=200,
            age_score=25,
            engagement_score=20,
            trend_score=10,
            content=content
        )
        
        assert "Update statistics" in recommendations
        assert "Add recent examples" in recommendations
    
    def test_low_engagement_recommendations(self):
        """Low engagement content gets headline refresh recommendation."""
        service = FreshnessService()
        content = {"original_text": "test", "word_count": 100}
        
        recommendations = service.generate_recommendations(
            age_days=10,
            age_score=35,
            engagement_score=10,
            trend_score=15,
            content=content
        )
        
        assert "Refresh headline" in recommendations
        assert "Add compelling call-to-action" in recommendations
    
    def test_low_trend_recommendations(self):
        """Low trend score content gets keyword recommendations."""
        service = FreshnessService()
        content = {"original_text": "test", "word_count": 100}
        
        recommendations = service.generate_recommendations(
            age_days=10,
            age_score=35,
            engagement_score=20,
            trend_score=5,
            content=content
        )
        
        assert "Add trending keywords" in recommendations
    
    def test_short_content_recommendations(self):
        """Short content gets expansion recommendation."""
        service = FreshnessService()
        content = {"original_text": "test", "word_count": 50}
        
        recommendations = service.generate_recommendations(
            age_days=10,
            age_score=35,
            engagement_score=20,
            trend_score=15,
            content=content
        )
        
        assert "Expand content depth" in recommendations
    
    def test_recommendations_limited_to_five(self):
        """Recommendations are limited to top 5."""
        service = FreshnessService()
        content = {"original_text": "test", "word_count": 50}
        
        recommendations = service.generate_recommendations(
            age_days=200,  # Very old
            age_score=5,
            engagement_score=5,  # Very low
            trend_score=5,  # Very low
            content=content
        )
        
        assert len(recommendations) <= 5


class TestFreshnessServiceFullAnalysis:
    """Tests for complete content analysis."""
    
    @pytest.fixture(autouse=True)
    def mock_supabase(self):
        """Mock supabase for unit tests that call _count_generated_assets."""
        with patch("app.services.freshness_service.get_supabase_client") as mock:
            mock_client = MagicMock()
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(count=0)
            mock.return_value = mock_client
            yield mock
    
    def test_analysis_returns_all_fields(self, mock_supabase):
        """Complete analysis returns all required fields."""
        service = FreshnessService()
        content = {
            "id": str(uuid4()),
            "original_text": "AI and machine learning are transforming content marketing automation workflows.",
            "title": "AI in Marketing",
            "word_count": 100,
            "source_url": "https://example.com",
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }
        
        result = service.analyze_content(content)
        
        assert "freshness_score" in result
        assert "age_days" in result
        assert "factors" in result
        assert "recommendations" in result
        assert isinstance(result["freshness_score"], int)
        assert 0 <= result["freshness_score"] <= 100
    
    def test_analysis_score_calculation(self, mock_supabase):
        """Analysis calculates score as sum of component scores."""
        service = FreshnessService()
        content = {
            "id": str(uuid4()),
            "original_text": "AI and machine learning automation.",
            "title": "AI",
            "word_count": 100,
            "created_at": datetime.now().isoformat()
        }
        
        result = service.analyze_content(content)
        
        expected_score = (
            result["factors"]["age_points"] +
            result["factors"]["engagement_points"] +
            result["factors"]["trend_points"]
        )
        assert result["freshness_score"] == expected_score
    
    def test_analysis_factors_sum_to_one(self, mock_supabase):
        """Factor weights should approximately sum to 1.0."""
        service = FreshnessService()
        content = {
            "id": str(uuid4()),
            "original_text": "Test content.",
            "title": "Test",
            "word_count": 100,
            "created_at": datetime.now().isoformat()
        }
        
        result = service.analyze_content(content)
        factors = result["factors"]
        
        total = factors["age_factor"] + factors["engagement_factor"] + factors["trend_factor"]
        assert 0.99 <= total <= 1.01  # Allow for floating point rounding


class TestFreshnessServiceStatus:
    """Tests for freshness status determination."""
    
    def test_fresh_status(self):
        """Score >= 80 is 'fresh'."""
        service = FreshnessService()
        assert service.get_freshness_status(80) == "fresh"
        assert service.get_freshness_status(90) == "fresh"
        assert service.get_freshness_status(100) == "fresh"
    
    def test_good_status(self):
        """60 <= score < 80 is 'good'."""
        service = FreshnessService()
        assert service.get_freshness_status(60) == "good"
        assert service.get_freshness_status(70) == "good"
        assert service.get_freshness_status(79) == "good"
    
    def test_aging_status(self):
        """40 <= score < 60 is 'aging'."""
        service = FreshnessService()
        assert service.get_freshness_status(40) == "aging"
        assert service.get_freshness_status(50) == "aging"
        assert service.get_freshness_status(59) == "aging"
    
    def test_stale_status(self):
        """20 <= score < 40 is 'stale'."""
        service = FreshnessService()
        assert service.get_freshness_status(20) == "stale"
        assert service.get_freshness_status(30) == "stale"
        assert service.get_freshness_status(39) == "stale"
    
    def test_outdated_status(self):
        """Score < 20 is 'outdated'."""
        service = FreshnessService()
        assert service.get_freshness_status(0) == "outdated"
        assert service.get_freshness_status(10) == "outdated"
        assert service.get_freshness_status(19) == "outdated"


class TestFreshnessServiceShouldRefresh:
    """Tests for should refresh determination."""
    
    def test_should_refresh_low_score(self):
        """Content with score < 50 should be refreshed."""
        service = FreshnessService()
        assert service.should_refresh(49, 10) is True
        assert service.should_refresh(30, 10) is True
        assert service.should_refresh(10, 10) is True
    
    def test_should_refresh_old_content(self):
        """Content older than 90 days should be refreshed."""
        service = FreshnessService()
        assert service.should_refresh(80, 91) is True
        assert service.should_refresh(80, 100) is True
        assert service.should_refresh(80, 365) is True
    
    def test_should_not_refresh_fresh_content(self):
        """Fresh content should not be refreshed."""
        service = FreshnessService()
        assert service.should_refresh(80, 10) is False
        assert service.should_refresh(60, 30) is False
    
    def test_should_not_refresh_borderline(self):
        """Borderline cases should not be refreshed."""
        service = FreshnessService()
        assert service.should_refresh(50, 90) is False


class TestFreshnessServiceSingleton:
    """Tests for singleton instance."""
    
    def test_singleton_instance_exists(self):
        """Singleton instance exists and is FreshnessService."""
        assert isinstance(freshness_service, FreshnessService)


# API Tests
class TestFreshnessAPI:
    """Tests for Freshness API endpoints."""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        with patch("app.routers.freshness.get_supabase_client") as mock:
            yield mock
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user."""
        user = Mock()
        user.id = uuid4()
        return user
    
    def test_analyze_content_success(self, mock_supabase, mock_user):
        """Test successful content analysis."""
        from app.routers.freshness import analyze_content_freshness
        
        content_id = uuid4()
        content_data = {
            "id": str(content_id),
            "user_id": str(mock_user.id),
            "title": "Test Content",
            "original_text": "AI and machine learning content.",
            "word_count": 100,
            "created_at": datetime.now().isoformat()
        }
        
        # Mock supabase responses
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = content_data
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        mock_client.table.return_value.upsert.return_value.execute.return_value.data = [{"id": str(uuid4())}]
        
        # Run the endpoint
        result = asyncio.run(analyze_content_freshness(
            content_id=content_id,
            request=Mock(force_reanalyze=False),
            user=mock_user
        ))
        
        assert result.content_id == content_id
        assert 0 <= result.freshness_score <= 100
        assert result.age_days >= 0
        assert result.status in ["fresh", "good", "aging", "stale", "outdated"]
        assert len(result.recommendations) >= 0
    
    def test_analyze_content_not_found(self, mock_supabase, mock_user):
        """Test analysis of non-existent content."""
        from app.routers.freshness import analyze_content_freshness
        from fastapi import HTTPException
        
        content_id = uuid4()
        
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = None
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(analyze_content_freshness(
                content_id=content_id,
                request=Mock(force_reanalyze=False),
                user=mock_user
            ))
        
        assert exc_info.value.status_code == 404


class TestFreshnessDashboard:
    """Tests for dashboard statistics."""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        with patch("app.routers.freshness.get_supabase_client") as mock:
            yield mock
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user."""
        user = Mock()
        user.id = uuid4()
        return user
    
    def test_dashboard_with_no_scores(self, mock_supabase, mock_user):
        """Test dashboard with no analyzed content."""
        from app.routers.freshness import get_freshness_dashboard
        
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        
        # Mock content count
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.count = 10
        
        # Mock empty freshness scores
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        result = asyncio.run(get_freshness_dashboard(user=mock_user))
        
        assert result.stats.total_content == 10
        assert result.stats.analyzed_content == 0
        assert result.stats.pending_analysis == 10
        assert result.stats.average_freshness_score == 0.0


class TestBulkAnalyze:
    """Tests for bulk analysis."""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        with patch("app.routers.freshness.get_supabase_client") as mock:
            yield mock
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user."""
        user = Mock()
        user.id = uuid4()
        return user
    
    def test_bulk_analyze_empty_content(self, mock_supabase, mock_user):
        """Test bulk analyze with no content."""
        from app.routers.freshness import bulk_analyze_content
        
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        result = asyncio.run(bulk_analyze_content(content_ids=None, user=mock_user))
        
        assert result.total_analyzed == 0
        assert result.freshness_scores == []
        assert result.summary == {}
    
    def test_bulk_analyze_with_content_ids(self, mock_supabase, mock_user):
        """Test bulk analyze with specific content IDs."""
        from app.routers.freshness import bulk_analyze_content
        
        content_ids = [uuid4(), uuid4()]
        
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        
        # Mock content data
        mock_client.table.return_value.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = [
            {
                "id": str(content_ids[0]),
                "user_id": str(mock_user.id),
                "title": "Content 1",
                "original_text": "AI content.",
                "word_count": 100,
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(content_ids[1]),
                "user_id": str(mock_user.id),
                "title": "Content 2",
                "original_text": "ML automation.",
                "word_count": 150,
                "created_at": datetime.now().isoformat()
            }
        ]
        
        # Mock upsert
        mock_client.table.return_value.upsert.return_value.execute.return_value.data = [{"id": str(uuid4())}]
        
        result = asyncio.run(bulk_analyze_content(content_ids=content_ids, user=mock_user))
        
        assert result.total_analyzed == 2
        assert len(result.freshness_scores) == 2


class TestStaleContent:
    """Tests for stale content listing."""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        with patch("app.routers.freshness.get_supabase_client") as mock:
            yield mock
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user."""
        user = Mock()
        user.id = uuid4()
        return user
    
    def test_list_stale_content(self, mock_supabase, mock_user):
        """Test listing stale content."""
        from app.routers.freshness import list_stale_content
        
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        
        # Mock stale content
        mock_client.table.return_value.select.return_value.eq.return_value.lt.return_value.order.return_value.range.return_value.execute.return_value.data = [
            {
                "content_id": str(uuid4()),
                "freshness_score": 30,
                "age_days": 100,
                "recommendations": ["Update statistics"],
                "created_at": datetime.now().isoformat(),
                "content": {"title": "Old Content", "created_at": datetime.now().isoformat()}
            }
        ]
        
        # Mock count
        mock_client.table.return_value.select.return_value.eq.return_value.lt.return_value.execute.return_value.count = 1
        
        result = asyncio.run(list_stale_content(threshold=50, page=1, page_size=20, user=mock_user))
        
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].freshness_score < 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

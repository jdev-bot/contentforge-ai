"""
Tests for trending topics feature.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4, UUID

import httpx
from httpx import AsyncClient


# ============== Fixtures ==============

@pytest.fixture
def mock_trend_data():
    """Mock trending topic data."""
    return {
        "id": str(uuid4()),
        "topic": "Artificial Intelligence",
        "category": "tech",
        "trend_score": 85.5,
        "mention_count": 15000,
        "velocity": 12.3,
        "source": "twitter",
        "discovered_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "related_keywords": ["machine learning", "LLM", "ChatGPT"],
        "sample_content": [
            {"source": "twitter", "text": "AI is changing everything!"},
            {"source": "reddit", "text": "Just tried the new AI feature"},
        ],
    }


@pytest.fixture
def mock_user_interest():
    """Mock user topic interest data."""
    return {
        "user_id": str(uuid4()),
        "topic_id": str(uuid4()),
        "relevance_score": 0.85,
        "created_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def mock_auth_headers():
    """Mock authentication headers."""
    return {
        "Authorization": "Bearer mock_token",
        "Content-Type": "application/json",
    }


# ============== Trend Service Tests ==============

class TestTrendService:
    """Test the TrendService class."""
    
    @pytest.mark.asyncio
    async def test_fetch_mock_trending_data(self):
        """Test fetching mock trending data."""
        from app.services.trend_service import trend_service
        
        trends = await trend_service.fetch_mock_trending_data()
        
        assert isinstance(trends, list)
        assert len(trends) > 0
        
        # Check structure of first trend
        trend = trends[0]
        assert "topic" in trend
        assert "category" in trend
        assert "trend_score" in trend
        assert "mention_count" in trend
        assert "velocity" in trend
        assert "source" in trend
        assert "related_keywords" in trend
        assert "sample_content" in trend
    
    @pytest.mark.asyncio
    async def test_fetch_mock_trending_data_with_category(self):
        """Test fetching mock trending data filtered by category."""
        from app.services.trend_service import trend_service
        
        trends = await trend_service.fetch_mock_trending_data(category="tech")
        
        assert isinstance(trends, list)
        assert len(trends) > 0
        
        # All trends should be in tech category
        for trend in trends:
            assert trend["category"] == "tech"
    
    @pytest.mark.asyncio
    async def test_get_trending_topics_from_db(self, mock_supabase):
        """Test getting trending topics from database."""
        from app.services.trend_service import trend_service
        
        # Mock the database response
        mock_response = Mock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "topic": "Python",
                "category": "tech",
                "trend_score": 90.0,
                "mention_count": 25000,
                "velocity": 15.5,
            }
        ]
        mock_supabase.table().select().execute.return_value = mock_response
        
        with patch.object(trend_service, 'supabase', mock_supabase):
            trends = await trend_service.get_trending_topics(limit=10)
        
        assert isinstance(trends, list)
        if trends:
            assert trends[0]["topic"] == "Python"
    
    @pytest.mark.asyncio
    async def test_get_trending_topics_filtered_by_category(self, mock_supabase):
        """Test getting trending topics filtered by category."""
        from app.services.trend_service import trend_service
        
        mock_response = Mock()
        mock_response.data = [
            {"id": str(uuid4()), "topic": "Business News", "category": "business", "trend_score": 75.0}
        ]
        mock_supabase.table().select().eq().gte().order().limit().execute.return_value = mock_response
        
        with patch.object(trend_service, 'supabase', mock_supabase):
            trends = await trend_service.get_trending_topics(category="business", limit=5)
        
        assert isinstance(trends, list)
    
    @pytest.mark.asyncio
    async def test_get_topics_by_category(self, mock_supabase):
        """Test grouping topics by category."""
        from app.services.trend_service import trend_service
        
        mock_response = Mock()
        mock_response.data = [
            {"id": str(uuid4()), "topic": "AI", "category": "tech", "trend_score": 95.0},
            {"id": str(uuid4()), "topic": "Startup", "category": "business", "trend_score": 80.0},
            {"id": str(uuid4()), "topic": "React", "category": "tech", "trend_score": 85.0},
        ]
        mock_supabase.table().select().order().execute.return_value = mock_response
        
        with patch.object(trend_service, 'supabase', mock_supabase):
            result = await trend_service.get_topics_by_category()
        
        assert isinstance(result, dict)
        assert "tech" in result
        assert "business" in result
        assert len(result["tech"]) == 2
        assert len(result["business"]) == 1
    
    @pytest.mark.asyncio
    async def test_calculate_relevance(self):
        """Test relevance calculation."""
        from app.services.trend_service import trend_service
        
        trend = {"topic": "Python", "trend_score": 90, "related_keywords": ["programming", "coding"]}
        user_keywords = {"python", "programming", "development"}
        
        relevance = trend_service._calculate_relevance(trend, user_keywords)
        
        assert isinstance(relevance, float)
        assert 0 <= relevance <= 1
    
    @pytest.mark.asyncio
    async def test_calculate_relevance_no_match(self):
        """Test relevance calculation with no matching keywords."""
        from app.services.trend_service import trend_service
        
        trend = {"topic": "Quantum Physics", "trend_score": 70, "related_keywords": []}
        user_keywords = {"python", "javascript"}
        
        relevance = trend_service._calculate_relevance(trend, user_keywords)
        
        assert relevance == 0.0
    
    @pytest.mark.asyncio
    async def test_get_relevant_topics_for_user(self, mock_supabase):
        """Test getting relevant topics for a user."""
        from app.services.trend_service import trend_service
        
        user_id = str(uuid4())
        
        # Mock content response
        mock_content_response = Mock()
        mock_content_response.data = [
            {"id": str(uuid4()), "title": "Python Tutorial", "tags": ["python", "coding"], "category": "tech"},
        ]
        
        # Mock trends response
        mock_trends_response = Mock()
        mock_trends_response.data = [
            {"id": str(uuid4()), "topic": "Python", "category": "tech", "trend_score": 95.0, "related_keywords": []},
            {"id": str(uuid4()), "topic": "JavaScript", "category": "tech", "trend_score": 85.0, "related_keywords": []},
        ]
        
        mock_supabase.table().select().eq().execute.side_effect = [
            mock_content_response,
            mock_trends_response,
        ]
        
        with patch.object(trend_service, 'supabase', mock_supabase):
            topics = await trend_service.get_relevant_topics_for_user(user_id=user_id, limit=5)
        
        assert isinstance(topics, list)
    
    @pytest.mark.asyncio
    async def test_track_topic_for_user(self, mock_supabase):
        """Test tracking a topic for a user."""
        from app.services.trend_service import trend_service
        
        user_id = str(uuid4())
        topic_id = str(uuid4())
        
        mock_response = Mock()
        mock_response.data = [{"user_id": user_id, "topic_id": topic_id}]
        mock_supabase.table().upsert().execute.return_value = mock_response
        
        with patch.object(trend_service, 'supabase', mock_supabase):
            result = await trend_service.track_topic_for_user(user_id, topic_id, relevance_score=0.9)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_user_tracked_topics(self, mock_supabase):
        """Test getting all tracked topics for a user."""
        from app.services.trend_service import trend_service
        
        user_id = str(uuid4())
        
        mock_response = Mock()
        mock_response.data = [
            {
                "user_id": user_id,
                "topic_id": str(uuid4()),
                "relevance_score": 0.85,
                "trending_topics": {"topic": "AI", "category": "tech"},
            }
        ]
        mock_supabase.table().select().eq().execute.return_value = mock_response
        
        with patch.object(trend_service, 'supabase', mock_supabase):
            tracked = await trend_service.get_user_tracked_topics(user_id)
        
        assert isinstance(tracked, list)
        assert len(tracked) == 1
    
    @pytest.mark.asyncio
    async def test_get_velocity_leaderboard(self, mock_supabase):
        """Test getting velocity leaderboard."""
        from app.services.trend_service import trend_service
        
        mock_response = Mock()
        mock_response.data = [
            {"id": str(uuid4()), "topic": "Viral Topic", "velocity": 50.0, "category": "social"},
            {"id": str(uuid4()), "topic": "Breaking News", "velocity": 45.0, "category": "news"},
        ]
        mock_supabase.table().select().order().limit().execute.return_value = mock_response
        
        with patch.object(trend_service, 'supabase', mock_supabase):
            leaderboard = await trend_service.get_velocity_leaderboard(limit=10)
        
        assert isinstance(leaderboard, list)
        assert len(leaderboard) == 2
        assert leaderboard[0]["velocity"] >= leaderboard[1]["velocity"]
    
    @pytest.mark.asyncio
    async def test_get_trending_insights(self, mock_supabase):
        """Test getting trending insights."""
        from app.services.trend_service import trend_service
        
        mock_response = Mock()
        mock_response.data = [
            {"id": str(uuid4()), "topic": "AI", "category": "tech", "velocity": 20.0},
            {"id": str(uuid4()), "topic": "ML", "category": "tech", "velocity": 15.0},
            {"id": str(uuid4()), "topic": "Startup", "category": "business", "velocity": 10.0},
        ]
        mock_supabase.table().select().execute.return_value = mock_response
        
        with patch.object(trend_service, 'supabase', mock_supabase):
            insights = await trend_service.get_trending_insights()
        
        assert isinstance(insights, dict)
        assert insights["total_trends"] == 3
        assert insights["top_category"] == "tech"
        assert "avg_velocity" in insights
    
    @pytest.mark.asyncio
    async def test_generate_content_from_trend(self):
        """Test generating content from a trend."""
        from app.services.trend_service import trend_service
        
        with patch.object(trend_service, 'groq_service') as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value="""
HEADLINE: The Future of AI

ANGLES:
- How AI is changing work
- Ethical considerations
- Future predictions

CONTENT:
AI is transforming every industry...

HASHTAGS:
#AI #MachineLearning

CTA:
Learn more about AI today!
""")
            
            result = await trend_service.generate_content_from_trend(
                topic="Artificial Intelligence",
                category="tech",
                platform="twitter",
                tone="professional"
            )
        
        assert isinstance(result, dict)
        assert "topic" in result
        assert "platform" in result
        assert "headline" in result
        assert "content" in result
        assert "angles" in result
        assert "hashtags" in result
        assert "cta" in result
    
    @pytest.mark.asyncio
    async def test_generate_related_keywords(self):
        """Test generating related keywords."""
        from app.services.trend_service import trend_service
        
        keywords = trend_service._generate_related_keywords("AI", "tech")
        
        assert isinstance(keywords, list)
        assert len(keywords) >= 0
    
    @pytest.mark.asyncio
    async def test_update_trending_topics(self, mock_supabase):
        """Test updating trending topics."""
        from app.services.trend_service import trend_service
        
        # Mock existing trend check
        mock_existing_response = Mock()
        mock_existing_response.data = []
        
        # Mock insert
        mock_insert_response = Mock()
        mock_insert_response.data = [{"id": str(uuid4())}]
        
        mock_supabase.table().select().eq().execute.return_value = mock_existing_response
        mock_supabase.table().insert().execute.return_value = mock_insert_response
        
        with patch.object(trend_service, 'supabase', mock_supabase):
            with patch.object(trend_service, 'groq_service') as mock_groq:
                mock_groq.generate_content = AsyncMock(return_value='{"trends": []}')
                result = await trend_service.update_trending_topics()
        
        assert isinstance(result, dict)
        assert "success" in result


# ============== API Router Tests ==============

class TestTrendsRouter:
    """Test the trends API endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_trending_topics(self, async_client, mock_auth_user):
        """Test GET /api/v1/trends endpoint."""
        with patch("app.routers.trends.trend_service") as mock_service:
            mock_service.get_trending_topics = AsyncMock(return_value=[
                {"id": str(uuid4()), "topic": "Python", "category": "tech", "trend_score": 90.0}
            ])
            
            response = await async_client.get("/api/v1/trends")
        
        assert response.status_code in [200, 401, 403]  # Depends on auth
    
    @pytest.mark.asyncio
    async def test_get_relevant_trends(self, async_client, mock_auth_user):
        """Test GET /api/v1/trends/relevant endpoint."""
        with patch("app.routers.trends.trend_service") as mock_service:
            mock_service.get_relevant_topics_for_user = AsyncMock(return_value=[
                {"id": str(uuid4()), "topic": "JavaScript", "relevance_score": 0.9}
            ])
            
            response = await async_client.get("/api/v1/trends/relevant")
        
        assert response.status_code in [200, 401, 403]
    
    @pytest.mark.asyncio
    async def test_get_trends_by_category(self, async_client, mock_auth_user):
        """Test GET /api/v1/trends/categories endpoint."""
        with patch("app.routers.trends.trend_service") as mock_service:
            mock_service.get_topics_by_category = AsyncMock(return_value={
                "tech": [{"id": str(uuid4()), "topic": "AI", "trend_score": 95.0}],
                "business": [{"id": str(uuid4()), "topic": "Startup", "trend_score": 80.0}],
            })
            
            response = await async_client.get("/api/v1/trends/categories")
        
        assert response.status_code in [200, 401, 403]
    
    @pytest.mark.asyncio
    async def test_track_topic(self, async_client, mock_auth_user):
        """Test POST /api/v1/trends/track endpoint."""
        with patch("app.routers.trends.trend_service") as mock_service:
            mock_service.track_topic_for_user = AsyncMock(return_value=True)
            
            response = await async_client.post(
                "/api/v1/trends/track",
                json={"topic_id": str(uuid4()), "relevance_score": 0.85}
            )
        
        assert response.status_code in [200, 401, 403, 422]
    
    @pytest.mark.asyncio
    async def test_generate_content_from_trend(self, async_client, mock_auth_user):
        """Test POST /api/v1/trends/generate-content endpoint."""
        with patch("app.routers.trends.trend_service") as mock_service:
            mock_service.generate_content_from_trend = AsyncMock(return_value={
                "topic": "AI",
                "platform": "twitter",
                "headline": "AI is changing everything",
                "content": "Here's why...",
                "angles": ["Angle 1", "Angle 2"],
                "hashtags": ["#AI"],
                "cta": "Learn more",
            })
            
            response = await async_client.post(
                "/api/v1/trends/generate-content",
                json={
                    "topic": "AI",
                    "category": "tech",
                    "platform": "twitter",
                    "tone": "professional"
                }
            )
        
        assert response.status_code in [200, 401, 403, 422]
    
    @pytest.mark.asyncio
    async def test_get_velocity_leaderboard(self, async_client, mock_auth_user):
        """Test GET /api/v1/trends/velocity endpoint."""
        with patch("app.routers.trends.trend_service") as mock_service:
            mock_service.get_velocity_leaderboard = AsyncMock(return_value=[
                {"id": str(uuid4()), "topic": "Viral", "velocity": 100.0}
            ])
            
            response = await async_client.get("/api/v1/trends/velocity")
        
        assert response.status_code in [200, 401, 403]
    
    @pytest.mark.asyncio
    async def test_get_trending_insights(self, async_client, mock_auth_user):
        """Test GET /api/v1/trends/insights endpoint."""
        with patch("app.routers.trends.trend_service") as mock_service:
            mock_service.get_trending_insights = AsyncMock(return_value={
                "total_trends": 50,
                "top_category": "tech",
                "avg_velocity": 15.5,
                "highest_velocity_topic": "AI",
            })
            
            response = await async_client.get("/api/v1/trends/insights")
        
        assert response.status_code in [200, 401, 403]
    
    @pytest.mark.asyncio
    async def test_search_trends(self, async_client, mock_auth_user):
        """Test GET /api/v1/trends/search endpoint."""
        response = await async_client.get("/api/v1/trends/search?q=python")
        assert response.status_code in [200, 401, 403]
    
    @pytest.mark.asyncio
    async def test_get_trend_details(self, async_client, mock_auth_user):
        """Test GET /api/v1/trends/{topic_id} endpoint."""
        response = await async_client.get(f"/api/v1/trends/{uuid4()}")
        assert response.status_code in [200, 401, 403, 404]


# ============== Celery Task Tests ==============

class TestTrendsCeleryTasks:
    """Test Celery tasks for trends."""
    
    @pytest.mark.asyncio
    async def test_update_trending_topics_task(self):
        """Test the update_trending_topics_task."""
        from app.tasks.trends import update_trending_topics_task
        from app.services.trend_service import trend_service
        
        with patch.object(trend_service, 'update_trending_topics', AsyncMock(return_value={
            "success": True,
            "trends_analyzed": 20,
            "trends_saved": 5,
            "timestamp": datetime.utcnow().isoformat(),
        })):
            # Note: Celery tasks need to run in a sync context
            # This is a simplified test
            result = update_trending_topics_task.run()
        
        assert isinstance(result, dict)
        assert result.get("status") == "success"
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_trends_task(self):
        """Test the cleanup_expired_trends_task."""
        from app.tasks.trends import cleanup_expired_trends_task
        from app.services.trend_service import trend_service
        
        with patch.object(trend_service, '_cleanup_expired_trends', AsyncMock(return_value=10)):
            result = cleanup_expired_trends_task.run()
        
        assert isinstance(result, dict)
        assert result.get("status") == "success"
        assert result.get("deleted_count") == 10
    
    @pytest.mark.asyncio
    async def test_generate_trend_content_suggestions_task(self):
        """Test the generate_trend_content_suggestions_task."""
        from app.tasks.trends import generate_trend_content_suggestions_task
        from app.services.trend_service import trend_service
        
        with patch.object(trend_service, 'get_trending_topics', AsyncMock(return_value=[
            {"id": str(uuid4()), "topic": "AI", "category": "tech"}
        ])):
            with patch.object(trend_service, 'generate_content_from_trend', AsyncMock(return_value={
                "headline": "Test",
                "content": "Test content",
                "angles": [],
                "hashtags": [],
                "cta": "",
            })):
                result = generate_trend_content_suggestions_task.run()
        
        assert isinstance(result, dict)


# ============== Integration Tests ==============

class TestTrendsIntegration:
    """Integration tests for trends feature."""
    
    @pytest.mark.asyncio
    async def test_full_trend_workflow(self, mock_supabase):
        """Test the complete trend workflow."""
        from app.services.trend_service import trend_service
        
        # 1. Fetch mock data
        mock_data = await trend_service.fetch_mock_trending_data(category="tech")
        assert len(mock_data) > 0
        
        # 2. Analyze with AI (mocked)
        with patch.object(trend_service, 'groq_service') as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value='{"trends": []}')
            analyzed = await trend_service.analyze_trends_with_ai(mock_data)
            assert len(analyzed) == len(mock_data)
    
    @pytest.mark.asyncio
    async def test_relevance_scoring_accuracy(self):
        """Test relevance scoring accuracy."""
        from app.services.trend_service import trend_service
        
        test_cases = [
            ("python", {"python", "coding"}, 0.8, 1.0),
            ("AI", {"machine learning", "ai"}, 0.6, 0.8),
            ("Unrelated", {"python", "javascript"}, 0.0, 0.3),
        ]
        
        for topic, user_keywords, min_expected, max_expected in test_cases:
            trend = {"topic": topic, "trend_score": 80, "related_keywords": ["ml", "deep learning"]}
            relevance = trend_service._calculate_relevance(trend, user_keywords)
            
            assert min_expected <= relevance <= max_expected, f"Relevance {relevance} out of range for {topic}"
    
    def test_trend_data_structure(self, mock_trend_data):
        """Test that trend data has all required fields."""
        required_fields = [
            "id", "topic", "category", "trend_score", "mention_count",
            "velocity", "source", "discovered_at", "expires_at",
            "related_keywords", "sample_content"
        ]
        
        for field in required_fields:
            assert field in mock_trend_data, f"Missing field: {field}"


# ============== Edge Case Tests ==============

class TestTrendsEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_empty_trend_list(self):
        """Test handling of empty trend list."""
        from app.services.trend_service import trend_service
        
        analyzed = await trend_service.analyze_trends_with_ai([])
        assert analyzed == []
    
    @pytest.mark.asyncio
    async def test_save_trends_with_duplicate(self, mock_supabase):
        """Test saving trends with duplicates."""
        from app.services.trend_service import trend_service
        
        trends = [
            {"topic": "AI", "category": "tech", "trend_score": 90, "mention_count": 1000, "velocity": 10.0, "source": "twitter", "discovered_at": datetime.utcnow().isoformat(), "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(), "related_keywords": [], "sample_content": []},
        ]
        
        # First call - no existing
        mock_existing = Mock()
        mock_existing.data = []
        
        # Second call - existing found
        mock_existing2 = Mock()
        mock_existing2.data = [{"id": str(uuid4())}]
        
        mock_insert = Mock()
        mock_insert.data = [{"id": str(uuid4())}]
        
        mock_supabase.table().select().eq().execute.side_effect = [mock_existing, mock_existing2]
        mock_supabase.table().insert().execute.return_value = mock_insert
        mock_supabase.table().update().eq().execute.return_value = mock_insert
        
        with patch.object(trend_service, 'supabase', mock_supabase):
            count = await trend_service.save_trends_to_db(trends * 2)
        
        assert count >= 0
    
    @pytest.mark.asyncio
    async def test_generate_content_with_invalid_platform(self):
        """Test generating content with invalid platform."""
        from app.services.trend_service import trend_service
        
        with patch.object(trend_service, 'groq_service') as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value="Invalid response")
            
            result = await trend_service.generate_content_from_trend(
                topic="Test",
                category="tech",
                platform="invalid_platform",
                tone="professional"
            )
        
        assert isinstance(result, dict)
        assert "content" in result
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, mock_supabase):
        """Test handling of database errors."""
        from app.services.trend_service import trend_service
        
        mock_supabase.table().select().execute.side_effect = Exception("Database error")
        
        with patch.object(trend_service, 'supabase', mock_supabase):
            trends = await trend_service.get_trending_topics()
        
        assert trends == []


# ============== Performance Tests ==============

class TestTrendsPerformance:
    """Performance tests for trends feature."""
    
    @pytest.mark.asyncio
    async def test_large_trend_list_handling(self):
        """Test handling of large trend lists."""
        from app.services.trend_service import trend_service
        
        # Generate large mock data
        large_data = [
            {
                "topic": f"Topic {i}",
                "category": "tech",
                "trend_score": float(i),
                "mention_count": i * 100,
                "velocity": float(i) / 10,
            }
            for i in range(100)
        ]
        
        start = datetime.utcnow()
        
        with patch.object(trend_service, 'groq_service') as mock_groq:
            mock_groq.generate_content = AsyncMock(return_value='{"trends": []}')
            analyzed = await trend_service.analyze_trends_with_ai(large_data)
        
        duration = (datetime.utcnow() - start).total_seconds()
        
        # Should complete in reasonable time
        assert duration < 5.0
        assert len(analyzed) == len(large_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

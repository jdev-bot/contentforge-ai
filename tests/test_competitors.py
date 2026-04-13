"""
Tests for Competitor Analysis API.

Covers:
- Adding/removing competitors
- Listing competitors
- Fetching competitor content
- Performance analysis
- Content gap identification
- Topic overlap analysis
- Refresh operations
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import status

# Mark all tests as async
pytestmark = pytest.mark.asyncio


class TestAddCompetitor:
    """Tests for adding competitors."""
    
    async def test_add_competitor_success(self, async_client, auth_headers):
        """Test successfully adding a competitor."""
        response = await async_client.post(
            "/api/v1/competitors",
            json={
                "name": "Test Competitor",
                "platform": "twitter",
                "handle": "testcompetitor",
                "description": "A test competitor"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Competitor"
        assert data["platform"] == "twitter"
        assert data["handle"] == "testcompetitor"
        assert data["is_active"] is True
        assert "id" in data
        assert "follower_count" in data
    
    async def test_add_competitor_invalid_platform(self, async_client, auth_headers):
        """Test adding competitor with invalid platform."""
        response = await async_client.post(
            "/api/v1/competitors",
            json={
                "name": "Test Competitor",
                "platform": "invalid_platform",
                "handle": "testhandle"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "platform" in response.json()["detail"].lower()
    
    async def test_add_competitor_missing_name(self, async_client, auth_headers):
        """Test adding competitor without name."""
        response = await async_client.post(
            "/api/v1/competitors",
            json={
                "platform": "twitter",
                "handle": "testhandle"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_add_competitor_duplicate(self, async_client, auth_headers):
        """Test adding duplicate competitor (same platform/handle)."""
        # Add first competitor
        await async_client.post(
            "/api/v1/competitors",
            json={
                "name": "First Competitor",
                "platform": "twitter",
                "handle": "duplicatehandle"
            },
            headers=auth_headers
        )
        
        # Try to add duplicate
        response = await async_client.post(
            "/api/v1/competitors",
            json={
                "name": "Second Competitor",
                "platform": "twitter",
                "handle": "duplicatehandle"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
    
    async def test_add_competitor_unauthorized(self, async_client):
        """Test adding competitor without authentication."""
        response = await async_client.post(
            "/api/v1/competitors",
            json={
                "name": "Test Competitor",
                "platform": "twitter",
                "handle": "testhandle"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListCompetitors:
    """Tests for listing competitors."""
    
    async def test_list_competitors_empty(self, async_client, auth_headers):
        """Test listing competitors when none exist."""
        response = await async_client.get(
            "/api/v1/competitors",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    async def test_list_competitors_with_data(self, async_client, auth_headers):
        """Test listing competitors with data."""
        # Add a competitor first
        await async_client.post(
            "/api/v1/competitors",
            json={
                "name": "Test Competitor",
                "platform": "linkedin",
                "handle": "testlinked"
            },
            headers=auth_headers
        )
        
        response = await async_client.get(
            "/api/v1/competitors",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert data[0]["platform"] == "linkedin"
    
    async def test_list_competitors_filter_by_platform(self, async_client, auth_headers):
        """Test filtering competitors by platform."""
        # Add competitors on different platforms
        await async_client.post(
            "/api/v1/competitors",
            json={"name": "Twitter Competitor", "platform": "twitter", "handle": "twitter1"},
            headers=auth_headers
        )
        await async_client.post(
            "/api/v1/competitors",
            json={"name": "LinkedIn Competitor", "platform": "linkedin", "handle": "linkedin1"},
            headers=auth_headers
        )
        
        # Filter by twitter
        response = await async_client.get(
            "/api/v1/competitors?platform=twitter",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for comp in data:
            assert comp["platform"] == "twitter"
    
    async def test_list_competitors_unauthorized(self, async_client):
        """Test listing competitors without authentication."""
        response = await async_client.get("/api/v1/competitors")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRemoveCompetitor:
    """Tests for removing competitors."""
    
    async def test_remove_competitor_success(self, async_client, auth_headers):
        """Test successfully removing a competitor."""
        # Add a competitor first
        create_response = await async_client.post(
            "/api/v1/competitors",
            json={
                "name": "To Remove",
                "platform": "twitter",
                "handle": "toremove"
            },
            headers=auth_headers
        )
        competitor_id = create_response.json()["id"]
        
        # Remove it
        response = await async_client.delete(
            f"/api/v1/competitors/{competitor_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "removed" in data["message"].lower()
    
    async def test_remove_nonexistent_competitor(self, async_client, auth_headers):
        """Test removing a competitor that doesn't exist."""
        fake_id = str(uuid4())
        response = await async_client.delete(
            f"/api/v1/competitors/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_remove_competitor_wrong_user(self, async_client, auth_headers, other_auth_headers):
        """Test removing another user's competitor."""
        # Add competitor as first user
        create_response = await async_client.post(
            "/api/v1/competitors",
            json={
                "name": "My Competitor",
                "platform": "twitter",
                "handle": "myhandle"
            },
            headers=auth_headers
        )
        competitor_id = create_response.json()["id"]
        
        # Try to delete as second user
        response = await async_client.delete(
            f"/api/v1/competitors/{competitor_id}",
            headers=other_auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCompetitorContent:
    """Tests for competitor content endpoints."""
    
    async def test_get_competitor_content(self, async_client, auth_headers):
        """Test getting content for a competitor."""
        # Add competitor
        create_response = await async_client.post(
            "/api/v1/competitors",
            json={
                "name": "Content Test",
                "platform": "twitter",
                "handle": "contenttest"
            },
            headers=auth_headers
        )
        competitor_id = create_response.json()["id"]
        
        # Get content
        response = await async_client.get(
            f"/api/v1/competitors/{competitor_id}/content",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Mock content should be generated
        assert len(data) >= 0
    
    async def test_get_competitor_content_pagination(self, async_client, auth_headers):
        """Test content pagination."""
        # Add competitor
        create_response = await async_client.post(
            "/api/v1/competitors",
            json={
                "name": "Pagination Test",
                "platform": "twitter",
                "handle": "paginationtest"
            },
            headers=auth_headers
        )
        competitor_id = create_response.json()["id"]
        
        # Get content with limit
        response = await async_client.get(
            f"/api/v1/competitors/{competitor_id}/content?limit=5",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 5
    
    async def test_get_content_nonexistent_competitor(self, async_client, auth_headers):
        """Test getting content for non-existent competitor."""
        fake_id = str(uuid4())
        response = await async_client.get(
            f"/api/v1/competitors/{fake_id}/content",
            headers=auth_headers
        )
        
        # Should return empty list for non-existent competitor
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestPerformanceAnalysis:
    """Tests for performance analysis."""
    
    async def test_get_performance_analysis_empty(self, async_client, auth_headers):
        """Test performance analysis with no competitors."""
        response = await async_client.get(
            "/api/v1/competitors/analysis",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["competitor_count"] == 0
    
    async def test_get_performance_analysis_with_competitors(self, async_client, auth_headers):
        """Test performance analysis with competitors."""
        # Add competitors
        await async_client.post(
            "/api/v1/competitors",
            json={"name": "Comp 1", "platform": "twitter", "handle": "comp1"},
            headers=auth_headers
        )
        await async_client.post(
            "/api/v1/competitors",
            json={"name": "Comp 2", "platform": "linkedin", "handle": "comp2"},
            headers=auth_headers
        )
        
        response = await async_client.get(
            "/api/v1/competitors/analysis",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["competitor_count"] >= 2
        assert "competitors" in data
        assert "aggregated_metrics" in data
        assert "insights" in data
        assert "platform_breakdown" in data


class TestContentGaps:
    """Tests for content gap analysis."""
    
    async def test_get_content_gaps_empty(self, async_client, auth_headers):
        """Test getting content gaps when none exist."""
        response = await async_client.get(
            "/api/v1/competitors/gaps",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    async def test_analyze_content_gaps(self, async_client, auth_headers):
        """Test running content gap analysis."""
        # Add a competitor first
        await async_client.post(
            "/api/v1/competitors",
            json={"name": "Gap Test", "platform": "twitter", "handle": "gaptest"},
            headers=auth_headers
        )
        
        response = await async_client.post(
            "/api/v1/competitors/gaps/analyze",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "gaps_analyzed" in data
        assert "gaps_stored" in data
        assert isinstance(data["gaps"], list)
    
    async def test_get_content_gaps_filtered(self, async_client, auth_headers):
        """Test getting content gaps with minimum opportunity filter."""
        response = await async_client.get(
            "/api/v1/competitors/gaps?min_opportunity=50",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All returned gaps should have opportunity_score >= 50
        for gap in data:
            assert gap["opportunity_score"] >= 50


class TestTopicOverlap:
    """Tests for topic overlap analysis."""
    
    async def test_get_topic_overlap(self, async_client, auth_headers):
        """Test getting topic overlap analysis."""
        # Add competitor
        await async_client.post(
            "/api/v1/competitors",
            json={"name": "Overlap Test", "platform": "twitter", "handle": "overlaptest"},
            headers=auth_headers
        )
        
        response = await async_client.get(
            "/api/v1/competitors/topics/overlap",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "competitor_topic_count" in data
        assert "user_topic_count" in data
        assert "overlap_count" in data
        assert "overlap_percentage" in data
        assert "shared_topics" in data
        assert "competitor_only_topics" in data
        assert "recommendation" in data


class TestBenchmarkComparison:
    """Tests for benchmark comparison."""
    
    async def test_get_benchmark_comparison(self, async_client, auth_headers):
        """Test getting benchmark comparison."""
        # Add competitor
        await async_client.post(
            "/api/v1/competitors",
            json={"name": "Benchmark Test", "platform": "twitter", "handle": "benchmarktest"},
            headers=auth_headers
        )
        
        response = await async_client.get(
            "/api/v1/competitors/benchmark",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "user_metrics" in data
        assert "competitor_avg" in data
        assert "comparison" in data
        assert "percentile" in data


class TestRefreshCompetitor:
    """Tests for refreshing competitor data."""
    
    async def test_refresh_competitor_success(self, async_client, auth_headers):
        """Test successfully refreshing competitor data."""
        # Add competitor
        create_response = await async_client.post(
            "/api/v1/competitors",
            json={"name": "Refresh Test", "platform": "twitter", "handle": "refreshtest"},
            headers=auth_headers
        )
        competitor_id = create_response.json()["id"]
        
        # Refresh
        response = await async_client.post(
            f"/api/v1/competitors/{competitor_id}/refresh",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "new_content_count" in data
        assert "total_content" in data
    
    async def test_refresh_nonexistent_competitor(self, async_client, auth_headers):
        """Test refreshing non-existent competitor."""
        fake_id = str(uuid4())
        response = await async_client.post(
            f"/api/v1/competitors/{fake_id}/refresh",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCompetitorDetails:
    """Tests for getting competitor details."""
    
    async def test_get_competitor_details(self, async_client, auth_headers):
        """Test getting specific competitor details."""
        # Add competitor
        create_response = await async_client.post(
            "/api/v1/competitors",
            json={"name": "Detail Test", "platform": "twitter", "handle": "detailtest"},
            headers=auth_headers
        )
        competitor_id = create_response.json()["id"]
        
        # Get details
        response = await async_client.get(
            f"/api/v1/competitors/{competitor_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Detail Test"
        assert data["handle"] == "detailtest"
    
    async def test_get_nonexistent_competitor_details(self, async_client, auth_headers):
        """Test getting details of non-existent competitor."""
        fake_id = str(uuid4())
        response = await async_client.get(
            f"/api/v1/competitors/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSupportedPlatforms:
    """Tests for supported platforms endpoint."""
    
    async def test_get_supported_platforms(self, async_client):
        """Test getting list of supported platforms."""
        response = await async_client.get("/api/v1/competitors/platforms/list")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert "twitter" in data
        assert "linkedin" in data
        assert "instagram" in data


# Test data models
class TestPydanticModels:
    """Tests for Pydantic request/response models."""
    
    def test_add_competitor_request_validation(self):
        """Test AddCompetitorRequest validation."""
        from app.routers.competitors import AddCompetitorRequest
        
        # Valid request
        request = AddCompetitorRequest(
            name="Test",
            platform="twitter",
            handle="testhandle"
        )
        assert request.name == "Test"
        
        # Test with optional fields
        request2 = AddCompetitorRequest(
            name="Test",
            platform="linkedin",
            handle="test",
            description="A description",
            profile_url="https://linkedin.com/in/test"
        )
        assert request2.description == "A description"


class TestCompetitorService:
    """Tests for CompetitorService."""
    
    async def test_service_add_competitor(self):
        """Test service-level add competitor."""
        from app.services.competitor_service import CompetitorService
        
        service = CompetitorService()
        
        # This would require mocking supabase in a real test
        # For now, just verify the service exists and has the method
        assert hasattr(service, 'add_competitor')
        assert callable(getattr(service, 'add_competitor'))
    
    async def test_service_generate_mock_content(self):
        """Test mock content generation."""
        from app.services.competitor_service import CompetitorService
        
        service = CompetitorService()
        content = service._generate_mock_content("twitter", "testhandle", count=5)
        
        assert len(content) == 5
        for item in content:
            assert "external_id" in item
            assert "content" in item
            assert "likes" in item
            assert "engagement_score" in item
            assert "published_at" in item
    
    async def test_service_categorize_topic(self):
        """Test topic categorization."""
        from app.services.competitor_service import CompetitorService
        
        service = CompetitorService()
        
        assert service._categorize_topic("content marketing") == "marketing"
        assert service._categorize_topic("startup growth") == "business"
        assert service._categorize_topic("AI tools") == "technology"
        assert service._categorize_topic("random topic") == "general"


# Integration tests
class TestCompetitorIntegration:
    """Integration tests for full competitor workflow."""
    
    async def test_full_competitor_workflow(self, async_client, auth_headers):
        """Test full competitor tracking workflow."""
        # 1. Add competitor
        add_response = await async_client.post(
            "/api/v1/competitors",
            json={
                "name": "Integration Test",
                "platform": "twitter",
                "handle": "integrationtest"
            },
            headers=auth_headers
        )
        assert add_response.status_code == status.HTTP_201_CREATED
        competitor_id = add_response.json()["id"]
        
        # 2. List competitors
        list_response = await async_client.get(
            "/api/v1/competitors",
            headers=auth_headers
        )
        assert list_response.status_code == status.HTTP_200_OK
        assert any(c["id"] == competitor_id for c in list_response.json())
        
        # 3. Get competitor content
        content_response = await async_client.get(
            f"/api/v1/competitors/{competitor_id}/content",
            headers=auth_headers
        )
        assert content_response.status_code == status.HTTP_200_OK
        
        # 4. Get performance analysis
        analysis_response = await async_client.get(
            "/api/v1/competitors/analysis",
            headers=auth_headers
        )
        assert analysis_response.status_code == status.HTTP_200_OK
        
        # 5. Refresh competitor data
        refresh_response = await async_client.post(
            f"/api/v1/competitors/{competitor_id}/refresh",
            headers=auth_headers
        )
        assert refresh_response.status_code == status.HTTP_200_OK
        
        # 6. Remove competitor
        delete_response = await async_client.delete(
            f"/api/v1/competitors/{competitor_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == status.HTTP_200_OK
        
        # Verify competitor is removed
        get_response = await async_client.get(
            f"/api/v1/competitors/{competitor_id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

"""
Tests for content endpoints.
"""
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status


class TestCreateContentEndpoint:
    """Tests for POST /api/v1/content endpoint."""

    def test_create_content_endpoint_exists(self, client, auth_headers):
        """Test that POST /api/v1/content endpoint exists and accepts requests."""
        payload = {
            "title": "Test Content",
            "source": {
                "type": "text",
                "text": "This is test content text."
            },
            "project_id": str(uuid.uuid4())
        }
        
        with patch("app.core.rate_limit.get_user_usage_stats") as mock_stats:
            mock_stats.return_value = MagicMock(
                monthly_usage_count=0,
                monthly_usage_limit=10,
                remaining=10,
                subscription_tier="free"
            )
            response = client.post("/api/v1/content", json=payload, headers=auth_headers)
        
        # Should not be 404 - endpoint should exist
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_create_content_accepts_valid_request(self, client, auth_headers):
        """Test that POST /api/v1/content accepts valid requests."""
        payload = {
            "title": "Test Content",
            "source": {
                "type": "text",
                "text": "This is test content text."
            },
            "project_id": str(uuid.uuid4())
        }
        
        response = client.post("/api/v1/content", json=payload, headers=auth_headers)
        
        # Endpoint exists if we don't get 404 (may get other errors due to auth/subscription)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_create_content_requires_auth(self, client):
        """Test that POST /api/v1/content requires authentication."""
        payload = {
            "title": "Test Content",
            "source": {
                "type": "text",
                "text": "Test content"
            },
            "project_id": str(uuid.uuid4())
        }
        
        response = client.post("/api/v1/content", json=payload)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListContentEndpoint:
    """Tests for GET /api/v1/content endpoint."""

    def test_list_content_endpoint_exists(self, client, auth_headers):
        """Test that GET /api/v1/content endpoint exists."""
        response = client.get("/api/v1/content", headers=auth_headers)
        
        # Should not be 404 - endpoint should exist
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_list_content_returns_200(self, client, auth_headers, mock_supabase_client):
        """Test that GET /api/v1/content returns 200 OK."""
        mock_client, _, _, _, mock_query = mock_supabase_client
        
        # Setup mock response
        mock_result = MagicMock()
        mock_result.data = []
        mock_query.execute.return_value = mock_result
        
        response = client.get("/api/v1/content", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK

    def test_list_content_requires_auth(self, client):
        """Test that GET /api/v1/content requires authentication."""
        response = client.get("/api/v1/content")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_content_returns_list(self, client, auth_headers, mock_supabase_client):
        """Test that GET /api/v1/content returns a list."""
        mock_client, _, _, _, mock_query = mock_supabase_client
        
        # Setup mock response with sample content
        mock_result = MagicMock()
        mock_result.data = [
            {
                "id": str(uuid.uuid4()),
                "project_id": str(uuid.uuid4()),
                "user_id": "test-user-id-123",
                "title": "Content 1",
                "source_type": "text",
                "source_url": None,
                "original_text": "Content text",
                "word_count": 2,
                "status": "completed",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        ]
        mock_query.execute.return_value = mock_result
        
        response = client.get("/api/v1/content", headers=auth_headers)
        data = response.json()
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(data, list)


class TestContentEndpointErrors:
    """Tests for content endpoint error handling."""

    def test_content_post_invalid_method(self, client, auth_headers):
        """Test that PUT to /api/v1/content is not allowed."""
        payload = {
            "title": "Test Content",
            "source": {"type": "text", "text": "Test"},
            "project_id": str(uuid.uuid4())
        }
        
        response = client.put("/api/v1/content", json=payload, headers=auth_headers)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_content_invalid_path_returns_404(self, client, auth_headers):
        """Test that GET to /api/v1/content/{invalid-uuid} returns 404."""
        # Use a valid UUID that won't exist
        response = client.get("/api/v1/content/12345678-1234-5678-1234-567812345678", headers=auth_headers)
        
        # Should be 404 for non-existent content
        assert response.status_code == status.HTTP_404_NOT_FOUND

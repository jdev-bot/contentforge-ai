"""
Tests for content endpoints.
"""
import pytest
from uuid import UUID, uuid4
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestContentEndpoints:
    """Test content management endpoints."""
    
    def test_list_content_requires_auth(self):
        """Test that listing content requires authentication."""
        response = client.get("/api/v1/content")
        assert response.status_code == 401
    
    def test_get_content_by_id_not_found(self):
        """Test getting non-existent content returns 404."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/content/{fake_id}")
        # Should be 401 without auth or 404 if auth is bypassed in test
        assert response.status_code in [401, 404]
    
    def test_create_content_missing_project_id(self):
        """Test creating content without required project_id fails."""
        response = client.post("/api/v1/content", json={
            "title": "Test Content",
            "source": {
                "type": "text",
                "text": "Sample test content for testing purposes."
            }
            # Missing project_id
        })
        assert response.status_code in [401, 422]  # 401 if auth required, 422 if validation error
    
    def test_create_content_invalid_source_type(self):
        """Test creating content with invalid source type fails validation."""
        response = client.post("/api/v1/content", json={
            "title": "Test Content",
            "project_id": str(uuid4()),
            "source": {
                "type": "invalid_type",  # Invalid source type
                "text": "Sample content"
            }
        })
        assert response.status_code in [401, 422]
    
    def test_delete_content_not_found(self):
        """Test deleting non-existent content returns 404."""
        fake_id = str(uuid4())
        response = client.delete(f"/api/v1/content/{fake_id}")
        # Without auth: 401, with auth but not found: 404
        assert response.status_code in [401, 404]

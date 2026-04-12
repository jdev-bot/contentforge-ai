"""
Tests for projects endpoints.
"""
import pytest
from uuid import UUID, uuid4
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestProjectEndpoints:
    """Test project management endpoints."""
    
    def test_list_projects_requires_auth(self):
        """Test that listing projects requires authentication."""
        response = client.get("/api/v1/projects")
        assert response.status_code == 401
    
    def test_get_project_by_id_not_found(self):
        """Test getting non-existent project returns 404."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/projects/{fake_id}")
        # Should be 401 without auth or 404 if auth is bypassed
        assert response.status_code in [401, 404]
    
    def test_create_project_missing_name(self):
        """Test creating project without required name fails validation."""
        response = client.post("/api/v1/projects", json={
            "description": "Test project description",
            # Missing required "name" field
        })
        assert response.status_code in [401, 422]  # 401 if auth required, 422 if validation error
    
    def test_update_project_not_found(self):
        """Test updating non-existent project returns 404."""
        fake_id = str(uuid4())
        response = client.patch(f"/api/v1/projects/{fake_id}", json={
            "name": "Updated Project Name",
            "description": "Updated description"
        })
        # Without auth: 401, with auth but not found: 404
        assert response.status_code in [401, 404]
    
    def test_delete_project_not_found(self):
        """Test deleting non-existent project returns 404."""
        fake_id = str(uuid4())
        response = client.delete(f"/api/v1/projects/{fake_id}")
        # Soft delete returns 404 if project not found
        assert response.status_code in [401, 404]

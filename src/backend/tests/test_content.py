"""
Content management tests for ContentForge AI.

Tests content creation, extraction, generation, and CRUD operations.
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import status
from uuid import uuid4

from tests.utils import create_auth_headers


class TestContentUnauthorized:
    """Tests for unauthorized content access."""
    
    @pytest.mark.unit
    def test_create_content_unauthorized(self, client):
        """Test creating content without authentication."""
        content_data = {
            "title": "Test Content",
            "project_id": str(uuid4()),
            "source": {
                "type": "text",
                "text": "Some text content",
            },
        }
        
        response = client.post("/api/v1/content", json=content_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.unit
    def test_list_content_unauthorized(self, client):
        """Test listing content without authentication."""
        response = client.get("/api/v1/content")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.unit
    def test_get_content_unauthorized(self, client):
        """Test getting content without authentication."""
        content_id = str(uuid4())
        response = client.get(f"/api/v1/content/{content_id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.unit
    def test_delete_content_unauthorized(self, client):
        """Test deleting content without authentication."""
        content_id = str(uuid4())
        response = client.delete(f"/api/v1/content/{content_id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestContentModels:
    """Tests for content data models."""
    
    @pytest.mark.unit
    def test_content_response_model(self, sample_content):
        """Test ContentResponse model structure."""
        # Verify sample content has required fields
        assert "id" in sample_content
        assert "project_id" in sample_content
        assert "user_id" in sample_content
        assert "title" in sample_content
        assert "source_type" in sample_content
        assert "status" in sample_content
        assert "created_at" in sample_content
        assert "updated_at" in sample_content
    
    @pytest.mark.unit
    def test_generated_asset_model(self, sample_generated_assets):
        """Test GeneratedAsset model structure."""
        for asset in sample_generated_assets:
            assert "id" in asset
            assert "content_id" in asset
            assert "user_id" in asset
            assert "type" in asset
            assert "content" in asset
            assert "status" in asset
    
    @pytest.mark.unit
    def test_content_source_model(self):
        """Test ContentSource model validation."""
        from app.routers.content import ContentSource
        
        # Valid text source
        source = ContentSource(type="text", text="Hello world")
        assert source.type == "text"
        assert source.text == "Hello world"
        
        # Valid URL source
        source = ContentSource(type="url", url="https://example.com/article")
        assert source.type == "url"
        assert str(source.url) == "https://example.com/article"
    
    @pytest.mark.unit
    def test_content_create_model(self):
        """Test ContentCreate model validation."""
        from app.routers.content import ContentCreate
        from uuid import uuid4
        
        project_id = uuid4()
        content = ContentCreate(
            title="Test Content",
            project_id=project_id,
            source={"type": "text", "text": "Hello"}
        )
        
        assert content.title == "Test Content"
        assert content.project_id == project_id
        assert content.source.type == "text"
    
    @pytest.mark.unit
    def test_content_create_missing_title(self):
        """Test ContentCreate model rejects missing title."""
        from app.routers.content import ContentCreate
        from pydantic import ValidationError
        from uuid import uuid4
        
        with pytest.raises(ValidationError) as exc_info:
            ContentCreate(
                project_id=uuid4(),
                source={"type": "text", "text": "Hello"}
            )
        
        assert "title" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_content_create_invalid_uuid(self):
        """Test ContentCreate model rejects invalid UUID."""
        from app.routers.content import ContentCreate
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            ContentCreate(
                title="Test",
                project_id="not-a-uuid",
                source={"type": "text", "text": "Hello"}
            )
        
        assert "project_id" in str(exc_info.value) or "UUID" in str(exc_info.value)

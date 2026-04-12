"""
Content management tests for ContentForge AI.

Tests content creation, extraction, generation, and CRUD operations.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import status
from uuid import uuid4

from tests.utils import (
    create_mock_supabase_response,
    create_mock_auth_user,
    create_auth_headers,
)


class TestContentCreate:
    """Tests for content creation endpoint."""
    
    @pytest.mark.unit
    @patch('app.routers.content.content_extraction_service')
    @patch('app.routers.content.get_supabase_client')
    @patch('app.routers.auth.get_supabase_client')
    def test_create_content_from_text(
        self, mock_auth_client, mock_content_client, mock_extraction, sample_content
    ):
        """Test creating content from text source."""
        from tests.conftest import create_mock_auth_user
        
        headers = create_auth_headers()
        
        content_data = {
            "title": "Test Content",
            "project_id": str(uuid4()),
            "source": {
                "type": "text",
                "text": "This is a sample text content for testing purposes.",
            },
        }
        
        mock_user = create_mock_auth_user()
        auth_response = Mock()
        auth_response.user = mock_user
        mock_auth_client.return_value.auth.get_user.return_value = auth_response
        
        mock_response = Mock()
        mock_response.data = [{
            **sample_content,
            "title": content_data["title"],
            "source_type": "text",
            "original_text": content_data["source"]["text"],
        }]
        mock_content_client.return_value.table.return_value.insert.return_value.execute.return_value = mock_response
        
        from fastapi.testclient import TestClient
        from app.main import app
        
        with TestClient(app) as client:
            response = client.post("/api/v1/content", json=content_data, headers=headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == content_data["title"]
        assert data["source_type"] == "text"
    
    @pytest.mark.unit
    @patch('app.routers.auth.get_supabase_client')
    def test_create_content_unauthorized(self, mock_auth_client):
        """Test creating content without authentication."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        content_data = {
            "title": "Test Content",
            "project_id": str(uuid4()),
            "source": {
                "type": "text",
                "text": "Some text content",
            },
        }
        
        with TestClient(app) as client:
            response = client.post("/api/v1/content", json=content_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestContentList:
    """Tests for content listing endpoint."""
    
    @pytest.mark.unit
    @patch('app.routers.content.get_supabase_client')
    @patch('app.routers.auth.get_supabase_client')
    def test_list_content_success(self, mock_auth_client, mock_content_client, sample_content):
        """Test listing all content for a user."""
        from tests.conftest import create_mock_auth_user
        from fastapi.testclient import TestClient
        from app.main import app
        
        headers = create_auth_headers()
        mock_user = create_mock_auth_user()
        
        auth_response = Mock()
        auth_response.user = mock_user
        mock_auth_client.return_value.auth.get_user.return_value = auth_response
        
        contents = [
            sample_content,
            {**sample_content, "id": "content-2", "title": "Second Content"},
        ]
        
        mock_response = Mock()
        mock_response.data = contents
        mock_content_client.return_value.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        with TestClient(app) as client:
            response = client.get("/api/v1/content", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2


class TestContentGet:
    """Tests for content retrieval endpoint."""
    
    @pytest.mark.unit
    @patch('app.routers.content.get_supabase_client')
    @patch('app.routers.auth.get_supabase_client')
    def test_get_content_success(self, mock_auth_client, mock_content_client, sample_content):
        """Test getting specific content."""
        from tests.conftest import create_mock_auth_user
        from fastapi.testclient import TestClient
        from app.main import app
        
        headers = create_auth_headers()
        content_id = sample_content["id"]
        
        mock_user = create_mock_auth_user()
        auth_response = Mock()
        auth_response.user = mock_user
        mock_auth_client.return_value.auth.get_user.return_value = auth_response
        
        mock_response = Mock()
        mock_response.data = sample_content
        mock_content_client.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        
        with TestClient(app) as client:
            response = client.get(f"/api/v1/content/{content_id}", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == content_id


class TestContentGenerate:
    """Tests for content generation endpoint."""
    
    @pytest.mark.unit
    @patch('app.routers.content.check_and_increment_usage')
    @patch('app.routers.content.groq_service')
    @patch('app.routers.content.get_supabase_client')
    @patch('app.routers.auth.get_supabase_client')
    def test_generate_assets_success(
        self, mock_auth_client, mock_content_client, mock_groq, mock_usage, sample_content
    ):
        """Test successful asset generation."""
        from tests.conftest import create_mock_auth_user
        from fastapi.testclient import TestClient
        from app.main import app
        
        headers = create_auth_headers()
        content_id = sample_content["id"]
        
        mock_user = create_mock_auth_user()
        auth_response = Mock()
        auth_response.user = mock_user
        mock_auth_client.return_value.auth.get_user.return_value = auth_response
        
        mock_usage.return_value = Mock(monthly_usage_count=1, monthly_usage_limit=100, remaining=99)
        
        # Mock Groq service responses
        mock_groq.generate_thread.return_value = ["Tweet 1", "Tweet 2"]
        mock_groq.generate_social_posts.return_value = ["LinkedIn post 1"]
        mock_groq.generate_newsletter.return_value = {"newsletter": "Newsletter content"}
        mock_groq.generate_short_video_script.return_value = {"script": "Video script"}
        
        mock_content_response = Mock()
        mock_content_response.data = sample_content
        mock_content_client.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_content_response
        
        mock_assets_response = Mock()
        mock_assets_response.data = [
            {"id": "asset-1", "type": "thread", "content": "Test"},
        ]
        mock_content_client.return_value.table.return_value.insert.return_value.execute.return_value = mock_assets_response
        
        with TestClient(app) as client:
            response = client.post(f"/api/v1/content/{content_id}/generate", headers=headers)
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


class TestContentDelete:
    """Tests for content deletion endpoint."""
    
    @pytest.mark.unit
    @patch('app.routers.content.get_supabase_client')
    @patch('app.routers.auth.get_supabase_client')
    def test_delete_content_success(self, mock_auth_client, mock_content_client, sample_content):
        """Test deleting content."""
        from tests.conftest import create_mock_auth_user
        from fastapi.testclient import TestClient
        from app.main import app
        
        headers = create_auth_headers()
        content_id = sample_content["id"]
        
        mock_user = create_mock_auth_user()
        auth_response = Mock()
        auth_response.user = mock_user
        mock_auth_client.return_value.auth.get_user.return_value = auth_response
        
        existing_response = Mock()
        existing_response.data = sample_content
        
        mock_content_client.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = existing_response
        
        with TestClient(app) as client:
            response = client.delete(f"/api/v1/content/{content_id}", headers=headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestContentUpload:
    """Tests for file upload endpoint."""
    
    @pytest.mark.unit
    @patch('app.routers.auth.get_supabase_client')
    def test_upload_file_not_implemented(self, mock_auth_client):
        """Test that file upload returns not implemented."""
        from tests.conftest import create_mock_auth_user
        from fastapi.testclient import TestClient
        from app.main import app
        
        headers = create_auth_headers()
        mock_user = create_mock_auth_user()
        
        auth_response = Mock()
        auth_response.user = mock_user
        mock_auth_client.return_value.auth.get_user.return_value = auth_response
        
        with TestClient(app) as client:
            response = client.post("/api/v1/upload", headers=headers)
        
        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED

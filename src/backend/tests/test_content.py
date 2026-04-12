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
    MockSupabaseBuilder
)


class TestContentCreate:
    """Tests for content creation endpoint."""
    
    @pytest.mark.unit
    def test_create_content_from_text(self, client, sample_content):
        """Test creating content from text source."""
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
        mock_response_data = {
            **sample_content,
            "title": content_data["title"],
            "source_type": "text",
            "original_text": content_data["source"]["text"],
            "word_count": 9,
        }
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("content", mock_response_data)
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/content", json=content_data, headers=headers)
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["title"] == content_data["title"]
            assert data["source_type"] == "text"
            assert data["word_count"] == 9
    
    @pytest.mark.unit
    @patch('app.routers.content.content_extraction_service')
    def test_create_content_from_url(self, mock_extraction, client, sample_content):
        """Test creating content from URL."""
        headers = create_auth_headers()
        
        extracted_text = "This is the extracted article content from the URL."
        mock_extraction.extract_from_url.return_value = extracted_text
        
        content_data = {
            "title": "URL Content",
            "project_id": str(uuid4()),
            "source": {
                "type": "url",
                "url": "https://example.com/article",
            },
        }
        
        mock_user = create_mock_auth_user()
        mock_response_data = {
            **sample_content,
            "title": "URL Content",
            "source_type": "url",
            "source_url": "https://example.com/article",
            "original_text": extracted_text,
            "word_count": 9,
        }
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("content", mock_response_data)
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/content", json=content_data, headers=headers)
            
            assert response.status_code == status.HTTP_201_CREATED
            mock_extraction.extract_from_url.assert_called_once_with("https://example.com/article")
    
    @pytest.mark.unit
    @patch('app.routers.content.content_extraction_service')
    def test_create_content_from_youtube(self, mock_extraction, client, sample_content):
        """Test creating content from YouTube URL."""
        headers = create_auth_headers()
        
        extracted_text = "This is the transcript from the YouTube video."
        mock_extraction.extract_from_youtube.return_value = extracted_text
        
        content_data = {
            "title": "YouTube Content",
            "project_id": str(uuid4()),
            "source": {
                "type": "youtube",
                "url": "https://youtube.com/watch?v=abcdef123",
            },
        }
        
        mock_user = create_mock_auth_user()
        mock_response_data = {
            **sample_content,
            "title": "YouTube Content",
            "source_type": "youtube",
            "source_url": "https://youtube.com/watch?v=abcdef123",
            "original_text": extracted_text,
        }
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("content", mock_response_data)
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/content", json=content_data, headers=headers)
            
            assert response.status_code == status.HTTP_201_CREATED
            mock_extraction.extract_from_youtube.assert_called_once()
    
    @pytest.mark.unit
    def test_create_content_missing_title(self, client):
        """Test creating content without title."""
        headers = create_auth_headers()
        
        content_data = {
            "project_id": str(uuid4()),
            "source": {
                "type": "text",
                "text": "Some text content",
            },
        }
        
        response = client.post("/api/v1/content", json=content_data, headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
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


class TestContentList:
    """Tests for content listing endpoint."""
    
    @pytest.mark.unit
    def test_list_content_success(self, client, sample_content):
        """Test listing all content for a user."""
        headers = create_auth_headers()
        
        mock_user = create_mock_auth_user()
        contents = [
            sample_content,
            {**sample_content, "id": "content-2", "title": "Second Content"},
        ]
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("content", contents)
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.get("/api/v1/content", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["title"] == sample_content["title"]
    
    @pytest.mark.unit
    def test_list_content_with_project_filter(self, client, sample_content):
        """Test listing content filtered by project."""
        headers = create_auth_headers()
        project_id = str(uuid4())
        
        mock_user = create_mock_auth_user()
        filtered_content = [{**sample_content, "project_id": project_id}]
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("content", filtered_content)
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.get(f"/api/v1/content?project_id={project_id}", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
    
    @pytest.mark.unit
    def test_list_content_empty(self, client):
        """Test listing content when user has no content."""
        headers = create_auth_headers()
        
        mock_user = create_mock_auth_user()
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("content", [])
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.get("/api/v1/content", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data == []


class TestContentGet:
    """Tests for content retrieval endpoint."""
    
    @pytest.mark.unit
    def test_get_content_success(self, client, sample_content):
        """Test getting specific content."""
        headers = create_auth_headers()
        content_id = sample_content["id"]
        
        mock_user = create_mock_auth_user()
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("content", sample_content, single=True)
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.get(f"/api/v1/content/{content_id}", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == content_id
            assert data["title"] == sample_content["title"]
    
    @pytest.mark.unit
    def test_get_content_not_found(self, client):
        """Test getting non-existent content."""
        headers = create_auth_headers()
        content_id = str(uuid4())
        
        mock_user = create_mock_auth_user()
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=None)
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.content.get_supabase_client', return_value=mock_client):
            response = client.get(f"/api/v1/content/{content_id}", headers=headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    def test_get_content_wrong_user(self, client, sample_content):
        """Test getting content belonging to another user."""
        headers = create_auth_headers()
        content_id = sample_content["id"]
        
        mock_user = create_mock_auth_user(user_id="different-user-id")
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=None)
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.content.get_supabase_client', return_value=mock_client):
            response = client.get(f"/api/v1/content/{content_id}", headers=headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestContentGenerate:
    """Tests for content generation endpoint."""
    
    @pytest.mark.unit
    @patch('app.routers.content.check_and_increment_usage')
    @patch('app.routers.content.groq_service')
    def test_generate_assets_success(
        self, mock_groq, mock_usage, client, sample_content, sample_generated_assets
    ):
        """Test successful asset generation."""
        headers = create_auth_headers()
        content_id = sample_content["id"]
        
        mock_user = create_mock_auth_user()
        mock_usage.return_value = Mock(monthly_usage_count=1, monthly_usage_limit=100, remaining=99)
        
        # Mock Groq service responses
        mock_groq.generate_thread.return_value = ["Tweet 1", "Tweet 2"]
        mock_groq.generate_social_posts.return_value = ["LinkedIn post 1"]
        mock_groq.generate_newsletter.return_value = {"newsletter": "Newsletter content"}
        mock_groq.generate_short_video_script.return_value = {"script": "Video script"}
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("content", sample_content, single=True)
        builder.with_table_response("generated_assets", sample_generated_assets)
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.post(f"/api/v1/content/{content_id}/generate", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.unit
    def test_generate_assets_content_not_found(self, client):
        """Test generating assets for non-existent content."""
        headers = create_auth_headers()
        content_id = str(uuid4())
        
        mock_user = create_mock_auth_user()
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=None)
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.content.get_supabase_client', return_value=mock_client):
            response = client.post(f"/api/v1/content/{content_id}/generate", headers=headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    @patch('app.routers.content.check_and_increment_usage')
    def test_generate_assets_no_text(self, mock_usage, client, sample_content):
        """Test generating assets when content has no text."""
        headers = create_auth_headers()
        content_id = sample_content["id"]
        
        mock_user = create_mock_auth_user()
        mock_usage.return_value = Mock(monthly_usage_count=1, monthly_usage_limit=100, remaining=99)
        
        content_no_text = {**sample_content, "original_text": None}
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("content", content_no_text, single=True)
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.post(f"/api/v1/content/{content_id}/generate", headers=headers)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "no content text" in response.json()["detail"].lower()


class TestContentAssets:
    """Tests for content assets listing endpoint."""
    
    @pytest.mark.unit
    def test_list_assets_success(self, client, sample_content, sample_generated_assets):
        """Test listing assets for content."""
        headers = create_auth_headers()
        content_id = sample_content["id"]
        
        mock_user = create_mock_auth_user()
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("generated_assets", sample_generated_assets)
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.get(f"/api/v1/content/{content_id}/assets", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["content_id"] == content_id


class TestContentDelete:
    """Tests for content deletion endpoint."""
    
    @pytest.mark.unit
    def test_delete_content_success(self, client, sample_content):
        """Test deleting content."""
        headers = create_auth_headers()
        content_id = sample_content["id"]
        
        mock_user = create_mock_auth_user()
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("content", sample_content, single=True)
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.delete(f"/api/v1/content/{content_id}", headers=headers)
            
            assert response.status_code == status.HTTP_204_NO_CONTENT
    
    @pytest.mark.unit
    def test_delete_content_not_found(self, client):
        """Test deleting non-existent content."""
        headers = create_auth_headers()
        content_id = str(uuid4())
        
        mock_user = create_mock_auth_user()
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=None)
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.content.get_supabase_client', return_value=mock_client):
            response = client.delete(f"/api/v1/content/{content_id}", headers=headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestContentUpload:
    """Tests for file upload endpoint."""
    
    @pytest.mark.unit
    def test_upload_file_not_implemented(self, client):
        """Test that file upload returns not implemented."""
        headers = create_auth_headers()
        
        mock_user = create_mock_auth_user()
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        
        with patch('app.routers.content.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/upload", headers=headers)
            
            assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED

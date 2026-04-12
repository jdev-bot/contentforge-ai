"""
Pytest configuration and fixtures for ContentForge AI backend tests.
"""
import os
import sys
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..", "src", "backend")
sys.path.insert(0, backend_path)

# Set test environment variables before importing app
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-role-key"
os.environ["GROQ_API_KEY"] = "test-groq-api-key"
os.environ["DEBUG"] = "true"


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client factory."""
    # Create mock auth
    mock_auth = MagicMock()
    
    # Create mock query chain
    mock_query = MagicMock()
    mock_query.eq = MagicMock(return_value=mock_query)
    mock_query.order = MagicMock(return_value=mock_query)
    mock_query.single = MagicMock(return_value=mock_query)
    mock_query.execute = MagicMock(return_value=MagicMock(data=[]))
    
    mock_table = MagicMock()
    mock_table.select = MagicMock(return_value=mock_query)
    mock_table.insert = MagicMock(return_value=mock_query)
    mock_table.update = MagicMock(return_value=mock_query)
    mock_table.delete = MagicMock(return_value=mock_query)
    
    # Create mock storage
    mock_storage = MagicMock()
    
    # Create main mock client
    mock_client = MagicMock()
    mock_client.auth = mock_auth
    mock_client.table = MagicMock(return_value=mock_table)
    mock_client.storage = mock_storage
    
    return mock_client, mock_auth, mock_table, mock_storage, mock_query


@pytest.fixture
def mock_user():
    """Create a mock authenticated user with proper string values."""
    user = MagicMock()
    user.id = "test-user-id-123"
    user.email = "test@example.com"
    user.user_metadata = {"full_name": "Test User"}
    return user


@pytest.fixture
def mock_session():
    """Create a mock Supabase session."""
    return MagicMock(
        access_token="test-access-token",
        refresh_token="test-refresh-token",
    )


@pytest.fixture
def auth_headers(mock_session):
    """Create authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {mock_session.access_token}"}


@pytest.fixture
def client():
    """Create a test client with mocked Supabase."""
    from fastapi.testclient import TestClient
    
    # Clear any cached supabase client
    from app.core import supabase as supabase_module
    supabase_module.get_supabase_client.cache_clear()
    
    # Create fresh mock for this test
    mock_auth = MagicMock()
    mock_query = MagicMock()
    mock_query.eq = MagicMock(return_value=mock_query)
    mock_query.order = MagicMock(return_value=mock_query)
    mock_query.single = MagicMock(return_value=mock_query)
    mock_query.execute = MagicMock(return_value=MagicMock(data=[]))
    
    mock_table = MagicMock()
    mock_table.select = MagicMock(return_value=mock_query)
    mock_table.insert = MagicMock(return_value=mock_query)
    mock_table.update = MagicMock(return_value=mock_query)
    mock_table.delete = MagicMock(return_value=mock_query)
    
    mock_storage = MagicMock()
    
    mock_client = MagicMock()
    mock_client.auth = mock_auth
    mock_client.table = MagicMock(return_value=mock_table)
    mock_client.storage = mock_storage
    
    # Patch the supabase client BEFORE importing the app
    with patch("app.core.supabase.get_supabase_client", return_value=mock_client):
        with patch("app.core.supabase.create_client", return_value=mock_client):
            from app.main import app
            with TestClient(app) as test_client:
                # Store mocks on client for test access
                test_client.mock_supabase = (mock_client, mock_auth, mock_table, mock_storage, mock_query)
                yield test_client


@pytest.fixture
def test_settings():
    """Return test settings."""
    from app.core.config import get_settings
    return get_settings()


@pytest.fixture
def mock_groq_service():
    """Mock Groq service for AI generation tests."""
    with patch("app.services.groq_service.groq_service") as mock:
        mock.generate_thread = MagicMock(return_value=["Tweet 1", "Tweet 2", "Tweet 3"])
        mock.generate_social_posts = MagicMock(return_value=["Post 1", "Post 2"])
        mock.generate_newsletter = MagicMock(return_value={"newsletter": "Newsletter content"})
        mock.generate_short_video_script = MagicMock(return_value={"script": "Video script content"})
        yield mock


@pytest.fixture
def mock_extraction_service():
    """Mock content extraction service."""
    with patch("app.services.extraction_service.content_extraction_service") as mock:
        mock.extract_from_url = MagicMock(return_value="Extracted content from URL")
        mock.extract_from_youtube = MagicMock(return_value="Video transcript content")
        mock.clean_text = MagicMock(return_value="Cleaned text content")
        yield mock

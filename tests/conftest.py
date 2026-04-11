"""
Pytest configuration and fixtures for ContentForge AI backend tests.
"""
import os
import sys
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

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

from app.main import app
from app.core.config import get_settings


@pytest.fixture(scope="session")
def test_settings():
    """Return test settings."""
    return get_settings()


@pytest.fixture
def client() -> Generator:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client."""
    mock_client = MagicMock()
    
    # Mock auth methods
    mock_auth = MagicMock()
    mock_client.auth = mock_auth
    
    # Mock table methods
    mock_table = MagicMock()
    mock_client.table = MagicMock(return_value=mock_table)
    
    # Mock storage methods
    mock_storage = MagicMock()
    mock_client.storage = mock_storage
    
    return mock_client, mock_auth, mock_table, mock_storage


@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    return MagicMock(
        id="test-user-id-123",
        email="test@example.com",
        user_metadata={"full_name": "Test User"},
    )


@pytest.fixture
def mock_session():
    """Create a mock Supabase session."""
    return MagicMock(
        access_token="test-access-token",
        refresh_token="test-refresh-token",
    )


@pytest.fixture
def auth_headers(mock_user, mock_session):
    """Create authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {mock_session.access_token}"}


@pytest.fixture(autouse=True)
def mock_get_supabase_client(mock_supabase):
    """Automatically mock Supabase client for all tests."""
    mock_client, _, _, _ = mock_supabase
    with patch("app.core.supabase.get_supabase_client", return_value=mock_client):
        yield mock_client


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

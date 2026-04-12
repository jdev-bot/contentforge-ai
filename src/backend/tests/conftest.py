"""
Pytest configuration and fixtures for ContentForge AI tests.
"""
import os
import sys
import pytest
from typing import Generator, Dict
from unittest.mock import Mock, MagicMock, patch

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from fastapi import Request

# Set test environment variables before importing app
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-role-key"
os.environ["GROQ_API_KEY"] = "test-groq-api-key"
os.environ["RATE_LIMIT_REQUESTS"] = "1000"
os.environ["RATE_LIMIT_WINDOW"] = "3600"

# Create a no-op middleware for testing
class NoOpMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)

# Patch the middleware classes before importing app
with patch('app.core.rate_limit.UsageTrackingMiddleware', NoOpMiddleware):
    with patch('app.core.error_tracking.ErrorTrackingMiddleware', NoOpMiddleware):
        from app.main import app
        from app.core.config import get_settings


@pytest.fixture(scope="session")
def settings():
    """Get test settings."""
    return get_settings()


@pytest.fixture
def client() -> Generator:
    """Create a test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    mock_client = MagicMock()
    mock_auth = MagicMock()
    mock_table = MagicMock()
    
    mock_client.auth = mock_auth
    mock_client.table = MagicMock(return_value=mock_table)
    
    return mock_client, mock_auth, mock_table


@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = Mock()
    user.id = "test-user-id-123"
    user.email = "test@example.com"
    user.user_metadata = {"full_name": "Test User"}
    return user


@pytest.fixture
def mock_auth_response(mock_user):
    """Create a mock auth response."""
    mock_response = Mock()
    mock_response.user = mock_user
    
    mock_session = Mock()
    mock_session.access_token = "test-access-token"
    mock_response.session = mock_session
    
    return mock_response


@pytest.fixture
def auth_headers():
    """Create authentication headers."""
    return {"Authorization": "Bearer test-access-token"}


@pytest.fixture
def sample_project():
    """Create a sample project."""
    return {
        "id": "test-project-id-456",
        "user_id": "test-user-id-123",
        "name": "Test Project",
        "description": "A test project for unit tests",
        "brand_voice": {"tone": "professional"},
        "target_platforms": ["twitter", "linkedin"],
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_content():
    """Create a sample content."""
    return {
        "id": "test-content-id-789",
        "project_id": "test-project-id-456",
        "user_id": "test-user-id-123",
        "title": "Test Content",
        "source_type": "url",
        "source_url": "https://example.com/article",
        "original_text": "This is a test article content. It has multiple sentences for testing purposes.",
        "word_count": 12,
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_generated_assets():
    """Create sample generated assets."""
    return [
        {
            "id": "asset-1",
            "content_id": "test-content-id-789",
            "user_id": "test-user-id-123",
            "type": "thread",
            "platform": "twitter",
            "content": "Test tweet thread content",
            "tokens_used": 150,
            "status": "generated",
            "created_at": "2024-01-01T00:00:00Z",
        },
        {
            "id": "asset-2",
            "content_id": "test-content-id-789",
            "user_id": "test-user-id-123",
            "type": "social_post",
            "platform": "linkedin",
            "content": "Test LinkedIn post content",
            "tokens_used": 200,
            "status": "generated",
            "created_at": "2024-01-01T00:00:00Z",
        },
    ]


@pytest.fixture
def sample_usage_stats():
    """Create sample usage stats."""
    return {
        "monthly_usage_count": 50,
        "monthly_usage_limit": 100,
        "remaining": 50,
    }


@pytest.fixture
def mock_request():
    """Create a mock request object."""
    request = Mock(spec=Request)
    request.headers = {}
    request.client = Mock()
    request.client.host = "127.0.0.1"
    request.state = Mock()
    request.state.user_id = None
    return request


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )

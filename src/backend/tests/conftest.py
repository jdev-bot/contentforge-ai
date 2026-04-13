"""
Pytest configuration and fixtures for ContentForge AI tests.
"""
import os
import sys
import pytest
from typing import Generator, Dict
from unittest.mock import Mock, MagicMock, patch, AsyncMock

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
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

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


def create_mock_auth_user(
    user_id: str = "test-user-id-123",
    email: str = "test@example.com",
    full_name: str = "Test User",
    is_active: bool = True
):
    """Create a mock authenticated user."""
    user = Mock()
    user.id = user_id
    user.email = email
    user.user_metadata = {"full_name": full_name}
    user.is_active = is_active
    return user


def _build_mock_supabase_client():
    """Build a mock Supabase client with chained query builders."""
    mock_auth = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "test-user-id-123"
    mock_user.email = "test@example.com"
    mock_user.user_metadata = {"full_name": "Test User"}
    mock_auth.get_user.return_value = MagicMock(user=mock_user)

    mock_query = MagicMock()
    mock_query.eq = MagicMock(return_value=mock_query)
    mock_query.neq = MagicMock(return_value=mock_query)
    mock_query.gt = MagicMock(return_value=mock_query)
    mock_query.gte = MagicMock(return_value=mock_query)
    mock_query.lt = MagicMock(return_value=mock_query)
    mock_query.lte = MagicMock(return_value=mock_query)
    mock_query.order = MagicMock(return_value=mock_query)
    mock_query.limit = MagicMock(return_value=mock_query)
    mock_query.offset = MagicMock(return_value=mock_query)
    mock_query.single = MagicMock(return_value=mock_query)
    mock_query.maybe_single = MagicMock(return_value=mock_query)
    mock_query.execute = MagicMock(return_value=MagicMock(data=[]))
    mock_query.contains = MagicMock(return_value=mock_query)
    mock_query.in_ = MagicMock(return_value=mock_query)

    mock_table = MagicMock()
    mock_table.select = MagicMock(return_value=mock_query)
    mock_table.insert = MagicMock(return_value=mock_query)
    mock_table.update = MagicMock(return_value=mock_query)
    mock_table.delete = MagicMock(return_value=mock_query)
    mock_table.upsert = MagicMock(return_value=mock_query)

    mock_storage = MagicMock()

    mock_client = MagicMock()
    mock_client.auth = mock_auth
    mock_client.table = MagicMock(return_value=mock_table)
    mock_client.storage = mock_storage

    return mock_client, mock_auth, mock_table, mock_storage, mock_query


def _build_mock_usage_stats():
    """Build mock usage stats for rate limiting."""
    mock_usage = MagicMock()
    mock_usage.remaining = 100
    mock_usage.monthly_usage_count = 10
    mock_usage.monthly_usage_limit = 100
    mock_usage.subscription_tier = "free"
    return mock_usage


# All module paths that import get_supabase_client from app.core.supabase
_SUPABASE_CLIENT_PATCH_TARGETS = [
    "app.core.supabase.get_supabase_client",
    "app.core.supabase.create_client",
    "app.core.rate_limit.get_supabase_client",
    "app.routers.ai_suggestions.get_supabase_client",
    "app.routers.auth.get_supabase_client",
    "app.routers.notifications.get_supabase_client",
    "app.routers.integrations.get_supabase_client",
    "app.routers.automation.get_supabase_client",
    "app.routers.webhooks.get_supabase_client",
    "app.routers.rss.get_supabase_client",
    "app.routers.user.get_supabase_client",
    "app.routers.analytics.get_supabase_client",
    "app.routers.alerts.get_supabase_client",
    "app.routers.projects.get_supabase_client",
    "app.routers.competitors.get_supabase_client",
    "app.routers.admin.get_supabase_client",
    "app.routers.freshness.get_supabase_client",
    "app.routers.content.get_supabase_client",
    "app.routers.search.get_supabase_client",
    "app.routers.stripe.get_supabase_client",
    "app.routers.organizations.get_supabase_client",
    "app.routers.ai_editor.get_supabase_client",
    "app.routers.distributions.get_supabase_client",
    "app.routers.health.get_supabase_client",
    "app.routers.trends.get_supabase_client",

    "app.routers.sentiment.get_supabase_client",
    "app.routers.quality_scoring.get_supabase_client",
    "app.routers.dashboards.get_supabase_client",
    "app.routers.reports.get_supabase_client",
    "app.services.audience_service.get_supabase_client",
    "app.services.freshness_service.get_supabase_client",
    "app.services.scheduler_service.get_supabase_client",
    "app.services.trend_service.get_supabase_client",
    "app.services.alert_service.get_supabase_client",
    "app.services.dashboard_service.get_supabase_client",
    "app.services.report_service.get_supabase_client",
    "app.services.competitor_service.get_supabase_client",
    "app.services.version_service.get_supabase_client",
    "app.services.audit_service.get_supabase_client",
    "app.services.quality_service.get_supabase_client",
    "app.services.sentiment_service.get_supabase_client",
    "app.core.trash.get_supabase_client",
    "app.core.error_tracking.get_supabase_client",
    "app.tasks.email.get_supabase_client",
]

_ADMIN_CLIENT_PATCH_TARGETS = [
    "app.core.supabase.get_supabase_admin_client",
    "app.routers.integrations.get_supabase_admin_client",
    "app.routers.webhooks.get_supabase_admin_client",
    "app.routers.user.get_supabase_admin_client",
    "app.routers.admin.get_supabase_admin_client",
    "app.routers.stripe.get_supabase_admin_client",
    "app.routers.organizations.get_supabase_admin_client",
    "app.services.audience_service.get_supabase_admin_client",
    "app.services.rss_service.get_supabase_admin_client",
    "app.services.dashboard_service.get_supabase_admin_client",
    "app.services.report_service.get_supabase_admin_client",
]

_RATE_LIMIT_PATCH_TARGETS = {
    "enforce_subscription_limit": [
        "app.routers.ai_suggestions",
        "app.routers.automation",
        "app.routers.competitors",
        "app.routers.content",
        "app.routers.ai_editor",
        "app.routers.trends",
        "app.routers.sentiment",
        "app.routers.quality_scoring",
    ],
    "check_and_increment_usage": [
        "app.routers.ai_suggestions",
        "app.routers.automation",
        "app.routers.competitors",
        "app.routers.content",
        "app.routers.ai_editor",
        "app.routers.trends",
        "app.routers.sentiment",
        "app.routers.quality_scoring",
    ],
    "rate_limit_dependency": [
        "app.routers.rss",
        "app.routers.scheduler",
    ],
}


@pytest.fixture(scope="session")
def settings():
    """Get test settings."""
    return get_settings()


@pytest.fixture
def client() -> Generator:
    """Create a test client with mocked Supabase."""
    from fastapi.testclient import TestClient
    from unittest.mock import MagicMock, patch
    
    mock_client, mock_auth, mock_table, mock_storage, mock_query = _build_mock_supabase_client()
    mock_usage = _build_mock_usage_stats()

    # Build context managers for all patches
    patches = []
    
    # Patch all get_supabase_client references
    # Use safe patching that skips targets where the attribute doesn't exist
    for target in _SUPABASE_CLIENT_PATCH_TARGETS:
        try:
            p = patch(target, return_value=mock_client)
            p.start()
            patches.append(p)
        except AttributeError:
            pass  # Module doesn't have this attribute — skip
    
    # Patch all get_supabase_admin_client references
    for target in _ADMIN_CLIENT_PATCH_TARGETS:
        try:
            p = patch(target, return_value=mock_client)
            p.start()
            patches.append(p)
        except AttributeError:
            pass  # Module doesn't have this attribute — skip
    
    # Patch rate limit enforcement to bypass auth/subscription checks
    for func_name, modules in _RATE_LIMIT_PATCH_TARGETS.items():
        for mod in modules:
            target = f"{mod}.{func_name}"
            try:
                p = patch(target, return_value=mock_usage)
                p.start()
                patches.append(p)
            except AttributeError:
                pass  # Module doesn't have this attribute — skip
    
    # Patch usage stats functions at the source module
    patches.append(patch("app.core.rate_limit.get_user_usage_stats", return_value=mock_usage))
    patches.append(patch("app.core.rate_limit.check_and_increment_usage", return_value=mock_usage))
    patches.append(patch("app.core.rate_limit.check_subscription_limit", return_value=mock_usage))
    patches.append(patch("app.core.rate_limit.check_monthly_reset", return_value=None))
    
    # Start all patches
    for p in patches:
        p.start()
    
    try:
        with TestClient(app) as test_client:
            # Store mocks on client for test access
            test_client.mock_supabase = (mock_client, mock_auth, mock_table, mock_storage, mock_query)
            yield test_client
    finally:
        # Stop all patches
        for p in patches:
            p.stop()


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    mock_client, mock_auth, mock_table, mock_storage, mock_query = _build_mock_supabase_client()
    return mock_client, mock_auth, mock_table


@pytest.fixture
def mock_user():
    """Create a mock user."""
    return create_mock_auth_user()


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
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "123e4567-e89b-12d3-a456-426614174001",
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
        "id": "123e4567-e89b-12d3-a456-426614174002",
        "project_id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "123e4567-e89b-12d3-a456-426614174001",
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
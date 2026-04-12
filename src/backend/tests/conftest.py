"""
Pytest fixtures for ContentForge AI tests.
"""
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

# Set test environment variables before importing app
os.environ["APP_NAME"] = "ContentForge AI Test"
os.environ["APP_ENV"] = "test"
os.environ["DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32bytes-long"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-role-key"
os.environ["GROQ_API_KEY"] = "test-groq-api-key"
os.environ["RESEND_API_KEY"] = "test-resend-api-key"
os.environ["STRIPE_SECRET_KEY"] = "test-stripe-secret-key"
os.environ["STRIPE_WEBHOOK_SECRET"] = "test-webhook-secret"

# Import app after setting env vars
from app.main import app


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client."""
    mock = MagicMock()
    
    # Mock auth methods
    mock.auth = MagicMock()
    mock.auth.sign_up = AsyncMock()
    mock.auth.sign_in_with_password = AsyncMock()
    mock.auth.sign_out = AsyncMock()
    mock.auth.get_user = AsyncMock()
    mock.auth.refresh_session = AsyncMock()
    
    # Mock table operations
    mock.table = MagicMock(return_value=MagicMock())
    mock.table().select = MagicMock(return_value=MagicMock())
    mock.table().insert = MagicMock(return_value=MagicMock())
    mock.table().update = MagicMock(return_value=MagicMock())
    mock.table().delete = MagicMock(return_value=MagicMock())
    mock.table().eq = MagicMock(return_value=MagicMock())
    mock.table().execute = AsyncMock()
    
    # Mock storage
    mock.storage = MagicMock()
    mock.storage.from_ = MagicMock(return_value=MagicMock())
    
    return mock


@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    return {
        "id": "test-user-id-123",
        "email": "test@example.com",
        "full_name": "Test User",
        "avatar_url": None,
        "subscription_tier": "free",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_auth_token():
    """Return a mock JWT token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test-token-for-mocking"


@pytest.fixture(autouse=True)
def reset_env_vars():
    """Reset environment variables between tests."""
    # Store original values
    original_vars = {key: os.environ.get(key) for key in [
        "APP_ENV", "DEBUG", "SECRET_KEY", "SUPABASE_URL", 
        "SUPABASE_KEY", "GROQ_API_KEY"
    ]}
    
    yield
    
    # Restore original values after test
    for key, value in original_vars.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]


@pytest.fixture
def mock_groq_response():
    """Create a mock Groq API response."""
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "llama-3.3-70b-versatile",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is a mock response from the AI model for testing purposes."
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }

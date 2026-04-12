"""
Authentication tests.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
from app.main import app

client = TestClient(app)


class MockAuthResponse:
    """Mock Supabase auth response."""
    def __init__(self, user=None, session=None):
        self.user = user
        self.session = session


class MockUser:
    """Mock Supabase user."""
    def __init__(self, id="test-user-id", email="test@example.com", user_metadata=None):
        self.id = id
        self.email = email
        self.user_metadata = user_metadata or {}


class MockSession:
    """Mock Supabase session."""
    def __init__(self, access_token="mock-token-123"):
        self.access_token = access_token


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client for auth tests."""
    mock = MagicMock()
    mock.auth = MagicMock()
    
    # Default successful sign_up response
    mock_user = MockUser(
        id="test-user-id",
        email="test@example.com",
        user_metadata={"full_name": "Test User"}
    )
    mock_session = MockSession(access_token="mock-jwt-token-123")
    
    mock.auth.sign_up = MagicMock(return_value=MockAuthResponse(
        user=mock_user,
        session=mock_session
    ))
    
    mock.auth.sign_in_with_password = MagicMock(return_value=MockAuthResponse(
        user=mock_user,
        session=mock_session
    ))
    
    mock.auth.sign_out = MagicMock()
    
    return mock


class TestAuthentication:
    """Test user authentication endpoints."""
    
    @patch("app.routers.auth.get_supabase_client")
    def test_register_user(self, mock_get_client, mock_supabase_client):
        """Test user registration."""
        mock_get_client.return_value = mock_supabase_client
        
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@example.com"
    
    @patch("app.routers.auth.get_supabase_client")
    def test_login_user(self, mock_get_client, mock_supabase_client):
        """Test user login."""
        mock_get_client.return_value = mock_supabase_client
        
        response = client.post("/api/v1/auth/login", json={
            "email": "test2@example.com",
            "password": "TestPassword123!"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_logout_user(self):
        """Test user logout."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 200

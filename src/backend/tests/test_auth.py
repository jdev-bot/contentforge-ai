"""
Authentication tests for ContentForge AI.

Tests user registration, login, logout, and current user retrieval.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import status

from tests.utils import (
    create_mock_supabase_response,
    create_mock_auth_user,
    create_mock_auth_session,
    create_auth_headers,
    assert_api_error,
    assert_api_success,
    MockSupabaseBuilder
)


class TestAuthRegister:
    """Tests for user registration endpoint."""
    
    @pytest.mark.unit
    def test_register_success(self, client):
        """Test successful user registration."""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New Test User",
        }
        
        mock_user = create_mock_auth_user(
            user_id="new-user-id",
            email="newuser@example.com",
            full_name="New Test User"
        )
        mock_session = create_mock_auth_session(user=mock_user)
        
        builder = MockSupabaseBuilder()
        builder.with_sign_up_response(user=mock_user, session=mock_session)
        
        with patch('app.routers.auth.get_supabase_client', return_value=builder.build()):
            # Act
            response = client.post("/api/v1/auth/register", json=user_data)
            
            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert "access_token" in data
            assert "user" in data
            assert data["user"]["email"] == "newuser@example.com"
            assert data["user"]["full_name"] == "New Test User"
    
    @pytest.mark.unit
    def test_register_missing_email(self, client):
        """Test registration with missing email."""
        user_data = {
            "password": "securepassword123",
            "full_name": "New Test User",
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        user_data = {
            "email": "not-an-email",
            "password": "securepassword123",
            "full_name": "New Test User",
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_register_weak_password(self, client):
        """Test registration with weak password (should still accept, validation is client-side)."""
        user_data = {
            "email": "test@example.com",
            "password": "123",
            "full_name": "Test User",
        }
        
        mock_user = create_mock_auth_user(email="test@example.com")
        mock_session = create_mock_auth_session(user=mock_user)
        
        builder = MockSupabaseBuilder()
        builder.with_sign_up_response(user=mock_user, session=mock_session)
        
        with patch('app.routers.auth.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/auth/register", json=user_data)
            
            # Backend accepts any password, actual validation in Supabase
            assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
    
    @pytest.mark.unit
    def test_register_existing_email(self, client):
        """Test registration with existing email."""
        user_data = {
            "email": "existing@example.com",
            "password": "securepassword123",
            "full_name": "Existing User",
        }
        
        mock_client = MagicMock()
        mock_client.auth.sign_up.side_effect = Exception("User already registered")
        
        with patch('app.routers.auth.get_supabase_client', return_value=mock_client):
            response = client.post("/api/v1/auth/register", json=user_data)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "already" in response.json()["detail"].lower() or "registration failed" in response.json()["detail"].lower()
    
    @pytest.mark.unit
    def test_register_email_confirmation_required(self, client):
        """Test registration when email confirmation is required."""
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New Test User",
        }
        
        mock_user = create_mock_auth_user(email="newuser@example.com")
        
        # No session = email confirmation required
        mock_response = Mock()
        mock_response.user = mock_user
        mock_response.session = None
        
        mock_client = MagicMock()
        mock_client.auth.sign_up.return_value = mock_response
        
        with patch('app.routers.auth.get_supabase_client', return_value=mock_client):
            response = client.post("/api/v1/auth/register", json=user_data)
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["access_token"] == ""  # Empty token when confirmation required


class TestAuthLogin:
    """Tests for user login endpoint."""
    
    @pytest.mark.unit
    def test_login_success(self, client):
        """Test successful user login."""
        login_data = {
            "email": "user@example.com",
            "password": "correctpassword",
        }
        
        mock_user = create_mock_auth_user(email="user@example.com", full_name="Test User")
        mock_session = create_mock_auth_session(user=mock_user, access_token="valid-token-123")
        
        builder = MockSupabaseBuilder()
        builder.with_sign_in_response(user=mock_user, session=mock_session)
        
        with patch('app.routers.auth.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/auth/login", json=login_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["access_token"] == "valid-token-123"
            assert data["token_type"] == "bearer"
            assert data["user"]["email"] == "user@example.com"
    
    @pytest.mark.unit
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            "email": "user@example.com",
            "password": "wrongpassword",
        }
        
        mock_client = MagicMock()
        mock_client.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")
        
        with patch('app.routers.auth.get_supabase_client', return_value=mock_client):
            response = client.post("/api/v1/auth/login", json=login_data)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "invalid" in response.json()["detail"].lower()
    
    @pytest.mark.unit
    def test_login_missing_password(self, client):
        """Test login with missing password."""
        login_data = {
            "email": "user@example.com",
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword",
        }
        
        mock_client = MagicMock()
        mock_client.auth.sign_in_with_password.side_effect = Exception("User not found")
        
        with patch('app.routers.auth.get_supabase_client', return_value=mock_client):
            response = client.post("/api/v1/auth/login", json=login_data)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthLogout:
    """Tests for user logout endpoint."""
    
    @pytest.mark.unit
    def test_logout_success(self, client):
        """Test successful logout."""
        headers = create_auth_headers("valid-token")
        
        mock_client = MagicMock()
        mock_client.auth.sign_out.return_value = None
        
        with patch('app.routers.auth.get_supabase_client', return_value=mock_client):
            response = client.post("/api/v1/auth/logout", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            assert "logged out" in response.json()["message"].lower()
    
    @pytest.mark.unit
    def test_logout_no_auth_header(self, client):
        """Test logout without authorization header."""
        response = client.post("/api/v1/auth/logout")
        
        # Should still succeed, just no-op
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.unit
    def test_logout_invalid_token(self, client):
        """Test logout with invalid token."""
        headers = create_auth_headers("invalid-token")
        
        mock_client = MagicMock()
        mock_client.auth.sign_out.side_effect = Exception("Invalid token")
        
        with patch('app.routers.auth.get_supabase_client', return_value=mock_client):
            response = client.post("/api/v1/auth/logout", headers=headers)
            
            # Should still succeed - client-side logout
            assert response.status_code == status.HTTP_200_OK


class TestAuthMe:
    """Tests for current user endpoint."""
    
    @pytest.mark.unit
    def test_get_current_user_success(self, client):
        """Test getting current authenticated user."""
        from app.routers.auth import get_auth_user
        headers = create_auth_headers("valid-token")
        
        mock_user = create_mock_auth_user(
            user_id="123e4567-e89b-12d3-a456-426614174010",
            email="current@example.com",
            full_name="Current User"
        )
        
        # Profile data response
        profile_data = {
            "subscription_tier": "free",
            "monthly_usage_count": 0,
            "monthly_usage_limit": 10,
        }
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=profile_data)
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        # Override get_auth_user to return our custom user for this test
        original_override = client.app.dependency_overrides.get(get_auth_user)
        client.app.dependency_overrides[get_auth_user] = lambda: mock_user
        try:
            with patch('app.routers.auth.get_supabase_client', return_value=mock_client):
                response = client.get("/api/v1/auth/me", headers=headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["email"] == "current@example.com"
                assert data["full_name"] == "Current User"
                assert data["is_active"] is True
        finally:
            if original_override is not None:
                client.app.dependency_overrides[get_auth_user] = original_override
    
    @pytest.mark.unit
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.unit
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        from app.routers.auth import get_auth_user
        headers = create_auth_headers("invalid-token")
        
        mock_client = MagicMock()
        mock_client.auth.get_user.side_effect = Exception("Invalid token")
        
        # Remove auth override so real get_auth_user runs (which will call supabase.auth.get_user)
        original_override = client.app.dependency_overrides.pop(get_auth_user, None)
        try:
            with patch('app.routers.auth.get_supabase_client', return_value=mock_client):
                response = client.get("/api/v1/auth/me", headers=headers)
                
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
        finally:
            if original_override is not None:
                client.app.dependency_overrides[get_auth_user] = original_override
    
    @pytest.mark.unit
    def test_get_current_user_expired_token(self, client):
        """Test getting current user with expired token."""
        from app.routers.auth import get_auth_user
        headers = create_auth_headers("expired-token")
        
        mock_client = MagicMock()
        mock_user_response = Mock()
        mock_user_response.user = None
        mock_client.auth.get_user.return_value = mock_user_response
        
        # Remove auth override so real get_auth_user runs
        original_override = client.app.dependency_overrides.pop(get_auth_user, None)
        try:
            with patch('app.routers.auth.get_supabase_client', return_value=mock_client):
                response = client.get("/api/v1/auth/me", headers=headers)
                
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
        finally:
            if original_override is not None:
                client.app.dependency_overrides[get_auth_user] = original_override
    
    @pytest.mark.unit
    def test_get_current_user_malformed_header(self, client):
        """Test getting current user with malformed auth header."""
        headers = {"Authorization": "NotBearer token"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthValidation:
    """Tests for auth input validation."""
    
    @pytest.mark.unit
    def test_register_empty_full_name(self, client):
        """Test registration with empty full name."""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "",
        }
        
        mock_user = create_mock_auth_user(full_name="")
        mock_session = create_mock_auth_session(user=mock_user)
        
        builder = MockSupabaseBuilder()
        builder.with_sign_up_response(user=mock_user, session=mock_session)
        
        with patch('app.routers.auth.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/auth/register", json=user_data)
            
            # Empty strings are still valid input
            assert response.status_code == status.HTTP_201_CREATED
    
    @pytest.mark.unit
    def test_register_unicode_in_name(self, client):
        """Test registration with unicode characters in name."""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "José García 中文",
        }
        
        mock_user = create_mock_auth_user(full_name="José García 中文")
        mock_session = create_mock_auth_session(user=mock_user)
        
        builder = MockSupabaseBuilder()
        builder.with_sign_up_response(user=mock_user, session=mock_session)
        
        with patch('app.routers.auth.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/auth/register", json=user_data)
            
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["user"]["full_name"] == "José García 中文"

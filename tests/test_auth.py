"""
Authentication endpoint tests for ContentForge AI.
Tests user registration, login, logout, and current user endpoints.
"""
import pytest
from fastapi import status
from unittest.mock import MagicMock, patch


class TestAuthRegister:
    """Test user registration endpoint."""
    
    def test_register_success(self, client, mock_supabase, mock_session):
        """Test successful user registration."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        # Mock successful sign up
        mock_user = MagicMock(
            id="new-user-id-456",
            email="newuser@example.com",
        )
        mock_auth.sign_up.return_value = MagicMock(
            user=mock_user,
            session=mock_session
        )
        
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "full_name": "New Test User"
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["access_token"] == "test-access-token"
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["full_name"] == "New Test User"
        
        mock_auth.sign_up.assert_called_once()
    
    def test_register_email_confirmation_required(self, client, mock_supabase):
        """Test registration when email confirmation is required."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        # Mock user without session (email confirmation required)
        mock_user = MagicMock(
            id="pending-user-id",
            email="pending@example.com",
        )
        mock_auth.sign_up.return_value = MagicMock(
            user=mock_user,
            session=None
        )
        
        response = client.post("/api/v1/auth/register", json={
            "email": "pending@example.com",
            "password": "SecurePassword123!",
            "full_name": "Pending User"
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["access_token"] == ""  # Empty token when confirmation required
        assert data["user"]["email"] == "pending@example.com"
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com"
            # Missing password and full_name
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_weak_password(self, client):
        """Test registration with weak password (still valid format)."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        mock_auth.sign_up.side_effect = Exception("Password too weak")
        
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "123",  # Very weak password
            "full_name": "Test User"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAuthLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client, mock_supabase, mock_session):
        """Test successful user login."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        mock_user = MagicMock(
            id="test-user-id-123",
            email="test@example.com",
            user_metadata={"full_name": "Test User"}
        )
        mock_auth.sign_in_with_password.return_value = MagicMock(
            user=mock_user,
            session=mock_session
        )
        
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "CorrectPassword123!"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["access_token"] == "test-access-token"
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["full_name"] == "Test User"
    
    def test_login_invalid_credentials(self, client, mock_supabase):
        """Test login with invalid credentials."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        mock_auth.sign_in_with_password.side_effect = Exception("Invalid credentials")
        
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client, mock_supabase):
        """Test login with non-existent user."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        mock_auth.sign_in_with_password.side_effect = Exception("User not found")
        
        response = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_email(self, client):
        """Test login with missing email."""
        response = client.post("/api/v1/auth/login", json={
            "password": "SomePassword123!"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_password(self, client):
        """Test login with missing password."""
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthLogout:
    """Test user logout endpoint."""
    
    def test_logout_success(self, client, mock_supabase, auth_headers):
        """Test successful logout."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Logged out successfully"
        mock_auth.sign_out.assert_called_once()
    
    def test_logout_no_token(self, client, mock_supabase):
        """Test logout without authorization header."""
        response = client.post("/api/v1/auth/logout")
        
        # Should still return success as it's a no-op
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Logged out successfully"
    
    def test_logout_invalid_token(self, client, mock_supabase):
        """Test logout with invalid token."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        # Mock sign_out to raise exception
        mock_auth.sign_out.side_effect = Exception("Invalid token")
        
        response = client.post("/api/v1/auth/logout", headers={
            "Authorization": "Bearer invalid-token"
        })
        
        # Should still return success (fail silently)
        assert response.status_code == status.HTTP_200_OK


class TestAuthMe:
    """Test current user endpoint."""
    
    def test_get_current_user_success(self, client, mock_supabase, auth_headers, mock_user, mock_session):
        """Test getting current user with valid token."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        mock_auth.get_user.return_value = MagicMock(user=mock_user)
        
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "test-user-id-123"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["is_active"] == True
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing or invalid authorization header" in response.json()["detail"]
    
    def test_get_current_user_invalid_token(self, client, mock_supabase):
        """Test getting current user with invalid token."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        mock_auth.get_user.side_effect = Exception("Invalid token")
        
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid-token"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authentication failed" in response.json()["detail"]
    
    def test_get_current_user_expired_token(self, client, mock_supabase):
        """Test getting current user with expired token."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        mock_auth.get_user.return_value = MagicMock(user=None)
        
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer expired-token"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token" in response.json()["detail"]
    
    def test_get_current_user_malformed_header(self, client):
        """Test getting current user with malformed authorization header."""
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "NotBearer token"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing or invalid authorization header" in response.json()["detail"]


class TestAuthIntegration:
    """Integration tests for authentication flow."""
    
    def test_full_auth_flow(self, client, mock_supabase, mock_session):
        """Test complete authentication flow: register -> login -> me -> logout."""
        mock_client, mock_auth, _, _ = mock_supabase
        
        # Register
        mock_user = MagicMock(
            id="flow-user-id",
            email="flow@example.com",
        )
        mock_auth.sign_up.return_value = MagicMock(
            user=mock_user,
            session=mock_session
        )
        
        register_response = client.post("/api/v1/auth/register", json={
            "email": "flow@example.com",
            "password": "FlowPassword123!",
            "full_name": "Flow Test User"
        })
        assert register_response.status_code == status.HTTP_201_CREATED
        token = register_response.json()["access_token"]
        
        # Get current user
        mock_auth.get_user.return_value = MagicMock(user=MagicMock(
            id="flow-user-id",
            email="flow@example.com",
            user_metadata={"full_name": "Flow Test User"}
        ))
        
        me_response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.json()["email"] == "flow@example.com"
        
        # Logout
        logout_response = client.post("/api/v1/auth/logout", headers={
            "Authorization": f"Bearer {token}"
        })
        assert logout_response.status_code == status.HTTP_200_OK

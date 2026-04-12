"""
Authentication endpoint tests for ContentForge AI.
Tests user registration, login, logout, and current user endpoints.
"""
import pytest
from fastapi import status
from unittest.mock import MagicMock


class TestAuthRegister:
    """Test user registration endpoint."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        
        # Mock successful sign up
        mock_user = MagicMock()
        mock_user.id = "new-user-id-456"
        mock_user.email = "newuser@example.com"
        mock_session = MagicMock()
        mock_session.access_token = "test-access-token"
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
        
        mock_auth.sign_up.assert_called_once()
    
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


class TestAuthLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client):
        """Test successful user login."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        
        mock_user = MagicMock()
        mock_user.id = "test-user-id-123"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {"full_name": "Test User"}
        mock_session = MagicMock()
        mock_session.access_token = "test-access-token"
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
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        
        mock_auth.sign_in_with_password.side_effect = Exception("Invalid credentials")
        
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid credentials" in response.json()["detail"]
    
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
    
    def test_logout_success(self, client):
        """Test successful logout."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        
        response = client.post("/api/v1/auth/logout", headers={
            "Authorization": "Bearer test-token"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Logged out successfully"
    
    def test_logout_no_token(self, client):
        """Test logout without authorization header."""
        response = client.post("/api/v1/auth/logout")
        
        # Should still return success as it's a no-op
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Logged out successfully"


class TestAuthMe:
    """Test current user endpoint."""
    
    def test_get_current_user_success(self, client):
        """Test getting current user with valid token."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        
        mock_user = MagicMock()
        mock_user.id = "test-user-id-123"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {"full_name": "Test User"}
        mock_auth.get_user.return_value = MagicMock(user=mock_user)
        
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer test-token"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "test-user-id-123"
        assert data["email"] == "test@example.com"
        assert data["is_active"] == True
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing or invalid authorization header" in response.json()["detail"]
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        mock_client, mock_auth, _, _, _ = client.mock_supabase
        
        mock_auth.get_user.side_effect = Exception("Invalid token")
        
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid-token"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authentication failed" in response.json()["detail"]
    
    def test_get_current_user_malformed_header(self, client):
        """Test getting current user with malformed authorization header."""
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "NotBearer token"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing or invalid authorization header" in response.json()["detail"]

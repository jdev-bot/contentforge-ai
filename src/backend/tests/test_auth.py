"""
Authentication tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAuthentication:
    """Test user authentication endpoints."""
    
    def test_register_user(self):
        """Test user registration."""
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        })
        assert response.status_code in [201, 400]  # 201 success or 400 if user exists
    
    def test_login_user(self):
        """Test user login."""
        # First register
        client.post("/api/v1/auth/register", json={
            "email": "test2@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        })
        
        # Then login
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

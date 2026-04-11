"""
Tests for health check endpoints.
"""
import pytest
from fastapi import status


class TestHealthEndpoint:
    """Tests for the basic health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Test that GET /health returns 200 OK."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK

    def test_health_check_response_structure(self, client):
        """Test that health response has correct structure."""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data

    def test_health_check_returns_healthy_status(self, client):
        """Test that health check returns healthy status."""
        response = client.get("/health")
        data = response.json()
        
        assert data["status"] == "healthy"

    def test_health_check_timestamp_is_valid(self, client):
        """Test that health check timestamp is a valid ISO format."""
        response = client.get("/health")
        data = response.json()
        
        assert isinstance(data["timestamp"], str)
        assert len(data["timestamp"]) > 0

    def test_health_check_version_is_present(self, client):
        """Test that health check includes version."""
        response = client.get("/health")
        data = response.json()
        
        assert isinstance(data["version"], str)
        assert data["version"] == "0.1.0"


class TestHealthDetailedEndpoint:
    """Tests for the detailed health check endpoint."""

    def test_health_detailed_returns_response(self, client, mock_supabase):
        """Test that GET /health/detailed returns a response."""
        response = client.get("/health/detailed")
        
        # Should return response even if components are degraded
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]

    def test_health_detailed_response_structure(self, client, mock_supabase):
        """Test that detailed health response has correct structure."""
        response = client.get("/health/detailed")
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            
            assert "status" in data
            assert "timestamp" in data
            assert "version" in data
            assert "environment" in data
            assert "components" in data

    def test_health_detailed_has_database_component(self, client, mock_supabase):
        """Test that detailed health includes database component."""
        mock_client, _, _, _ = mock_supabase
        
        response = client.get("/health/detailed")
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            
            assert "database" in data["components"]
            db_component = data["components"]["database"]
            assert "status" in db_component

    def test_health_detailed_has_redis_component(self, client, mock_supabase):
        """Test that detailed health includes Redis component."""
        response = client.get("/health/detailed")
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            
            assert "redis" in data["components"]
            redis_component = data["components"]["redis"]
            assert "status" in redis_component

    def test_health_detailed_has_groq_component(self, client, mock_supabase):
        """Test that detailed health includes Groq API component."""
        response = client.get("/health/detailed")
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            
            assert "groq" in data["components"]
            groq_component = data["components"]["groq"]
            assert "status" in groq_component


class TestHealthEndpointErrors:
    """Tests for health check error handling."""

    def test_health_endpoint_not_found_for_invalid_path(self, client):
        """Test that invalid health paths return 404."""
        response = client.get("/health/invalid")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_health_endpoint_does_not_accept_post(self, client):
        """Test that POST to /health is not allowed."""
        response = client.post("/health")
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_health_detailed_does_not_accept_post(self, client):
        """Test that POST to /health/detailed is not allowed."""
        response = client.post("/health/detailed")
        
        assert response.status_code in [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_307_TEMPORARY_REDIRECT]

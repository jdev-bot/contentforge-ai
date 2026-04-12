"""
Tests for analytics router functionality.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock


class TestAnalyticsEndpoints:
    """Test suite for analytics endpoints."""

    def _setup_mock_user(self, mock_auth):
        """Helper to setup mock authenticated user."""
        mock_user = MagicMock()
        mock_user.id = "test-user-id-123"
        mock_user.email = "test@example.com"
        mock_auth.get_user.return_value = MagicMock(user=mock_user)
        return mock_user

    def test_get_dashboard_kpis_success(self, client):
        """Test successful retrieval of dashboard KPIs."""
        mock_client, mock_auth, mock_table, mock_storage, mock_query = client.mock_supabase
        self._setup_mock_user(mock_auth)
        
        # Setup mock data
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        now = datetime.now().isoformat()
        
        # Single execute that returns one value - we need to set up a proper side effect chain
        call_count = [0]
        def mock_execute():
            call_count[0] += 1
            if call_count[0] == 1:
                return Mock(data=[
                    {"created_at": thirty_days_ago},
                    {"created_at": now},
                ])
            elif call_count[0] == 2:
                return Mock(data=[
                    {"created_at": thirty_days_ago},
                    {"created_at": now},
                    {"created_at": now},
                ])
            else:
                return Mock(data=[
                    {"status": "published", "platform": "twitter"},
                    {"status": "published", "platform": "linkedin"},
                    {"status": "failed", "platform": "twitter"},
                ])
        
        mock_query.execute = mock_execute
        
        response = client.get("/api/v1/analytics/dashboard", headers={"Authorization": "Bearer test-token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_content"] == 2
        assert data["total_assets"] == 3
        assert data["total_distributions"] == 3
        assert data["published_distributions"] == 2
        assert "distribution_success_rate" in data

    def test_get_content_metrics_success(self, client):
        """Test successful retrieval of content metrics."""
        mock_client, mock_auth, mock_table, mock_storage, mock_query = client.mock_supabase
        self._setup_mock_user(mock_auth)
        
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        now = datetime.now().isoformat()
        
        mock_query.execute.return_value = Mock(data=[
            {"status": "completed", "created_at": thirty_days_ago},
            {"status": "completed", "created_at": now},
            {"status": "failed", "created_at": now},
        ])
        
        response = client.get("/api/v1/analytics/content", headers={"Authorization": "Bearer test-token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_content"] == 3
        assert len(data["by_status"]) == 2

    def test_get_asset_metrics_success(self, client):
        """Test successful retrieval of asset metrics."""
        mock_client, mock_auth, mock_table, mock_storage, mock_query = client.mock_supabase
        self._setup_mock_user(mock_auth)
        
        mock_query.execute.return_value = Mock(data=[
            {"type": "thread", "platform": "twitter"},
            {"type": "social_post", "platform": "linkedin"},
            {"type": "newsletter", "platform": None},
        ])
        
        response = client.get("/api/v1/analytics/assets", headers={"Authorization": "Bearer test-token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_assets"] == 3
        assert len(data["by_type"]) == 3

    def test_get_distribution_metrics_success(self, client):
        """Test successful retrieval of distribution metrics."""
        mock_client, mock_auth, mock_table, mock_storage, mock_query = client.mock_supabase
        self._setup_mock_user(mock_auth)
        
        mock_query.execute.return_value = Mock(data=[
            {"status": "published", "platform": "twitter"},
            {"status": "published", "platform": "twitter"},
            {"status": "failed", "platform": "twitter"},
            {"status": "published", "platform": "linkedin"},
        ])
        
        response = client.get("/api/v1/analytics/distributions", headers={"Authorization": "Bearer test-token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_distributions"] == 4
        assert "by_status" in data
        assert "by_platform" in data
        assert "success_rate" in data

    def test_get_usage_metrics_with_date_range(self, client):
        """Test usage metrics with different date ranges."""
        mock_client, mock_auth, mock_table, mock_storage, mock_query = client.mock_supabase
        self._setup_mock_user(mock_auth)
        
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        now = datetime.now().isoformat()
        
        mock_query.execute.return_value = Mock(data=[
            {"created_at": seven_days_ago, "event_type": "content_generation"},
            {"created_at": now, "event_type": "asset_generation"},
        ])
        
        response = client.get("/api/v1/analytics/usage?days=7", headers={"Authorization": "Bearer test-token"})
        
        assert response.status_code == 200
        data = response.json()
        assert "daily_counts" in data
        assert "weekly_counts" in data
        assert "monthly_counts" in data
        assert data["total_in_period"] == 2
        assert "average_daily" in data

    def test_export_analytics_csv(self, client):
        """Test CSV export of analytics data."""
        mock_client, mock_auth, mock_table, mock_storage, mock_query = client.mock_supabase
        self._setup_mock_user(mock_auth)
        
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        call_count = [0]
        def mock_execute():
            call_count[0] += 1
            if call_count[0] == 1:
                return Mock(data=[
                    {"created_at": thirty_days_ago, "title": "Test", "source_type": "url", "status": "completed", "word_count": 100},
                ])
            elif call_count[0] == 2:
                return Mock(data=[
                    {"created_at": thirty_days_ago, "type": "thread", "platform": "twitter", "tokens_used": 150, "status": "generated"},
                ])
            else:
                return Mock(data=[
                    {"created_at": thirty_days_ago, "event_type": "content_generation", "tokens_used": 50, "metadata": {}},
                ])
        
        mock_query.execute = mock_execute
        
        response = client.get("/api/v1/analytics/export?format=csv&days=30", headers={"Authorization": "Bearer test-token"})
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

    def test_export_analytics_json(self, client):
        """Test JSON export of analytics data."""
        mock_client, mock_auth, mock_table, mock_storage, mock_query = client.mock_supabase
        self._setup_mock_user(mock_auth)
        
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        call_count = [0]
        def mock_execute():
            call_count[0] += 1
            if call_count[0] == 1:
                return Mock(data=[
                    {"id": "1", "created_at": thirty_days_ago, "title": "Test", "source_type": "url", "status": "completed", "word_count": 100},
                ])
            elif call_count[0] == 2:
                return Mock(data=[
                    {"id": "2", "created_at": thirty_days_ago, "type": "thread", "platform": "twitter", "tokens_used": 150, "status": "generated"},
                ])
            else:
                return Mock(data=[
                    {"id": "3", "created_at": thirty_days_ago, "event_type": "content_generation", "tokens_used": 50, "metadata": {}},
                ])
        
        mock_query.execute = mock_execute
        
        response = client.get("/api/v1/analytics/export/json?days=30", headers={"Authorization": "Bearer test-token"})
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert "export_info" in data
        assert "content" in data
        assert "assets" in data
        assert "usage" in data
        assert "summary" in data
        assert data["summary"]["total_content"] == 1

    def test_analytics_endpoints_require_auth(self, client):
        """Test that analytics endpoints require authentication."""
        endpoints = [
            "/api/v1/analytics/dashboard",
            "/api/v1/analytics/content",
            "/api/v1/analytics/assets",
            "/api/v1/analytics/distributions",
            "/api/v1/analytics/usage",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require auth"

    def test_dashboard_handles_empty_data(self, client):
        """Test dashboard handles empty data gracefully."""
        mock_client, mock_auth, mock_table, mock_storage, mock_query = client.mock_supabase
        self._setup_mock_user(mock_auth)
        
        call_count = [0]
        def mock_execute():
            call_count[0] += 1
            return Mock(data=[])
        
        mock_query.execute = mock_execute
        
        response = client.get("/api/v1/analytics/dashboard", headers={"Authorization": "Bearer test-token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_content"] == 0
        assert data["total_assets"] == 0
        assert data["total_distributions"] == 0
        assert data["distribution_success_rate"] == 0.0

    def test_usage_metrics_invalid_days(self, client):
        """Test usage metrics validation for days parameter."""
        self._setup_mock_user(client.mock_supabase[1])
        
        response = client.get("/api/v1/analytics/usage?days=5", headers={"Authorization": "Bearer test-token"})
        
        # FastAPI Query validation with ge=7 should reject this
        assert response.status_code == 422

    def test_export_csv_only_supported(self, client):
        """Test that only CSV format is supported for old endpoint."""
        self._setup_mock_user(client.mock_supabase[1])
        
        response = client.get("/api/v1/analytics/export?format=json", headers={"Authorization": "Bearer test-token"})
        
        assert response.status_code == 400
        assert "Only CSV format" in response.json()["detail"]

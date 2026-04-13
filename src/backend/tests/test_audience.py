"""
Tests for audience growth metrics API.
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock


# Fixtures
@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    user = Mock()
    user.id = str(uuid4())
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client."""
    with patch("app.services.audience_service.get_supabase_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def audience_service(mock_supabase):
    """Create an AudienceService instance with mocked dependencies."""
    from app.services.audience_service import AudienceService
    return AudienceService()


# Test Service Layer

class TestAudienceService:
    """Tests for the AudienceService class."""
    
    def test_record_metric(self, audience_service, mock_supabase, mock_user):
        """Test recording a new audience metric."""
        # Arrange
        mock_response = Mock()
        mock_response.data = [{
            "id": str(uuid4()),
            "user_id": mock_user.id,
            "platform": "twitter",
            "metric_type": "followers",
            "value": 1000,
            "period": "daily",
            "recorded_at": datetime.utcnow().isoformat()
        }]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        # Act
        result = audience_service.record_metric(
            user_id=mock_user.id,
            platform="twitter",
            metric_type="followers",
            value=1000
        )
        
        # Assert
        assert result is not None
        assert result["platform"] == "twitter"
        assert result["metric_type"] == "followers"
        assert result["value"] == 1000
    
    def test_get_growth_metrics(self, audience_service, mock_supabase, mock_user):
        """Test retrieving growth metrics."""
        # Arrange
        mock_response = Mock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "user_id": mock_user.id,
                "platform": "twitter",
                "metric_type": "followers",
                "value": 1000,
                "recorded_at": datetime.utcnow().isoformat()
            }
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.order.return_value.execute.return_value = mock_response
        
        # Mock _calculate_growth_rate to return consistent values
        with patch.object(audience_service, '_calculate_growth_rate') as mock_growth:
            mock_growth.return_value = 5.5
            
            # Act
            result = audience_service.get_growth_metrics(mock_user.id, days=30)
            
            # Assert
            assert "metrics" in result
            assert "growth_rates" in result
            assert result["period_days"] == 30
    
    def test_get_platforms_metrics(self, audience_service, mock_supabase, mock_user):
        """Test retrieving platform-specific metrics."""
        # Arrange
        mock_response = Mock()
        mock_response.data = [
            {"platform": "twitter", "metric_type": "followers", "value": 1000},
            {"platform": "linkedin", "metric_type": "followers", "value": 500}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.execute.return_value = mock_response
        
        with patch.object(audience_service, '_get_current_followers') as mock_followers, \
             patch.object(audience_service, '_calculate_follower_growth') as mock_growth:
            mock_followers.return_value = 1000
            mock_growth.return_value = 50
            
            # Act
            result = audience_service.get_platforms_metrics(mock_user.id, days=30)
            
            # Assert
            assert isinstance(result, list)
            assert len(result) == 2
    
    def test_get_historical_data(self, audience_service, mock_supabase, mock_user):
        """Test retrieving historical data."""
        # Arrange
        mock_response = Mock()
        mock_response.data = [
            {"recorded_at": (datetime.utcnow() - timedelta(days=i)).isoformat(), "value": 1000 + i}
            for i in range(10)
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.execute.return_value = mock_response
        
        # Act
        result = audience_service.get_historical_data(
            user_id=mock_user.id,
            metric_type="followers",
            days=30
        )
        
        # Assert
        assert len(result) == 10
        assert all("recorded_at" in item for item in result)
    
    def test_calculate_growth_snapshot(self, audience_service, mock_supabase, mock_user):
        """Test calculating and storing a growth snapshot."""
        # Arrange
        mock_response = Mock()
        mock_response.data = [{
            "id": str(uuid4()),
            "user_id": mock_user.id,
            "total_followers": 1500,
            "new_followers_7d": 50,
            "new_followers_30d": 200,
            "engagement_rate": 3.5,
            "top_performing_content": [],
            "recorded_at": datetime.utcnow().isoformat()
        }]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        with patch.object(audience_service, '_get_total_followers') as mock_total, \
             patch.object(audience_service, '_calculate_follower_growth') as mock_growth, \
             patch.object(audience_service, '_calculate_engagement_rate') as mock_engagement, \
             patch.object(audience_service, '_identify_top_performing_content') as mock_top:
            mock_total.return_value = 1500
            mock_growth.side_effect = [50, 200]  # 7d, 30d
            mock_engagement.return_value = 3.5
            mock_top.return_value = []
            
            # Act
            result = audience_service.calculate_growth_snapshot(mock_user.id)
            
            # Assert
            assert result is not None
            assert result["total_followers"] == 1500
    
    def test_calculate_growth_rate(self, audience_service, mock_supabase, mock_user):
        """Test growth rate calculation."""
        # Arrange
        current_followers = 1100
        past_followers = 1000
        
        with patch.object(audience_service, '_get_followers_at_date') as mock_followers:
            mock_followers.side_effect = [current_followers, past_followers]
            
            # Act
            result = audience_service._calculate_growth_rate(mock_user.id, None, 30)
            
            # Assert
            assert result == 10.0  # (1100 - 1000) / 1000 * 100
    
    def test_calculate_growth_rate_zero_past(self, audience_service, mock_supabase, mock_user):
        """Test growth rate calculation when past followers is zero."""
        # Arrange
        with patch.object(audience_service, '_get_followers_at_date') as mock_followers:
            mock_followers.side_effect = [100, 0]
            
            # Act
            result = audience_service._calculate_growth_rate(mock_user.id, None, 30)
            
            # Assert
            assert result == 0.0
    
    def test_get_current_followers(self, audience_service, mock_supabase, mock_user):
        """Test getting current follower count."""
        # Arrange
        mock_response = Mock()
        mock_response.data = [{"value": 1500}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        
        # Act
        result = audience_service._get_current_followers(mock_user.id, "twitter")
        
        # Assert
        assert result == 1500
    
    def test_calculate_follower_growth(self, audience_service, mock_supabase, mock_user):
        """Test calculating absolute follower growth."""
        # Arrange
        with patch.object(audience_service, '_get_followers_at_date') as mock_followers:
            mock_followers.side_effect = [1500, 1400]  # current, past
            
            # Act
            result = audience_service._calculate_follower_growth(mock_user.id, "twitter", 7)
            
            # Assert
            assert result == 100
    
    def test_predict_growth(self, audience_service, mock_supabase, mock_user):
        """Test growth prediction."""
        # Arrange
        with patch.object(audience_service, '_calculate_follower_growth') as mock_growth, \
             patch.object(audience_service, '_get_total_followers') as mock_total:
            mock_growth.side_effect = [210, 70]  # 30d, 7d
            mock_total.return_value = 1000
            
            # Act
            result = audience_service._predict_growth(mock_user.id)
            
            # Assert
            assert "projected_30d" in result
            assert "projected_90d" in result
            assert "growth_rate" in result
            assert result["confidence"] in ["low", "medium", "high"]
    
    def test_generate_insights(self, audience_service, mock_supabase, mock_user):
        """Test generating audience insights."""
        # Arrange
        with patch.object(audience_service, 'get_growth_metrics') as mock_growth, \
             patch.object(audience_service, 'get_platforms_metrics') as mock_platforms, \
             patch.object(audience_service, 'get_latest_snapshot') as mock_snapshot:
            
            mock_growth.return_value = {
                "metrics": [],
                "growth_rates": {"7d": 2.5, "30d": 10.0, "90d": 25.0},
                "current_totals": {},
                "platform": None,
                "period_days": 30
            }
            mock_platforms.return_value = []
            mock_snapshot.return_value = {
                "total_followers": 1500,
                "engagement_rate": 3.5
            }
            
            # Act
            result = audience_service.generate_insights(mock_user.id, days=30)
            
            # Assert
            assert "summary" in result
            assert "trends" in result
            assert "comparisons" in result
            assert "predictions" in result
            assert "recommendations" in result


# Test API Endpoints

class TestAudienceRouter:
    """Tests for the audience router endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)
    
    def test_get_growth_metrics_endpoint(self, client, mock_user):
        """Test the GET /api/v1/audience/growth endpoint."""
        with patch("app.routers.audience.get_auth_user", return_value=mock_user), \
             patch("app.routers.audience.audience_service") as mock_service:
            
            mock_service.get_growth_metrics.return_value = {
                "metrics": [],
                "growth_rates": {"7d": 5.0, "30d": 15.0, "90d": 30.0},
                "current_totals": {"twitter": 1000},
                "platform": None,
                "period_days": 30
            }
            
            response = client.get("/api/v1/audience/growth?days=30")
            
            assert response.status_code == 200
            data = response.json()
            assert "growth_rates" in data
            assert data["growth_rates"]["30d"] == 15.0
    
    def test_get_platforms_metrics_endpoint(self, client, mock_user):
        """Test the GET /api/v1/audience/platforms endpoint."""
        with patch("app.routers.audience.get_auth_user", return_value=mock_user), \
             patch("app.routers.audience.audience_service") as mock_service:
            
            mock_service.get_platforms_metrics.return_value = [
                {
                    "platform": "twitter",
                    "current_followers": 1000,
                    "growth_7d": 50,
                    "growth_30d": 200
                }
            ]
            
            response = client.get("/api/v1/audience/platforms")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["platform"] == "twitter"
    
    def test_get_historical_data_endpoint(self, client, mock_user):
        """Test the GET /api/v1/audience/history endpoint."""
        with patch("app.routers.audience.get_auth_user", return_value=mock_user), \
             patch("app.routers.audience.audience_service") as mock_service:
            
            mock_service.get_historical_data.return_value = [
                {"recorded_at": datetime.utcnow().isoformat(), "value": 1000}
            ]
            
            response = client.get("/api/v1/audience/history?days=90&metric_type=followers")
            
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
    
    def test_record_metric_endpoint(self, client, mock_user):
        """Test the POST /api/v1/audience/record endpoint."""
        with patch("app.routers.audience.get_auth_user", return_value=mock_user), \
             patch("app.routers.audience.audience_service") as mock_service:
            
            mock_service.record_metric.return_value = {
                "id": str(uuid4()),
                "user_id": mock_user.id,
                "platform": "twitter",
                "metric_type": "followers",
                "value": 1500,
                "period": "daily",
                "recorded_at": datetime.utcnow().isoformat()
            }
            
            payload = {
                "platform": "twitter",
                "metric_type": "followers",
                "value": 1500,
                "period": "daily"
            }
            
            response = client.post("/api/v1/audience/record", json=payload)
            
            assert response.status_code == 201
            data = response.json()
            assert data["platform"] == "twitter"
            assert data["value"] == 1500
    
    def test_receive_webhook_endpoint(self, client):
        """Test the POST /api/v1/audience/webhook/{platform} endpoint."""
        with patch("app.routers.audience.audience_service") as mock_service:
            
            mock_service.record_metric.return_value = {
                "id": str(uuid4()),
                "platform": "twitter",
                "metric_type": "followers",
                "value": 1500
            }
            
            payload = {
                "platform": "twitter",
                "metric_type": "followers",
                "value": 1500,
                "metadata": {"user_id": str(uuid4())}
            }
            
            response = client.post("/api/v1/audience/webhook/twitter", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_receive_webhook_invalid_platform(self, client):
        """Test webhook with invalid platform."""
        payload = {
            "platform": "invalid_platform",
            "metric_type": "followers",
            "value": 1500,
            "metadata": {"user_id": str(uuid4())}
        }
        
        response = client.post("/api/v1/audience/webhook/invalidplatform", json=payload)
        
        assert response.status_code == 400
    
    def test_get_insights_endpoint(self, client, mock_user):
        """Test the GET /api/v1/audience/insights endpoint."""
        with patch("app.routers.audience.get_auth_user", return_value=mock_user), \
             patch("app.routers.audience.audience_service") as mock_service:
            
            mock_service.generate_insights.return_value = {
                "summary": {"total_followers": 1500, "growth_rate_30d": 10.0},
                "trends": {"trend": "growing", "direction": "up"},
                "comparisons": {"improved": True, "change_percent": 5.0},
                "predictions": {"projected_30d": 100},
                "platforms": [],
                "ai_insights": {"summary": "Test summary"},
                "recommendations": ["Post more content"]
            }
            
            response = client.get("/api/v1/audience/insights")
            
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert "recommendations" in data
    
    def test_generate_snapshot_endpoint(self, client, mock_user):
        """Test the POST /api/v1/audience/snapshot endpoint."""
        with patch("app.routers.audience.get_auth_user", return_value=mock_user), \
             patch("app.routers.audience.audience_service") as mock_service:
            
            mock_service.calculate_growth_snapshot.return_value = {
                "id": str(uuid4()),
                "total_followers": 1500
            }
            
            response = client.post("/api/v1/audience/snapshot")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_delete_metric_endpoint(self, client, mock_user):
        """Test the DELETE /api/v1/audience/metrics/{metric_id} endpoint."""
        with patch("app.routers.audience.get_auth_user", return_value=mock_user), \
             patch("app.routers.audience.audience_service") as mock_service:
            
            mock_supabase = MagicMock()
            mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = Mock(data=[{"id": str(uuid4())}])
            mock_service.supabase = mock_supabase
            
            metric_id = str(uuid4())
            response = client.delete(f"/api/v1/audience/metrics/{metric_id}")
            
            assert response.status_code == 204


# Test Celery Tasks

class TestAudienceTasks:
    """Tests for audience Celery tasks."""
    
    def test_calculate_growth_metrics_task(self):
        """Test the calculate_growth_metrics Celery task."""
        with patch("app.tasks.audience.get_supabase_admin_client") as mock_get_client, \
             patch("app.tasks.audience.audience_service") as mock_service:
            
            # Mock Supabase response
            mock_client = MagicMock()
            mock_client.table.return_value.select.return_value.gte.return_value.execute.return_value = Mock(
                data=[{"user_id": "user-1"}, {"user_id": "user-1"}, {"user_id": "user-2"}]
            )
            mock_get_client.return_value = mock_client
            
            mock_service.calculate_growth_snapshot.return_value = {"id": "snapshot-1"}
            
            # Import and run task
            from app.tasks.audience import calculate_growth_metrics
            result = calculate_growth_metrics()
            
            assert result["success"] is True
            assert result["processed"] == 2  # 2 unique users
    
    def test_calculate_user_growth_metrics_task(self):
        """Test the calculate_user_growth_metrics Celery task."""
        with patch("app.tasks.audience.audience_service") as mock_service:
            mock_service.calculate_growth_snapshot.return_value = {"id": "snapshot-1"}
            
            from app.tasks.audience import calculate_user_growth_metrics
            result = calculate_user_growth_metrics("user-1")
            
            assert result["success"] is True
            assert result["user_id"] == "user-1"
    
    def test_process_platform_webhook_task(self):
        """Test the process_platform_webhook Celery task."""
        with patch("app.tasks.audience.audience_service") as mock_service:
            mock_service.record_metric.return_value = {"id": "metric-1"}
            
            from app.tasks.audience import process_platform_webhook
            payload = {
                "user_id": "user-1",
                "metric_type": "followers",
                "value": 1000
            }
            result = process_platform_webhook("twitter", payload)
            
            assert result["success"] is True
            assert result["platform"] == "twitter"
    
    def test_cleanup_old_audience_metrics_task(self):
        """Test the cleanup_old_audience_metrics Celery task."""
        with patch("app.tasks.audience.get_supabase_admin_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.table.return_value.delete.return_value.lt.return_value.execute.return_value = Mock(
                data=[{"id": "old-1"}, {"id": "old-2"}]
            )
            mock_get_client.return_value = mock_client
            
            from app.tasks.audience import cleanup_old_audience_metrics
            result = cleanup_old_audience_metrics(days=365)
            
            assert result["success"] is True
            assert result["deleted_metrics"] == 2


# Test Models

class TestAudienceModels:
    """Tests for Pydantic models."""
    
    def test_audience_metric_create(self):
        """Test AudienceMetricCreate model validation."""
        from app.routers.audience import AudienceMetricCreate
        
        metric = AudienceMetricCreate(
            platform="twitter",
            metric_type="followers",
            value=1000
        )
        
        assert metric.platform == "twitter"
        assert metric.metric_type == "followers"
        assert metric.value == 1000
        assert metric.period == "daily"
    
    def test_audience_metric_create_validation(self):
        """Test AudienceMetricCreate value validation."""
        from app.routers.audience import AudienceMetricCreate
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            AudienceMetricCreate(
                platform="twitter",
                metric_type="followers",
                value=-1  # Negative value should fail
            )
    
    def test_webhook_payload(self):
        """Test WebhookPayload model."""
        from app.routers.audience import WebhookPayload
        
        payload = WebhookPayload(
            platform="twitter",
            metric_type="followers",
            value=1000,
            metadata={"user_id": "user-1"}
        )
        
        assert payload.platform == "twitter"
        assert payload.metadata["user_id"] == "user-1"


# Database Integration Tests (marked as integration)

@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    def test_migration_applies(self):
        """Test that the migration file is valid SQL."""
        import os
        
        migration_path = os.path.join(
            os.path.dirname(__file__),
            "..", "migrations", "015_audience_metrics.sql"
        )
        
        assert os.path.exists(migration_path)
        
        with open(migration_path, 'r') as f:
            content = f.read()
            
        # Check for required tables
        assert "CREATE TABLE IF NOT EXISTS audience_metrics" in content
        assert "CREATE TABLE IF NOT EXISTS growth_snapshots" in content
        
        # Check for required columns
        assert "user_id uuid" in content
        assert "platform varchar(50)" in content
        assert "metric_type varchar(50)" in content
        assert "value int" in content
        
        # Check for indexes
        assert "CREATE INDEX" in content
        
        # Check for RLS
        assert "ENABLE ROW LEVEL SECURITY" in content

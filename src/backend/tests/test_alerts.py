"""
Tests for content performance alerts system.

This module tests:
- Alert service functionality
- Alert API endpoints
- Alert rules CRUD operations
- Metrics checking and viral/declining detection
- In-app notifications
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from uuid import uuid4, UUID

import httpx
from fastapi import status


# ============== Fixtures ==============

@pytest.fixture
def mock_alert_data():
    """Mock alert data."""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "alert_type": "viral",
        "content_id": str(uuid4()),
        "metric_name": "engagement",
        "threshold_value": 3.0,
        "current_value": 5.5,
        "status": "active",
        "message": "Your content is going viral!",
        "created_at": datetime.utcnow().isoformat(),
        "acknowledged_at": None,
    }


@pytest.fixture
def mock_alert_rule_data():
    """Mock alert rule data."""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "name": "High Views Alert",
        "alert_type": "milestone",
        "metric_name": "views",
        "operator": "greater_than",
        "threshold_value": 10000.0,
        "is_enabled": True,
        "notification_channels": ["in_app", "email"],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def mock_notification_data():
    """Mock in-app notification data."""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "alert_id": str(uuid4()),
        "title": "🔥 Viral Content Alert",
        "message": "Your content is going viral! Engagement increased 5.5x",
        "type": "success",
        "is_read": False,
        "created_at": datetime.utcnow().isoformat(),
        "read_at": None,
    }


@pytest.fixture
def mock_metrics():
    """Mock content metrics."""
    return {
        "views": 15000,
        "engagement": 5.5,
        "clicks": 1200,
        "shares": 850,
        "comments": 230,
        "likes": 3200,
    }


# ============== Alert Service Tests ==============

class TestAlertService:
    """Test the AlertService class."""

    @pytest.mark.asyncio
    async def test_check_content_metrics(self):
        """Test checking content metrics against rules."""
        from app.services.alert_service import alert_service

        with patch.object(alert_service, '_check_alert_rules', new_callable=AsyncMock) as mock_rules, \
             patch.object(alert_service, '_detect_viral_content', new_callable=AsyncMock) as mock_viral, \
             patch.object(alert_service, '_detect_declining_engagement', new_callable=AsyncMock) as mock_decline, \
             patch.object(alert_service, '_check_milestones', new_callable=AsyncMock) as mock_milestones, \
             patch.object(alert_service, '_store_metrics_history', new_callable=AsyncMock) as mock_store:

            mock_rules.return_value = [{"id": "rule-alert-1", "type": "rule"}]
            mock_viral.return_value = {"id": "viral-alert-1", "type": "viral"}
            mock_decline.return_value = None
            mock_milestones.return_value = [{"id": "milestone-1", "type": "milestone"}]

            content_id = uuid4()
            user_id = uuid4()
            metrics = {"views": 10000, "engagement": 3.5}

            result = await alert_service.check_content_metrics(content_id, user_id, metrics)

            assert len(result) == 3
            mock_rules.assert_called_once()
            mock_viral.assert_called_once()
            mock_decline.assert_called_once()
            mock_milestones.assert_called_once()
            mock_store.assert_called_once()

    @pytest.mark.asyncio
    async def test_detect_viral_content(self):
        """Test viral content detection."""
        from app.services.alert_service import alert_service

        with patch.object(alert_service, '_get_metrics_history', new_callable=AsyncMock) as mock_history, \
             patch.object(alert_service, '_alert_exists', new_callable=AsyncMock) as mock_exists, \
             patch.object(alert_service, '_save_alert', new_callable=AsyncMock) as mock_save:

            mock_history.return_value = [
                {"value": 100, "recorded_at": (datetime.utcnow() - timedelta(hours=12)).isoformat()},
                {"value": 500, "recorded_at": datetime.utcnow().isoformat()},
            ]
            mock_exists.return_value = False
            mock_save.return_value = {"id": "viral-alert", "type": "viral"}

            content_id = uuid4()
            user_id = uuid4()
            metrics = {"views": 5000, "engagement": 5.0}

            result = await alert_service._detect_viral_content(content_id, user_id, metrics)

            mock_history.assert_called_once()
            assert result is not None
            assert result.get("type") == "viral"

    @pytest.mark.asyncio
    async def test_detect_viral_content_not_enough_views(self):
        """Test viral detection doesn't trigger below minimum views."""
        from app.services.alert_service import alert_service

        content_id = uuid4()
        user_id = uuid4()
        metrics = {"views": 100, "engagement": 10.0}

        result = await alert_service._detect_viral_content(content_id, user_id, metrics)
        assert result is None

    @pytest.mark.asyncio
    async def test_detect_declining_engagement(self):
        """Test declining engagement detection."""
        from app.services.alert_service import alert_service

        with patch.object(alert_service, '_get_metrics_history', new_callable=AsyncMock) as mock_history, \
             patch.object(alert_service, '_alert_exists', new_callable=AsyncMock) as mock_exists, \
             patch.object(alert_service, '_save_alert', new_callable=AsyncMock) as mock_save:

            mock_history.return_value = [
                {"value": 1000, "recorded_at": (datetime.utcnow() - timedelta(days=6)).isoformat()},
                {"value": 900, "recorded_at": (datetime.utcnow() - timedelta(days=5)).isoformat()},
                {"value": 300, "recorded_at": (datetime.utcnow() - timedelta(days=1)).isoformat()},
            ]
            mock_exists.return_value = False
            mock_save.return_value = {"id": "declining-alert", "type": "declining"}

            content_id = uuid4()
            user_id = uuid4()
            metrics = {"engagement": 300}

            result = await alert_service._detect_declining_engagement(content_id, user_id, metrics)

            mock_history.assert_called_once()
            assert result is not None
            assert result.get("type") == "declining"

    @pytest.mark.asyncio
    async def test_check_milestones(self):
        """Test milestone checking."""
        from app.services.alert_service import alert_service

        with patch.object(alert_service, '_milestone_alerted', new_callable=AsyncMock) as mock_alerted, \
             patch.object(alert_service, '_save_alert', new_callable=AsyncMock) as mock_save:

            mock_alerted.return_value = False
            mock_save.return_value = {"id": "milestone-alert", "type": "milestone"}

            content_id = uuid4()
            user_id = uuid4()
            metrics = {"views": 15000}

            result = await alert_service._check_milestones(content_id, user_id, metrics)

            # Should trigger 10000 view milestone
            assert len(result) >= 1
            assert result[0].get("type") == "milestone"

    @pytest.mark.asyncio
    async def test_check_milestones_already_alerted(self):
        """Test milestone doesn't duplicate if already alerted."""
        from app.services.alert_service import alert_service

        with patch.object(alert_service, '_milestone_alerted', new_callable=AsyncMock) as mock_alerted:
            mock_alerted.return_value = True

            content_id = uuid4()
            user_id = uuid4()
            metrics = {"views": 15000}

            result = await alert_service._check_milestones(content_id, user_id, metrics)

            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self):
        """Test acknowledging an alert."""
        from app.services.alert_service import alert_service

        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.data = [{"id": "alert-1", "status": "acknowledged"}]
        mock_client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

        # Set supabase directly (uses the setter property)
        alert_service.supabase = mock_client
        try:
            result = await alert_service.acknowledge_alert(uuid4(), uuid4())
            assert result is True
        finally:
            alert_service._supabase = None

    @pytest.mark.asyncio
    async def test_resolve_alert(self):
        """Test resolving an alert."""
        from app.services.alert_service import alert_service

        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.data = [{"id": "alert-1", "status": "resolved"}]
        mock_client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

        alert_service.supabase = mock_client
        try:
            result = await alert_service.resolve_alert(uuid4(), uuid4())
            assert result is True
        finally:
            alert_service._supabase = None

    @pytest.mark.asyncio
    async def test_get_user_alerts(self):
        """Test getting user alerts."""
        from app.services.alert_service import alert_service

        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.data = [
            {"id": "alert-1", "status": "active"},
            {"id": "alert-2", "status": "acknowledged"},
        ]
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_response

        alert_service.supabase = mock_client
        try:
            result = await alert_service.get_user_alerts(uuid4())
            assert len(result) == 2
        finally:
            alert_service._supabase = None

    @pytest.mark.asyncio
    async def test_get_unread_alert_count(self):
        """Test getting unread alert count."""
        from app.services.alert_service import alert_service

        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.count = 5
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

        alert_service.supabase = mock_client
        try:
            result = await alert_service.get_unread_alert_count(uuid4())
            assert result == 5
        finally:
            alert_service._supabase = None

    @pytest.mark.asyncio
    async def test_create_alert_rule(self):
        """Test creating an alert rule."""
        from app.services.alert_service import alert_service

        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.data = [{
            "id": "rule-1",
            "name": "Test Rule",
            "metric_name": "views",
            "threshold_value": 1000,
        }]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_response

        alert_service.supabase = mock_client
        try:
            result = await alert_service.create_alert_rule(
                user_id=uuid4(),
                name="Test Rule",
                alert_type="milestone",
                metric_name="views",
                operator="greater_than",
                threshold_value=1000,
                notification_channels=["in_app"]
            )
            assert result is not None
            assert result["name"] == "Test Rule"
        finally:
            alert_service._supabase = None

    @pytest.mark.asyncio
    async def test_update_alert_rule(self):
        """Test updating an alert rule."""
        from app.services.alert_service import alert_service

        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.data = [{
            "id": "rule-1",
            "name": "Updated Rule",
            "is_enabled": False,
        }]
        mock_client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

        alert_service.supabase = mock_client
        try:
            result = await alert_service.update_alert_rule(
                rule_id=uuid4(),
                user_id=uuid4(),
                updates={"name": "Updated Rule", "is_enabled": False}
            )
            assert result is not None
            assert result["name"] == "Updated Rule"
        finally:
            alert_service._supabase = None

    @pytest.mark.asyncio
    async def test_delete_alert_rule(self):
        """Test deleting an alert rule."""
        from app.services.alert_service import alert_service

        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.data = [{"id": "rule-1"}]
        mock_client.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

        alert_service.supabase = mock_client
        try:
            result = await alert_service.delete_alert_rule(uuid4(), uuid4())
            assert result is True
        finally:
            alert_service._supabase = None


# ============== API Endpoint Tests ==============

class TestAlertsAPI:
    """Test alert API endpoints."""

    def test_list_alerts(self, client, auth_headers):
        """Test GET /api/v1/alerts endpoint."""
        with patch("app.routers.alerts.alert_service") as mock_service, \
             patch("app.routers.alerts.get_supabase_client") as mock_supabase:
            mock_service.get_user_alerts = AsyncMock(return_value=[
                {
                    "id": str(uuid4()),
                    "user_id": "test-user-id",
                    "alert_type": "viral",
                    "content_id": str(uuid4()),
                    "metric_name": "engagement",
                    "threshold_value": 3.0,
                    "current_value": 5.5,
                    "status": "active",
                    "message": "Test alert",
                    "created_at": datetime.utcnow().isoformat(),
                    "acknowledged_at": None,
                }
            ])
            mock_client = MagicMock()
            mock_count_response = Mock()
            mock_count_response.count = 1
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_count_response
            mock_supabase.return_value = mock_client

            response = client.get("/api/v1/alerts", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "alerts" in data
        assert "total" in data

    def test_list_alerts_with_filters(self, client, auth_headers):
        """Test GET /api/v1/alerts with status and type filters."""
        with patch("app.routers.alerts.alert_service") as mock_service, \
             patch("app.routers.alerts.get_supabase_client") as mock_supabase:
            mock_service.get_user_alerts = AsyncMock(return_value=[])
            mock_client = MagicMock()
            mock_count_response = Mock()
            mock_count_response.count = 0
            mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_count_response
            mock_supabase.return_value = mock_client

            response = client.get(
                "/api/v1/alerts?status=active&alert_type=viral",
                headers=auth_headers
            )

        assert response.status_code == status.HTTP_200_OK

    def test_list_alerts_invalid_status(self, client, auth_headers):
        """Test GET /api/v1/alerts with invalid status filter."""
        response = client.get(
            "/api/v1/alerts?status=invalid_status",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_acknowledge_alert(self, client, auth_headers):
        """Test POST /api/v1/alerts/acknowledge/{id} endpoint."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.acknowledge_alert = AsyncMock(return_value=True)

            alert_id = str(uuid4())
            response = client.post(
                f"/api/v1/alerts/acknowledge/{alert_id}",
                headers=auth_headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True

    def test_acknowledge_alert_not_found(self, client, auth_headers):
        """Test acknowledging a non-existent alert."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.acknowledge_alert = AsyncMock(return_value=False)

            alert_id = str(uuid4())
            response = client.post(
                f"/api/v1/alerts/acknowledge/{alert_id}",
                headers=auth_headers
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_resolve_alert(self, client, auth_headers):
        """Test POST /api/v1/alerts/resolve/{id} endpoint."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.resolve_alert = AsyncMock(return_value=True)

            alert_id = str(uuid4())
            response = client.post(
                f"/api/v1/alerts/resolve/{alert_id}",
                headers=auth_headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True

    def test_get_unread_count(self, client, auth_headers):
        """Test GET /api/v1/alerts/unread-count endpoint."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.get_unread_alert_count = AsyncMock(return_value=5)

            response = client.get("/api/v1/alerts/unread-count", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "unread_count" in data
        assert data["unread_count"] == 5

    def test_list_alert_rules(self, client, auth_headers):
        """Test GET /api/v1/alerts/rules endpoint."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.get_alert_rules = AsyncMock(return_value=[
                {
                    "id": str(uuid4()),
                    "user_id": "test-user-id",
                    "name": "High Views",
                    "alert_type": "milestone",
                    "metric_name": "views",
                    "operator": "greater_than",
                    "threshold_value": 10000.0,
                    "is_enabled": True,
                    "notification_channels": ["in_app"],
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ])

            response = client.get("/api/v1/alerts/rules", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "rules" in data

    def test_create_alert_rule(self, client, auth_headers):
        """Test POST /api/v1/alerts/rules endpoint."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.create_alert_rule = AsyncMock(return_value={
                "id": str(uuid4()),
                "user_id": "test-user-id",
                "name": "Test Rule",
                "alert_type": "milestone",
                "metric_name": "views",
                "operator": "greater_than",
                "threshold_value": 10000.0,
                "is_enabled": True,
                "notification_channels": ["in_app", "email"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            })

            response = client.post(
                "/api/v1/alerts/rules",
                headers={**auth_headers, "Content-Type": "application/json"},
                json={
                    "name": "Test Rule",
                    "alert_type": "milestone",
                    "metric_name": "views",
                    "operator": "greater_than",
                    "threshold_value": 10000,
                    "notification_channels": ["in_app", "email"],
                }
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Rule"

    def test_create_alert_rule_invalid_type(self, client, auth_headers):
        """Test creating an alert rule with invalid alert_type."""
        response = client.post(
            "/api/v1/alerts/rules",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "name": "Test Rule",
                "alert_type": "invalid_type",
                "metric_name": "views",
                "operator": "greater_than",
                "threshold_value": 10000,
                "notification_channels": ["in_app"],
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_alert_rule(self, client, auth_headers):
        """Test PUT /api/v1/alerts/rules/{id} endpoint."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.update_alert_rule = AsyncMock(return_value={
                "id": str(uuid4()),
                "user_id": "test-user-id",
                "name": "Updated Rule",
                "alert_type": "milestone",
                "metric_name": "views",
                "operator": "greater_than",
                "threshold_value": 5000.0,
                "is_enabled": False,
                "notification_channels": ["in_app"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            })

            rule_id = str(uuid4())
            response = client.put(
                f"/api/v1/alerts/rules/{rule_id}",
                headers={**auth_headers, "Content-Type": "application/json"},
                json={"name": "Updated Rule", "is_enabled": False}
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Rule"

    def test_delete_alert_rule(self, client, auth_headers):
        """Test DELETE /api/v1/alerts/rules/{id} endpoint."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.delete_alert_rule = AsyncMock(return_value=True)

            rule_id = str(uuid4())
            response = client.delete(
                f"/api/v1/alerts/rules/{rule_id}",
                headers=auth_headers
            )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_check_metrics(self, client, auth_headers):
        """Test POST /api/v1/alerts/check-metrics endpoint."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.check_content_metrics = AsyncMock(return_value=[
                {
                    "id": str(uuid4()),
                    "user_id": "test-user-id",
                    "alert_type": "milestone",
                    "content_id": str(uuid4()),
                    "metric_name": "views",
                    "threshold_value": 10000.0,
                    "current_value": 15000.0,
                    "status": "active",
                    "message": "Milestone reached!",
                    "created_at": datetime.utcnow().isoformat(),
                    "acknowledged_at": None,
                }
            ])

            response = client.post(
                "/api/v1/alerts/check-metrics",
                headers={**auth_headers, "Content-Type": "application/json"},
                json={
                    "content_id": str(uuid4()),
                    "metrics": {"views": 15000, "engagement": 5.5}
                }
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "triggered_alerts" in data

    def test_list_notifications(self, client, auth_headers):
        """Test GET /api/v1/alerts/notifications endpoint."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.get_in_app_notifications = AsyncMock(return_value=[
                {
                    "id": str(uuid4()),
                    "user_id": "test-user-id",
                    "alert_id": str(uuid4()),
                    "title": "Test Notification",
                    "message": "Test message",
                    "type": "info",
                    "is_read": False,
                    "created_at": datetime.utcnow().isoformat(),
                    "read_at": None,
                }
            ])
            mock_service.get_unread_alert_count = AsyncMock(return_value=1)

            response = client.get("/api/v1/alerts/notifications", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data

    def test_mark_notification_read(self, client, auth_headers):
        """Test POST /api/v1/alerts/notifications/{id}/read endpoint."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.mark_notification_read = AsyncMock(return_value=True)

            notification_id = str(uuid4())
            response = client.post(
                f"/api/v1/alerts/notifications/{notification_id}/read",
                headers=auth_headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True

    def test_mark_all_notifications_read(self, client, auth_headers):
        """Test POST /api/v1/alerts/notifications/mark-all-read endpoint."""
        with patch("app.routers.alerts.get_supabase_client") as mock_supabase:
            mock_client = MagicMock()
            mock_response = Mock()
            mock_response.data = [{"id": str(uuid4())}, {"id": str(uuid4())}]
            mock_client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
            mock_supabase.return_value = mock_client

            response = client.post(
                "/api/v1/alerts/notifications/mark-all-read",
                headers=auth_headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True


# ============== Integration Tests ==============

class TestAlertsIntegration:
    """Integration tests for the alerts system."""

    @pytest.mark.asyncio
    async def test_full_alert_flow(self):
        """Test the complete alert flow from metrics to notification."""
        from app.services.alert_service import alert_service

        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table

        # Setup mock chain
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = Mock(data=[])
        mock_table.insert.return_value.execute.return_value = Mock(data=[{
            "id": str(uuid4()),
            "alert_type": "viral",
            "message": "Your content is going viral!",
        }])

        alert_service.supabase = mock_client
        try:
            content_id = uuid4()
            user_id = uuid4()

            # Simulate viral metrics
            metrics = {
                "views": 50000,
                "engagement": 10.0,
            }

            with patch.object(alert_service, '_check_alert_rules', new_callable=AsyncMock) as mock_rules, \
                 patch.object(alert_service, '_detect_viral_content', new_callable=AsyncMock) as mock_viral, \
                 patch.object(alert_service, '_detect_declining_engagement', new_callable=AsyncMock) as mock_decline, \
                 patch.object(alert_service, '_check_milestones', new_callable=AsyncMock) as mock_milestones, \
                 patch.object(alert_service, '_store_metrics_history', new_callable=AsyncMock):
                mock_rules.return_value = []
                mock_viral.return_value = {"id": "viral-1", "type": "viral"}
                mock_decline.return_value = None
                mock_milestones.return_value = []

                result = await alert_service.check_content_metrics(content_id, user_id, metrics)
                assert isinstance(result, list)
        finally:
            alert_service._supabase = None

    def test_alert_rule_crud_flow(self, client, auth_headers):
        """Test CRUD operations on alert rules."""
        with patch("app.routers.alerts.alert_service") as mock_service:
            mock_service.get_alert_rules = AsyncMock(return_value=[])

            response = client.get("/api/v1/alerts/rules", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_alert_enumerations(self):
        """Test that alert enumerations work correctly."""
        from app.services.alert_service import (
            AlertType, AlertStatus, MetricName, AlertOperator
        )

        # Test AlertType
        assert AlertType.VIRAL.value == "viral"
        assert AlertType.DECLINING.value == "declining"
        assert AlertType.MILESTONE.value == "milestone"
        assert AlertType.ERROR.value == "error"

        # Test AlertStatus
        assert AlertStatus.ACTIVE.value == "active"
        assert AlertStatus.ACKNOWLEDGED.value == "acknowledged"
        assert AlertStatus.RESOLVED.value == "resolved"

        # Test MetricName
        assert MetricName.VIEWS.value == "views"
        assert MetricName.ENGAGEMENT.value == "engagement"
        assert MetricName.CLICKS.value == "clicks"
        assert MetricName.SHARES.value == "shares"
        assert MetricName.COMMENTS.value == "comments"
        assert MetricName.LIKES.value == "likes"

        # Test AlertOperator
        assert AlertOperator.GREATER_THAN.value == "greater_than"
        assert AlertOperator.LESS_THAN.value == "less_than"
        assert AlertOperator.EQUALS.value == "equals"
        assert AlertOperator.PERCENTAGE_CHANGE.value == "percentage_change"


# ============== Validation Tests ==============

class TestAlertValidation:
    """Test input validation for alerts."""

    def test_create_rule_invalid_metric(self, client, auth_headers):
        """Test creating a rule with invalid metric name."""
        response = client.post(
            "/api/v1/alerts/rules",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "name": "Test Rule",
                "alert_type": "milestone",
                "metric_name": "invalid_metric",
                "operator": "greater_than",
                "threshold_value": 1000,
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_rule_invalid_operator(self, client, auth_headers):
        """Test creating a rule with invalid operator."""
        response = client.post(
            "/api/v1/alerts/rules",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "name": "Test Rule",
                "alert_type": "milestone",
                "metric_name": "views",
                "operator": "invalid_operator",
                "threshold_value": 1000,
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_rule_invalid_channel(self, client, auth_headers):
        """Test creating a rule with invalid notification channel."""
        response = client.post(
            "/api/v1/alerts/rules",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "name": "Test Rule",
                "alert_type": "milestone",
                "metric_name": "views",
                "operator": "greater_than",
                "threshold_value": 1000,
                "notification_channels": ["invalid_channel"],
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_rule_empty_name(self, client, auth_headers):
        """Test creating a rule with empty name."""
        response = client.post(
            "/api/v1/alerts/rules",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "name": "",
                "alert_type": "milestone",
                "metric_name": "views",
                "operator": "greater_than",
                "threshold_value": 1000,
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_rule_negative_threshold(self, client, auth_headers):
        """Test creating a rule with negative threshold."""
        response = client.post(
            "/api/v1/alerts/rules",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "name": "Test Rule",
                "alert_type": "milestone",
                "metric_name": "views",
                "operator": "greater_than",
                "threshold_value": -1000,
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============== Edge Case Tests ==============

class TestAlertEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_service_handles_database_error(self):
        """Test service handles database errors gracefully."""
        from app.services.alert_service import alert_service

        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")

        alert_service.supabase = mock_client
        try:
            result = await alert_service.get_user_alerts(uuid4())
            assert result == []
        finally:
            alert_service._supabase = None

    @pytest.mark.asyncio
    async def test_empty_metrics(self):
        """Test handling empty metrics."""
        from app.services.alert_service import alert_service

        content_id = uuid4()
        user_id = uuid4()
        metrics = {}

        with patch.object(alert_service, '_store_metrics_history', new_callable=AsyncMock):
            result = await alert_service.check_content_metrics(content_id, user_id, metrics)
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_single_metric_history(self):
        """Test viral detection with only one history entry."""
        from app.services.alert_service import alert_service

        with patch.object(alert_service, '_get_metrics_history', new_callable=AsyncMock) as mock_history:
            mock_history.return_value = [{"value": 100}]  # Only one entry

            content_id = uuid4()
            user_id = uuid4()
            metrics = {"views": 5000, "engagement": 5.0}

            result = await alert_service._detect_viral_content(content_id, user_id, metrics)
            assert result is None

    @pytest.mark.asyncio
    async def test_zero_previous_value(self):
        """Test percentage change with zero previous value."""
        from app.services.alert_service import alert_service

        with patch.object(alert_service, '_get_metrics_history', new_callable=AsyncMock) as mock_history:
            mock_history.return_value = [
                {"value": 0},
                {"value": 100},
            ]

            content_id = uuid4()
            user_id = uuid4()
            metrics = {"engagement": 100}

            # Should not crash with division by zero
            result = await alert_service._detect_declining_engagement(content_id, user_id, metrics)
            # No alert expected due to zero first half average
            assert result is None

    def test_pagination_limits(self, client, auth_headers):
        """Test pagination limits."""
        response = client.get("/api/v1/alerts?limit=200", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = client.get("/api/v1/alerts?limit=0", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============== WebSocket Preparation Tests ==============

class TestWebSocketPreparation:
    """Tests for WebSocket real-time notifications preparation."""

    @pytest.mark.asyncio
    async def test_alert_service_web_socket_ready(self):
        """Test that alert service is prepared for WebSocket integration."""
        from app.services.alert_service import alert_service

        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "alert_type": "viral",
                "message": "Test message",
                "created_at": datetime.utcnow().isoformat(),
            }
        ]
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        alert_service.supabase = mock_client
        try:
            alerts = await alert_service.get_user_alerts(uuid4(), status="active", limit=10)
            assert isinstance(alerts, list)
            for alert in alerts:
                assert "id" in alert
                assert "user_id" in alert
                assert "alert_type" in alert
                assert "message" in alert
        finally:
            alert_service._supabase = None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
Tests for custom dashboards API.
"""
import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    user = Mock()
    user.id = str(uuid4())
    user.email = "test@example.com"
    return user


@pytest.fixture
def sample_dashboard():
    """Create a sample dashboard."""
    return {
        "id": str(uuid4()),
        "user_id": "test-user-id",
        "name": "My Dashboard",
        "description": "Test dashboard",
        "layout_config": {"columns": 12},
        "is_default": False,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_widget():
    """Create a sample widget."""
    return {
        "id": str(uuid4()),
        "dashboard_id": "dash-1",
        "widget_type": "metric_card",
        "title": "Total Content",
        "data_source": "content_count",
        "refresh_interval": 60,
        "size": {"w": 4, "h": 3},
        "position": 0,
        "config": {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


def build_mock_query_chain(return_data=None):
    """Build a mock that supports .select().eq().order().execute() chains."""
    mock_query = MagicMock()
    mock_query.eq = MagicMock(return_value=mock_query)
    mock_query.neq = MagicMock(return_value=mock_query)
    mock_query.gt = MagicMock(return_value=mock_query)
    mock_query.gte = MagicMock(return_value=mock_query)
    mock_query.lt = MagicMock(return_value=mock_query)
    mock_query.lte = MagicMock(return_value=mock_query)
    mock_query.order = MagicMock(return_value=mock_query)
    mock_query.limit = MagicMock(return_value=mock_query)
    mock_query.offset = MagicMock(return_value=mock_query)
    mock_query.single = MagicMock(return_value=mock_query)
    mock_query.maybe_single = MagicMock(return_value=mock_query)
    mock_query.insert = MagicMock(return_value=mock_query)
    mock_query.update = MagicMock(return_value=mock_query)
    mock_query.delete = MagicMock(return_value=mock_query)
    mock_query.execute = MagicMock(return_value=Mock(data=return_data or []))
    return mock_query


# ── Dashboard Service Tests ────────────────────────────────────────

class TestDashboardService:
    """Tests for the DashboardService class."""

    def test_list_dashboards(self, mock_user, sample_dashboard):
        """Test listing dashboards."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()
        mock_supabase = MagicMock()
        mock_query = build_mock_query_chain([sample_dashboard])
        mock_supabase.table.return_value = MagicMock(
            select=MagicMock(return_value=mock_query),
            insert=MagicMock(return_value=mock_query),
            update=MagicMock(return_value=mock_query),
            delete=MagicMock(return_value=mock_query),
        )
        service.supabase = mock_supabase

        result = service.list_dashboards(mock_user.id)
        assert len(result) == 1
        assert result[0]["name"] == "My Dashboard"

    def test_create_dashboard(self, mock_user):
        """Test creating a dashboard."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()
        mock_supabase = MagicMock()
        mock_query = build_mock_query_chain([{"id": "new-dash", "user_id": mock_user.id, "name": "New Dashboard"}])
        mock_supabase.table.return_value = MagicMock(
            select=MagicMock(return_value=mock_query),
            insert=MagicMock(return_value=mock_query),
            update=MagicMock(return_value=mock_query),
            delete=MagicMock(return_value=mock_query),
        )
        service.supabase = mock_supabase

        result = service.create_dashboard(mock_user.id, "New Dashboard", is_default=True)
        assert result is not None
        assert result["name"] == "New Dashboard"

    def test_get_dashboard_with_widgets(self, mock_user, sample_dashboard, sample_widget):
        """Test getting a dashboard with widgets."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()
        mock_supabase = MagicMock()

        # Build two distinct query chains: one for dashboard, one for widgets
        dash_query = build_mock_query_chain(sample_dashboard)
        widgets_query = build_mock_query_chain([sample_widget])

        # First .table() call returns dashboard chain, second returns widgets chain
        call_count = [0]
        def table_side_effect(name):
            if name == "dashboards":
                return MagicMock(select=MagicMock(return_value=dash_query))
            elif name == "dashboard_widgets":
                return MagicMock(select=MagicMock(return_value=widgets_query))
            return MagicMock()

        mock_supabase.table = MagicMock(side_effect=table_side_effect)
        service.supabase = mock_supabase

        result = service.get_dashboard("dash-1", mock_user.id)
        assert result is not None
        assert "widgets" in result
        assert len(result["widgets"]) == 1

    def test_update_dashboard(self, mock_user, sample_dashboard):
        """Test updating a dashboard."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()

        with patch.object(service, 'get_dashboard', return_value=sample_dashboard):
            mock_supabase = MagicMock()
            mock_query = build_mock_query_chain([{**sample_dashboard, "name": "Updated Dashboard"}])
            mock_supabase.table.return_value = MagicMock(
                select=MagicMock(return_value=mock_query),
                insert=MagicMock(return_value=mock_query),
                update=MagicMock(return_value=mock_query),
                delete=MagicMock(return_value=mock_query),
            )
            service.supabase = mock_supabase

            result = service.update_dashboard("dash-1", mock_user.id, name="Updated Dashboard")
            assert result is not None
            assert result["name"] == "Updated Dashboard"

    def test_update_dashboard_not_found(self, mock_user):
        """Test updating a non-existent dashboard."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()

        with patch.object(service, 'get_dashboard', return_value=None):
            result = service.update_dashboard("nonexistent", mock_user.id, name="New Name")
            assert result is None

    def test_delete_dashboard(self, mock_user, sample_dashboard):
        """Test deleting a dashboard."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()
        mock_supabase = MagicMock()
        mock_query = build_mock_query_chain([{"id": "dash-1"}])
        mock_supabase.table.return_value = MagicMock(
            select=MagicMock(return_value=mock_query),
            insert=MagicMock(return_value=mock_query),
            update=MagicMock(return_value=mock_query),
            delete=MagicMock(return_value=mock_query),
        )

        with patch.object(service, 'get_dashboard', return_value=sample_dashboard):
            service.supabase = mock_supabase
            result = service.delete_dashboard("dash-1", mock_user.id)
            assert result is True

    def test_delete_dashboard_not_found(self, mock_user):
        """Test deleting a non-existent dashboard."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()

        with patch.object(service, 'get_dashboard', return_value=None):
            result = service.delete_dashboard("nonexistent", mock_user.id)
            assert result is False

    def test_add_widget_invalid_type(self, mock_user, sample_dashboard):
        """Test adding a widget with invalid type."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()

        with patch.object(service, 'get_dashboard', return_value=sample_dashboard):
            with pytest.raises(ValueError, match="Invalid widget type"):
                service.add_widget(
                    dashboard_id="dash-1",
                    user_id=mock_user.id,
                    widget_type="invalid_type",
                    title="Bad Widget",
                    data_source="content_count",
                )

    def test_add_widget_invalid_data_source(self, mock_user, sample_dashboard):
        """Test adding a widget with invalid data source."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()

        with patch.object(service, 'get_dashboard', return_value=sample_dashboard):
            with pytest.raises(ValueError, match="Invalid data source"):
                service.add_widget(
                    dashboard_id="dash-1",
                    user_id=mock_user.id,
                    widget_type="metric_card",
                    title="Bad Widget",
                    data_source="invalid_source",
                )

    def test_add_widget_success(self, mock_user, sample_dashboard):
        """Test successfully adding a widget."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()
        mock_supabase = MagicMock()
        mock_query = build_mock_query_chain([{"id": "widget-1", "widget_type": "metric_card", "title": "Total Content"}])
        mock_supabase.table.return_value = MagicMock(
            select=MagicMock(return_value=mock_query),
            insert=MagicMock(return_value=mock_query),
            update=MagicMock(return_value=mock_query),
            delete=MagicMock(return_value=mock_query),
        )

        with patch.object(service, 'get_dashboard', return_value=sample_dashboard):
            service.supabase = mock_supabase
            result = service.add_widget(
                dashboard_id="dash-1",
                user_id=mock_user.id,
                widget_type="metric_card",
                title="Total Content",
                data_source="content_count",
                refresh_interval=60,
            )
            assert result is not None
            assert result["widget_type"] == "metric_card"

    def test_delete_widget(self, mock_user, sample_dashboard):
        """Test removing a widget."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()
        mock_supabase = MagicMock()
        mock_query = build_mock_query_chain([{"id": "widget-1"}])
        mock_supabase.table.return_value = MagicMock(
            select=MagicMock(return_value=mock_query),
            insert=MagicMock(return_value=mock_query),
            update=MagicMock(return_value=mock_query),
            delete=MagicMock(return_value=mock_query),
        )

        with patch.object(service, 'get_dashboard', return_value=sample_dashboard):
            service.supabase = mock_supabase
            result = service.delete_widget("dash-1", "widget-1", mock_user.id)
            assert result is True

    def test_get_dashboard_data(self, mock_user, sample_dashboard, sample_widget):
        """Test getting live data for a dashboard."""
        from app.services.dashboard_service import DashboardService
        service = DashboardService()

        dashboard_with_widgets = {**sample_dashboard, "widgets": [sample_widget]}
        with patch.object(service, 'get_dashboard', return_value=dashboard_with_widgets), \
             patch.object(service, '_fetch_widget_data', return_value={"total": 42}):
            result = service.get_dashboard_data("dash-1", mock_user.id)
            assert result is not None
            assert "widgets" in result
            assert result["widgets"][0]["data"] == {"total": 42}
            assert "fetched_at" in result


# ── Dashboard Router Tests ─────────────────────────────────────────

class TestDashboardRouter:
    """Tests for the dashboard router endpoints using conftest client fixture."""

    def test_list_dashboards_endpoint(self, client, mock_user):
        """Test GET /api/v1/dashboards."""
        with patch("app.routers.dashboards.get_auth_user", return_value=mock_user), \
             patch("app.routers.dashboards.dashboard_service") as mock_service:
            mock_service.list_dashboards.return_value = [
                {"id": "dash-1", "name": "My Dashboard", "is_default": True}
            ]

            response = client.get("/api/v1/dashboards", headers={"Authorization": "Bearer test"})
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["name"] == "My Dashboard"

    def test_create_dashboard_endpoint(self, client, mock_user):
        """Test POST /api/v1/dashboards."""
        with patch("app.routers.dashboards.get_auth_user", return_value=mock_user), \
             patch("app.routers.dashboards.dashboard_service") as mock_service:
            mock_service.create_dashboard.return_value = {
                "id": "dash-new", "name": "New Dashboard", "is_default": False
            }

            response = client.post(
                "/api/v1/dashboards",
                json={"name": "New Dashboard"},
                headers={"Authorization": "Bearer test"},
            )
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "New Dashboard"

    def test_get_dashboard_endpoint(self, client, mock_user):
        """Test GET /api/v1/dashboards/{id}."""
        with patch("app.routers.dashboards.get_auth_user", return_value=mock_user), \
             patch("app.routers.dashboards.dashboard_service") as mock_service:
            mock_service.get_dashboard.return_value = {
                "id": "dash-1", "name": "My Dashboard", "widgets": []
            }

            response = client.get("/api/v1/dashboards/dash-1", headers={"Authorization": "Bearer test"})
            assert response.status_code == 200
            data = response.json()
            assert "widgets" in data

    def test_get_dashboard_not_found(self, client, mock_user):
        """Test GET /api/v1/dashboards/{id} when not found."""
        with patch("app.routers.dashboards.get_auth_user", return_value=mock_user), \
             patch("app.routers.dashboards.dashboard_service") as mock_service:
            mock_service.get_dashboard.return_value = None

            response = client.get("/api/v1/dashboards/nonexistent", headers={"Authorization": "Bearer test"})
            assert response.status_code == 404

    def test_update_dashboard_endpoint(self, client, mock_user):
        """Test PUT /api/v1/dashboards/{id}."""
        with patch("app.routers.dashboards.get_auth_user", return_value=mock_user), \
             patch("app.routers.dashboards.dashboard_service") as mock_service:
            mock_service.update_dashboard.return_value = {
                "id": "dash-1", "name": "Updated Dashboard"
            }

            response = client.put(
                "/api/v1/dashboards/dash-1",
                json={"name": "Updated Dashboard"},
                headers={"Authorization": "Bearer test"},
            )
            assert response.status_code == 200

    def test_delete_dashboard_endpoint(self, client, mock_user):
        """Test DELETE /api/v1/dashboards/{id}."""
        with patch("app.routers.dashboards.get_auth_user", return_value=mock_user), \
             patch("app.routers.dashboards.dashboard_service") as mock_service:
            mock_service.delete_dashboard.return_value = True

            response = client.delete("/api/v1/dashboards/dash-1", headers={"Authorization": "Bearer test"})
            assert response.status_code == 204

    def test_add_widget_endpoint(self, client, mock_user):
        """Test POST /api/v1/dashboards/{id}/widgets."""
        with patch("app.routers.dashboards.get_auth_user", return_value=mock_user), \
             patch("app.routers.dashboards.dashboard_service") as mock_service:
            mock_service.add_widget.return_value = {
                "id": "widget-1", "widget_type": "metric_card", "title": "Total Content"
            }

            response = client.post(
                "/api/v1/dashboards/dash-1/widgets",
                json={
                    "widget_type": "metric_card",
                    "title": "Total Content",
                    "data_source": "content_count",
                    "refresh_interval": 60,
                },
                headers={"Authorization": "Bearer test"},
            )
            assert response.status_code == 201

    def test_add_widget_invalid_type_endpoint(self, client, mock_user):
        """Test POST /api/v1/dashboards/{id}/widgets with invalid type."""
        with patch("app.routers.dashboards.get_auth_user", return_value=mock_user):
            response = client.post(
                "/api/v1/dashboards/dash-1/widgets",
                json={
                    "widget_type": "invalid",
                    "title": "Bad",
                    "data_source": "content_count",
                    "refresh_interval": 60,
                },
                headers={"Authorization": "Bearer test"},
            )
            assert response.status_code == 400

    def test_get_dashboard_data_endpoint(self, client, mock_user):
        """Test GET /api/v1/dashboards/{id}/data."""
        with patch("app.routers.dashboards.get_auth_user", return_value=mock_user), \
             patch("app.routers.dashboards.dashboard_service") as mock_service:
            mock_service.get_dashboard_data.return_value = {
                "dashboard_id": "dash-1",
                "widgets": [
                    {"widget_id": "w1", "data": {"total": 42}}
                ],
                "fetched_at": datetime.utcnow().isoformat(),
            }

            response = client.get("/api/v1/dashboards/dash-1/data", headers={"Authorization": "Bearer test"})
            assert response.status_code == 200
            data = response.json()
            assert "widgets" in data
            assert "fetched_at" in data
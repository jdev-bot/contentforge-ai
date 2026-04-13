"""
Tests for Audit Logs service and router.
"""
import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock


# ── Fixtures ──

@pytest.fixture
def mock_user():
    user = Mock()
    user.id = str(uuid4())
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_supabase():
    with patch("app.services.audit_service.get_supabase_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def audit_svc(mock_supabase):
    from app.services.audit_service import AuditService
    svc = AuditService()
    svc.supabase = mock_supabase
    return svc


@pytest.fixture
def sample_audit_log():
    return {
        "id": str(uuid4()),
        "actor_id": str(uuid4()),
        "actor_email": "test@example.com",
        "action": "content.created",
        "resource_type": "content",
        "resource_id": str(uuid4()),
        "details": {"title": "Test Content"},
        "ip_address": "127.0.0.1",
        "user_agent": "TestAgent/1.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ── Service Tests ──

class TestAuditService:
    """Tests for the AuditService class."""

    def test_log_creates_entry(self, audit_svc, mock_supabase, mock_user):
        """Test creating an audit log entry."""
        log_id = str(uuid4())
        mock_response = Mock()
        mock_response.data = [{
            "id": log_id,
            "actor_id": str(mock_user.id),
            "actor_email": mock_user.email,
            "action": "content.created",
            "resource_type": "content",
            "resource_id": str(uuid4()),
            "details": {"title": "Test"},
            "ip_address": "127.0.0.1",
            "user_agent": "TestAgent/1.0",
            "timestamp": datetime.utcnow().isoformat(),
        }]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        result = audit_svc.log(
            actor_id=str(mock_user.id),
            actor_email=mock_user.email,
            action="content.created",
            resource_type="content",
            resource_id=str(uuid4()),
            details={"title": "Test"},
            ip_address="127.0.0.1",
            user_agent="TestAgent/1.0",
        )

        assert result is not None
        assert result["action"] == "content.created"
        assert result["actor_email"] == mock_user.email

    def test_log_with_minimal_fields(self, audit_svc, mock_supabase, mock_user):
        """Test creating an audit log with only required fields."""
        mock_response = Mock()
        mock_response.data = [{
            "id": str(uuid4()),
            "actor_id": str(mock_user.id),
            "actor_email": "",
            "action": "user.login",
            "resource_type": "session",
            "resource_id": str(uuid4()),
            "details": {},
            "ip_address": None,
            "user_agent": None,
            "timestamp": datetime.utcnow().isoformat(),
        }]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        result = audit_svc.log(
            actor_id=str(mock_user.id),
            actor_email="",
            action="user.login",
            resource_type="session",
            resource_id=str(uuid4()),
        )

        assert result is not None
        assert result["action"] == "user.login"

    def test_list_logs_with_filters(self, audit_svc, mock_supabase, mock_user):
        """Test listing audit logs with filtering."""
        mock_response = Mock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "actor_id": str(mock_user.id),
                "actor_email": mock_user.email,
                "action": "content.updated",
                "resource_type": "content",
                "resource_id": str(uuid4()),
                "details": {},
                "ip_address": None,
                "user_agent": None,
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]
        # Set up chained query
        chain = mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value
        chain.eq.return_value.range.return_value.execute.return_value = mock_response

        result = audit_svc.list_logs(
            user_id=str(mock_user.id),
            action="content.updated",
        )

        assert len(result) == 1
        assert result[0]["action"] == "content.updated"

    def test_list_logs_with_date_range(self, audit_svc, mock_supabase, mock_user):
        """Test listing audit logs with date range filtering."""
        mock_response = Mock()
        mock_response.data = []
        chain = mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value
        chain.gte.return_value.lte.return_value.range.return_value.execute.return_value = mock_response

        result = audit_svc.list_logs(
            user_id=str(mock_user.id),
            date_from="2024-01-01T00:00:00",
            date_to="2024-12-31T23:59:59",
        )

        assert result == []

    def test_get_log_found(self, audit_svc, mock_supabase, mock_user, sample_audit_log):
        """Test getting a specific audit log entry."""
        mock_response = Mock()
        mock_response.data = sample_audit_log
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        result = audit_svc.get_log(sample_audit_log["id"], str(mock_user.id))
        assert result is not None
        assert result["action"] == "content.created"

    def test_get_log_not_found(self, audit_svc, mock_supabase, mock_user):
        """Test getting a log that doesn't exist returns None."""
        mock_response = Mock()
        mock_response.data = None
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        result = audit_svc.get_log(str(uuid4()), str(mock_user.id))
        assert result is None

    def test_get_stats(self, audit_svc, mock_supabase, mock_user):
        """Test getting audit log statistics."""
        mock_response = Mock()
        mock_response.data = [
            {"action": "content.created"},
            {"action": "content.created"},
            {"action": "content.updated"},
            {"action": "user.login"},
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        result = audit_svc.get_stats(user_id=str(mock_user.id))

        assert result["total"] == 4
        assert result["action_counts"]["content.created"] == 2
        assert result["action_counts"]["content.updated"] == 1
        assert result["action_counts"]["user.login"] == 1

    def test_get_stats_with_date_filter(self, audit_svc, mock_supabase, mock_user):
        """Test getting stats with date range filtering."""
        mock_response = Mock()
        mock_response.data = [
            {"action": "content.created"},
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = mock_response

        result = audit_svc.get_stats(
            user_id=str(mock_user.id),
            date_from="2024-01-01",
            date_to="2024-12-31",
        )

        assert result["total"] == 1
        assert result["date_from"] == "2024-01-01"
        assert result["date_to"] == "2024-12-31"

    def test_export_csv(self, audit_svc, mock_supabase, mock_user):
        """Test exporting audit logs as CSV."""
        log_id = str(uuid4())
        mock_response = Mock()
        mock_response.data = [
            {
                "id": log_id,
                "actor_id": str(mock_user.id),
                "actor_email": mock_user.email,
                "action": "content.created",
                "resource_type": "content",
                "resource_id": str(uuid4()),
                "details": {"title": "Test"},
                "ip_address": "127.0.0.1",
                "user_agent": "TestAgent/1.0",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        csv_output = audit_svc.export_csv(user_id=str(mock_user.id))

        assert "id" in csv_output
        assert "actor_id" in csv_output
        assert "content.created" in csv_output
        assert log_id in csv_output

    def test_export_csv_with_filters(self, audit_svc, mock_supabase, mock_user):
        """Test exporting audit logs as CSV with filters."""
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        csv_output = audit_svc.export_csv(
            user_id=str(mock_user.id),
            date_from="2024-01-01",
            date_to="2024-12-31",
            action="content.created",
        )

        assert "id" in csv_output  # header row present even with no data

    def test_cleanup_expired(self, audit_svc, mock_supabase):
        """Test cleaning up expired audit logs."""
        mock_response = Mock()
        mock_response.data = [{"id": str(uuid4())}, {"id": str(uuid4())}]
        mock_supabase.table.return_value.delete.return_value.lt.return_value.execute.return_value = mock_response

        deleted_count = audit_svc.cleanup_expired(retention_days=90)

        assert deleted_count == 2

    def test_cleanup_expired_with_organization(self, audit_svc, mock_supabase):
        """Test cleaning up expired audit logs scoped to an organization."""
        mock_response = Mock()
        mock_response.data = [{"id": str(uuid4())}]
        mock_supabase.table.return_value.delete.return_value.lt.return_value.eq.return_value.execute.return_value = mock_response

        deleted_count = audit_svc.cleanup_expired(
            organization_id="org-123",
            retention_days=30,
        )

        assert deleted_count == 1


# ── Router Tests ──

class TestAuditLogsRouter:
    """Tests for the audit logs router endpoints."""

    @pytest.fixture
    def client(self, mock_user):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.routers.auth import get_auth_user

        app.dependency_overrides[get_auth_user] = lambda: mock_user
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()

    def test_list_audit_logs_endpoint(self, client, mock_user):
        """Test GET /api/v1/audit-logs."""
        with patch("app.routers.audit_logs.audit_service") as mock_svc:
            mock_svc.list_logs.return_value = [
                {
                    "id": str(uuid4()),
                    "actor_id": str(mock_user.id),
                    "actor_email": mock_user.email,
                    "action": "content.created",
                    "resource_type": "content",
                    "resource_id": str(uuid4()),
                    "details": {},
                    "ip_address": None,
                    "user_agent": None,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ]

            response = client.get("/api/v1/audit-logs")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["action"] == "content.created"

    def test_list_audit_logs_with_filters(self, client, mock_user):
        """Test GET /api/v1/audit-logs with query parameters."""
        with patch("app.routers.audit_logs.audit_service") as mock_svc:
            mock_svc.list_logs.return_value = []

            response = client.get(
                "/api/v1/audit-logs?action=content.updated&resource_type=content&limit=10"
            )

            assert response.status_code == 200
            mock_svc.list_logs.assert_called_once()

    def test_get_audit_log_endpoint(self, client, mock_user):
        """Test GET /api/v1/audit-logs/{id}."""
        log_id = str(uuid4())

        with patch("app.routers.audit_logs.audit_service") as mock_svc:
            mock_svc.get_log.return_value = {
                "id": log_id,
                "actor_id": str(mock_user.id),
                "actor_email": mock_user.email,
                "action": "user.login",
                "resource_type": "session",
                "resource_id": str(uuid4()),
                "details": {},
                "ip_address": "127.0.0.1",
                "user_agent": "Mozilla/5.0",
                "timestamp": datetime.utcnow().isoformat(),
            }

            response = client.get(f"/api/v1/audit-logs/{log_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["action"] == "user.login"

    def test_get_audit_log_not_found(self, client, mock_user):
        """Test GET /api/v1/audit-logs/{id} with non-existent ID."""
        log_id = str(uuid4())

        with patch("app.routers.audit_logs.audit_service") as mock_svc:
            mock_svc.get_log.return_value = None

            response = client.get(f"/api/v1/audit-logs/{log_id}")

            assert response.status_code == 404

    def test_export_audit_logs_endpoint(self, client, mock_user):
        """Test GET /api/v1/audit-logs/export."""
        with patch("app.routers.audit_logs.audit_service") as mock_svc:
            mock_svc.export_csv.return_value = "id,actor_id,actor_email,action\n1,test,user@test.com,content.created\n"

            response = client.get("/api/v1/audit-logs/export")

            assert response.status_code == 200
            assert "text/csv" in response.headers.get("content-type", "")
            assert "attachment" in response.headers.get("content-disposition", "")

    def test_audit_log_stats_endpoint(self, client, mock_user):
        """Test GET /api/v1/audit-logs/stats."""
        with patch("app.routers.audit_logs.audit_service") as mock_svc:
            mock_svc.get_stats.return_value = {
                "total": 15,
                "action_counts": {
                    "content.created": 5,
                    "content.updated": 3,
                    "user.login": 7,
                },
                "date_from": None,
                "date_to": None,
            }

            response = client.get("/api/v1/audit-logs/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 15
            assert data["action_counts"]["content.created"] == 5
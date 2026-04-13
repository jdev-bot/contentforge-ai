"""
Tests for report scheduling API.
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
def sample_report():
    """Create a sample scheduled report."""
    return {
        "id": str(uuid4()),
        "user_id": "test-user-id",
        "name": "Weekly Summary",
        "description": "Weekly content summary report",
        "report_type": "content_summary",
        "schedule": "0 9 * * 1",  # Every Monday at 9 AM
        "format": "html",
        "recipients": ["test@example.com"],
        "filters": {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_report_run():
    """Create a sample report run."""
    return {
        "id": str(uuid4()),
        "report_id": "report-1",
        "user_id": "test-user-id",
        "status": "completed",
        "format": "html",
        "storage_path": "reports/content_summary_20240101.html",
        "file_name": "content_summary_20240101_090000.html",
        "generated_at": datetime.utcnow().isoformat(),
        "error_message": None,
    }


# ── Report Service Tests ───────────────────────────────────────────

class TestReportService:
    """Tests for the ReportService class."""

    def test_list_reports(self, mock_user, sample_report):
        """Test listing reports."""
        from app.services.report_service import ReportService
        service = ReportService()
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = Mock(
            data=[sample_report]
        )
        service.supabase = mock_supabase

        result = service.list_reports(mock_user.id)
        assert len(result) == 1
        assert result[0]["name"] == "Weekly Summary"

    def test_create_report(self, mock_user):
        """Test creating a report."""
        from app.services.report_service import ReportService
        service = ReportService()
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[{"id": "new-report", "name": "New Report", "report_type": "content_summary"}]
        )
        service.supabase = mock_supabase

        result = service.create_report(
            user_id=mock_user.id,
            name="New Report",
            report_type="content_summary",
            schedule="0 9 * * 1",
            format="html",
            recipients=["test@example.com"],
        )
        assert result is not None
        assert result["name"] == "New Report"

    def test_create_report_invalid_type(self, mock_user):
        """Test creating a report with invalid type."""
        from app.services.report_service import ReportService
        service = ReportService()

        with pytest.raises(ValueError, match="Invalid report type"):
            service.create_report(
                user_id=mock_user.id,
                name="Bad Report",
                report_type="invalid_type",
                schedule="0 9 * * 1",
            )

    def test_create_report_invalid_format(self, mock_user):
        """Test creating a report with invalid format."""
        from app.services.report_service import ReportService
        service = ReportService()

        with pytest.raises(ValueError, match="Invalid format"):
            service.create_report(
                user_id=mock_user.id,
                name="Bad Format",
                report_type="content_summary",
                schedule="0 9 * * 1",
                format="xml",
            )

    def test_get_report(self, mock_user, sample_report):
        """Test getting a report."""
        from app.services.report_service import ReportService
        service = ReportService()
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = Mock(
            data=sample_report
        )
        service.supabase = mock_supabase

        result = service.get_report("report-1", mock_user.id)
        assert result is not None
        assert result["name"] == "Weekly Summary"

    def test_update_report(self, mock_user, sample_report):
        """Test updating a report."""
        from app.services.report_service import ReportService
        service = ReportService()

        with patch.object(service, 'get_report', return_value=sample_report):
            mock_supabase = MagicMock()
            mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = Mock(
                data=[{**sample_report, "name": "Updated Report"}]
            )
            service.supabase = mock_supabase

            result = service.update_report("report-1", mock_user.id, name="Updated Report")
            assert result is not None
            assert result["name"] == "Updated Report"

    def test_update_report_not_found(self, mock_user):
        """Test updating a non-existent report."""
        from app.services.report_service import ReportService
        service = ReportService()

        with patch.object(service, 'get_report', return_value=None):
            result = service.update_report("nonexistent", mock_user.id, name="New Name")
            assert result is None

    def test_delete_report(self, mock_user, sample_report):
        """Test deleting a report."""
        from app.services.report_service import ReportService
        service = ReportService()
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = Mock(data=[])

        with patch.object(service, 'get_report', return_value=sample_report):
            service.supabase = mock_supabase
            result = service.delete_report("report-1", mock_user.id)
            assert result is True

    def test_delete_report_not_found(self, mock_user):
        """Test deleting a non-existent report."""
        from app.services.report_service import ReportService
        service = ReportService()

        with patch.object(service, 'get_report', return_value=None):
            result = service.delete_report("nonexistent", mock_user.id)
            assert result is False

    def test_generate_report(self, mock_user, sample_report):
        """Test generating a report."""
        from app.services.report_service import ReportService
        service = ReportService()
        mock_supabase = MagicMock()

        with patch.object(service, 'get_report', return_value=sample_report), \
             patch.object(service, '_gather_report_data', return_value={"total_content": 42}), \
             patch.object(service, '_store_report', return_value="reports/test.html"), \
             patch.object(service, '_send_report_email'):
            mock_supabase.table.return_value.insert.return_value.execute.return_value = Mock(
                data=[{"id": "run-1", "status": "completed"}]
            )
            service.supabase = mock_supabase

            result = service.generate_report("report-1", mock_user.id)
            assert result is not None
            assert result["status"] == "completed"

    def test_get_report_history(self, mock_user, sample_report, sample_report_run):
        """Test getting report history."""
        from app.services.report_service import ReportService
        service = ReportService()
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = Mock(
            data=[sample_report_run]
        )

        with patch.object(service, 'get_report', return_value=sample_report):
            service.supabase = mock_supabase
            result = service.get_report_history("report-1", mock_user.id)
            assert len(result) == 1
            assert result[0]["status"] == "completed"


# ── Report Router Tests ────────────────────────────────────────────

class TestReportRouter:
    """Tests for the report router endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_list_reports_endpoint(self, client, mock_user):
        """Test GET /api/v1/reports."""
        with patch("app.routers.reports.get_auth_user", return_value=mock_user), \
             patch("app.routers.reports.report_service") as mock_service:
            mock_service.list_reports.return_value = [
                {"id": "report-1", "name": "Weekly Summary"}
            ]

            response = client.get("/api/v1/reports", headers={"Authorization": "Bearer test"})
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_create_report_endpoint(self, client, mock_user):
        """Test POST /api/v1/reports."""
        with patch("app.routers.reports.get_auth_user", return_value=mock_user), \
             patch("app.routers.reports.report_service") as mock_service:
            mock_service.create_report.return_value = {
                "id": "report-new", "name": "New Report", "report_type": "content_summary"
            }

            response = client.post(
                "/api/v1/reports",
                json={
                    "name": "New Report",
                    "report_type": "content_summary",
                    "schedule": "0 9 * * 1",
                    "format": "html",
                    "recipients": ["test@example.com"],
                },
                headers={"Authorization": "Bearer test"},
            )
            assert response.status_code == 201

    def test_create_report_invalid_type_endpoint(self, client, mock_user):
        """Test POST /api/v1/reports with invalid type."""
        with patch("app.routers.reports.get_auth_user", return_value=mock_user):
            response = client.post(
                "/api/v1/reports",
                json={
                    "name": "Bad Report",
                    "report_type": "invalid_type",
                    "schedule": "0 9 * * 1",
                },
                headers={"Authorization": "Bearer test"},
            )
            assert response.status_code == 400

    def test_get_report_endpoint(self, client, mock_user):
        """Test GET /api/v1/reports/{id}."""
        with patch("app.routers.reports.get_auth_user", return_value=mock_user), \
             patch("app.routers.reports.report_service") as mock_service:
            mock_service.get_report.return_value = {
                "id": "report-1", "name": "Weekly Summary", "report_type": "content_summary"
            }

            response = client.get("/api/v1/reports/report-1", headers={"Authorization": "Bearer test"})
            assert response.status_code == 200

    def test_get_report_not_found_endpoint(self, client, mock_user):
        """Test GET /api/v1/reports/{id} when not found."""
        with patch("app.routers.reports.get_auth_user", return_value=mock_user), \
             patch("app.routers.reports.report_service") as mock_service:
            mock_service.get_report.return_value = None

            response = client.get("/api/v1/reports/nonexistent", headers={"Authorization": "Bearer test"})
            assert response.status_code == 404

    def test_delete_report_endpoint(self, client, mock_user):
        """Test DELETE /api/v1/reports/{id}."""
        with patch("app.routers.reports.get_auth_user", return_value=mock_user), \
             patch("app.routers.reports.report_service") as mock_service:
            mock_service.delete_report.return_value = True

            response = client.delete("/api/v1/reports/report-1", headers={"Authorization": "Bearer test"})
            assert response.status_code == 204

    def test_generate_report_endpoint(self, client, mock_user):
        """Test POST /api/v1/reports/{id}/generate."""
        with patch("app.routers.reports.get_auth_user", return_value=mock_user), \
             patch("app.routers.reports.report_service") as mock_service:
            mock_service.generate_report.return_value = {
                "id": "run-1", "status": "completed", "format": "html"
            }

            response = client.post("/api/v1/reports/report-1/generate", headers={"Authorization": "Bearer test"})
            assert response.status_code == 200

    def test_get_report_history_endpoint(self, client, mock_user):
        """Test GET /api/v1/reports/{id}/history."""
        with patch("app.routers.reports.get_auth_user", return_value=mock_user), \
             patch("app.routers.reports.report_service") as mock_service:
            mock_service.get_report_history.return_value = [
                {"id": "run-1", "status": "completed", "generated_at": datetime.utcnow().isoformat()}
            ]

            response = client.get("/api/v1/reports/report-1/history", headers={"Authorization": "Bearer test"})
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_download_report_endpoint(self, client, mock_user):
        """Test GET /api/v1/reports/{id}/download/{run_id}."""
        with patch("app.routers.reports.get_auth_user", return_value=mock_user), \
             patch("app.routers.reports.report_service") as mock_service:
            mock_service.download_report.return_value = {
                "id": "run-1", "file_name": "report.html", "download_url": "https://example.com/report.html"
            }

            response = client.get("/api/v1/reports/report-1/download/run-1", headers={"Authorization": "Bearer test"})
            assert response.status_code == 200
            data = response.json()
            assert "download_url" in data


# ── Celery Task Tests ──────────────────────────────────────────────

class TestReportTasks:
    """Tests for report Celery tasks."""

    def test_generate_scheduled_reports(self):
        """Test the generate_scheduled_reports task."""
        with patch("app.tasks.reports.get_supabase_admin_client") as mock_get_client, \
             patch("app.tasks.reports.report_service") as mock_service:
            mock_client = MagicMock()
            mock_client.table.return_value.select.return_value.execute.return_value = Mock(
                data=[{"id": "report-1", "user_id": "user-1", "schedule": "0 9 * * 1", "name": "Weekly"}]
            )
            mock_get_client.return_value = mock_client
            mock_service.generate_report.return_value = {"id": "run-1", "status": "completed"}

            from app.tasks.reports import generate_scheduled_reports
            result = generate_scheduled_reports()
            assert result["success"] is True
            assert result["generated"] == 1

    def test_generate_single_report_task(self):
        """Test the generate_single_report task."""
        with patch("app.tasks.reports.report_service") as mock_service:
            mock_service.generate_report.return_value = {"id": "run-1", "status": "completed"}

            from app.tasks.reports import generate_single_report
            result = generate_single_report("report-1", "user-1")
            assert result["success"] is True

    def test_cleanup_old_report_runs_task(self):
        """Test the cleanup_old_report_runs task."""
        with patch("app.tasks.reports.get_supabase_admin_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.table.return_value.delete.return_value.lt.return_value.execute.return_value = Mock(
                data=[{"id": "old-run-1"}, {"id": "old-run-2"}]
            )
            mock_get_client.return_value = mock_client

            from app.tasks.reports import cleanup_old_report_runs
            result = cleanup_old_report_runs(days=90)
            assert result["success"] is True
            assert result["deleted"] == 2
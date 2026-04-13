"""
Tests for Version History service and router.
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
    with patch("app.services.version_service.get_supabase_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def version_svc(mock_supabase):
    from app.services.version_service import VersionService
    svc = VersionService()
    svc.supabase = mock_supabase
    return svc


@pytest.fixture
def sample_version():
    return {
        "id": str(uuid4()),
        "content_id": str(uuid4()),
        "user_id": str(uuid4()),
        "version_number": 1,
        "title": "Test Title",
        "body": "Test body content for versioning.",
        "metadata": {
            "change_summary": "Initial version",
            "word_count": 5,
            "word_count_delta": 0,
        },
        "created_by": str(uuid4()),
        "created_at": datetime.utcnow().isoformat(),
    }


# ── Service Tests ──

class TestVersionService:
    """Tests for the VersionService class."""

    def test_list_versions(self, version_svc, mock_supabase, mock_user):
        """Test listing versions for a content item."""
        content_id = str(uuid4())
        mock_response = Mock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "content_id": content_id,
                "user_id": str(mock_user.id),
                "version_number": 2,
                "title": "v2",
                "body": "body2",
                "metadata": {},
                "created_by": str(mock_user.id),
                "created_at": datetime.utcnow().isoformat(),
            },
            {
                "id": str(uuid4()),
                "content_id": content_id,
                "user_id": str(mock_user.id),
                "version_number": 1,
                "title": "v1",
                "body": "body1",
                "metadata": {},
                "created_by": str(mock_user.id),
                "created_at": datetime.utcnow().isoformat(),
            },
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_response

        result = version_svc.list_versions(content_id, str(mock_user.id))
        assert len(result) == 2
        assert result[0]["version_number"] == 2

    def test_get_version_found(self, version_svc, mock_supabase, mock_user, sample_version):
        """Test getting a specific version that exists."""
        mock_response = Mock()
        mock_response.data = sample_version
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        result = version_svc.get_version(sample_version["content_id"], sample_version["id"], str(mock_user.id))
        assert result is not None
        assert result["version_number"] == 1

    def test_get_version_not_found(self, version_svc, mock_supabase, mock_user):
        """Test getting a version that doesn't exist returns None."""
        mock_response = Mock()
        mock_response.data = None
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        result = version_svc.get_version(str(uuid4()), str(uuid4()), str(mock_user.id))
        assert result is None

    def test_create_version_with_explicit_content(self, version_svc, mock_supabase, mock_user):
        """Test creating a version with explicit title and body."""
        content_id = str(uuid4())

        # Mock: get latest version number
        latest_mock = Mock()
        latest_mock.data = [{"version_number": 3}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = latest_mock

        # Mock: get previous version body for word count delta
        prev_mock = Mock()
        prev_mock.data = {"body": "previous content with some words"}
        # We need to set up the chain for the single() call
        single_chain = mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.single.return_value
        single_chain.execute.return_value = prev_mock

        # Mock: insert
        insert_mock = Mock()
        insert_mock.data = [{
            "id": str(uuid4()),
            "content_id": content_id,
            "version_number": 4,
            "title": "New Version",
            "body": "New body text",
            "metadata": {"change_summary": "Manual save", "word_count": 3, "word_count_delta": -2},
            "created_by": str(mock_user.id),
            "created_at": datetime.utcnow().isoformat(),
        }]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = insert_mock

        # Mock: count for pruning
        count_mock = Mock()
        count_mock.data = []
        count_mock.count = 2
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = count_mock

        result = version_svc.create_version(
            content_id=content_id,
            user_id=str(mock_user.id),
            title="New Version",
            body="New body text",
            change_summary="Manual save",
        )
        assert result is not None
        assert result["version_number"] == 4

    def test_create_version_fetches_current_content(self, version_svc, mock_supabase, mock_user):
        """Test that create_version fetches current content when title/body not provided."""
        content_id = str(uuid4())

        # Mock: content fetch
        content_mock = Mock()
        content_mock.data = {"title": "Fetched Title", "original_text": "Fetched body"}
        single_chain = mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value
        single_chain.execute.return_value = content_mock

        # Mock: latest version number (no prior versions)
        latest_mock = Mock()
        latest_mock.data = []
        # Need separate chain for the order call
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = latest_mock

        # Mock: insert
        insert_mock = Mock()
        insert_mock.data = [{
            "id": str(uuid4()),
            "content_id": content_id,
            "version_number": 1,
            "title": "Fetched Title",
            "body": "Fetched body",
            "metadata": {"change_summary": "Version 1", "word_count": 2, "word_count_delta": 0},
            "created_by": str(mock_user.id),
            "created_at": datetime.utcnow().isoformat(),
        }]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = insert_mock

        # Mock: count for pruning
        count_mock = Mock()
        count_mock.data = []
        count_mock.count = 1
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = count_mock

        result = version_svc.create_version(content_id=content_id, user_id=str(mock_user.id))
        assert result is not None
        assert result["title"] == "Fetched Title"

    def test_compute_diff_unified(self, version_svc, mock_supabase, mock_user):
        """Test computing unified diff between two versions."""
        v1_id = str(uuid4())
        v2_id = str(uuid4())
        content_id = str(uuid4())

        v1_data = {
            "id": v1_id, "content_id": content_id,
            "version_number": 1, "title": "v1",
            "body": "Line one\nLine two\nLine three",
            "metadata": {}, "created_by": str(mock_user.id),
            "created_at": datetime.utcnow().isoformat(),
        }
        v2_data = {
            "id": v2_id, "content_id": content_id,
            "version_number": 2, "title": "v2",
            "body": "Line one\nLine modified\nLine three",
            "metadata": {}, "created_by": str(mock_user.id),
            "created_at": datetime.utcnow().isoformat(),
        }

        # Mock get_version
        with patch.object(version_svc, "get_version") as mock_get:
            mock_get.side_effect = [v1_data, v2_data]

            result = version_svc.compute_diff(
                content_id=content_id,
                version_id_1=v1_id,
                version_id_2=v2_id,
                user_id=str(mock_user.id),
                format="unified",
            )

        assert "diff" in result
        assert result["format"] == "unified"
        assert "version_1" in result
        assert "version_2" in result
        # Unified diff should contain markers
        assert "-" in result["diff"] or "+" in result["diff"] or result["diff"] == ""

    def test_compute_diff_html(self, version_svc, mock_supabase, mock_user):
        """Test computing HTML diff between two versions."""
        v1_id = str(uuid4())
        v2_id = str(uuid4())
        content_id = str(uuid4())

        v1_data = {
            "id": v1_id, "content_id": content_id,
            "version_number": 1, "title": "v1",
            "body": "Original text here",
            "metadata": {}, "created_by": str(mock_user.id),
            "created_at": datetime.utcnow().isoformat(),
        }
        v2_data = {
            "id": v2_id, "content_id": content_id,
            "version_number": 2, "title": "v2",
            "body": "Modified text here",
            "metadata": {}, "created_by": str(mock_user.id),
            "created_at": datetime.utcnow().isoformat(),
        }

        with patch.object(version_svc, "get_version") as mock_get:
            mock_get.side_effect = [v1_data, v2_data]

            result = version_svc.compute_diff(
                content_id=content_id,
                version_id_1=v1_id,
                version_id_2=v2_id,
                user_id=str(mock_user.id),
                format="html",
            )

        assert result["format"] == "html"
        assert "<table" in result["diff"]

    def test_restore_version(self, version_svc, mock_supabase, mock_user):
        """Test restoring a previous version."""
        content_id = str(uuid4())
        version_id = str(uuid4())

        version_data = {
            "id": version_id,
            "content_id": content_id,
            "version_number": 2,
            "title": "Restored Title",
            "body": "Restored body",
            "metadata": {},
            "created_by": str(mock_user.id),
            "created_at": datetime.utcnow().isoformat(),
        }

        with patch.object(version_svc, "get_version", return_value=version_data), \
             patch.object(version_svc, "create_version") as mock_create:
            mock_create.return_value = {
                "id": str(uuid4()),
                "version_number": 3,
                "title": "Restored Title",
                "body": "Restored body",
            }

            result = version_svc.restore_version(
                content_id=content_id,
                version_id=version_id,
                user_id=str(mock_user.id),
            )

        assert result["restored_from_version"] == 2
        assert result["new_version"]["version_number"] == 3

    def test_delete_version(self, version_svc, mock_supabase, mock_user):
        """Test deleting a version."""
        mock_response = Mock()
        mock_response.data = [{"id": str(uuid4())}]
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

        result = version_svc.delete_version(str(uuid4()), str(uuid4()), str(mock_user.id))
        assert result is True

    def test_delete_version_not_found(self, version_svc, mock_supabase, mock_user):
        """Test deleting a version that doesn't exist."""
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

        result = version_svc.delete_version(str(uuid4()), str(uuid4()), str(mock_user.id))
        assert result is False


# ── Router Tests ──

class TestVersionHistoryRouter:
    """Tests for the version history router endpoints."""

    @pytest.fixture
    def client(self, mock_user):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.routers.auth import get_auth_user

        app.dependency_overrides[get_auth_user] = lambda: mock_user
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()

    def test_list_versions_endpoint(self, client, mock_user):
        """Test GET /api/v1/content/{id}/versions."""
        with patch("app.routers.version_history.version_service") as mock_svc:
            mock_svc.list_versions.return_value = [
                {
                    "id": str(uuid4()),
                    "content_id": str(uuid4()),
                    "version_number": 1,
                    "title": "v1",
                    "body": "body1",
                    "metadata": {},
                    "created_by": str(mock_user.id),
                    "created_at": datetime.utcnow().isoformat(),
                }
            ]

            content_id = str(uuid4())
            response = client.get(f"/api/v1/content/{content_id}/versions")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["version_number"] == 1

    def test_create_version_endpoint(self, client, mock_user):
        """Test POST /api/v1/content/{id}/versions."""
        content_id = str(uuid4())
        version_id = str(uuid4())

        with patch("app.routers.version_history.version_service") as mock_svc:
            mock_svc.create_version.return_value = {
                "id": version_id,
                "content_id": content_id,
                "version_number": 1,
                "title": "Manual Save",
                "body": "Saved body",
                "metadata": {"change_summary": "Manual savepoint", "word_count": 2, "word_count_delta": 0},
                "created_by": str(mock_user.id),
                "created_at": datetime.utcnow().isoformat(),
            }

            response = client.post(
                f"/api/v1/content/{content_id}/versions",
                json={"change_summary": "Manual savepoint"},
            )

            assert response.status_code == 201
            data = response.json()
            assert data["version_number"] == 1

    def test_diff_versions_endpoint(self, client, mock_user):
        """Test GET /api/v1/content/{id}/versions/diff."""
        content_id = str(uuid4())
        v1 = str(uuid4())
        v2 = str(uuid4())

        with patch("app.routers.version_history.version_service") as mock_svc:
            mock_svc.compute_diff.return_value = {
                "version_1": {"id": v1, "version_number": 1, "created_at": datetime.utcnow().isoformat()},
                "version_2": {"id": v2, "version_number": 2, "created_at": datetime.utcnow().isoformat()},
                "format": "unified",
                "diff": "--- v1\n+++ v2\n@@ -1 +1 @@\n-old\n+new",
            }

            response = client.get(
                f"/api/v1/content/{content_id}/versions/diff?v1={v1}&v2={v2}"
            )

            assert response.status_code == 200
            data = response.json()
            assert "diff" in data
            assert data["format"] == "unified"

    def test_restore_version_endpoint(self, client, mock_user):
        """Test POST /api/v1/content/{id}/versions/{vid}/restore."""
        content_id = str(uuid4())
        version_id = str(uuid4())

        with patch("app.routers.version_history.version_service") as mock_svc:
            mock_svc.restore_version.return_value = {
                "restored_from_version": 2,
                "new_version": {"id": str(uuid4()), "version_number": 3},
            }

            response = client.post(
                f"/api/v1/content/{content_id}/versions/{version_id}/restore"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["restored_from_version"] == 2

    def test_delete_version_endpoint(self, client, mock_user):
        """Test DELETE /api/v1/content/{id}/versions/{vid}."""
        content_id = str(uuid4())
        version_id = str(uuid4())

        with patch("app.routers.version_history.version_service") as mock_svc:
            mock_svc.delete_version.return_value = True

            response = client.delete(
                f"/api/v1/content/{content_id}/versions/{version_id}"
            )

            assert response.status_code == 204

    def test_get_version_endpoint(self, client, mock_user):
        """Test GET /api/v1/content/{id}/versions/{vid}."""
        content_id = str(uuid4())
        version_id = str(uuid4())

        with patch("app.routers.version_history.version_service") as mock_svc:
            mock_svc.get_version.return_value = {
                "id": version_id,
                "content_id": content_id,
                "version_number": 2,
                "title": "v2",
                "body": "body2",
                "metadata": {},
                "created_by": str(mock_user.id),
                "created_at": datetime.utcnow().isoformat(),
            }

            response = client.get(
                f"/api/v1/content/{content_id}/versions/{version_id}"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["version_number"] == 2
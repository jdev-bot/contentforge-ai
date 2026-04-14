"""
Tests for the distributions router.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app

client = TestClient(app)


class MockUser:
    """Mock user for authentication."""

    def __init__(self, user_id=None, email="test@example.com"):
        self.id = user_id or uuid4()
        self.email = email
        self.user_metadata = {"full_name": "Test User"}


class MockSupabaseUser:
    """Mock Supabase user object."""

    def __init__(self, user_id=None):
        self.user = MockUser(user_id)


class TestDistributions:
    """Test distribution endpoints."""

    @pytest.fixture
    def mock_auth_dependencies(self):
        """Mock all auth and supabase dependencies."""
        user_id = uuid4()
        user = MockUser(user_id)

        with patch("app.routers.distributions.get_auth_user") as mock_auth, patch(
            "app.routers.auth.get_supabase_client"
        ) as mock_supabase_auth, patch(
            "app.routers.distributions.get_supabase_client"
        ) as mock_supabase_dist:

            mock_auth.return_value = user

            # Mock supabase auth
            supabase_auth_mock = MagicMock()
            mock_supabase_user = MockSupabaseUser(user_id)
            supabase_auth_mock.auth.get_user.return_value = mock_supabase_user
            mock_supabase_auth.return_value = supabase_auth_mock

            # Mock supabase for distributions
            supabase_dist_mock = MagicMock()
            mock_supabase_dist.return_value = supabase_dist_mock

            yield {
                "user": user,
                "supabase_auth": supabase_auth_mock,
                "supabase_dist": supabase_dist_mock,
            }

    def test_create_distribution_success(self, mock_auth_dependencies):
        """Test creating a distribution successfully."""
        user = mock_auth_dependencies["user"]
        mock_supabase = mock_auth_dependencies["supabase_dist"]
        asset_id = uuid4()
        distribution_id = uuid4()

        # Mock asset check
        asset_result = MagicMock()
        asset_result.data = {"id": str(asset_id), "user_id": str(user.id)}
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = (
            asset_result
        )

        # Mock insert
        insert_result = MagicMock()
        insert_result.data = [
            {
                "id": str(distribution_id),
                "asset_id": str(asset_id),
                "user_id": str(user.id),
                "platform": "twitter",
                "status": "pending",
                "scheduled_at": None,
                "published_url": None,
                "external_id": None,
                "error_message": None,
                "retry_count": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            insert_result
        )

        response = client.post(
            "/api/v1/distributions",
            json={
                "asset_id": str(asset_id),
                "platform": "twitter",
                "scheduled_at": None,
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["platform"] == "twitter"
        assert data["status"] == "pending"
        assert data["asset_id"] == str(asset_id)

    def test_create_distribution_asset_not_found(self, mock_auth_dependencies):
        """Test creating distribution with non-existent asset."""
        user = mock_auth_dependencies["user"]
        mock_supabase = mock_auth_dependencies["supabase_dist"]
        asset_id = uuid4()

        # Mock asset check - not found
        asset_result = MagicMock()
        asset_result.data = None
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = (
            asset_result
        )

        response = client.post(
            "/api/v1/distributions",
            json={"asset_id": str(asset_id), "platform": "twitter"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 404
        assert "Asset not found" in response.json()["detail"]

    def test_list_distributions(self, mock_auth_dependencies):
        """Test listing distributions for a user."""
        user = mock_auth_dependencies["user"]
        mock_supabase = mock_auth_dependencies["supabase_dist"]
        distribution_id = uuid4()
        asset_id = uuid4()

        list_result = MagicMock()
        list_result.data = [
            {
                "id": str(distribution_id),
                "asset_id": str(asset_id),
                "user_id": str(user.id),
                "platform": "linkedin",
                "status": "scheduled",
                "scheduled_at": (
                    datetime.now(timezone.utc) + timedelta(days=1)
                ).isoformat(),
                "published_url": None,
                "external_id": None,
                "error_message": None,
                "retry_count": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            list_result
        )

        response = client.get(
            "/api/v1/distributions", headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["platform"] == "linkedin"
        assert data[0]["status"] == "scheduled"

    def test_get_distribution_success(self, mock_auth_dependencies):
        """Test getting a specific distribution."""
        user = mock_auth_dependencies["user"]
        mock_supabase = mock_auth_dependencies["supabase_dist"]
        distribution_id = uuid4()
        asset_id = uuid4()

        get_result = MagicMock()
        get_result.data = {
            "id": str(distribution_id),
            "asset_id": str(asset_id),
            "user_id": str(user.id),
            "platform": "instagram",
            "status": "published",
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "published_url": "https://instagram.com/p/abc123",
            "external_id": None,
            "error_message": None,
            "retry_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = (
            get_result
        )

        response = client.get(
            f"/api/v1/distributions/{distribution_id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "instagram"
        assert data["status"] == "published"
        assert data["published_url"] == "https://instagram.com/p/abc123"

    def test_cancel_distribution_success(self, mock_auth_dependencies):
        """Test cancelling a scheduled distribution."""
        user = mock_auth_dependencies["user"]
        mock_supabase = mock_auth_dependencies["supabase_dist"]
        distribution_id = uuid4()
        asset_id = uuid4()

        # Mock get existing
        existing_result = MagicMock()
        existing_result.data = {
            "id": str(distribution_id),
            "asset_id": str(asset_id),
            "user_id": str(user.id),
            "platform": "email",
            "status": "pending",  # Can delete if not published
        }
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = (
            existing_result
        )

        # Mock delete
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = (
            MagicMock()
        )

        response = client.delete(
            f"/api/v1/distributions/{distribution_id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 204

    def test_cancel_published_distribution_fails(self, mock_auth_dependencies):
        """Test that cancelling a published distribution fails."""
        user = mock_auth_dependencies["user"]
        mock_supabase = mock_auth_dependencies["supabase_dist"]
        distribution_id = uuid4()
        asset_id = uuid4()

        # Mock get existing - already published
        existing_result = MagicMock()
        existing_result.data = {
            "id": str(distribution_id),
            "asset_id": str(asset_id),
            "user_id": str(user.id),
            "platform": "blog",
            "status": "published",
        }
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = (
            existing_result
        )

        response = client.delete(
            f"/api/v1/distributions/{distribution_id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert (
            "Cannot delete already published distribution" in response.json()["detail"]
        )

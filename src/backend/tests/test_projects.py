"""
Project management tests for ContentForge AI.

Tests project CRUD operations.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import status
from uuid import uuid4

from tests.utils import (
    create_mock_supabase_response,
    create_mock_auth_user,
    create_auth_headers,
    MockSupabaseBuilder,
    create_test_project_data
)


class TestProjectCreate:
    """Tests for project creation endpoint."""
    
    @pytest.mark.unit
    def test_create_project_success(self, client, sample_project):
        """Test successful project creation."""
        headers = create_auth_headers()
        
        project_data = create_test_project_data(
            name="New Project",
            description="A new test project"
        )
        
        mock_user = create_mock_auth_user()
        mock_response_data = {
            **sample_project,
            "name": project_data["name"],
            "description": project_data["description"],
        }
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", mock_response_data)
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/projects", json=project_data, headers=headers)
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["name"] == project_data["name"]
            assert data["description"] == project_data["description"]
            assert "id" in data
            assert "user_id" in data
    
    @pytest.mark.unit
    def test_create_project_minimal(self, client, sample_project):
        """Test project creation with minimal data."""
        headers = create_auth_headers()
        
        project_data = {"name": "Minimal Project"}
        
        mock_user = create_mock_auth_user()
        mock_response_data = {
            **sample_project,
            "name": "Minimal Project",
            "description": None,
        }
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", mock_response_data)
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/projects", json=project_data, headers=headers)
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["name"] == "Minimal Project"
    
    @pytest.mark.unit
    def test_create_project_with_brand_voice(self, client, sample_project):
        """Test project creation with brand voice configuration."""
        headers = create_auth_headers()
        
        project_data = create_test_project_data(
            name="Branded Project",
            brand_voice={"tone": "casual", "style": "friendly"},
            target_platforms=["twitter", "linkedin", "instagram"]
        )
        
        mock_user = create_mock_auth_user()
        mock_response_data = {
            **sample_project,
            "name": project_data["name"],
            "brand_voice": project_data["brand_voice"],
            "target_platforms": project_data["target_platforms"],
        }
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", mock_response_data)
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/projects", json=project_data, headers=headers)
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["brand_voice"] == {"tone": "casual", "style": "friendly"}
            assert data["target_platforms"] == ["twitter", "linkedin", "instagram"]
    
    @pytest.mark.unit
    def test_create_project_missing_name(self, client):
        """Test project creation without name."""
        headers = create_auth_headers()
        
        project_data = {
            "description": "A project without a name",
        }
        
        response = client.post("/api/v1/projects", json=project_data, headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_create_project_empty_name(self, client):
        """Test project creation with empty name."""
        headers = create_auth_headers()
        
        project_data = {"name": ""}
        
        mock_user = create_mock_auth_user()
        mock_response_data = {
            "id": str(uuid4()),
            "user_id": mock_user.id,
            "name": "",
            "description": None,
            "brand_voice": {},
            "target_platforms": [],
            "is_active": True,
        }
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", mock_response_data)
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            # Empty strings may be allowed at API level
            response = client.post("/api/v1/projects", json=project_data, headers=headers)
            
            # API accepts empty strings, validation would be at DB or business logic level
            assert response.status_code == status.HTTP_201_CREATED
    
    @pytest.mark.unit
    def test_create_project_unauthorized(self, client):
        """Test project creation without authentication."""
        project_data = create_test_project_data()
        
        response = client.post("/api/v1/projects", json=project_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProjectList:
    """Tests for project listing endpoint."""
    
    @pytest.mark.unit
    def test_list_projects_success(self, client, sample_project):
        """Test listing all projects for a user."""
        headers = create_auth_headers()
        
        mock_user = create_mock_auth_user()
        projects = [
            sample_project,
            {**sample_project, "id": str(uuid4()), "name": "Second Project"},
        ]
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", projects)
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            response = client.get("/api/v1/projects", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["name"] == sample_project["name"]
    
    @pytest.mark.unit
    def test_list_projects_active_only(self, client, sample_project):
        """Test listing only active projects."""
        headers = create_auth_headers()
        
        mock_user = create_mock_auth_user()
        active_projects = [
            {**sample_project, "is_active": True},
        ]
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", active_projects)
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            response = client.get("/api/v1/projects?is_active=true", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert all(p["is_active"] for p in data)
    
    @pytest.mark.unit
    def test_list_projects_empty(self, client):
        """Test listing projects when user has none."""
        headers = create_auth_headers()
        
        mock_user = create_mock_auth_user()
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", [])
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            response = client.get("/api/v1/projects", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data == []
    
    @pytest.mark.unit
    def test_list_projects_ordered_by_date(self, client, sample_project):
        """Test that projects are ordered by creation date."""
        headers = create_auth_headers()
        
        mock_user = create_mock_auth_user()
        projects = [
            {**sample_project, "created_at": "2024-01-01T00:00:00Z", "name": "Older"},
            {**sample_project, "id": str(uuid4()), "created_at": "2024-01-02T00:00:00Z", "name": "Newer"},
        ]
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", projects)
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            response = client.get("/api/v1/projects", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            # Should be ordered by created_at desc
            assert data[0]["name"] == "Newer"
            assert data[1]["name"] == "Older"


class TestProjectGet:
    """Tests for project retrieval endpoint."""
    
    @pytest.mark.unit
    def test_get_project_success(self, client, sample_project):
        """Test getting a specific project."""
        headers = create_auth_headers()
        project_id = sample_project["id"]
        
        mock_user = create_mock_auth_user()
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", sample_project, single=True)
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == project_id
            assert data["name"] == sample_project["name"]
    
    @pytest.mark.unit
    def test_get_project_not_found(self, client):
        """Test getting non-existent project."""
        headers = create_auth_headers()
        project_id = str(uuid4())
        
        mock_user = create_mock_auth_user()
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=None)
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.projects.get_supabase_client', return_value=mock_client):
            response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    def test_get_project_wrong_user(self, client, sample_project):
        """Test getting project belonging to another user."""
        headers = create_auth_headers()
        project_id = sample_project["id"]
        
        mock_user = create_mock_auth_user(user_id="different-user-id")
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=None)
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.projects.get_supabase_client', return_value=mock_client):
            response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    def test_get_project_invalid_uuid(self, client):
        """Test getting project with invalid UUID format."""
        headers = create_auth_headers()
        
        response = client.get("/api/v1/projects/not-a-uuid", headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestProjectUpdate:
    """Tests for project update endpoint."""
    
    @pytest.mark.unit
    def test_update_project_success(self, client, sample_project):
        """Test successful project update."""
        headers = create_auth_headers()
        project_id = sample_project["id"]
        
        update_data = {
            "name": "Updated Project Name",
            "description": "Updated description",
        }
        
        mock_user = create_mock_auth_user()
        existing_project = sample_project
        updated_project = {**sample_project, **update_data}
        
        # Create a mock table that returns existing project on first call, updated on second
        mock_table = MagicMock()
        
        # First call for checking existence
        mock_select = MagicMock()
        mock_select.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=existing_project)
        
        # Second call for updating
        mock_update = MagicMock()
        mock_update.eq.return_value.execute.return_value = \
            create_mock_supabase_response(data=[updated_project])
        
        mock_table.select.return_value.eq.return_value = mock_select
        mock_table.update.return_value = mock_update
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.projects.get_supabase_client', return_value=mock_client):
            response = client.patch(f"/api/v1/projects/{project_id}", json=update_data, headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Updated Project Name"
            assert data["description"] == "Updated description"
    
    @pytest.mark.unit
    def test_update_project_partial(self, client, sample_project):
        """Test partial project update."""
        headers = create_auth_headers()
        project_id = sample_project["id"]
        
        update_data = {"name": "Only Name Updated"}
        
        mock_user = create_mock_auth_user()
        updated_project = {**sample_project, "name": "Only Name Updated"}
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=sample_project)
        mock_table.update.return_value.eq.return_value.execute.return_value = \
            create_mock_supabase_response(data=[updated_project])
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.projects.get_supabase_client', return_value=mock_client):
            response = client.patch(f"/api/v1/projects/{project_id}", json=update_data, headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Only Name Updated"
            assert data["description"] == sample_project["description"]  # Unchanged
    
    @pytest.mark.unit
    def test_update_project_not_found(self, client):
        """Test updating non-existent project."""
        headers = create_auth_headers()
        project_id = str(uuid4())
        
        update_data = {"name": "New Name"}
        
        mock_user = create_mock_auth_user()
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=None)
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.projects.get_supabase_client', return_value=mock_client):
            response = client.patch(f"/api/v1/projects/{project_id}", json=update_data, headers=headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    def test_update_project_brand_voice(self, client, sample_project):
        """Test updating project brand voice."""
        headers = create_auth_headers()
        project_id = sample_project["id"]
        
        update_data = {
            "brand_voice": {"tone": "humorous", "style": "casual"},
        }
        
        mock_user = create_mock_auth_user()
        updated_project = {**sample_project, "brand_voice": {"tone": "humorous", "style": "casual"}}
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=sample_project)
        mock_table.update.return_value.eq.return_value.execute.return_value = \
            create_mock_supabase_response(data=[updated_project])
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.projects.get_supabase_client', return_value=mock_client):
            response = client.patch(f"/api/v1/projects/{project_id}", json=update_data, headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["brand_voice"] == {"tone": "humorous", "style": "casual"}
    
    @pytest.mark.unit
    def test_update_project_target_platforms(self, client, sample_project):
        """Test updating project target platforms."""
        headers = create_auth_headers()
        project_id = sample_project["id"]
        
        update_data = {
            "target_platforms": ["tiktok", "youtube"],
        }
        
        mock_user = create_mock_auth_user()
        updated_project = {**sample_project, "target_platforms": ["tiktok", "youtube"]}
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=sample_project)
        mock_table.update.return_value.eq.return_value.execute.return_value = \
            create_mock_supabase_response(data=[updated_project])
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.projects.get_supabase_client', return_value=mock_client):
            response = client.patch(f"/api/v1/projects/{project_id}", json=update_data, headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["target_platforms"] == ["tiktok", "youtube"]
    
    @pytest.mark.unit
    def test_update_project_deactivate(self, client, sample_project):
        """Test deactivating a project."""
        headers = create_auth_headers()
        project_id = sample_project["id"]
        
        update_data = {"is_active": False}
        
        mock_user = create_mock_auth_user()
        updated_project = {**sample_project, "is_active": False}
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            create_mock_supabase_response(data=sample_project)
        mock_table.update.return_value.eq.return_value.execute.return_value = \
            create_mock_supabase_response(data=[updated_project])
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.projects.get_supabase_client', return_value=mock_client):
            response = client.patch(f"/api/v1/projects/{project_id}", json=update_data, headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["is_active"] is False


class TestProjectDelete:
    """Tests for project deletion endpoint."""
    
    @pytest.mark.unit
    def test_delete_project_success(self, client, sample_project):
        """Test successful project deletion (soft delete)."""
        headers = create_auth_headers()
        project_id = sample_project["id"]
        
        mock_user = create_mock_auth_user()
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", {**sample_project, "is_active": False})
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            response = client.delete(f"/api/v1/projects/{project_id}", headers=headers)
            
            assert response.status_code == status.HTTP_204_NO_CONTENT
    
    @pytest.mark.unit
    def test_delete_project_not_found(self, client):
        """Test deleting non-existent project."""
        headers = create_auth_headers()
        project_id = str(uuid4())
        
        mock_user = create_mock_auth_user()
        
        mock_table = MagicMock()
        mock_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = \
            create_mock_supabase_response(data=None)
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.projects.get_supabase_client', return_value=mock_client):
            response = client.delete(f"/api/v1/projects/{project_id}", headers=headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    def test_delete_project_is_soft_delete(self, client, sample_project):
        """Test that delete is soft delete (sets is_active to false)."""
        headers = create_auth_headers()
        project_id = sample_project["id"]
        
        mock_user = create_mock_auth_user()
        
        # Verify update is called with is_active=False
        mock_table = MagicMock()
        mock_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = \
            create_mock_supabase_response(data=[{**sample_project, "is_active": False}])
        
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = Mock(user=mock_user)
        mock_client.table.return_value = mock_table
        
        with patch('app.routers.projects.get_supabase_client', return_value=mock_client):
            response = client.delete(f"/api/v1/projects/{project_id}", headers=headers)
            
            assert response.status_code == status.HTTP_204_NO_CONTENT
            # Verify the update was called
            mock_table.update.assert_called_once()
            call_args = mock_table.update.call_args
            assert call_args[0][0] == {"is_active": False}


class TestProjectValidation:
    """Tests for project input validation."""
    
    @pytest.mark.unit
    def test_create_project_name_too_long(self, client, sample_project):
        """Test creating project with very long name."""
        headers = create_auth_headers()
        
        project_data = {
            "name": "A" * 1000,  # Very long name
            "description": "Description",
        }
        
        mock_user = create_mock_auth_user()
        mock_response = {**sample_project, "name": project_data["name"]}
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", mock_response)
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/projects", json=project_data, headers=headers)
            
            # API accepts any string length, DB would enforce limits
            assert response.status_code == status.HTTP_201_CREATED
    
    @pytest.mark.unit
    def test_create_project_unicode_in_name(self, client, sample_project):
        """Test creating project with unicode characters."""
        headers = create_auth_headers()
        
        project_data = {
            "name": "プロジェクト Project 🔥",
            "description": "Description with émojis 🎉",
        }
        
        mock_user = create_mock_auth_user()
        mock_response = {**sample_project, "name": project_data["name"], "description": project_data["description"]}
        
        builder = MockSupabaseBuilder()
        builder.with_user(mock_user)
        builder.with_table_response("projects", mock_response)
        
        with patch('app.routers.projects.get_supabase_client', return_value=builder.build()):
            response = client.post("/api/v1/projects", json=project_data, headers=headers)
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["name"] == "プロジェクト Project 🔥"

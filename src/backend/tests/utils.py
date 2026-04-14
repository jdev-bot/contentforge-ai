"""
Test utilities and helpers for ContentForge AI tests.
"""

import json
from typing import Dict, Any, Optional
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone


def create_mock_supabase_response(
    data: Optional[Any] = None, error: Optional[str] = None
):
    """
    Create a mock Supabase response.

    Args:
        data: Response data
        error: Error message (if any)

    Returns:
        Mock response object
    """
    response = Mock()
    response.data = data if data is not None else []
    response.error = error
    return response


def create_mock_auth_user(
    user_id: str = None,
    email: str = "test@example.com",
    full_name: str = "Test User",
    is_active: bool = True,
) -> Mock:
    """
    Create a mock authenticated user.

    Args:
        user_id: User ID (auto-generated if None)
        email: User email
        full_name: User's full name
        is_active: Whether user is active

    Returns:
        Mock user object
    """
    user = Mock()
    user.id = user_id or str(uuid4())
    user.email = email
    user.user_metadata = {"full_name": full_name}
    user.is_active = is_active
    return user


def create_mock_auth_session(
    access_token: str = "test-token", user: Mock = None
) -> Mock:
    """
    Create a mock auth session.

    Args:
        access_token: JWT access token
        user: Mock user object

    Returns:
        Mock session object
    """
    session = Mock()
    session.access_token = access_token
    session.user = user or create_mock_auth_user()
    return session


def create_auth_headers(token: str = "test-access-token") -> Dict[str, str]:
    """
    Create authentication headers for API requests.

    Args:
        token: Bearer token

    Returns:
        Headers dictionary
    """
    return {"Authorization": f"Bearer {token}"}


def create_test_project_data(
    name: str = "Test Project",
    description: str = "Test description",
    brand_voice: Optional[Dict] = None,
    target_platforms: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Create test project data.

    Args:
        name: Project name
        description: Project description
        brand_voice: Brand voice configuration
        target_platforms: List of target platforms

    Returns:
        Project data dictionary
    """
    return {
        "name": name,
        "description": description,
        "brand_voice": brand_voice or {"tone": "professional", "style": "concise"},
        "target_platforms": target_platforms or ["twitter", "linkedin"],
    }


def create_test_content_data(
    title: str = "Test Content",
    source_type: str = "text",
    source_url: Optional[str] = None,
    text: Optional[str] = None,
    project_id: str = None,
) -> Dict[str, Any]:
    """
    Create test content data.

    Args:
        title: Content title
        source_type: Type of source (url, youtube, text)
        source_url: Source URL
        text: Raw text content
        project_id: Associated project ID

    Returns:
        Content data dictionary
    """
    return {
        "title": title,
        "project_id": project_id or str(uuid4()),
        "source": {
            "type": source_type,
            "url": source_url,
            "text": text or "This is test content for unit testing.",
        },
    }


def validate_uuid(value: str) -> bool:
    """
    Validate if a string is a valid UUID.

    Args:
        value: String to validate

    Returns:
        True if valid UUID, False otherwise
    """
    try:
        uuid4(value)
        return True
    except (ValueError, TypeError):
        return False


def create_mock_table_chain(return_value: Any = None, single_return: Any = None):
    """
    Create a mock Supabase table query chain.

    Args:
        return_value: Value to return from execute()
        single_return: Value to return from single().execute()

    Returns:
        Mock table object with chainable methods
    """
    mock_table = MagicMock()

    # Set up the chain
    mock_response = create_mock_supabase_response(data=return_value)
    mock_table.execute.return_value = mock_response

    # Single returns different data if specified
    if single_return is not None:
        mock_single_response = create_mock_supabase_response(data=single_return)
        mock_table.single.return_value.execute.return_value = mock_single_response
    else:
        mock_table.single.return_value.execute.return_value = mock_response

    return mock_table


def assert_api_error(
    response, expected_status: int, expected_detail: Optional[str] = None
):
    """
    Assert that an API response is an error.

    Args:
        response: TestClient response
        expected_status: Expected HTTP status code
        expected_detail: Expected error detail message
    """
    assert response.status_code == expected_status
    data = response.json()
    assert "detail" in data
    if expected_detail:
        assert expected_detail in data["detail"]


def assert_api_success(response, expected_status: int = 200):
    """
    Assert that an API response is successful.

    Args:
        response: TestClient response
        expected_status: Expected HTTP status code
    """
    assert response.status_code == expected_status
    data = response.json()
    assert isinstance(data, (dict, list))


class MockSupabaseBuilder:
    """
    Builder pattern for creating complex mock Supabase responses.
    """

    def __init__(self):
        self.client = MagicMock()
        self.auth = MagicMock()
        self.client.auth = self.auth
        self._table_responses = {}

    def with_user(self, user: Mock = None):
        """Set the authenticated user."""
        self.auth.get_user.return_value = Mock(user=user or create_mock_auth_user())
        return self

    def with_sign_up_response(self, user: Mock = None, session: Mock = None):
        """Set sign up response."""
        response = Mock()
        response.user = user or create_mock_auth_user()
        response.session = session or create_mock_auth_session(user=response.user)
        self.auth.sign_up.return_value = response
        return self

    def with_sign_in_response(self, user: Mock = None, session: Mock = None):
        """Set sign in response."""
        response = Mock()
        response.user = user or create_mock_auth_user()
        response.session = session or create_mock_auth_session(user=response.user)
        self.auth.sign_in_with_password.return_value = response
        return self

    def with_table_response(self, table_name: str, data: Any, single: bool = False):
        """Set response for a table query."""
        self._table_responses[table_name] = (data, single)
        return self

    def build(self):
        """Build the mock client."""

        # Set up table method to return configured responses
        def table_side_effect(name):
            mock_table = MagicMock()
            if name in self._table_responses:
                data, single = self._table_responses[name]
                if single:
                    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = create_mock_supabase_response(
                        data=data
                    )
                else:
                    mock_table.select.return_value.execute.return_value = (
                        create_mock_supabase_response(data=data)
                    )
                mock_table.insert.return_value.execute.return_value = (
                    create_mock_supabase_response(
                        data=[data] if not isinstance(data, list) else data
                    )
                )
                mock_table.update.return_value.eq.return_value.execute.return_value = (
                    create_mock_supabase_response(
                        data=[data] if not isinstance(data, list) else data
                    )
                )
                mock_table.delete.return_value.eq.return_value.execute.return_value = (
                    create_mock_supabase_response(data=[])
                )
            return mock_table

        self.client.table = MagicMock(side_effect=table_side_effect)
        return self.client


def freeze_time(timestamp: str = "2024-01-01T00:00:00Z"):
    """
    Context manager to freeze time for tests.

    Args:
        timestamp: ISO format timestamp
    """
    from contextlib import contextmanager
    from unittest.mock import patch

    @contextmanager
    def _freeze():
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = dt
            mock_datetime.now.return_value = dt
            yield

    return _freeze()

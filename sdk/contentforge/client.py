"""
ContentForge AI Python SDK — API Client

Provides a synchronous and asynchronous client for the ContentForge AI API
with API key authentication, content CRUD, AI generation, analytics,
and webhook registration.
"""
import json
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin

import requests

from .models import Content, Project, Asset, Distribution, WebhookEndpoint
from .exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    ContentForgeError,
)


class ContentForgeClient:
    """
    ContentForge AI API client.

    Usage:
        client = ContentForgeClient(api_key="cf-...", base_url="https://api.contentforge.ai")
        content = client.create_content(title="My Post", project_id="...", source=...)
        assets = client.generate_assets(content_id=content.id)

    Args:
        api_key: API key for authentication (starts with "cf-").
        base_url: Base URL of the ContentForge API. Defaults to http://localhost:8000/api/v1.
        timeout: Request timeout in seconds. Defaults to 30.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: int = 30,
    ):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"contentforge-sdk/0.1.0",
        })

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        """Build a full URL from a relative path."""
        return f"{self.base_url}/{path.lstrip('/')}"

    def _handle_response(self, response: requests.Response) -> Any:
        """Process an HTTP response, raising typed exceptions on errors."""
        if 200 <= response.status_code < 300:
            if response.status_code == 204:
                return None
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text

        # Error handling
        try:
            detail = response.json().get("detail", response.text)
        except (json.JSONDecodeError, AttributeError):
            detail = response.text

        if response.status_code == 401:
            raise AuthenticationError(detail)
        elif response.status_code == 404:
            raise NotFoundError(detail)
        elif response.status_code == 422:
            raise ValidationError(detail)
        elif response.status_code == 429:
            raise RateLimitError(detail)
        elif response.status_code >= 500:
            raise ServerError(detail)
        else:
            raise ContentForgeError(f"HTTP {response.status_code}: {detail}")

    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        """Perform a GET request."""
        response = self._session.get(self._url(path), params=params, timeout=self.timeout)
        return self._handle_response(response)

    def _post(self, path: str, data: Optional[Dict] = None) -> Any:
        """Perform a POST request."""
        response = self._session.post(self._url(path), json=data, timeout=self.timeout)
        return self._handle_response(response)

    def _put(self, path: str, data: Optional[Dict] = None) -> Any:
        """Perform a PUT request."""
        response = self._session.put(self._url(path), json=data, timeout=self.timeout)
        return self._handle_response(response)

    def _patch(self, path: str, data: Optional[Dict] = None) -> Any:
        """Perform a PATCH request."""
        response = self._session.patch(self._url(path), json=data, timeout=self.timeout)
        return self._handle_response(response)

    def _delete(self, path: str) -> Any:
        """Perform a DELETE request."""
        response = self._session.delete(self._url(path), timeout=self.timeout)
        return self._handle_response(response)

    # ------------------------------------------------------------------
    # Content CRUD
    # ------------------------------------------------------------------

    def create_content(
        self,
        title: str,
        project_id: str,
        source_type: str = "text",
        source_url: Optional[str] = None,
        original_text: Optional[str] = None,
    ) -> Content:
        """Create a new content item."""
        data = {
            "title": title,
            "project_id": project_id,
            "source": {
                "type": source_type,
                "url": source_url,
                "text": original_text,
            },
        }
        result = self._post("/content", data)
        return Content.from_api(result)

    def list_content(
        self,
        project_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Content]:
        """List content items."""
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if project_id:
            params["project_id"] = project_id
        result = self._get("/content", params=params)
        if isinstance(result, list):
            return [Content.from_api(item) for item in result]
        return [Content.from_api(item) for item in result.get("items", result.get("content", []))]

    def get_content(self, content_id: str) -> Content:
        """Get a content item by ID."""
        result = self._get(f"/content/{content_id}")
        return Content.from_api(result)

    def update_content(self, content_id: str, **kwargs) -> Content:
        """Update a content item."""
        result = self._patch(f"/content/{content_id}", data=kwargs)
        return Content.from_api(result)

    def delete_content(self, content_id: str) -> None:
        """Delete a content item."""
        self._delete(f"/content/{content_id}")

    # ------------------------------------------------------------------
    # AI Generation
    # ------------------------------------------------------------------

    def generate_assets(self, content_id: str) -> List[Asset]:
        """Generate AI assets for a content item."""
        result = self._post(f"/content/{content_id}/generate")
        if isinstance(result, list):
            return [Asset.from_api(item) for item in result]
        return [Asset.from_api(item) for item in result.get("assets", [])]

    def list_assets(self, content_id: str) -> List[Asset]:
        """List generated assets for a content item."""
        result = self._get(f"/content/{content_id}/assets")
        if isinstance(result, list):
            return [Asset.from_api(item) for item in result]
        return [Asset.from_api(item) for item in result.get("assets", [])]

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        """Create a new project."""
        data = {"name": name}
        if description:
            data["description"] = description
        result = self._post("/projects", data)
        return Project.from_api(result)

    def list_projects(self) -> List[Project]:
        """List all projects."""
        result = self._get("/projects")
        if isinstance(result, list):
            return [Project.from_api(item) for item in result]
        return [Project.from_api(item) for item in result.get("projects", [])]

    def get_project(self, project_id: str) -> Project:
        """Get a project by ID."""
        result = self._get(f"/projects/{project_id}")
        return Project.from_api(result)

    def delete_project(self, project_id: str) -> None:
        """Delete a project."""
        self._delete(f"/projects/{project_id}")

    # ------------------------------------------------------------------
    # Distributions
    # ------------------------------------------------------------------

    def create_distribution(
        self,
        asset_id: str,
        platform: str,
        scheduled_at: Optional[str] = None,
    ) -> Distribution:
        """Create a new distribution."""
        data = {"asset_id": asset_id, "platform": platform}
        if scheduled_at:
            data["scheduled_at"] = scheduled_at
        result = self._post("/distributions", data)
        return Distribution.from_api(result)

    def list_distributions(
        self,
        status: Optional[str] = None,
    ) -> List[Distribution]:
        """List distributions."""
        params: Dict[str, Any] = {}
        if status:
            params["status"] = status
        result = self._get("/distributions", params=params)
        if isinstance(result, list):
            return [Distribution.from_api(item) for item in result]
        return [Distribution.from_api(item) for item in result.get("distributions", [])]

    def publish_now(self, distribution_id: str) -> Distribution:
        """Publish a distribution immediately."""
        result = self._post(f"/distributions/{distribution_id}/publish-now")
        return Distribution.from_api(result)

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_content_metrics(self) -> Dict[str, Any]:
        """Get content analytics metrics."""
        return self._get("/analytics/content")

    def get_asset_metrics(self) -> Dict[str, Any]:
        """Get asset analytics metrics."""
        return self._get("/analytics/assets")

    def get_usage_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get usage analytics metrics."""
        return self._get("/analytics/usage", params={"days": days})

    def get_distribution_metrics(self) -> Dict[str, Any]:
        """Get distribution analytics metrics."""
        return self._get("/analytics/distributions")

    def get_dashboard_kpis(self) -> Dict[str, Any]:
        """Get dashboard KPI metrics."""
        return self._get("/analytics/dashboard")

    # ------------------------------------------------------------------
    # Webhooks
    # ------------------------------------------------------------------

    def register_webhook(
        self,
        name: str,
        endpoint_url: str,
        events: Optional[List[str]] = None,
        secret: Optional[str] = None,
    ) -> WebhookEndpoint:
        """Register a webhook endpoint."""
        data = {
            "name": name,
            "endpoint_url": endpoint_url,
        }
        if events:
            data["events"] = events
        if secret:
            data["secret"] = secret
        result = self._post("/webhooks", data)
        return WebhookEndpoint.from_api(result)

    def list_webhooks(self) -> List[WebhookEndpoint]:
        """List registered webhook endpoints."""
        result = self._get("/webhooks")
        if isinstance(result, list):
            return [WebhookEndpoint.from_api(item) for item in result]
        return [WebhookEndpoint.from_api(item) for item in result.get("webhooks", [])]

    def delete_webhook(self, webhook_id: str) -> None:
        """Delete a webhook endpoint."""
        self._delete(f"/webhooks/{webhook_id}")

    # ------------------------------------------------------------------
    # Plugin System
    # ------------------------------------------------------------------

    def list_plugins(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """List plugins in the marketplace."""
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        return self._get("/plugins", params=params)

    def get_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """Get a plugin by ID."""
        return self._get(f"/plugins/{plugin_id}")

    def install_plugin(
        self,
        plugin_id: str,
        organization_id: str,
        custom_config: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Install a plugin for an organization."""
        data = {
            "plugin_id": plugin_id,
            "organization_id": organization_id,
        }
        if custom_config:
            data["custom_config"] = custom_config
        return self._post(f"/organizations/{organization_id}/plugins/install", data)

    def uninstall_plugin(
        self,
        install_id: str,
        organization_id: str,
    ) -> None:
        """Uninstall a plugin from an organization."""
        self._delete(f"/organizations/{organization_id}/plugins/{install_id}")

    def list_installed_plugins(
        self,
        organization_id: str,
        is_enabled: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """List plugins installed for an organization."""
        params: Dict[str, Any] = {}
        if is_enabled is not None:
            params["is_enabled"] = str(is_enabled).lower()
        return self._get(f"/organizations/{organization_id}/plugins", params=params)

    def get_plugin_config(
        self,
        install_id: str,
        organization_id: str,
    ) -> Dict[str, Any]:
        """Get configuration for an installed plugin."""
        return self._get(f"/organizations/{organization_id}/plugins/{install_id}/config")

    def update_plugin_config(
        self,
        install_id: str,
        organization_id: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update configuration for an installed plugin."""
        return self._put(
            f"/organizations/{organization_id}/plugins/{install_id}/config",
            data={"config": config},
        )

    def toggle_plugin(
        self,
        install_id: str,
        organization_id: str,
        is_enabled: bool,
    ) -> Dict[str, Any]:
        """Enable or disable an installed plugin."""
        return self._patch(
            f"/organizations/{organization_id}/plugins/{install_id}/toggle",
            data={"is_enabled": is_enabled},
        )

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def close(self):
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
"""
Plugin router for the ContentForge AI plugin system.
Provides REST API endpoints for plugin registry, installation, configuration,
and lifecycle management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from pydantic import BaseModel, Field

from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.plugin_service import (
    AVAILABLE_HOOKS,
    AVAILABLE_PERMISSIONS,
    PluginHook,
    PluginPermission,
    PluginService,
    get_plugin_service,
)

router = APIRouter()


# ============================================================================
# Request / Response Models
# ============================================================================


class PluginCreate(BaseModel):
    """Request model for registering a new plugin."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Plugin display name"
    )
    slug: Optional[str] = Field(
        None, max_length=255, description="URL-friendly slug (auto-generated from name)"
    )
    description: str = Field(
        default="", max_length=2000, description="Plugin description"
    )
    version: str = Field(
        default="1.0.0", max_length=20, description="Semver version string"
    )
    category: str = Field(
        default="utility",
        description="Plugin category (utility, analytics, distribution, editor, integration)",
    )
    icon_url: Optional[str] = None
    homepage_url: Optional[str] = None
    repository_url: Optional[str] = None
    permissions: List[str] = Field(
        default_factory=list, description="List of permissions the plugin requires"
    )
    hooks: List[str] = Field(
        default_factory=list, description="Lifecycle hooks the plugin subscribes to"
    )
    config_schema: Dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema for plugin configuration"
    )
    default_config: Dict[str, Any] = Field(
        default_factory=dict, description="Default configuration values"
    )
    is_official: bool = Field(
        default=False, description="Whether this is an official ContentForge plugin"
    )
    status: str = Field(
        default="published", description="Publication status: draft or published"
    )


class PluginUpdate(BaseModel):
    """Request model for updating a plugin."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    version: Optional[str] = Field(None, max_length=20)
    category: Optional[str] = None
    icon_url: Optional[str] = None
    homepage_url: Optional[str] = None
    repository_url: Optional[str] = None
    permissions: Optional[List[str]] = None
    hooks: Optional[List[str]] = None
    config_schema: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class PluginResponse(BaseModel):
    """Response model for a plugin in the registry."""

    id: UUID
    name: str
    slug: str
    description: str
    version: str
    category: str
    author_id: UUID
    icon_url: Optional[str] = None
    homepage_url: Optional[str] = None
    repository_url: Optional[str] = None
    permissions: Any
    hooks: Any
    config_schema: Any
    default_config: Any
    is_official: bool
    status: str
    downloads: int
    rating_avg: float
    rating_count: int
    created_at: datetime
    updated_at: datetime


class PluginListResponse(BaseModel):
    """Response for listing plugins in the marketplace."""

    plugins: List[PluginResponse]
    total: int


class PluginInstallRequest(BaseModel):
    """Request model for installing a plugin."""

    plugin_id: UUID
    organization_id: UUID
    custom_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Custom config overrides"
    )


class InstalledPluginResponse(BaseModel):
    """Response model for an installed plugin instance."""

    id: UUID
    plugin_id: UUID
    organization_id: UUID
    installed_by: UUID
    config: Any
    is_enabled: bool
    installed_at: datetime
    updated_at: datetime
    plugin: Optional[PluginResponse] = None


class InstalledPluginListResponse(BaseModel):
    """Response for listing installed plugins."""

    plugins: List[InstalledPluginResponse]
    total: int


class PluginConfigUpdate(BaseModel):
    """Request model for updating plugin configuration."""

    config: Dict[str, Any] = Field(..., description="Full plugin configuration object")


class PluginToggleRequest(BaseModel):
    """Request model for enabling/disabling a plugin."""

    is_enabled: bool


class PluginPermissionsValidation(BaseModel):
    """Response for a permissions validation check."""

    valid: bool
    errors: List[str]


class PluginMetaResponse(BaseModel):
    """Response for available hooks and permissions metadata."""

    hooks: List[Dict[str, str]]
    permissions: List[Dict[str, str]]


# ============================================================================
# Plugin Registry (Marketplace) Endpoints
# ============================================================================


@router.get("/plugins", response_model=PluginListResponse)
async def list_plugins(
    category: Optional[str] = None,
    is_official: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user=Depends(get_auth_user),
):
    """
    List all plugins in the marketplace.

    Query parameters:
    - category: Filter by plugin category
    - is_official: Filter official plugins
    - search: Search plugin names
    - limit: Results per page (1-100)
    - offset: Pagination offset
    """
    service = get_plugin_service()
    result = await service.list_plugins(
        category=category,
        is_official=is_official,
        search=search,
        limit=limit,
        offset=offset,
    )
    return PluginListResponse(**result)


@router.get("/plugins/meta", response_model=PluginMetaResponse)
async def get_plugin_meta(user=Depends(get_auth_user)):
    """Get available plugin hooks and permissions metadata."""
    hooks = [
        {"value": h, "label": h.replace("on_", "").replace("_", " ").title()}
        for h in AVAILABLE_HOOKS
    ]
    permissions = [
        {"value": p, "label": p.replace("_", " ").title()}
        for p in AVAILABLE_PERMISSIONS
    ]
    return PluginMetaResponse(hooks=hooks, permissions=permissions)


@router.get("/plugins/{plugin_id}", response_model=PluginResponse)
async def get_plugin(
    plugin_id: UUID,
    user=Depends(get_auth_user),
):
    """Get a specific plugin by ID."""
    service = get_plugin_service()
    plugin = await service.get_plugin(str(plugin_id))
    if not plugin:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Plugin not found",
        )
    return plugin


@router.post(
    "/plugins", response_model=PluginResponse, status_code=http_status.HTTP_201_CREATED
)
async def create_plugin(
    plugin_data: PluginCreate,
    user=Depends(get_auth_user),
):
    """
    Register a new plugin in the marketplace.

    Validates permissions and hooks before creating.
    """
    service = get_plugin_service()
    user_id = str(user.id)

    # Validate hooks and permissions
    data_dict = plugin_data.model_dump()
    errors = service.validate_permissions(data_dict, plugin_data.hooks)
    if errors:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Permission validation failed: {'; '.join(errors)}",
        )

    try:
        plugin = await service.create_plugin(data_dict, user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    return plugin


@router.put("/plugins/{plugin_id}", response_model=PluginResponse)
async def update_plugin(
    plugin_id: UUID,
    plugin_data: PluginUpdate,
    user=Depends(get_auth_user),
):
    """Update a plugin (only the author can update)."""
    service = get_plugin_service()
    user_id = str(user.id)
    data_dict = plugin_data.model_dump(exclude_none=True)

    try:
        plugin = await service.update_plugin(str(plugin_id), user_id, data_dict)
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )

    return plugin


@router.delete("/plugins/{plugin_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_plugin(
    plugin_id: UUID,
    user=Depends(get_auth_user),
):
    """Delete a plugin from the registry (only the author can delete)."""
    service = get_plugin_service()
    user_id = str(user.id)

    try:
        await service.delete_plugin(str(plugin_id), user_id)
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc))

    return None


# ============================================================================
# Plugin Installation Endpoints
# ============================================================================


@router.get(
    "/organizations/{organization_id}/plugins",
    response_model=InstalledPluginListResponse,
)
async def list_installed_plugins(
    organization_id: UUID,
    is_enabled: Optional[bool] = None,
    user=Depends(get_auth_user),
):
    """
    List all plugins installed for an organization.

    Query parameters:
    - is_enabled: Filter by enabled/disabled status
    """
    service = get_plugin_service()
    plugins = await service.list_installed_plugins(
        str(organization_id),
        is_enabled=is_enabled,
    )
    return InstalledPluginListResponse(plugins=plugins, total=len(plugins))


@router.post(
    "/organizations/{organization_id}/plugins/install",
    response_model=InstalledPluginResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def install_plugin(
    organization_id: UUID,
    install_data: PluginInstallRequest,
    user=Depends(get_auth_user),
):
    """
    Install a plugin for an organization.

    The plugin must be published in the marketplace.
    Organization-scoped configuration can be provided.
    """
    service = get_plugin_service()
    user_id = str(user.id)

    try:
        installed = await service.install_plugin(
            plugin_id=str(install_data.plugin_id),
            organization_id=str(organization_id),
            user_id=user_id,
            custom_config=install_data.custom_config,
        )
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )

    return installed


@router.get(
    "/organizations/{organization_id}/plugins/{install_id}",
    response_model=InstalledPluginResponse,
)
async def get_installed_plugin(
    organization_id: UUID,
    install_id: UUID,
    user=Depends(get_auth_user),
):
    """Get a specific installed plugin instance."""
    service = get_plugin_service()
    installed = await service.get_installed_plugin(
        str(install_id), str(organization_id)
    )
    if not installed:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Installed plugin not found",
        )
    return installed


@router.delete(
    "/organizations/{organization_id}/plugins/{install_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
)
async def uninstall_plugin(
    organization_id: UUID,
    install_id: UUID,
    user=Depends(get_auth_user),
):
    """Uninstall a plugin from an organization."""
    service = get_plugin_service()
    user_id = str(user.id)

    try:
        await service.uninstall_plugin(str(install_id), str(organization_id), user_id)
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc))

    return None


# ============================================================================
# Plugin Configuration Endpoints
# ============================================================================


@router.get("/organizations/{organization_id}/plugins/{install_id}/config")
async def get_plugin_config(
    organization_id: UUID,
    install_id: UUID,
    user=Depends(get_auth_user),
):
    """Get the configuration for an installed plugin."""
    service = get_plugin_service()
    try:
        config = await service.get_plugin_config(str(install_id), str(organization_id))
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc))
    return {"config": config}


@router.put("/organizations/{organization_id}/plugins/{install_id}/config")
async def update_plugin_config(
    organization_id: UUID,
    install_id: UUID,
    config_data: PluginConfigUpdate,
    user=Depends(get_auth_user),
):
    """Update the configuration for an installed plugin."""
    service = get_plugin_service()
    try:
        result = await service.update_plugin_config(
            str(install_id), str(organization_id), config_data.config
        )
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )
    return result


# ============================================================================
# Plugin Enable/Disable Endpoints
# ============================================================================


@router.patch("/organizations/{organization_id}/plugins/{install_id}/toggle")
async def toggle_plugin(
    organization_id: UUID,
    install_id: UUID,
    toggle_data: PluginToggleRequest,
    user=Depends(get_auth_user),
):
    """Enable or disable an installed plugin."""
    service = get_plugin_service()
    try:
        result = await service.toggle_plugin(
            str(install_id), str(organization_id), toggle_data.is_enabled
        )
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )
    return result


# ============================================================================
# Plugin Permissions Validation Endpoint
# ============================================================================


@router.post(
    "/plugins/validate-permissions", response_model=PluginPermissionsValidation
)
async def validate_permissions(
    plugin_data: PluginCreate,
    user=Depends(get_auth_user),
):
    """
    Validate a plugin's declared permissions against its requested hooks.

    Returns whether the permissions are valid and any validation errors.
    """
    service = get_plugin_service()
    errors = service.validate_permissions(plugin_data.model_dump(), plugin_data.hooks)
    return PluginPermissionsValidation(
        valid=len(errors) == 0,
        errors=errors,
    )

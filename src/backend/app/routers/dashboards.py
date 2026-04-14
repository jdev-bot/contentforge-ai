"""
Custom dashboards router with widget management and live data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.dashboard_service import (
    VALID_DATA_SOURCES,
    VALID_REFRESH_INTERVALS,
    VALID_WIDGET_TYPES,
    dashboard_service,
)

router = APIRouter()


# ── Pydantic Models ─────────────────────────────────────────────────


class WidgetConfig(BaseModel):
    """Widget creation/update configuration."""

    widget_type: str = Field(..., description="Type of widget")
    title: str = Field(..., description="Widget title")
    data_source: str = Field(..., description="Data source for widget")
    refresh_interval: int = Field(60, description="Refresh interval in seconds")
    size: Optional[Dict[str, int]] = Field(None, description="Widget size {w, h}")
    position: Optional[int] = Field(None, description="Widget position in grid")
    config: Optional[Dict[str, Any]] = Field(
        None, description="Additional widget config"
    )


class WidgetUpdateConfig(BaseModel):
    """Widget update configuration (all fields optional)."""

    widget_type: Optional[str] = None
    title: Optional[str] = None
    data_source: Optional[str] = None
    refresh_interval: Optional[int] = None
    size: Optional[Dict[str, int]] = None
    position: Optional[int] = None
    config: Optional[Dict[str, Any]] = None


class DashboardCreate(BaseModel):
    """Create a new dashboard."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    layout_config: Optional[Dict[str, Any]] = Field(
        None, description="Layout configuration"
    )
    is_default: bool = False


class DashboardUpdate(BaseModel):
    """Update a dashboard."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    layout_config: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None


# ── Dashboard Endpoints ─────────────────────────────────────────────


@router.get("/dashboards")
async def list_dashboards(user=Depends(get_auth_user)):
    """List all dashboards for the authenticated user."""
    try:
        dashboards = dashboard_service.list_dashboards(user.id)
        return dashboards
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list dashboards: {str(e)}",
        )


@router.post("/dashboards", status_code=status.HTTP_201_CREATED)
async def create_dashboard(dashboard: DashboardCreate, user=Depends(get_auth_user)):
    """Create a new custom dashboard."""
    try:
        result = dashboard_service.create_dashboard(
            user_id=user.id,
            name=dashboard.name,
            description=dashboard.description,
            layout_config=dashboard.layout_config,
            is_default=dashboard.is_default,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dashboard: {str(e)}",
        )


@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(dashboard_id: str, user=Depends(get_auth_user)):
    """Get a dashboard with its widgets."""
    dashboard = dashboard_service.get_dashboard(dashboard_id, user.id)
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )
    return dashboard


@router.put("/dashboards/{dashboard_id}")
async def update_dashboard(
    dashboard_id: str, dashboard: DashboardUpdate, user=Depends(get_auth_user)
):
    """Update a dashboard's name, description, or layout."""
    try:
        result = dashboard_service.update_dashboard(
            dashboard_id=dashboard_id,
            user_id=user.id,
            name=dashboard.name,
            description=dashboard.description,
            layout_config=dashboard.layout_config,
            is_default=dashboard.is_default,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update dashboard: {str(e)}",
        )


@router.delete("/dashboards/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard(dashboard_id: str, user=Depends(get_auth_user)):
    """Delete a dashboard and its widgets."""
    deleted = dashboard_service.delete_dashboard(dashboard_id, user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )


# ── Widget Endpoints ────────────────────────────────────────────────


@router.post("/dashboards/{dashboard_id}/widgets", status_code=status.HTTP_201_CREATED)
async def add_widget(
    dashboard_id: str, widget: WidgetConfig, user=Depends(get_auth_user)
):
    """Add a widget to a dashboard."""
    try:
        if widget.widget_type not in VALID_WIDGET_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid widget type. Valid types: {', '.join(VALID_WIDGET_TYPES)}",
            )
        if widget.data_source not in VALID_DATA_SOURCES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data source. Valid sources: {', '.join(VALID_DATA_SOURCES)}",
            )
        if widget.refresh_interval not in VALID_REFRESH_INTERVALS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid refresh interval. Valid values: {', '.join(str(v) for v in VALID_REFRESH_INTERVALS)}",
            )

        result = dashboard_service.add_widget(
            dashboard_id=dashboard_id,
            user_id=user.id,
            widget_type=widget.widget_type,
            title=widget.title,
            data_source=widget.data_source,
            refresh_interval=widget.refresh_interval,
            size=widget.size,
            position=widget.position or 0,
            config=widget.config,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found",
            )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add widget: {str(e)}",
        )


@router.put("/dashboards/{dashboard_id}/widgets/{widget_id}")
async def update_widget(
    dashboard_id: str,
    widget_id: str,
    widget: WidgetUpdateConfig,
    user=Depends(get_auth_user),
):
    """Update a widget's configuration."""
    try:
        if widget.widget_type and widget.widget_type not in VALID_WIDGET_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid widget type. Valid types: {', '.join(VALID_WIDGET_TYPES)}",
            )
        if widget.data_source and widget.data_source not in VALID_DATA_SOURCES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data source. Valid sources: {', '.join(VALID_DATA_SOURCES)}",
            )
        if (
            widget.refresh_interval
            and widget.refresh_interval not in VALID_REFRESH_INTERVALS
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid refresh interval. Valid values: {', '.join(str(v) for v in VALID_REFRESH_INTERVALS)}",
            )

        result = dashboard_service.update_widget(
            dashboard_id=dashboard_id,
            widget_id=widget_id,
            user_id=user.id,
            widget_type=widget.widget_type,
            title=widget.title,
            data_source=widget.data_source,
            refresh_interval=widget.refresh_interval,
            size=widget.size,
            position=widget.position,
            config=widget.config,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard or widget not found",
            )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update widget: {str(e)}",
        )


@router.delete(
    "/dashboards/{dashboard_id}/widgets/{widget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_widget(dashboard_id: str, widget_id: str, user=Depends(get_auth_user)):
    """Remove a widget from a dashboard."""
    deleted = dashboard_service.delete_widget(dashboard_id, widget_id, user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard or widget not found",
        )


# ── Live Data ──────────────────────────────────────────────────────


@router.get("/dashboards/{dashboard_id}/data")
async def get_dashboard_data(dashboard_id: str, user=Depends(get_auth_user)):
    """Get live data for all widgets in a dashboard."""
    data = dashboard_service.get_dashboard_data(dashboard_id, user.id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )
    return data

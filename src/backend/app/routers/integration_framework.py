"""
Custom Integrations Framework Router for ContentForge AI API.

This router provides endpoints for:
- Managing integration configurations (CRUD)
- Testing integration connections
- Triggering and processing integration events
- Retrying failed events
- Viewing integration logs and health status
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator

from app.services.integration_framework_service import (
    EventStatus, IntegrationType, integration_framework_service)

router = APIRouter()


# ============== Pydantic Models ==============

class IntegrationConfigCreate(BaseModel):
    """Create integration config request model."""
    name: str = Field(..., min_length=1, max_length=255, description="Integration name")
    type: str = Field(..., description="Integration type: webhook, api, polling, streaming")
    provider: str = Field(..., min_length=1, max_length=255, description="Provider name")
    credentials: Dict[str, Any] = Field(default_factory=dict, description="Encrypted credentials")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Integration settings")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = [t.value for t in IntegrationType]
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return v


class IntegrationConfigUpdate(BaseModel):
    """Update integration config request model."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    provider: Optional[str] = Field(None, min_length=1, max_length=255)
    credentials: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = [t.value for t in IntegrationType]
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return v


class IntegrationConfigResponse(BaseModel):
    """Integration config response model."""
    id: str
    user_id: str
    name: str
    type: str
    provider: str
    credentials: Dict[str, Any]
    settings: Dict[str, Any]
    enabled: bool
    created_at: str
    updated_at: str


class IntegrationTestResponse(BaseModel):
    """Integration test result response model."""
    success: bool
    message: str
    latency_ms: int


class IntegrationEventCreate(BaseModel):
    """Trigger integration event request model."""
    event_type: str = Field(..., min_length=1, max_length=255, description="Event type")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload")


class IntegrationEventResponse(BaseModel):
    """Integration event response model."""
    id: str
    user_id: str
    config_id: str
    event_type: str
    payload: Dict[str, Any]
    status: str
    retries: int
    created_at: str


class IntegrationLogResponse(BaseModel):
    """Integration log response model."""
    id: str
    config_id: str
    event_id: Optional[str] = None
    level: str
    message: str
    created_at: str


class IntegrationLogListResponse(BaseModel):
    """Integration log list response model."""
    logs: List[IntegrationLogResponse]
    total: int


class IntegrationStatusResponse(BaseModel):
    """Integration health status response model."""
    config_id: str
    name: str
    type: str
    provider: str
    enabled: bool
    health_status: str
    total_events_24h: int
    completed_events_24h: int
    failed_events_24h: int
    pending_events: int
    last_event_at: Optional[str] = None
    last_log: Optional[Dict[str, Any]] = None


class RetryEventResponse(BaseModel):
    """Retry event response model."""
    success: bool
    message: str
    event: Optional[IntegrationEventResponse] = None


# ============== Dependency ==============

from app.routers.auth import get_auth_user

# ============== Integration Config Endpoints ==============

@router.post("/integration-framework/configs", response_model=IntegrationConfigResponse, status_code=status.HTTP_201_CREATED)
async def register_integration(
    config: IntegrationConfigCreate,
    user=Depends(get_auth_user),
):
    """Register a new integration configuration."""
    try:
        result = await integration_framework_service.register_integration(
            user_id=user.id,
            name=config.name,
            type=config.type,
            provider=config.provider,
            credentials=config.credentials,
            settings=config.settings,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register integration",
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register integration: {str(e)}",
        )


@router.get("/integration-framework/configs", response_model=List[IntegrationConfigResponse])
async def list_integrations(user=Depends(get_auth_user)):
    """List all integration configurations for the current user."""
    try:
        integrations = await integration_framework_service.list_integrations(user_id=user.id)
        return integrations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list integrations: {str(e)}",
        )


@router.put("/integration-framework/configs/{config_id}", response_model=IntegrationConfigResponse)
async def update_integration(
    config_id: UUID,
    updates: IntegrationConfigUpdate,
    user=Depends(get_auth_user),
):
    """Update an existing integration configuration."""
    try:
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )
        result = await integration_framework_service.update_integration(
            config_id=config_id,
            user_id=user.id,
            updates=update_data,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found or you don't have permission",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update integration: {str(e)}",
        )


@router.delete("/integration-framework/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    config_id: UUID,
    user=Depends(get_auth_user),
):
    """Delete an integration configuration."""
    try:
        success = await integration_framework_service.delete_integration(
            config_id=config_id,
            user_id=user.id,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found or you don't have permission",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete integration: {str(e)}",
        )


# ============== Integration Test Endpoint ==============

@router.post("/integration-framework/configs/{config_id}/test", response_model=IntegrationTestResponse)
async def test_integration(
    config_id: UUID,
    user=Depends(get_auth_user),
):
    """Test an integration connection."""
    try:
        result = await integration_framework_service.test_integration(
            config_id=config_id,
            user_id=user.id,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test integration: {str(e)}",
        )


# ============== Integration Event Endpoints ==============

@router.post("/integration-framework/configs/{config_id}/events", response_model=IntegrationEventResponse, status_code=status.HTTP_201_CREATED)
async def trigger_integration_event(
    config_id: UUID,
    event: IntegrationEventCreate,
    user=Depends(get_auth_user),
):
    """Trigger an integration event."""
    try:
        result = await integration_framework_service.trigger_event(
            user_id=user.id,
            config_id=str(config_id),
            event_type=event.event_type,
            payload=event.payload,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found or is disabled",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger integration event: {str(e)}",
        )


@router.post("/integration-framework/events/{event_id}/retry", response_model=RetryEventResponse)
async def retry_failed_event(
    event_id: UUID,
    user=Depends(get_auth_user),
):
    """Retry a failed integration event."""
    try:
        result = await integration_framework_service.retry_failed_event(
            event_id=event_id,
            user_id=user.id,
        )
        if not result:
            return RetryEventResponse(
                success=False,
                message="Event not found, not in failed state, or max retries exceeded",
            )
        return RetryEventResponse(
            success=True,
            message="Event retried successfully",
            event=result,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry event: {str(e)}",
        )


# ============== Integration Logs Endpoint ==============

@router.get("/integration-framework/configs/{config_id}/logs", response_model=IntegrationLogListResponse)
async def get_integration_logs(
    config_id: UUID,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user=Depends(get_auth_user),
):
    """Get integration logs."""
    try:
        logs = await integration_framework_service.get_logs(
            config_id=str(config_id),
            user_id=user.id,
            limit=limit,
            offset=offset,
        )
        return IntegrationLogListResponse(logs=logs, total=len(logs))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration logs: {str(e)}",
        )


# ============== Integration Status Endpoint ==============

@router.get("/integration-framework/configs/{config_id}/status", response_model=IntegrationStatusResponse)
async def get_integration_status(
    config_id: UUID,
    user=Depends(get_auth_user),
):
    """Get integration health status."""
    try:
        result = await integration_framework_service.get_integration_status(
            config_id=str(config_id),
            user_id=user.id,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found or you don't have permission",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration status: {str(e)}",
        )
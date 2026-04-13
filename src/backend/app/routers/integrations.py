"""
Integration router for third-party integrations.
Includes Zapier, webhooks, and WordPress integrations.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Request, BackgroundTasks, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import uuid
import json
import hmac
import hashlib

from app.core.supabase import get_supabase_client, get_supabase_admin_client
from app.routers.auth import get_auth_user
from app.services.integration_services import (
    IntegrationFactory,
    AVAILABLE_EVENT_TYPES,
    BaseIntegrationService
)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class IntegrationCreate(BaseModel):
    """Request model for creating an integration."""
    integration_type: str = Field(..., description="Type: zapier, webhook, wordpress")
    name: str = Field(..., min_length=1, max_length=255, description="Display name")
    config: Dict[str, Any] = Field(default_factory=dict, description="Integration configuration")
    is_active: bool = Field(default=True, description="Whether the integration is active")


class IntegrationUpdate(BaseModel):
    """Request model for updating an integration."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class IntegrationResponse(BaseModel):
    """Response model for an integration."""
    id: UUID
    user_id: UUID
    integration_type: str
    name: str
    config: Dict[str, Any]
    is_active: bool
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class IntegrationListResponse(BaseModel):
    """Response model for listing integrations."""
    integrations: List[IntegrationResponse]
    total: int


class IntegrationTypeInfo(BaseModel):
    """Information about an available integration type."""
    type: str
    name: str
    description: str
    icon: str
    config_schema: Dict[str, Any]


class IntegrationTypesResponse(BaseModel):
    """Response for available integration types."""
    types: List[IntegrationTypeInfo]
    event_types: List[Dict[str, str]]


class IntegrationTestResponse(BaseModel):
    """Response for integration connection test."""
    success: bool
    message: str
    integration_id: UUID


class WebhookDeliveryResponse(BaseModel):
    """Response model for webhook delivery."""
    id: UUID
    webhook_id: UUID
    event_type: str
    status: str
    attempts: int
    response_status: Optional[int] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    error_message: Optional[str] = None


class WebhookDeliveryListResponse(BaseModel):
    """Response for listing webhook deliveries."""
    deliveries: List[WebhookDeliveryResponse]
    total: int
    page: int
    limit: int


class IncomingWebhookPayload(BaseModel):
    """Payload model for incoming webhooks."""
    event_type: str = Field(..., description="Type of event")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")


class IncomingWebhookResponse(BaseModel):
    """Response for incoming webhook."""
    success: bool
    message: str
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    processed_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Integration CRUD Endpoints
# ============================================================================

@router.get("/integrations", response_model=IntegrationListResponse)
async def list_integrations(
    integration_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    user=Depends(get_auth_user)
):
    """
    List all integrations for the current user.
    
    Query parameters:
    - integration_type: Filter by type (zapier, webhook, wordpress)
    - is_active: Filter by active status
    """
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    # Build query
    query = supabase.table("integrations").select("*", count="exact").eq("user_id", user_id)
    
    if integration_type:
        query = query.eq("integration_type", integration_type)
    
    if is_active is not None:
        query = query.eq("is_active", is_active)
    
    # Order by created_at desc
    query = query.order("created_at", desc=True)
    
    result = query.execute()
    
    # Mask sensitive config fields in response
    integrations = []
    for item in result.data or []:
        # Clone config and mask sensitive fields
        masked_config = item.get("config", {}).copy()
        for key in ["secret", "application_password", "api_key", "token", "password"]:
            if key in masked_config:
                masked_config[key] = "***REDACTED***"
        
        integrations.append({
            **item,
            "config": masked_config
        })
    
    return IntegrationListResponse(
        integrations=integrations,
        total=result.count or len(integrations)
    )


@router.get("/integrations/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: UUID,
    user=Depends(get_auth_user)
):
    """Get a specific integration by ID."""
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    result = supabase.table("integrations").select("*").eq("id", str(integration_id)).eq("user_id", user_id).single().execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Mask sensitive config
    data = result.data
    masked_config = data.get("config", {}).copy()
    for key in ["secret", "application_password", "api_key", "token", "password"]:
        if key in masked_config:
            masked_config[key] = "***REDACTED***"
    data["config"] = masked_config
    
    return data


@router.post("/integrations", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_data: IntegrationCreate,
    user=Depends(get_auth_user)
):
    """
    Create a new integration.
    
    Validates the configuration before saving.
    """
    user_id = str(user.id)
    
    # Validate integration type
    try:
        service = IntegrationFactory.create_service(integration_data.integration_type)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Validate config
    is_valid, error_message = await service.validate_config(integration_data.config)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid configuration: {error_message}"
        )
    
    # Create integration
    supabase = get_supabase_client()
    
    new_integration = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "integration_type": integration_data.integration_type,
        "name": integration_data.name,
        "config": integration_data.config,
        "is_active": integration_data.is_active,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("integrations").insert(new_integration).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create integration"
        )
    
    # Mask sensitive config in response
    data = result.data[0]
    masked_config = data.get("config", {}).copy()
    for key in ["secret", "application_password", "api_key", "token", "password"]:
        if key in masked_config:
            masked_config[key] = "***REDACTED***"
    data["config"] = masked_config
    
    return data


@router.put("/integrations/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: UUID,
    integration_data: IntegrationUpdate,
    user=Depends(get_auth_user)
):
    """
    Update an existing integration.
    
    Validates the configuration if provided.
    """
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    # Check integration exists and belongs to user
    existing = supabase.table("integrations").select("*").eq("id", str(integration_id)).eq("user_id", user_id).single().execute()
    
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # If config is being updated, validate it
    if integration_data.config is not None:
        integration_type = existing.data["integration_type"]
        try:
            service = IntegrationFactory.create_service(integration_type)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        is_valid, error_message = await service.validate_config(integration_data.config)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid configuration: {error_message}"
            )
    
    # Build update data
    update_data = {"updated_at": datetime.utcnow().isoformat()}
    
    if integration_data.name is not None:
        update_data["name"] = integration_data.name
    
    if integration_data.config is not None:
        update_data["config"] = integration_data.config
    
    if integration_data.is_active is not None:
        update_data["is_active"] = integration_data.is_active
    
    result = supabase.table("integrations").update(update_data).eq("id", str(integration_id)).eq("user_id", user_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update integration"
        )
    
    # Mask sensitive config in response
    data = result.data[0]
    masked_config = data.get("config", {}).copy()
    for key in ["secret", "application_password", "api_key", "token", "password"]:
        if key in masked_config:
            masked_config[key] = "***REDACTED***"
    data["config"] = masked_config
    
    return data


@router.delete("/integrations/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: UUID,
    user=Depends(get_auth_user)
):
    """Delete an integration."""
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    # Check integration exists and belongs to user
    existing = supabase.table("integrations").select("id").eq("id", str(integration_id)).eq("user_id", user_id).execute()
    
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Delete integration (cascade will handle webhook_deliveries)
    supabase.table("integrations").delete().eq("id", str(integration_id)).eq("user_id", user_id).execute()
    
    return None


# ============================================================================
# Integration Types Endpoint
# ============================================================================

@router.get("/integrations/types", response_model=IntegrationTypesResponse)
async def get_integration_types(user=Depends(get_auth_user)):
    """
    Get available integration types and their configuration schemas.
    
    Returns all supported integration types with their metadata and
    the event types that can trigger webhooks.
    """
    types = IntegrationFactory.get_available_types()
    
    return IntegrationTypesResponse(
        types=types,
        event_types=AVAILABLE_EVENT_TYPES
    )


# ============================================================================
# Integration Test Endpoint
# ============================================================================

@router.post("/integrations/{integration_id}/test", response_model=IntegrationTestResponse)
async def test_integration(
    integration_id: UUID,
    user=Depends(get_auth_user)
):
    """
    Test an integration connection.
    
    Sends a test ping to verify the integration is working correctly.
    """
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    # Get integration
    result = supabase.table("integrations").select("*").eq("id", str(integration_id)).eq("user_id", user_id).single().execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    integration = result.data
    
    # Skip if inactive
    if not integration.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot test inactive integration. Please activate it first."
        )
    
    # Create service and test connection
    try:
        service = IntegrationFactory.create_service(
            integration["integration_type"],
            integration_id=str(integration_id),
            config=integration["config"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    success, message = await service.test_connection()
    
    # Update last_used_at timestamp
    if success:
        supabase.table("integrations").update({
            "last_used_at": datetime.utcnow().isoformat()
        }).eq("id", str(integration_id)).execute()
    
    return IntegrationTestResponse(
        success=success,
        message=message or ("Connection successful" if success else "Connection failed"),
        integration_id=integration_id
    )


# ============================================================================
# Incoming Webhook Endpoint
# ============================================================================

@router.post("/webhooks/incoming/{token}", response_model=IncomingWebhookResponse)
async def incoming_webhook(
    token: str,
    payload: IncomingWebhookPayload,
    request: Request,
    x_signature: Optional[str] = Header(None, alias="X-Webhook-Signature"),
    background_tasks: BackgroundTasks = None
):
    """
    Receive incoming webhook from external systems.
    
    The token identifies the integration. Supports signature verification
    if the integration has a secret configured.
    """
    supabase = get_supabase_admin_client()
    
    # Find integration by token (stored in config)
    # Note: In production, consider a separate tokens table for better security
    result = supabase.table("integrations").select("*").eq("config->>incoming_token", token).eq("is_active", True).execute()
    
    if not result.data:
        # Also check for a token field
        result = supabase.table("integrations").select("*").eq("config->>token", token).eq("is_active", True).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or inactive webhook token"
            )
    
    integration = result.data[0]
    config = integration.get("config", {})
    
    # Verify signature if secret is configured
    secret = config.get("incoming_secret") or config.get("secret")
    if secret:
        body = await request.body()
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not x_signature or not hmac.compare_digest(expected_sig, x_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
    
    # Process the incoming webhook based on event type
    event_type = payload.event_type
    event_data = payload.data
    
    # Log the incoming webhook
    try:
        supabase.table("webhook_deliveries").insert({
            "id": str(uuid.uuid4()),
            "webhook_id": integration["id"],
            "event_type": f"incoming.{event_type}",
            "payload": event_data,
            "status": "delivered",
            "attempts": 1,
            "delivered_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"[Incoming Webhook] Failed to log delivery: {e}")
    
    # Update last_used_at
    supabase.table("integrations").update({
        "last_used_at": datetime.utcnow().isoformat()
    }).eq("id", integration["id"]).execute()
    
    return IncomingWebhookResponse(
        success=True,
        message=f"Received {event_type} event from {integration['integration_type']}",
        event_id=str(uuid.uuid4())
    )


# ============================================================================
# Webhook Delivery Endpoints
# ============================================================================

@router.get("/integrations/{integration_id}/deliveries", response_model=WebhookDeliveryListResponse)
async def list_webhook_deliveries(
    integration_id: UUID,
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    user=Depends(get_auth_user)
):
    """
    List webhook deliveries for an integration.
    
    Query parameters:
    - status: Filter by status (pending, delivered, failed, retrying)
    - event_type: Filter by event type
    - page: Page number (default: 1)
    - limit: Items per page (default: 50, max: 100)
    """
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    # Check integration exists and belongs to user
    integration = supabase.table("integrations").select("id").eq("id", str(integration_id)).eq("user_id", user_id).execute()
    
    if not integration.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Limit page size
    limit = min(limit, 100)
    offset = (page - 1) * limit
    
    # Build query
    query = supabase.table("webhook_deliveries").select("*", count="exact").eq("webhook_id", str(integration_id))
    
    if status:
        query = query.eq("status", status)
    
    if event_type:
        query = query.eq("event_type", event_type)
    
    # Order by created_at desc
    query = query.order("created_at", desc=True)
    
    # Pagination
    query = query.range(offset, offset + limit - 1)
    
    result = query.execute()
    
    return WebhookDeliveryListResponse(
        deliveries=result.data or [],
        total=result.count or 0,
        page=page,
        limit=limit
    )


@router.post("/integrations/{integration_id}/deliveries/{delivery_id}/retry")
async def retry_webhook_delivery(
    integration_id: UUID,
    delivery_id: UUID,
    user=Depends(get_auth_user)
):
    """
    Retry a failed webhook delivery.
    
    Only deliveries with status 'failed' can be retried.
    """
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    # Check integration exists and belongs to user
    integration = supabase.table("integrations").select("*").eq("id", str(integration_id)).eq("user_id", user_id).single().execute()
    
    if not integration.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Get the failed delivery
    delivery = supabase.table("webhook_deliveries").select("*").eq("id", str(delivery_id)).eq("webhook_id", str(integration_id)).single().execute()
    
    if not delivery.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    if delivery.data["status"] not in ["failed", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot retry delivery with status '{delivery.data['status']}'"
        )
    
    # Reset status to pending and increment attempts
    supabase.table("webhook_deliveries").update({
        "status": "pending",
        "attempts": delivery.data["attempts"] + 1,
        "error_message": None
    }).eq("id", str(delivery_id)).execute()
    
    # TODO: Trigger actual retry via background task
    # For now, just return success
    
    return {"success": True, "message": "Delivery queued for retry"}


# ============================================================================
# Trigger Integration Event (for testing/manual triggers)
# ============================================================================

@router.post("/integrations/{integration_id}/trigger")
async def trigger_integration_event(
    integration_id: UUID,
    event_type: str,
    payload: Dict[str, Any],
    user=Depends(get_auth_user)
):
    """
    Manually trigger an integration event.
    
    Useful for testing or manual automation.
    """
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    # Get integration
    result = supabase.table("integrations").select("*").eq("id", str(integration_id)).eq("user_id", user_id).single().execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    integration = result.data
    
    if not integration.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration is not active"
        )
    
    # Create service and send event
    try:
        service = IntegrationFactory.create_service(
            integration["integration_type"],
            integration_id=str(integration_id),
            config=integration["config"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    success, message = await service.send_event(event_type, payload)
    
    # Update last_used_at
    if success:
        supabase.table("integrations").update({
            "last_used_at": datetime.utcnow().isoformat()
        }).eq("id", str(integration_id)).execute()
    
    return {
        "success": success,
        "message": message or ("Event sent successfully" if success else "Failed to send event"),
        "event_type": event_type,
        "integration_id": str(integration_id)
    }

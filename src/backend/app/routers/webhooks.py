"""
Webhook endpoints for n8n integration and external system callbacks.
"""
from fastapi import APIRouter, Header, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import uuid

from app.core.supabase import get_supabase_client, get_supabase_admin_client
from app.routers.auth import get_auth_user

router = APIRouter()


class ContentProcessedPayload(BaseModel):
    """Payload for content-processed webhook."""
    content_id: UUID
    status: str  # "completed", "failed"
    extracted_text: Optional[str] = None
    word_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class DistributionCompletedPayload(BaseModel):
    """Payload for distribution-completed webhook."""
    distribution_id: UUID
    status: str  # "published", "failed", "cancelled"
    platform: str
    published_url: Optional[str] = None
    external_id: Optional[str] = None
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WebhookResponse(BaseModel):
    """Webhook response model."""
    success: bool
    message: str
    webhook_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    processed_at: datetime = Field(default_factory=datetime.utcnow)


def verify_webhook_secret(request: Request) -> bool:
    """Verify webhook request has valid secret."""
    # Get webhook secret from header
    webhook_secret = request.headers.get("x-webhook-secret")
    
    # In production, compare against configured secret
    # For now, we accept any secret for testing
    # TODO: Implement proper secret verification from config
    expected_secret = getattr(get_settings(), 'N8N_WEBHOOK_SECRET', None)
    
    if expected_secret:
        return webhook_secret == expected_secret
    
    # If no secret configured, accept all (for development)
    return True


@router.post("/webhooks/n8n/content-processed", response_model=WebhookResponse)
async def content_processed_webhook(
    payload: ContentProcessedPayload,
    request: Request,
    x_n8n_signature: Optional[str] = Header(None),
    x_webhook_secret: Optional[str] = Header(None),
):
    """
    Webhook endpoint for n8n to notify when content processing is complete.
    
    This is called after n8n workflows finish processing content
    (e.g., transcription from audio, summarization, etc.).
    
    Headers:
    - x-n8n-signature: Optional signature for verification
    - x-webhook-secret: Webhook secret for authentication
    
    Payload:
    - content_id: UUID of the content being processed
    - status: "completed" or "failed"
    - extracted_text: The processed content text
    - word_count: Word count of the processed content
    - metadata: Additional metadata from processing
    - error_message: Error details if failed
    """
    # Verify webhook secret (optional in development)
    if not verify_webhook_secret(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret",
        )
    
    supabase = get_supabase_client()
    
    try:
        # Update content record with processing results
        update_data = {
            "status": payload.status,
            "updated_at": datetime.utcnow().isoformat(),
            "n8n_processed_at": datetime.utcnow().isoformat(),
        }
        
        if payload.extracted_text:
            update_data["original_text"] = payload.extracted_text
            update_data["word_count"] = payload.word_count or len(payload.extracted_text.split())
        
        if payload.metadata:
            # Merge with existing metadata
            current = supabase.table("content").select("metadata").eq("id", str(payload.content_id)).execute()
            if current.data and current.data[0].get("metadata"):
                existing = current.data[0]["metadata"]
                existing.update(payload.metadata)
                update_data["metadata"] = existing
            else:
                update_data["metadata"] = payload.metadata
        
        if payload.error_message:
            update_data["error_message"] = payload.error_message
            update_data["status"] = "failed"
        
        result = supabase.table("content").update(update_data).eq(
            "id", str(payload.content_id)
        ).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            )
        
        return WebhookResponse(
            success=True,
            message=f"Content {payload.content_id} processing completed",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}",
        )


@router.post("/webhooks/n8n/distribution-completed", response_model=WebhookResponse)
async def distribution_completed_webhook(
    payload: DistributionCompletedPayload,
    request: Request,
    x_n8n_signature: Optional[str] = Header(None),
    x_webhook_secret: Optional[str] = Header(None),
):
    """
    Webhook endpoint for n8n to notify when distribution is complete.
    
    This is called after n8n workflows finish publishing content
    to external platforms (Twitter, LinkedIn, etc.).
    
    Headers:
    - x-n8n-signature: Optional signature for verification
    - x-webhook-secret: Webhook secret for authentication
    
    Payload:
    - distribution_id: UUID of the distribution
    - status: "published", "failed", or "cancelled"
    - platform: Platform where content was published
    - published_url: URL of the published content
    - external_id: External platform's ID for the post
    - published_at: When the content was published
    - error_message: Error details if failed
    - metadata: Additional metadata from the platform
    """
    # Verify webhook secret (optional in development)
    if not verify_webhook_secret(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret",
        )
    
    supabase = get_supabase_client()
    
    try:
        # Update distribution record
        update_data = {
            "status": payload.status,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        if payload.published_url:
            update_data["published_url"] = payload.published_url
        
        if payload.external_id:
            update_data["external_id"] = payload.external_id
        
        if payload.published_at:
            update_data["published_at"] = payload.published_at.isoformat()
        elif payload.status == "published":
            update_data["published_at"] = datetime.utcnow().isoformat()
        
        if payload.error_message:
            update_data["error_message"] = payload.error_message
        
        if payload.metadata:
            # Merge with existing metadata
            current = supabase.table("distributions").select("metadata").eq("id", str(payload.distribution_id)).execute()
            if current.data and current.data[0].get("metadata"):
                existing = current.data[0]["metadata"]
                existing.update(payload.metadata)
                update_data["metadata"] = existing
            else:
                update_data["metadata"] = payload.metadata
        
        result = supabase.table("distributions").update(update_data).eq(
            "id", str(payload.distribution_id)
        ).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Distribution not found",
            )
        
        return WebhookResponse(
            success=True,
            message=f"Distribution {payload.distribution_id} completed with status: {payload.status}",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}",
        )


# Webhook configuration endpoints for admin

class WebhookConfig(BaseModel):
    """Webhook configuration model."""
    webhook_url: str
    secret: Optional[str] = None
    events: List[str]
    is_active: bool = True


@router.get("/webhooks/config", response_model=Dict[str, Any])
async def get_webhook_config(
    user=Depends(get_auth_user)
):
    """
    Get webhook configuration for the current user.
    
    Returns webhook URLs and configuration settings.
    """
    from app.core.config import get_settings
    settings = get_settings()
    
    return {
        "webhooks": {
            "content_processed": {
                "url": f"/api/v1/webhooks/n8n/content-processed",
                "method": "POST",
                "description": "Called when content processing is complete",
            },
            "distribution_completed": {
                "url": f"/api/v1/webhooks/n8n/distribution-completed",
                "method": "POST",
                "description": "Called when distribution is complete",
            },
        },
        "base_url": getattr(settings, 'API_BASE_URL', 'https://api.contentforge.ai'),
    }


# Trigger webhook endpoints (for testing)

@router.post("/webhooks/test/content/{content_id}")
async def test_content_webhook(
    content_id: UUID,
    user=Depends(get_auth_user)
):
    """
    Test the content-processed webhook.
    
    Simulates n8n calling the webhook with test data.
    """
    test_payload = {
        "content_id": str(content_id),
        "status": "completed",
        "extracted_text": "This is test content from the webhook simulation.",
        "word_count": 9,
        "metadata": {
            "test": True,
            "source": "webhook_test_endpoint",
        }
    }
    
    return {
        "message": "Test webhook payload prepared",
        "payload": test_payload,
        "endpoint": "/api/v1/webhooks/n8n/content-processed",
    }


@router.post("/webhooks/test/distribution/{distribution_id}")
async def test_distribution_webhook(
    distribution_id: UUID,
    user=Depends(get_auth_user)
):
    """
    Test the distribution-completed webhook.
    
    Simulates n8n calling the webhook with test data.
    """
    test_payload = {
        "distribution_id": str(distribution_id),
        "status": "published",
        "platform": "twitter",
        "published_url": "https://twitter.com/test/status/123456789",
        "external_id": "123456789",
        "metadata": {
            "test": True,
            "source": "webhook_test_endpoint",
        }
    }
    
    return {
        "message": "Test webhook payload prepared",
        "payload": test_payload,
        "endpoint": "/api/v1/webhooks/n8n/distribution-completed",
    }


import uuid
from app.core.config import get_settings

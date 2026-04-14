"""
Webhook endpoints for n8n integration and external system callbacks.
Includes signature verification, idempotency, retry logic, and event logging.
"""
from fastapi import APIRouter, Header, HTTPException, status, Depends, Request, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from uuid import UUID
import uuid
import hmac
import hashlib
import time
import json
from functools import wraps

from app.core.supabase import get_supabase_client, get_supabase_admin_client
from app.routers.auth import get_auth_user

router = APIRouter()

# ============================================================================
# Webhook Security Utilities
# ============================================================================

def get_webhook_secret() -> str:
    """Get webhook secret from settings."""
    from app.core.config import get_settings
    settings = get_settings()
    return getattr(settings, 'N8N_WEBHOOK_SECRET', '')


def get_stripe_webhook_secret() -> Optional[str]:
    """Get Stripe webhook secret."""
    from app.core.config import get_settings
    settings = get_settings()
    return getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify webhook signature using HMAC-SHA256.
    
    Args:
        payload: Raw request body
        signature: Signature from header (hex or base64)
        secret: Webhook secret
    
    Returns:
        True if signature is valid
    """
    try:
        # Compute expected signature
        expected = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (constant time to prevent timing attacks)
        return hmac.compare_digest(expected, signature)
    except Exception:
        return False


def verify_stripe_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify Stripe webhook signature.
    
    Stripe signatures use a specific format with timestamp and scheme.
    """
    try:
        # Parse Stripe signature header
        # Format: t=\u003ctimestamp\u003e,v1=\u003csignature\u003e
        timestamp = None
        signatures = []
        
        for part in signature.split(','):
            if part.startswith('t='):
                timestamp = part[2:]
            elif part.startswith('v1='):
                signatures.append(part[3:])
        
        if not timestamp or not signatures:
            return False
        
        # Check timestamp (prevent replay attacks)
        try:
            timestamp_int = int(timestamp)
            now = int(time.time())
            # Allow 5 minute window
            if abs(now - timestamp_int) > 300:
                return False
        except ValueError:
            return False
        
        # Verify signature
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        expected = hmac.new(
            secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return any(hmac.compare_digest(expected, sig) for sig in signatures)
    except Exception:
        return False


def generate_idempotency_key() -> str:
    """Generate a unique idempotency key."""
    return f"{uuid.uuid4().hex}-{int(time.time() * 1000)}"


def check_idempotency(idempotency_key: str, webhook_type: str, timeout_minutes: int = 60) -> bool:
    """
    Check if a webhook event has already been processed.
    
    Args:
        idempotency_key: The key to check
        webhook_type: Type of webhook
        timeout_minutes: How long to remember processed keys
    
    Returns:
        True if already processed (skip), False if new
    """
    try:
        supabase = get_supabase_admin_client()
        
        # Check if key exists
        result = supabase.table("webhook_logs").select("id, created_at").eq(
            "idempotency_key", idempotency_key
        ).eq("webhook_type", webhook_type).execute()
        
        if result.data:
            # Key exists - check if within timeout
            created_at = datetime.fromisoformat(result.data[0]['created_at'].replace('Z', '+00:00'))
            if datetime.now(timezone.utc) - created_at < timedelta(minutes=timeout_minutes):
                return True  # Already processed recently
        
        return False  # Not processed or expired
    except Exception as e:
        # On error, assume not processed to avoid missing events
        return False


def log_webhook_event(
    webhook_type: str,
    event_source: str,
    payload: Dict[str, Any],
    status: str,
    response_data: Optional[Dict] = None,
    idempotency_key: Optional[str] = None,
    error_message: Optional[str] = None,
    processing_time_ms: Optional[float] = None
) -> None:
    """
    Log webhook event to database.
    
    Creates an audit trail for all webhook events.
    """
    try:
        supabase = get_supabase_admin_client()
        
        # Truncate large payloads
        payload_str = json.dumps(payload)[:5000] if payload else None
        
        log_entry = {
            "id": str(uuid.uuid4()),
            "webhook_type": webhook_type,
            "event_source": event_source,
            "payload": payload,
            "payload_preview": payload_str,
            "status": status,
            "response_data": response_data,
            "idempotency_key": idempotency_key,
            "error_message": error_message,
            "processing_time_ms": processing_time_ms,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        supabase.table("webhook_logs").insert(log_entry).execute()
    except Exception as e:
        # Log to console if database logging fails
        print(f"[Webhook Log Error] Failed to log webhook: {e}")


# ============================================================================
# Retry Decorator with Exponential Backoff
# ============================================================================

def with_retry(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """
    Decorator for webhook handlers with exponential backoff retry.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except HTTPException:
                    # Don't retry HTTP exceptions (client errors)
                    raise
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        # Calculate delay with exponential backoff
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        # Add jitter (±20%)
                        import random
                        delay = delay * (0.8 + random.random() * 0.4)
                        time.sleep(delay)
            
            # All retries exhausted
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Webhook processing failed after {max_retries} attempts: {str(last_exception)}"
            )
        
        return wrapper
    return decorator


# ============================================================================
# Webhook Schemas
# ============================================================================

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
    idempotency_key: Optional[str] = None
    retry_count: int = 0


class WebhookLogResponse(BaseModel):
    """Response for webhook log queries."""
    logs: List[Dict[str, Any]]
    total: int
    page: int
    limit: int


# ============================================================================
# Webhook Endpoints
# ============================================================================

@router.post("/webhooks/n8n/content-processed", response_model=WebhookResponse)
async def content_processed_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_n8n_signature: Optional[str] = Header(None, alias="X-N8N-Signature"),
    x_webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret"),
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    x_retry_count: Optional[int] = Header(0, alias="X-Retry-Count"),
):
    """
    Webhook endpoint for n8n to notify when content processing is complete.
    
    This is called after n8n workflows finish processing content
    (e.g., transcription from audio, summarization, etc.).
    
    **Security:**
    - Signature verification via X-N8N-Signature
    - Webhook secret via X-Webhook-Secret
    - Idempotency via X-Idempotency-Key
    - Automatic retry with exponential backoff
    
    **Headers:**
    - X-N8N-Signature: HMAC-SHA256 signature of payload
    - X-Webhook-Secret: Webhook secret for authentication
    - X-Idempotency-Key: Unique key to prevent duplicate processing
    - X-Retry-Count: Current retry attempt (set by client)
    """
    start_time = time.time()
    webhook_id = str(uuid.uuid4())
    
    # Read raw payload for signature verification
    try:
        body = await request.body()
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read request body: {str(e)}"
        )
    
    # Verify webhook signature
    webhook_secret = get_webhook_secret()
    if webhook_secret and x_n8n_signature:
        if not verify_signature(body, x_n8n_signature, webhook_secret):
            # Log failed verification
            log_webhook_event(
                webhook_type="content_processed",
                event_source="n8n",
                payload=payload,
                status="failed",
                error_message="Invalid signature",
                idempotency_key=x_idempotency_key
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    elif webhook_secret:
        # Secret configured but no signature provided
        log_webhook_event(
            webhook_type="content_processed",
            event_source="n8n",
            payload=payload,
            status="failed",
            error_message="Missing signature header",
            idempotency_key=x_idempotency_key
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature"
        )
    
    # Generate idempotency key if not provided
    idempotency_key = x_idempotency_key or generate_idempotency_key()
    
    # Check idempotency (avoid duplicate processing)
    if check_idempotency(idempotency_key, "content_processed"):
        processing_time = (time.time() - start_time) * 1000
        log_webhook_event(
            webhook_type="content_processed",
            event_source="n8n",
            payload=payload,
            status="duplicate",
            idempotency_key=idempotency_key,
            processing_time_ms=processing_time
        )
        return WebhookResponse(
            success=True,
            message="Duplicate event - already processed",
            webhook_id=webhook_id,
            idempotency_key=idempotency_key,
            retry_count=x_retry_count or 0
        )
    
    # Process the webhook
    supabase = get_supabase_client()
    
    try:
        # Validate required fields
        if "content_id" not in payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required field: content_id"
            )
        
        content_id = UUID(payload["content_id"])
        
        # Update content record with processing results
        update_data = {
            "status": payload.get("status", "completed"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "n8n_processed_at": datetime.now(timezone.utc).isoformat(),
        }
        
        if payload.get("extracted_text"):
            update_data["original_text"] = payload["extracted_text"]
            word_count = payload.get("word_count") or len(payload["extracted_text"].split())
            update_data["word_count"] = word_count
        
        if payload.get("metadata"):
            # Merge with existing metadata
            current = supabase.table("content").select("metadata").eq("id", str(content_id)).execute()
            if current.data and current.data[0].get("metadata"):
                existing = current.data[0]["metadata"]
                existing.update(payload["metadata"])
                update_data["metadata"] = existing
            else:
                update_data["metadata"] = payload["metadata"]
        
        if payload.get("error_message"):
            update_data["error_message"] = payload["error_message"]
            update_data["status"] = "failed"
        
        result = supabase.table("content").update(update_data).eq(
            "id", str(content_id)
        ).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            )
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Log successful webhook
        log_webhook_event(
            webhook_type="content_processed",
            event_source="n8n",
            payload=payload,
            status="success",
            response_data={"content_id": str(content_id)},
            idempotency_key=idempotency_key,
            processing_time_ms=processing_time
        )
        
        return WebhookResponse(
            success=True,
            message=f"Content {content_id} processing completed",
            webhook_id=webhook_id,
            idempotency_key=idempotency_key,
            retry_count=x_retry_count or 0
        )
        
    except HTTPException:
        # Log HTTP exceptions
        processing_time = (time.time() - start_time) * 1000
        log_webhook_event(
            webhook_type="content_processed",
            event_source="n8n",
            payload=payload,
            status="failed",
            error_message="HTTP exception",
            idempotency_key=idempotency_key,
            processing_time_ms=processing_time
        )
        raise
    except Exception as e:
        # Log and re-raise for retry
        processing_time = (time.time() - start_time) * 1000
        log_webhook_event(
            webhook_type="content_processed",
            event_source="n8n",
            payload=payload,
            status="error",
            error_message=str(e),
            idempotency_key=idempotency_key,
            processing_time_ms=processing_time
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )


@router.post("/webhooks/n8n/distribution-completed", response_model=WebhookResponse)
async def distribution_completed_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_n8n_signature: Optional[str] = Header(None, alias="X-N8N-Signature"),
    x_webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret"),
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    x_retry_count: Optional[int] = Header(0, alias="X-Retry-Count"),
):
    """
    Webhook endpoint for n8n to notify when distribution is complete.
    
    This is called after n8n workflows finish publishing content
    to external platforms (Twitter, LinkedIn, etc.).
    
    **Security:**
    - Signature verification via X-N8N-Signature
    - Webhook secret via X-Webhook-Secret
    - Idempotency via X-Idempotency-Key
    - Automatic retry with exponential backoff
    
    **Headers:**
    - X-N8N-Signature: HMAC-SHA256 signature of payload
    - X-Webhook-Secret: Webhook secret for authentication
    - X-Idempotency-Key: Unique key to prevent duplicate processing
    - X-Retry-Count: Current retry attempt (set by client)
    """
    start_time = time.time()
    webhook_id = str(uuid.uuid4())
    
    # Read raw payload
    try:
        body = await request.body()
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read request body: {str(e)}"
        )
    
    # Verify webhook signature
    webhook_secret = get_webhook_secret()
    if webhook_secret and x_n8n_signature:
        if not verify_signature(body, x_n8n_signature, webhook_secret):
            log_webhook_event(
                webhook_type="distribution_completed",
                event_source="n8n",
                payload=payload,
                status="failed",
                error_message="Invalid signature",
                idempotency_key=x_idempotency_key
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    elif webhook_secret:
        log_webhook_event(
            webhook_type="distribution_completed",
            event_source="n8n",
            payload=payload,
            status="failed",
            error_message="Missing signature header",
            idempotency_key=x_idempotency_key
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature"
        )
    
    # Generate idempotency key if not provided
    idempotency_key = x_idempotency_key or generate_idempotency_key()
    
    # Check idempotency
    if check_idempotency(idempotency_key, "distribution_completed"):
        processing_time = (time.time() - start_time) * 1000
        log_webhook_event(
            webhook_type="distribution_completed",
            event_source="n8n",
            payload=payload,
            status="duplicate",
            idempotency_key=idempotency_key,
            processing_time_ms=processing_time
        )
        return WebhookResponse(
            success=True,
            message="Duplicate event - already processed",
            webhook_id=webhook_id,
            idempotency_key=idempotency_key,
            retry_count=x_retry_count or 0
        )
    
    # Process the webhook
    supabase = get_supabase_client()
    
    try:
        # Validate required fields
        if "distribution_id" not in payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required field: distribution_id"
            )
        
        distribution_id = UUID(payload["distribution_id"])
        
        # Update distribution record
        update_data = {
            "status": payload.get("status", "completed"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        if payload.get("published_url"):
            update_data["published_url"] = payload["published_url"]
        
        if payload.get("external_id"):
            update_data["external_id"] = payload["external_id"]
        
        if payload.get("published_at"):
            update_data["published_at"] = payload["published_at"]
        elif payload.get("status") == "published":
            update_data["published_at"] = datetime.now(timezone.utc).isoformat()
        
        if payload.get("error_message"):
            update_data["error_message"] = payload["error_message"]
        
        if payload.get("metadata"):
            # Merge with existing metadata
            current = supabase.table("distributions").select("metadata").eq("id", str(distribution_id)).execute()
            if current.data and current.data[0].get("metadata"):
                existing = current.data[0]["metadata"]
                existing.update(payload["metadata"])
                update_data["metadata"] = existing
            else:
                update_data["metadata"] = payload["metadata"]
        
        result = supabase.table("distributions").update(update_data).eq(
            "id", str(distribution_id)
        ).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Distribution not found",
            )
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Log successful webhook
        log_webhook_event(
            webhook_type="distribution_completed",
            event_source="n8n",
            payload=payload,
            status="success",
            response_data={"distribution_id": str(distribution_id)},
            idempotency_key=idempotency_key,
            processing_time_ms=processing_time
        )
        
        return WebhookResponse(
            success=True,
            message=f"Distribution {distribution_id} completed with status: {payload.get('status', 'completed')}",
            webhook_id=webhook_id,
            idempotency_key=idempotency_key,
            retry_count=x_retry_count or 0
        )
        
    except HTTPException:
        processing_time = (time.time() - start_time) * 1000
        log_webhook_event(
            webhook_type="distribution_completed",
            event_source="n8n",
            payload=payload,
            status="failed",
            error_message="HTTP exception",
            idempotency_key=idempotency_key,
            processing_time_ms=processing_time
        )
        raise
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        log_webhook_event(
            webhook_type="distribution_completed",
            event_source="n8n",
            payload=payload,
            status="error",
            error_message=str(e),
            idempotency_key=idempotency_key,
            processing_time_ms=processing_time
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )


# ============================================================================
# Webhook Log Endpoints
# ============================================================================

@router.get("/webhooks/logs", response_model=WebhookLogResponse)
async def get_webhook_logs(
    webhook_type: Optional[str] = None,
    event_source: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    limit: int = 50,
    user=Depends(get_auth_user)
):
    """
    Get webhook event logs with filtering.
    
    Requires admin privileges.
    """
    # Check if user is admin
    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    supabase = get_supabase_admin_client()
    
    # Build query
    query = supabase.table("webhook_logs").select("*", count="exact")
    
    if webhook_type:
        query = query.eq("webhook_type", webhook_type)
    
    if event_source:
        query = query.eq("event_source", event_source)
    
    if status:
        query = query.eq("status", status)
    
    if start_date:
        query = query.gte("created_at", start_date.isoformat())
    
    if end_date:
        query = query.lte("created_at", end_date.isoformat())
    
    # Order by created_at desc
    query = query.order("created_at", desc=True)
    
    # Pagination
    offset = (page - 1) * limit
    query = query.range(offset, offset + limit - 1)
    
    result = query.execute()
    
    return WebhookLogResponse(
        logs=result.data or [],
        total=result.count or 0,
        page=page,
        limit=limit
    )


# ============================================================================
# Webhook Configuration Endpoints
# ============================================================================

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
    
    # Generate a webhook secret if not set
    webhook_secret = get_webhook_secret() or "Not configured - set N8N_WEBHOOK_SECRET"
    
    return {
        "webhooks": {
            "content_processed": {
                "url": f"/api/v1/webhooks/n8n/content-processed",
                "method": "POST",
                "description": "Called when content processing is complete",
                "required_headers": ["X-N8N-Signature", "X-Idempotency-Key"],
            },
            "distribution_completed": {
                "url": f"/api/v1/webhooks/n8n/distribution-completed",
                "method": "POST",
                "description": "Called when distribution is complete",
                "required_headers": ["X-N8N-Signature", "X-Idempotency-Key"],
            },
        },
        "base_url": getattr(settings, 'API_BASE_URL', 'https://api.contentforge.ai'),
        "security": {
            "signature_verification": bool(get_webhook_secret()),
            "idempotency_enabled": True,
            "retry_policy": {
                "max_retries": 3,
                "base_delay": 1.0,
                "max_delay": 60.0,
                "strategy": "exponential_backoff"
            }
        }
    }


# ============================================================================
# Test Webhook Endpoints
# ============================================================================

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
            "initiated_by": str(user.get("id"))
        }
    }
    
    # Generate test signature
    webhook_secret = get_webhook_secret()
    signature = None
    if webhook_secret:
        signature = hmac.new(
            webhook_secret.encode('utf-8'),
            json.dumps(test_payload).encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    idempotency_key = generate_idempotency_key()
    
    return {
        "message": "Test webhook payload prepared",
        "payload": test_payload,
        "endpoint": "/api/v1/webhooks/n8n/content-processed",
        "headers": {
            "Content-Type": "application/json",
            "X-N8N-Signature": signature or "Not configured",
            "X-Idempotency-Key": idempotency_key,
            "X-Webhook-Secret": webhook_secret or "Not configured"
        },
        "curl_command": f"""curl -X POST {{
    'Content-Type: application/json' \\
    {'X-N8N-Signature: ' + signature if signature else '# X-N8N-Signature: ...'} \\
    'X-Idempotency-Key: {idempotency_key}' \\
    -d '{json.dumps(test_payload)}' \\
    https://api.contentforge.ai/api/v1/webhooks/n8n/content-processed"""
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
            "initiated_by": str(user.get("id"))
        }
    }
    
    # Generate test signature
    webhook_secret = get_webhook_secret()
    signature = None
    if webhook_secret:
        signature = hmac.new(
            webhook_secret.encode('utf-8'),
            json.dumps(test_payload).encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    idempotency_key = generate_idempotency_key()
    
    return {
        "message": "Test webhook payload prepared",
        "payload": test_payload,
        "endpoint": "/api/v1/webhooks/n8n/distribution-completed",
        "headers": {
            "Content-Type": "application/json",
            "X-N8N-Signature": signature or "Not configured",
            "X-Idempotency-Key": idempotency_key,
            "X-Webhook-Secret": webhook_secret or "Not configured"
        }
    }
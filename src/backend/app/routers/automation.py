"""
Automation Rules router for auto-generate, auto-publish, webhook triggers, and scheduling.
"""
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.rate_limit import (UsageStats, check_and_increment_usage,
                                 enforce_subscription_limit)
from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user

router = APIRouter()


class TriggerType(str, Enum):
    CONTENT_CREATED = "content_created"
    CONTENT_UPDATED = "content_updated"
    SCHEDULED_TIME = "scheduled_time"
    WEBHOOK_RECEIVED = "webhook_received"
    USAGE_THRESHOLD = "usage_threshold"
    MANUAL = "manual"


class ActionType(str, Enum):
    GENERATE_ASSETS = "generate_assets"
    PUBLISH_CONTENT = "publish_content"
    SEND_EMAIL = "send_email"
    CALL_WEBHOOK = "call_webhook"
    UPDATE_STATUS = "update_status"
    CREATE_TASK = "create_task"


class AutomationRuleStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class ScheduleConfig(BaseModel):
    frequency: str = Field(..., description="once, hourly, daily, weekly, monthly, custom")
    cron_expression: Optional[str] = None
    run_at: Optional[datetime] = None
    timezone: str = "UTC"
    days_of_week: Optional[List[int]] = None  # 0=Sunday, 6=Saturday
    times_of_day: Optional[List[str]] = None  # ["09:00", "15:00"]


class WebhookConfig(BaseModel):
    url: str
    method: str = "POST"
    headers: Optional[Dict[str, str]] = None
    payload_template: Optional[str] = None
    secret: Optional[str] = None


class ConditionConfig(BaseModel):
    field: str
    operator: str  # eq, neq, gt, lt, contains, starts_with, ends_with
    value: Any


class AutomationRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: Optional[UUID] = None
    trigger_type: TriggerType
    trigger_config: Optional[Dict[str, Any]] = None
    conditions: Optional[List[ConditionConfig]] = None
    action_type: ActionType
    action_config: Dict[str, Any]
    schedule_config: Optional[ScheduleConfig] = None
    webhook_config: Optional[WebhookConfig] = None
    enabled: bool = True


class AutomationRuleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    project_id: Optional[UUID] = None
    user_id: UUID
    trigger_type: str
    trigger_config: Optional[Dict[str, Any]] = None
    conditions: Optional[List[ConditionConfig]] = None
    action_type: str
    action_config: Dict[str, Any]
    schedule_config: Optional[ScheduleConfig] = None
    webhook_config: Optional[WebhookConfig] = None
    status: str
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    created_at: datetime
    updated_at: datetime


class AutomationLogResponse(BaseModel):
    id: UUID
    rule_id: UUID
    user_id: UUID
    status: str  # running, completed, failed
    triggered_by: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    created_at: datetime


class WebhookEndpointCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: Optional[UUID] = None
    secret: Optional[str] = None
    allowed_ips: Optional[List[str]] = None


class WebhookEndpointResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    project_id: Optional[UUID] = None
    user_id: UUID
    endpoint_url: str
    secret: Optional[str] = None
    allowed_ips: Optional[List[str]] = None
    is_active: bool = True
    total_calls: int = 0
    last_called_at: Optional[datetime] = None
    created_at: datetime


class QueueItemResponse(BaseModel):
    id: UUID
    user_id: UUID
    content_id: UUID
    asset_id: Optional[UUID] = None
    platform: str
    status: str  # pending, scheduled, processing, published, failed
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime


# ============ Automation Rules CRUD ============

@router.post("/automation/rules", response_model=AutomationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_automation_rule(
    rule_data: AutomationRuleCreate,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """Create a new automation rule."""
    usage_stats = check_and_increment_usage(str(user.id))
    
    supabase = get_supabase_client()
    
    try:
        # Calculate next_run_at if scheduled
        next_run_at = None
        if rule_data.trigger_type == TriggerType.SCHEDULED_TIME and rule_data.schedule_config:
            if rule_data.schedule_config.frequency == "once" and rule_data.schedule_config.run_at:
                next_run_at = rule_data.schedule_config.run_at
            elif rule_data.schedule_config.frequency == "hourly":
                next_run_at = datetime.now(timezone.utc) + timedelta(hours=1)
            elif rule_data.schedule_config.frequency == "daily":
                next_run_at = datetime.now(timezone.utc) + timedelta(days=1)
        
        rule_record = {
            "name": rule_data.name,
            "description": rule_data.description,
            "project_id": str(rule_data.project_id) if rule_data.project_id else None,
            "user_id": str(user.id),
            "trigger_type": rule_data.trigger_type.value,
            "trigger_config": rule_data.trigger_config,
            "conditions": [c.model_dump() for c in rule_data.conditions] if rule_data.conditions else None,
            "action_type": rule_data.action_type.value,
            "action_config": rule_data.action_config,
            "schedule_config": rule_data.schedule_config.model_dump() if rule_data.schedule_config else None,
            "webhook_config": rule_data.webhook_config.model_dump() if rule_data.webhook_config else None,
            "status": AutomationRuleStatus.ACTIVE.value if rule_data.enabled else AutomationRuleStatus.PAUSED.value,
            "next_run_at": next_run_at.isoformat() if next_run_at else None,
            "run_count": 0,
            "success_count": 0,
            "fail_count": 0,
        }
        
        result = supabase.table("automation_rules").insert(rule_record).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create automation rule",
            )
        
        return AutomationRuleResponse(**result.data[0])
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/automation/rules", response_model=List[AutomationRuleResponse])
async def list_automation_rules(
    project_id: Optional[UUID] = None,
    status: Optional[str] = None,
    trigger_type: Optional[str] = None,
    user=Depends(get_auth_user)
):
    """List all automation rules for the user."""
    supabase = get_supabase_client()
    
    try:
        query = supabase.table("automation_rules").select("*").eq("user_id", str(user.id))
        
        if project_id:
            query = query.eq("project_id", str(project_id))
        if status:
            query = query.eq("status", status)
        if trigger_type:
            query = query.eq("trigger_type", trigger_type)
        
        query = query.order("created_at", desc=True)
        result = query.execute()
        
        return [AutomationRuleResponse(**r) for r in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/automation/rules/{rule_id}", response_model=AutomationRuleResponse)
async def get_automation_rule(
    rule_id: UUID,
    user=Depends(get_auth_user)
):
    """Get a specific automation rule."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("automation_rules").select("*").eq("id", str(rule_id)).eq("user_id", str(user.id)).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation rule not found",
            )
        
        return AutomationRuleResponse(**result.data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.patch("/automation/rules/{rule_id}", response_model=AutomationRuleResponse)
async def update_automation_rule(
    rule_id: UUID,
    rule_data: AutomationRuleCreate,
    user=Depends(get_auth_user)
):
    """Update an automation rule."""
    supabase = get_supabase_client()
    
    try:
        # Check rule exists
        existing = supabase.table("automation_rules").select("id").eq("id", str(rule_id)).eq("user_id", str(user.id)).single().execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation rule not found",
            )
        
        update_data = {
            "name": rule_data.name,
            "description": rule_data.description,
            "trigger_type": rule_data.trigger_type.value,
            "trigger_config": rule_data.trigger_config,
            "conditions": [c.model_dump() for c in rule_data.conditions] if rule_data.conditions else None,
            "action_type": rule_data.action_type.value,
            "action_config": rule_data.action_config,
            "schedule_config": rule_data.schedule_config.model_dump() if rule_data.schedule_config else None,
            "webhook_config": rule_data.webhook_config.model_dump() if rule_data.webhook_config else None,
            "updated_at": "now()",
        }
        
        result = supabase.table("automation_rules").update(update_data).eq("id", str(rule_id)).execute()
        
        return AutomationRuleResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/automation/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation_rule(
    rule_id: UUID,
    user=Depends(get_auth_user)
):
    """Delete an automation rule."""
    supabase = get_supabase_client()
    
    try:
        # Check rule exists
        existing = supabase.table("automation_rules").select("id").eq("id", str(rule_id)).eq("user_id", str(user.id)).single().execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation rule not found",
            )
        
        # Delete associated logs first
        supabase.table("automation_logs").delete().eq("rule_id", str(rule_id)).execute()
        
        # Delete the rule
        supabase.table("automation_rules").delete().eq("id", str(rule_id)).execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/automation/rules/{rule_id}/toggle")
async def toggle_automation_rule(
    rule_id: UUID,
    user=Depends(get_auth_user)
):
    """Toggle automation rule status (active/paused)."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("automation_rules").select("status").eq("id", str(rule_id)).eq("user_id", str(user.id)).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation rule not found",
            )
        
        current_status = result.data["status"]
        new_status = AutomationRuleStatus.PAUSED.value if current_status == AutomationRuleStatus.ACTIVE.value else AutomationRuleStatus.ACTIVE.value
        
        update_result = supabase.table("automation_rules").update({"status": new_status}).eq("id", str(rule_id)).execute()
        
        return {"status": new_status, "rule_id": str(rule_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/automation/rules/{rule_id}/run")
async def run_automation_rule(
    rule_id: UUID,
    background_tasks: BackgroundTasks,
    user=Depends(get_auth_user)
):
    """Manually trigger an automation rule."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("automation_rules").select("*").eq("id", str(rule_id)).eq("user_id", str(user.id)).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation rule not found",
            )
        
        rule = result.data
        
        # Create log entry
        log_data = {
            "rule_id": str(rule_id),
            "user_id": str(user.id),
            "status": "running",
            "triggered_by": "manual",
            "input_data": {"manual_trigger": True},
        }
        
        log_result = supabase.table("automation_logs").insert(log_data).execute()
        log_id = log_result.data[0]["id"]
        
        # Execute the action in background
        background_tasks.add_task(execute_automation_action, rule, log_id, str(user.id), supabase)
        
        return {"message": "Automation rule triggered", "log_id": str(log_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============ Automation Logs ============

@router.get("/automation/logs", response_model=List[AutomationLogResponse])
async def list_automation_logs(
    rule_id: Optional[UUID] = None,
    status: Optional[str] = None,
    limit: int = 50,
    user=Depends(get_auth_user)
):
    """List automation execution logs."""
    supabase = get_supabase_client()
    
    try:
        query = supabase.table("automation_logs").select("*").eq("user_id", str(user.id))
        
        if rule_id:
            query = query.eq("rule_id", str(rule_id))
        if status:
            query = query.eq("status", status)
        
        query = query.order("created_at", desc=True).limit(limit)
        result = query.execute()
        
        return [AutomationLogResponse(**l) for l in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============ Webhook Endpoints ============

@router.post("/automation/webhooks", response_model=WebhookEndpointResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook_endpoint(
    webhook_data: WebhookEndpointCreate,
    user=Depends(get_auth_user)
):
    """Create a new webhook endpoint for receiving external triggers."""
    supabase = get_supabase_client()
    
    try:
        # Generate unique endpoint path
        import uuid as uuid_module
        webhook_uuid = uuid_module.uuid4()
        endpoint_path = f"/webhooks/incoming/{webhook_uuid}"
        
        webhook_record = {
            "name": webhook_data.name,
            "description": webhook_data.description,
            "project_id": str(webhook_data.project_id) if webhook_data.project_id else None,
            "user_id": str(user.id),
            "endpoint_url": endpoint_path,
            "secret": webhook_data.secret,
            "allowed_ips": webhook_data.allowed_ips,
            "is_active": True,
            "total_calls": 0,
        }
        
        result = supabase.table("webhook_endpoints").insert(webhook_record).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create webhook endpoint",
            )
        
        return WebhookEndpointResponse(**result.data[0])
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/automation/webhooks", response_model=List[WebhookEndpointResponse])
async def list_webhook_endpoints(
    user=Depends(get_auth_user)
):
    """List all webhook endpoints."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("webhook_endpoints").select("*").eq("user_id", str(user.id)).order("created_at", desc=True).execute()
        
        return [WebhookEndpointResponse(**w) for w in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/automation/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook_endpoint(
    webhook_id: UUID,
    user=Depends(get_auth_user)
):
    """Delete a webhook endpoint."""
    supabase = get_supabase_client()
    
    try:
        existing = supabase.table("webhook_endpoints").select("id").eq("id", str(webhook_id)).eq("user_id", str(user.id)).single().execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook endpoint not found",
            )
        
        supabase.table("webhook_endpoints").delete().eq("id", str(webhook_id)).execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============ Publishing Queue ============

@router.get("/automation/queue", response_model=List[QueueItemResponse])
async def get_publishing_queue(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    user=Depends(get_auth_user)
):
    """Get the publishing queue for the user."""
    supabase = get_supabase_client()
    
    try:
        query = supabase.table("publishing_queue").select("*").eq("user_id", str(user.id))
        
        if status:
            query = query.eq("status", status)
        if platform:
            query = query.eq("platform", platform)
        
        query = query.order("scheduled_for", desc=True)
        result = query.execute()
        
        return [QueueItemResponse(**q) for q in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/automation/queue/{queue_id}/cancel")
async def cancel_queue_item(
    queue_id: UUID,
    user=Depends(get_auth_user)
):
    """Cancel a scheduled publish."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("publishing_queue").update({
            "status": "cancelled",
            "updated_at": "now()"
        }).eq("id", str(queue_id)).eq("user_id", str(user.id)).eq("status", "pending").execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue item not found or already processed",
            )
        
        return {"message": "Queue item cancelled", "queue_id": str(queue_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/automation/queue/{queue_id}/retry")
async def retry_queue_item(
    queue_id: UUID,
    user=Depends(get_auth_user)
):
    """Retry a failed queue item."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("publishing_queue").update({
            "status": "pending",
            "error_message": None,
            "retry_count": 0,
            "updated_at": "now()"
        }).eq("id", str(queue_id)).eq("user_id", str(user.id)).eq("status", "failed").execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue item not found or not in failed status",
            )
        
        return {"message": "Queue item queued for retry", "queue_id": str(queue_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============ Smart Scheduling ============

@router.get("/automation/best-times/{platform}")
async def get_best_posting_times(
    platform: str,
    user=Depends(get_auth_user)
):
    """Get AI-suggested best times to post for a platform based on engagement data."""
    supabase = get_supabase_client()
    
    try:
        # Get user's past distribution data for this platform
        result = supabase.table("distributions").select("published_at, engagement_rate").eq("user_id", str(user.id)).eq("platform", platform).not_.is_("published_at", "null").execute()
        
        # Default suggestions based on industry standards
        default_times = {
            "twitter": ["09:00", "12:00", "15:00", "18:00"],
            "linkedin": ["08:00", "12:00", "17:00"],
            "facebook": ["09:00", "13:00", "15:00"],
            "instagram": ["11:00", "14:00", "19:00"],
            "tiktok": ["07:00", "12:00", "19:00", "21:00"],
        }
        
        best_times = default_times.get(platform.lower(), ["09:00", "15:00"])
        
        return {
            "platform": platform,
            "best_times": best_times,
            "timezone_recommendation": "Consider your audience's timezone",
            "frequency_recommendation": "1-2 posts per day for optimal engagement",
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/automation/schedule/bulk")
async def bulk_schedule_content(
    content_ids: List[UUID],
    platform: str,
    start_time: datetime,
    interval_minutes: int = 60,
    user=Depends(get_auth_user)
):
    """Bulk schedule content with intervals."""
    supabase = get_supabase_client()
    
    try:
        queue_items = []
        current_time = start_time
        
        for content_id in content_ids:
            queue_item = {
                "user_id": str(user.id),
                "content_id": str(content_id),
                "platform": platform,
                "status": "scheduled",
                "scheduled_for": current_time.isoformat(),
            }
            queue_items.append(queue_item)
            current_time += timedelta(minutes=interval_minutes)
        
        result = supabase.table("publishing_queue").insert(queue_items).execute()
        
        return {
            "scheduled_count": len(result.data),
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(minutes=interval_minutes * (len(content_ids) - 1))).isoformat(),
            "queue_items": [str(item["id"]) for item in result.data],
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============ Helper Functions ============

async def execute_automation_action(rule: Dict[str, Any], log_id: str, user_id: str, supabase):
    """Execute an automation action and update the log."""
    import time
    start_time = time.time()
    
    try:
        action_type = rule.get("action_type")
        action_config = rule.get("action_config", {})
        
        # Execute based on action type
        if action_type == ActionType.GENERATE_ASSETS.value:
            # Trigger asset generation
            pass
        elif action_type == ActionType.PUBLISH_CONTENT.value:
            # Trigger content publish
            pass
        elif action_type == ActionType.SEND_EMAIL.value:
            # Send email notification
            pass
        elif action_type == ActionType.CALL_WEBHOOK.value:
            # Call external webhook
            pass
        elif action_type == ActionType.UPDATE_STATUS.value:
            # Update content status
            pass
        elif action_type == ActionType.CREATE_TASK.value:
            # Create task
            pass
        
        # Update log as completed
        execution_time = int((time.time() - start_time) * 1000)
        supabase.table("automation_logs").update({
            "status": "completed",
            "output_data": {"success": True},
            "execution_time_ms": execution_time,
        }).eq("id", log_id).execute()
        
        # Update rule stats
        supabase.table("automation_rules").update({
            "last_run_at": "now()",
            "run_count": rule.get("run_count", 0) + 1,
            "success_count": rule.get("success_count", 0) + 1,
        }).eq("id", rule["id"]).execute()
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        supabase.table("automation_logs").update({
            "status": "failed",
            "error_message": str(e),
            "execution_time_ms": execution_time,
        }).eq("id", log_id).execute()
        
        supabase.table("automation_rules").update({
            "last_run_at": "now()",
            "run_count": rule.get("run_count", 0) + 1,
            "fail_count": rule.get("fail_count", 0) + 1,
        }).eq("id", rule["id"]).execute()
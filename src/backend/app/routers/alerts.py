"""
Alerts Router for Content Performance Monitoring API.

This router provides endpoints for:
- Managing content performance alerts
- Creating and managing alert rules
- Acknowledging and resolving alerts
- Getting unread alert counts
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator

from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.alert_service import (
    alert_service,
    AlertType,
    AlertStatus,
    MetricName,
    AlertOperator,
)

router = APIRouter()


# ============== Pydantic Models ==============

class AlertResponse(BaseModel):
    """Alert response model."""
    id: str
    user_id: str
    alert_type: str
    content_id: Optional[str] = None
    metric_name: str
    threshold_value: float
    current_value: float
    status: str
    message: Optional[str] = None
    created_at: str
    acknowledged_at: Optional[str] = None


class AlertListResponse(BaseModel):
    """Alert list response model."""
    alerts: List[AlertResponse]
    total: int
    limit: int
    offset: int


class AlertRuleCreate(BaseModel):
    """Create alert rule request model."""
    name: str = Field(..., min_length=1, max_length=255, description="Rule name")
    alert_type: str = Field(..., description="Alert type: viral, declining, milestone, error")
    metric_name: str = Field(..., description="Metric: views, engagement, clicks, shares, comments, likes")
    operator: str = Field(..., description="Operator: greater_than, less_than, equals, percentage_change")
    threshold_value: float = Field(..., gt=0, description="Threshold value")
    notification_channels: List[str] = Field(
        default=["in_app"],
        description="Notification channels: in_app, email, slack"
    )

    @field_validator("alert_type")
    @classmethod
    def validate_alert_type(cls, v):
        allowed = ["viral", "declining", "milestone", "error"]
        if v not in allowed:
            raise ValueError(f"alert_type must be one of {allowed}")
        return v

    @field_validator("metric_name")
    @classmethod
    def validate_metric_name(cls, v):
        allowed = ["views", "engagement", "clicks", "shares", "comments", "likes"]
        if v not in allowed:
            raise ValueError(f"metric_name must be one of {allowed}")
        return v

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v):
        allowed = ["greater_than", "less_than", "equals", "percentage_change"]
        if v not in allowed:
            raise ValueError(f"operator must be one of {allowed}")
        return v

    @field_validator("notification_channels")
    @classmethod
    def validate_channels(cls, v):
        allowed = ["in_app", "email", "slack"]
        for channel in v:
            if channel not in allowed:
                raise ValueError(f"notification_channels must only contain {allowed}")
        return v


class AlertRuleUpdate(BaseModel):
    """Update alert rule request model."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    alert_type: Optional[str] = None
    metric_name: Optional[str] = None
    operator: Optional[str] = None
    threshold_value: Optional[float] = Field(None, gt=0)
    is_enabled: Optional[bool] = None
    notification_channels: Optional[List[str]] = None

    @field_validator("alert_type")
    @classmethod
    def validate_alert_type(cls, v):
        if v is None:
            return v
        allowed = ["viral", "declining", "milestone", "error"]
        if v not in allowed:
            raise ValueError(f"alert_type must be one of {allowed}")
        return v

    @field_validator("metric_name")
    @classmethod
    def validate_metric_name(cls, v):
        if v is None:
            return v
        allowed = ["views", "engagement", "clicks", "shares", "comments", "likes"]
        if v not in allowed:
            raise ValueError(f"metric_name must be one of {allowed}")
        return v

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v):
        if v is None:
            return v
        allowed = ["greater_than", "less_than", "equals", "percentage_change"]
        if v not in allowed:
            raise ValueError(f"operator must be one of {allowed}")
        return v

    @field_validator("notification_channels")
    @classmethod
    def validate_channels(cls, v):
        if v is None:
            return v
        allowed = ["in_app", "email", "slack"]
        for channel in v:
            if channel not in allowed:
                raise ValueError(f"notification_channels must only contain {allowed}")
        return v


class AlertRuleResponse(BaseModel):
    """Alert rule response model."""
    id: str
    user_id: str
    name: str
    alert_type: str
    metric_name: str
    operator: str
    threshold_value: float
    is_enabled: bool
    notification_channels: List[str]
    created_at: str
    updated_at: str


class AlertRuleListResponse(BaseModel):
    """Alert rule list response model."""
    rules: List[AlertRuleResponse]
    total: int


class AcknowledgeAlertRequest(BaseModel):
    """Acknowledge alert request model."""
    pass


class AcknowledgeAlertResponse(BaseModel):
    """Acknowledge alert response model."""
    success: bool
    message: str


class UnreadCountResponse(BaseModel):
    """Unread count response model."""
    unread_count: int


class CheckMetricsRequest(BaseModel):
    """Check metrics request model."""
    content_id: UUID
    metrics: dict = Field(..., description="Metrics dictionary (views, engagement, clicks, etc.)")


class CheckMetricsResponse(BaseModel):
    """Check metrics response model."""
    triggered_alerts: List[AlertResponse]
    message: str


class InAppNotificationResponse(BaseModel):
    """In-app notification response model."""
    id: str
    user_id: str
    alert_id: Optional[str] = None
    title: str
    message: str
    type: str
    is_read: bool
    created_at: str
    read_at: Optional[str] = None


class NotificationListResponse(BaseModel):
    """Notification list response model."""
    notifications: List[InAppNotificationResponse]
    total: int
    unread_count: int


# ============== Alert Endpoints ==============

@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(
    status: Optional[str] = Query(None, description="Filter by status: active, acknowledged, resolved"),
    alert_type: Optional[str] = Query(None, description="Filter by type: viral, declining, milestone, error"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    user=Depends(get_auth_user),
):
    """
    List content performance alerts for the current user.

    Returns alerts sorted by created_at in descending order (newest first).
    Can be filtered by status and alert type.
    """
    # Validate status filter
    if status and status not in ["active", "acknowledged", "resolved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status filter. Must be one of: active, acknowledged, resolved"
        )

    # Validate alert_type filter
    if alert_type and alert_type not in ["viral", "declining", "milestone", "error"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid alert_type filter. Must be one of: viral, declining, milestone, error"
        )

    try:
        alerts = await alert_service.get_user_alerts(
            user_id=user.id,
            status=status,
            alert_type=alert_type,
            limit=limit,
            offset=offset
        )

        # Get total count for pagination
        supabase = get_supabase_client()
        query = supabase.table("content_alerts").select("id", count="exact").eq("user_id", str(user.id))
        if status:
            query = query.eq("status", status)
        if alert_type:
            query = query.eq("alert_type", alert_type)
        count_result = query.execute()
        total = count_result.count or 0

        return AlertListResponse(
            alerts=alerts,
            total=total,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alerts: {str(e)}"
        )


@router.post("/alerts/acknowledge/{alert_id}", response_model=AcknowledgeAlertResponse)
async def acknowledge_alert(
    alert_id: UUID,
    user=Depends(get_auth_user),
):
    """
    Acknowledge a content performance alert.

    Acknowledged alerts remain visible but are marked as seen by the user.
    """
    try:
        success = await alert_service.acknowledge_alert(alert_id, user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found or you don't have permission"
            )

        return AcknowledgeAlertResponse(
            success=True,
            message="Alert acknowledged successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )


@router.post("/alerts/resolve/{alert_id}", response_model=AcknowledgeAlertResponse)
async def resolve_alert(
    alert_id: UUID,
    user=Depends(get_auth_user),
):
    """
    Mark an alert as resolved.

    Resolved alerts are considered closed and no longer require attention.
    """
    try:
        success = await alert_service.resolve_alert(alert_id, user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found or you don't have permission"
            )

        return AcknowledgeAlertResponse(
            success=True,
            message="Alert resolved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve alert: {str(e)}"
        )


@router.get("/alerts/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(user=Depends(get_auth_user)):
    """
    Get the count of active (unread) alerts for the current user.

    Useful for showing a notification badge in the UI.
    """
    try:
        count = await alert_service.get_unread_alert_count(user.id)
        return UnreadCountResponse(unread_count=count)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )


# ============== Alert Rules Endpoints ==============

@router.get("/alerts/rules", response_model=AlertRuleListResponse)
async def list_alert_rules(
    is_enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    user=Depends(get_auth_user),
):
    """
    List alert rules for the current user.

    Returns all alert rules created by the user, optionally filtered by enabled status.
    """
    try:
        rules = await alert_service.get_alert_rules(
            user_id=user.id,
            is_enabled=is_enabled
        )

        return AlertRuleListResponse(
            rules=rules,
            total=len(rules)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alert rules: {str(e)}"
        )


@router.post("/alerts/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    rule: AlertRuleCreate,
    user=Depends(get_auth_user),
):
    """
    Create a new alert rule.

    Alert rules define conditions for when alerts should be triggered based on content metrics.
    """
    try:
        created_rule = await alert_service.create_alert_rule(
            user_id=user.id,
            name=rule.name,
            alert_type=rule.alert_type,
            metric_name=rule.metric_name,
            operator=rule.operator,
            threshold_value=rule.threshold_value,
            notification_channels=rule.notification_channels
        )

        if not created_rule:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create alert rule"
            )

        return created_rule

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert rule: {str(e)}"
        )


@router.put("/alerts/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: UUID,
    updates: AlertRuleUpdate,
    user=Depends(get_auth_user),
):
    """
    Update an existing alert rule.

    Only the rule owner can update their rules.
    """
    try:
        update_data = updates.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        updated_rule = await alert_service.update_alert_rule(
            rule_id=rule_id,
            user_id=user.id,
            updates=update_data
        )

        if not updated_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert rule not found or you don't have permission"
            )

        return updated_rule

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alert rule: {str(e)}"
        )


@router.delete("/alerts/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
    rule_id: UUID,
    user=Depends(get_auth_user),
):
    """
    Delete an alert rule.

    Only the rule owner can delete their rules. This action is permanent.
    """
    try:
        success = await alert_service.delete_alert_rule(rule_id, user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert rule not found or you don't have permission"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete alert rule: {str(e)}"
        )


# ============== Metrics Check Endpoint ==============

@router.post("/alerts/check-metrics", response_model=CheckMetricsResponse)
async def check_metrics(
    request: CheckMetricsRequest,
    user=Depends(get_auth_user),
):
    """
    Check content metrics against alert rules and thresholds.

    This endpoint is typically called by background jobs or webhooks when new metrics
    are available. It evaluates all rules and automatic detection algorithms.
    """
    try:
        triggered = await alert_service.check_content_metrics(
            content_id=request.content_id,
            user_id=user.id,
            metrics=request.metrics
        )

        return CheckMetricsResponse(
            triggered_alerts=triggered,
            message=f"Checked metrics. {len(triggered)} alert(s) triggered."
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check metrics: {str(e)}"
        )


# ============== In-App Notifications Endpoints ==============

@router.get("/alerts/notifications", response_model=NotificationListResponse)
async def list_notifications(
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    limit: int = Query(50, ge=1, le=100),
    user=Depends(get_auth_user),
):
    """
    List in-app notifications for the current user.

    Returns notifications sorted by creation time (newest first).
    """
    try:
        notifications = await alert_service.get_in_app_notifications(
            user_id=user.id,
            is_read=is_read,
            limit=limit
        )

        # Get unread count
        unread_count = await alert_service.get_unread_alert_count(user.id)

        return NotificationListResponse(
            notifications=notifications,
            total=len(notifications),
            unread_count=unread_count
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )


@router.post("/alerts/notifications/{notification_id}/read", response_model=AcknowledgeAlertResponse)
async def mark_notification_read(
    notification_id: UUID,
    user=Depends(get_auth_user),
):
    """
    Mark an in-app notification as read.
    """
    try:
        success = await alert_service.mark_notification_read(notification_id, user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or you don't have permission"
            )

        return AcknowledgeAlertResponse(
            success=True,
            message="Notification marked as read"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )


@router.post("/alerts/notifications/mark-all-read", response_model=AcknowledgeAlertResponse)
async def mark_all_notifications_read(user=Depends(get_auth_user)):
    """
    Mark all in-app notifications as read for the current user.
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("in_app_notifications").update({
            "is_read": True,
        }).eq("user_id", str(user.id)).eq("is_read", False).execute()

        updated_count = len(result.data or [])

        return AcknowledgeAlertResponse(
            success=True,
            message=f"{updated_count} notification(s) marked as read"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notifications as read: {str(e)}"
        )

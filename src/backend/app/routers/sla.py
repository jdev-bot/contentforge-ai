"""
SLA Monitoring Router for ContentForge AI API.

This router provides endpoints for:
- Managing SLA policies (CRUD)
- Recording SLA metrics
- Checking compliance
- Viewing SLA dashboard
- Managing SLA alerts
- Viewing uptime, response time, and error rate SLA data
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator

from app.services.sla_service import SLAMetricType, SLASeverity, sla_service

router = APIRouter()


# ============== Pydantic Models ==============

class SLAPolicyCreate(BaseModel):
    """Create SLA policy request model."""
    name: str = Field(..., min_length=1, max_length=255, description="Policy name")
    metric: str = Field(..., description="Metric type: uptime, response_time, error_rate, throughput")
    threshold: float = Field(..., description="Threshold value for the metric")
    window_minutes: int = Field(..., gt=0, description="Time window in minutes")
    severity: str = Field(default="warning", description="Severity: critical, warning, info")

    @field_validator("metric")
    @classmethod
    def validate_metric(cls, v: str) -> str:
        allowed = [m.value for m in SLAMetricType]
        if v not in allowed:
            raise ValueError(f"metric must be one of {allowed}")
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        allowed = [s.value for s in SLASeverity]
        if v not in allowed:
            raise ValueError(f"severity must be one of {allowed}")
        return v


class SLAPolicyUpdate(BaseModel):
    """Update SLA policy request model."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    metric: Optional[str] = None
    threshold: Optional[float] = None
    window_minutes: Optional[int] = Field(None, gt=0)
    severity: Optional[str] = None
    enabled: Optional[bool] = None

    @field_validator("metric")
    @classmethod
    def validate_metric(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = [m.value for m in SLAMetricType]
        if v not in allowed:
            raise ValueError(f"metric must be one of {allowed}")
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = [s.value for s in SLASeverity]
        if v not in allowed:
            raise ValueError(f"severity must be one of {allowed}")
        return v


class SLAPolicyResponse(BaseModel):
    """SLA policy response model."""
    id: str
    user_id: str
    name: str
    metric: str
    threshold: float
    window_minutes: int
    severity: str
    enabled: bool
    created_at: str
    updated_at: str


class SLAMetricRecord(BaseModel):
    """Record SLA metric request model."""
    metric_type: str = Field(..., description="Metric type: uptime, response_time, error_rate, throughput")
    value: float = Field(..., description="Metric value")
    labels: Optional[Dict[str, str]] = Field(None, description="Optional labels for the metric")

    @field_validator("metric_type")
    @classmethod
    def validate_metric_type(cls, v: str) -> str:
        allowed = [m.value for m in SLAMetricType]
        if v not in allowed:
            raise ValueError(f"metric_type must be one of {allowed}")
        return v


class SLAMetricResponse(BaseModel):
    """SLA metric response model."""
    id: str
    user_id: str
    metric_type: str
    value: float
    labels: Dict[str, str]
    created_at: str


class SLADashboardResponse(BaseModel):
    """SLA dashboard response model."""
    uptime_percentage: float
    avg_response_time_ms: float
    error_rate: float
    throughput_rps: float
    active_alerts: int
    policy_compliance: Dict[str, bool]


class SLAAlertResponse(BaseModel):
    """SLA alert response model."""
    id: str
    user_id: str
    policy_id: str
    metric_type: str
    current_value: float
    threshold: float
    severity: str
    message: str
    created_at: str
    acknowledged: bool
    acknowledged_at: Optional[str] = None


class SLAAlertListResponse(BaseModel):
    """SLA alert list response model."""
    alerts: List[SLAAlertResponse]
    total: int


class SLAUptimeResponse(BaseModel):
    """SLA uptime response model."""
    uptime_percentage: float
    total_samples: int
    period_days: int
    daily_data: List[Dict[str, Any]]


class SLAResponseTimeResponse(BaseModel):
    """SLA response time response model."""
    avg_ms: float
    p50_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
    total_samples: int
    period_days: int
    daily_data: List[Dict[str, Any]]


class SLAErrorRateResponse(BaseModel):
    """SLA error rate response model."""
    error_rate: float
    total_samples: int
    period_days: int
    daily_data: List[Dict[str, Any]]


class SLAComplianceResponse(BaseModel):
    """SLA compliance check response model."""
    policy_id: str
    metric: str
    compliant: bool
    current_value: Optional[float]
    threshold: float
    message: str


class AcknowledgeAlertResponse(BaseModel):
    """Acknowledge alert response model."""
    success: bool
    message: str


# ============== Dependency ==============

from app.routers.auth import get_auth_user

# ============== SLA Policy Endpoints ==============

@router.post("/sla/policies", response_model=SLAPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_sla_policy(
    policy: SLAPolicyCreate,
    user=Depends(get_auth_user),
):
    """Create a new SLA policy."""
    try:
        result = await sla_service.create_policy(
            user_id=user.id,
            name=policy.name,
            metric=policy.metric,
            threshold=policy.threshold,
            window_minutes=policy.window_minutes,
            severity=policy.severity,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create SLA policy",
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create SLA policy: {str(e)}",
        )


@router.get("/sla/policies", response_model=List[SLAPolicyResponse])
async def list_sla_policies(user=Depends(get_auth_user)):
    """List all SLA policies for the current user."""
    try:
        policies = await sla_service.list_policies(user_id=user.id)
        return policies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list SLA policies: {str(e)}",
        )


@router.put("/sla/policies/{policy_id}", response_model=SLAPolicyResponse)
async def update_sla_policy(
    policy_id: UUID,
    updates: SLAPolicyUpdate,
    user=Depends(get_auth_user),
):
    """Update an existing SLA policy."""
    try:
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )
        result = await sla_service.update_policy(
            policy_id=policy_id,
            user_id=user.id,
            updates=update_data,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA policy not found or you don't have permission",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update SLA policy: {str(e)}",
        )


@router.delete("/sla/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sla_policy(
    policy_id: UUID,
    user=Depends(get_auth_user),
):
    """Delete an SLA policy."""
    try:
        success = await sla_service.delete_policy(policy_id=policy_id, user_id=user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA policy not found or you don't have permission",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete SLA policy: {str(e)}",
        )


# ============== SLA Metrics Endpoints ==============

@router.post("/sla/metrics", response_model=SLAMetricResponse, status_code=status.HTTP_201_CREATED)
async def record_sla_metric(
    metric: SLAMetricRecord,
    user=Depends(get_auth_user),
):
    """Record an SLA metric data point."""
    try:
        result = await sla_service.record_metric(
            user_id=user.id,
            metric_type=metric.metric_type,
            value=metric.value,
            labels=metric.labels,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record SLA metric",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record SLA metric: {str(e)}",
        )


# ============== SLA Dashboard Endpoint ==============

@router.get("/sla/dashboard", response_model=SLADashboardResponse)
async def get_sla_dashboard(user=Depends(get_auth_user)):
    """Get SLA dashboard with aggregated metrics."""
    try:
        dashboard = await sla_service.get_dashboard(user_id=user.id)
        return dashboard
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get SLA dashboard: {str(e)}",
        )


# ============== SLA Alerts Endpoints ==============

@router.get("/sla/alerts", response_model=SLAAlertListResponse)
async def list_sla_alerts(
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledged status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_auth_user),
):
    """List SLA alerts for the current user."""
    try:
        alerts = await sla_service.get_alerts(
            user_id=user.id,
            acknowledged=acknowledged,
            limit=limit,
            offset=offset,
        )
        return SLAAlertListResponse(alerts=alerts, total=len(alerts))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list SLA alerts: {str(e)}",
        )


@router.put("/sla/alerts/{alert_id}/acknowledge", response_model=AcknowledgeAlertResponse)
async def acknowledge_sla_alert(
    alert_id: UUID,
    user=Depends(get_auth_user),
):
    """Acknowledge an SLA alert."""
    try:
        success = await sla_service.acknowledge_alert(alert_id=alert_id, user_id=user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA alert not found or you don't have permission",
            )
        return AcknowledgeAlertResponse(success=True, message="Alert acknowledged successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge SLA alert: {str(e)}",
        )


# ============== SLA Compliance Endpoint ==============

@router.get("/sla/policies/{policy_id}/compliance", response_model=SLAComplianceResponse)
async def check_sla_compliance(
    policy_id: UUID,
    user=Depends(get_auth_user),
):
    """Check if current metrics comply with an SLA policy."""
    try:
        result = await sla_service.check_compliance(policy_id=policy_id, user_id=user.id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA policy not found or you don't have permission",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check SLA compliance: {str(e)}",
        )


# ============== SLA Analytics Endpoints ==============

@router.get("/sla/uptime", response_model=SLAUptimeResponse)
async def get_sla_uptime(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    user=Depends(get_auth_user),
):
    """Get uptime SLA metrics over a time period."""
    try:
        result = await sla_service.get_uptime_sla(user_id=user.id, days=days)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get uptime SLA: {str(e)}",
        )


@router.get("/sla/response-time", response_model=SLAResponseTimeResponse)
async def get_sla_response_time(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    user=Depends(get_auth_user),
):
    """Get response time SLA metrics over a time period."""
    try:
        result = await sla_service.get_response_time_sla(user_id=user.id, days=days)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get response time SLA: {str(e)}",
        )


@router.get("/sla/error-rate", response_model=SLAErrorRateResponse)
async def get_sla_error_rate(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    user=Depends(get_auth_user),
):
    """Get error rate SLA metrics over a time period."""
    try:
        result = await sla_service.get_error_rate_sla(user_id=user.id, days=days)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get error rate SLA: {str(e)}",
        )
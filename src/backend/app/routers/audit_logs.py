"""
Audit Logs router — endpoints for querying, exporting, and viewing audit log statistics.

Route order matters: specific paths (like /export, /stats) must come before parameterized paths (like /{log_id}).
"""

import io
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.routers.auth import get_auth_user
from app.services.audit_service import audit_service

router = APIRouter()


class AuditLogResponse(BaseModel):
    id: str
    actor_id: str
    actor_email: str
    action: str
    resource_type: str
    resource_id: str
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime


class AuditStatsResponse(BaseModel):
    total: int
    action_counts: dict
    date_from: Optional[str] = None
    date_to: Optional[str] = None


# ── Specific paths BEFORE parameterized paths ──


@router.get("/audit-logs/export")
async def export_audit_logs(
    user=Depends(get_auth_user),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
):
    """Export audit logs as CSV download."""
    try:
        csv_content = audit_service.export_csv(
            user_id=str(user.id),
            date_from=date_from,
            date_to=date_to,
            action=action,
            resource_type=resource_type,
        )
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=audit_logs_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/audit-logs/stats", response_model=AuditStatsResponse)
async def audit_log_stats(
    user=Depends(get_auth_user),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Get audit log statistics — action counts by type."""
    try:
        stats = audit_service.get_stats(
            user_id=str(user.id),
            date_from=date_from,
            date_to=date_to,
        )
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ── Parameterized paths ──


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    user=Depends(get_auth_user),
    actor_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List audit logs with filtering by actor, action, resource, and date range."""
    try:
        logs = audit_service.list_logs(
            user_id=str(user.id),
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        return logs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/audit-logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: UUID,
    user=Depends(get_auth_user),
):
    """Get a specific audit log entry."""
    try:
        log = audit_service.get_log(
            log_id=str(log_id),
            user_id=str(user.id),
        )
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit log not found",
            )
        return log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

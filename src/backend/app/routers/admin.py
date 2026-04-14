"""
Admin router for system management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from app.routers.auth import get_auth_user
from app.core.error_tracking import get_recent_errors, get_error_summary
from app.core.supabase import get_supabase_client, get_supabase_admin_client

router = APIRouter()


class ErrorLogEntry(BaseModel):
    """Error log entry response model."""
    id: UUID
    timestamp: datetime
    status_code: int
    error_type: str
    message: str
    detail: Optional[str] = None
    path: str
    method: str
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ErrorListResponse(BaseModel):
    """Response model for error list."""
    total: int
    errors: List[ErrorLogEntry]


class ErrorSummaryResponse(BaseModel):
    """Response model for error summary."""
    total: int
    period_hours: int
    by_status_code: Dict[str, int]
    by_type: Dict[str, int]


def is_admin_user(user) -> bool:
    """Check if user has admin role."""
    # Check user metadata for admin role
    user_metadata = user.user_metadata or {}
    app_metadata = user.app_metadata or {}
    
    # Check various places where admin role might be stored
    roles = (
        user_metadata.get("roles", []) +
        app_metadata.get("roles", []) +
        (["admin"] if user_metadata.get("is_admin") else []) +
        (["admin"] if app_metadata.get("is_admin") else [])
    )
    
    return "admin" in roles or user.email in ["admin@contentforge.ai"]


@router.get("/admin/errors", response_model=ErrorListResponse)
async def get_admin_errors(
    limit: int = 100,
    user=Depends(get_auth_user)
):
    """
    Get the last 100 errors (admin only).
    
    Args:
    - limit: Maximum number of errors to return (default: 100, max: 500)
    
    Returns a list of recent errors with full details.
    """
    # Check if user is admin
    if not is_admin_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    # Validate limit
    if limit < 1:
        limit = 1
    elif limit > 500:
        limit = 500
    
    try:
        errors = get_recent_errors(limit=limit)
        
        error_entries = []
        for error in errors:
            # Convert to ErrorLogEntry
            entry = ErrorLogEntry(
                id=UUID(error.get("id", str(uuid.uuid4()))),
                timestamp=datetime.fromisoformat(error.get("timestamp").replace("Z", "+00:00")) if error.get("timestamp") else datetime.now(timezone.utc),
                status_code=error.get("status_code", 0),
                error_type=error.get("error_type", "unknown"),
                message=error.get("message", ""),
                detail=error.get("detail"),
                path=error.get("path", ""),
                method=error.get("method", ""),
                user_id=UUID(error.get("user_id")) if error.get("user_id") else None,
                ip_address=error.get("ip_address"),
                user_agent=error.get("user_agent"),
                metadata=error.get("metadata"),
            )
            error_entries.append(entry)
        
        return ErrorListResponse(
            total=len(error_entries),
            errors=error_entries
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve errors: {str(e)}",
        )


@router.get("/admin/errors/summary", response_model=ErrorSummaryResponse)
async def get_admin_errors_summary(
    hours: int = 24,
    user=Depends(get_auth_user)
):
    """
    Get error summary statistics (admin only).
    
    Args:
    - hours: Time period in hours to analyze (default: 24)
    
    Returns aggregated error statistics.
    """
    # Check if user is admin
    if not is_admin_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    try:
        summary = get_error_summary(hours=hours)
        
        return ErrorSummaryResponse(
            total=summary.get("total", 0),
            period_hours=hours,
            by_status_code={str(k): v for k, v in summary.get("by_status_code", {}).items()},
            by_type=summary.get("by_type", {})
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve error summary: {str(e)}",
        )


@router.delete("/admin/errors/{error_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_error(
    error_id: UUID,
    user=Depends(get_auth_user)
):
    """
    Delete a specific error log entry (admin only).
    
    Args:
    - error_id: ID of the error to delete
    """
    # Check if user is admin
    if not is_admin_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    try:
        supabase = get_supabase_admin_client()
        supabase.table("error_logs").delete().eq("id", str(error_id)).execute()
        
        return None
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete error: {str(e)}",
        )


# Additional admin utilities
import uuid

@router.get("/admin/users/stats")
async def get_user_stats(
    user=Depends(get_auth_user)
):
    """
    Get user statistics (admin only).
    
    Returns:
    - Total user count
    - Users by subscription tier
    - Active users in last 24 hours
    """
    # Check if user is admin
    if not is_admin_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    try:
        supabase = get_supabase_admin_client()
        
        # Get total profiles
        profiles_result = supabase.table("profiles").select("*", count="exact").execute()
        total_users = profiles_result.count
        
        # Count by tier
        tiers = {}
        for profile in profiles_result.data:
            tier = profile.get("subscription_tier", "free")
            tiers[tier] = tiers.get(tier, 0) + 1
        
        return {
            "total_users": total_users,
            "by_tier": tiers,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user stats: {str(e)}",
        )

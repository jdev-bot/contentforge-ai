"""
Audit Log Service

Handles audit log creation, querying, statistics, CSV export, and retention management.
"""
import csv
import io
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

SUPPORTED_ACTIONS = frozenset({
    "content.created",
    "content.updated",
    "content.deleted",
    "content.published",
    "user.login",
    "user.logout",
    "user.settings_changed",
    "project.created",
    "project.deleted",
    "team.member_added",
    "team.member_removed",
    "api_key.rotated",
})

DEFAULT_RETENTION_DAYS = 90


class AuditService:
    """Service for audit log management."""

    def __init__(self):
        self._supabase = None

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    @supabase.setter
    def supabase(self, value):
        self._supabase = value

    def log(
        self,
        actor_id: str,
        actor_email: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an audit log entry."""
        if action not in SUPPORTED_ACTIONS:
            logger.warning(f"Unsupported audit action: {action}")
            # Still log it but flag as unsupported

        data = {
            "actor_id": actor_id,
            "actor_email": actor_email,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        result = self.supabase.table("audit_logs").insert(data).execute()
        return result.data[0] if result.data else None

    def list_logs(
        self,
        user_id: str,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List audit logs with filtering."""
        query = (
            self.supabase.table("audit_logs")
            .select("*")
            .eq("actor_id", user_id)
            .order("timestamp", desc=True)
        )

        if actor_id:
            query = query.eq("actor_id", actor_id)
        if action:
            query = query.eq("action", action)
        if resource_type:
            query = query.eq("resource_type", resource_type)
        if resource_id:
            query = query.eq("resource_id", resource_id)
        if date_from:
            query = query.gte("timestamp", date_from)
        if date_to:
            query = query.lte("timestamp", date_to)

        query = query.range(offset, offset + limit - 1)

        result = query.execute()
        return result.data or []

    def get_log(
        self,
        log_id: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get a specific audit log entry."""
        result = (
            self.supabase.table("audit_logs")
            .select("*")
            .eq("id", log_id)
            .eq("actor_id", user_id)
            .single()
            .execute()
        )
        return result.data if result.data else None

    def get_stats(
        self,
        user_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get audit log statistics — action counts by type."""
        query = (
            self.supabase.table("audit_logs")
            .select("action")
            .eq("actor_id", user_id)
        )

        if date_from:
            query = query.gte("timestamp", date_from)
        if date_to:
            query = query.lte("timestamp", date_to)

        result = query.execute()
        logs = result.data or []

        # Count by action type
        action_counts: Dict[str, int] = {}
        for entry in logs:
            action = entry.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "total": len(logs),
            "action_counts": action_counts,
            "date_from": date_from,
            "date_to": date_to,
        }

    def export_csv(
        self,
        user_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> str:
        """Export audit logs as CSV string."""
        query = (
            self.supabase.table("audit_logs")
            .select("*")
            .eq("actor_id", user_id)
            .order("timestamp", desc=True)
        )

        if date_from:
            query = query.gte("timestamp", date_from)
        if date_to:
            query = query.lte("timestamp", date_to)
        if action:
            query = query.eq("action", action)
        if resource_type:
            query = query.eq("resource_type", resource_type)

        result = query.execute()
        logs = result.data or []

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "id", "actor_id", "actor_email", "action",
            "resource_type", "resource_id", "details",
            "ip_address", "user_agent", "timestamp",
        ])
        for entry in logs:
            writer.writerow([
                entry.get("id", ""),
                entry.get("actor_id", ""),
                entry.get("actor_email", ""),
                entry.get("action", ""),
                entry.get("resource_type", ""),
                entry.get("resource_id", ""),
                entry.get("details", ""),
                entry.get("ip_address", ""),
                entry.get("user_agent", ""),
                entry.get("timestamp", ""),
            ])

        return output.getvalue()

    def cleanup_expired(
        self,
        organization_id: Optional[str] = None,
        retention_days: int = DEFAULT_RETENTION_DAYS,
    ) -> int:
        """
        Remove audit logs older than retention period.
        Returns count of deleted entries.
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()

        query = self.supabase.table("audit_logs").delete().lt("timestamp", cutoff)

        if organization_id:
            query = query.eq("organization_id", organization_id)

        result = query.execute()
        return len(result.data) if result.data else 0


# Decorator for auto-logging
def audit_log(action: str, resource_type: str):
    """
    Decorator to automatically log an auditable action.
    Applied to FastAPI route handlers; extracts request context for actor info.
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Execute the original function first
            result = await func(*args, **kwargs)

            # Try to extract context for audit logging
            request = kwargs.get("request")
            user = kwargs.get("user")

            if user:
                try:
                    from app.services.audit_service import audit_service
                    audit_service.log(
                        actor_id=str(user.id),
                        actor_email=getattr(user, "email", ""),
                        action=action,
                        resource_type=resource_type,
                        resource_id=str(getattr(result, "id", "")) if result else "",
                        ip_address=request.client.host if request and hasattr(request, "client") else None,
                        user_agent=request.headers.get("user-agent") if request else None,
                    )
                except Exception as e:
                    logger.error(f"Audit logging failed: {e}")

            return result

        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


# Global service instance
audit_service = AuditService()
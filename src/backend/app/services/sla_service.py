"""
SLA Monitoring Service for ContentForge AI.

This service handles:
- SLA policy management (CRUD)
- Metric recording and compliance checking
- Dashboard aggregation (uptime, response time, error rate, throughput)
- Alert generation and lifecycle management
"""

import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class SLAMetricType(str, Enum):
    """SLA metric types."""

    UPTIME = "uptime"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"


class SLASeverity(str, Enum):
    """SLA alert severity levels."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class SLAPolicy:
    """SLA Policy model."""

    def __init__(
        self,
        policy_id: str,
        name: str,
        metric: str,
        threshold: float,
        window_minutes: int,
        severity: str,
        enabled: bool = True,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.policy_id = policy_id
        self.name = name
        self.metric = metric
        self.threshold = threshold
        self.window_minutes = window_minutes
        self.severity = severity
        self.enabled = enabled
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "metric": self.metric,
            "threshold": self.threshold,
            "window_minutes": self.window_minutes,
            "severity": self.severity,
            "enabled": self.enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class SLAMetric:
    """SLA Metric data point model."""

    def __init__(
        self,
        metric_id: str,
        metric_type: str,
        value: float,
        timestamp: str,
        labels: Optional[Dict[str, str]] = None,
    ):
        self.metric_id = metric_id
        self.metric_type = metric_type
        self.value = value
        self.timestamp = timestamp
        self.labels = labels or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "metric_type": self.metric_type,
            "value": self.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
        }


class SLAAlert:
    """SLA Alert model."""

    def __init__(
        self,
        alert_id: str,
        policy_id: str,
        metric_type: str,
        current_value: float,
        threshold: float,
        severity: str,
        message: str,
        created_at: str,
        acknowledged: bool = False,
    ):
        self.alert_id = alert_id
        self.policy_id = policy_id
        self.metric_type = metric_type
        self.current_value = current_value
        self.threshold = threshold
        self.severity = severity
        self.message = message
        self.created_at = created_at
        self.acknowledged = acknowledged

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "policy_id": self.policy_id,
            "metric_type": self.metric_type,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "severity": self.severity,
            "message": self.message,
            "created_at": self.created_at,
            "acknowledged": self.acknowledged,
        }


class SLADashboard:
    """SLA Dashboard aggregation model."""

    def __init__(
        self,
        uptime_percentage: float,
        avg_response_time_ms: float,
        error_rate: float,
        throughput_rps: float,
        active_alerts: int,
        policy_compliance: Dict[str, bool],
    ):
        self.uptime_percentage = uptime_percentage
        self.avg_response_time_ms = avg_response_time_ms
        self.error_rate = error_rate
        self.throughput_rps = throughput_rps
        self.active_alerts = active_alerts
        self.policy_compliance = policy_compliance

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uptime_percentage": self.uptime_percentage,
            "avg_response_time_ms": self.avg_response_time_ms,
            "error_rate": self.error_rate,
            "throughput_rps": self.throughput_rps,
            "active_alerts": self.active_alerts,
            "policy_compliance": self.policy_compliance,
        }


class SLAService:
    """Service for managing SLA policies, metrics, and alerts."""

    def __init__(self):
        """Initialize the SLA service."""
        self._supabase = None

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    @supabase.setter
    def supabase(self, value):
        self._supabase = value

    async def create_policy(
        self,
        user_id: UUID,
        name: str,
        metric: str,
        threshold: float,
        window_minutes: int,
        severity: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new SLA policy.

        Args:
            user_id: Owner user ID
            name: Policy name
            metric: Metric type (uptime/response_time/error_rate/throughput)
            threshold: Threshold value
            window_minutes: Time window in minutes
            severity: Alert severity (critical/warning/info)

        Returns:
            Created policy dict or None on error
        """
        try:
            policy = {
                "user_id": str(user_id),
                "name": name,
                "metric": metric,
                "threshold": threshold,
                "window_minutes": window_minutes,
                "severity": severity,
                "enabled": True,
            }
            result = self.supabase.table("sla_policies").insert(policy).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
        except Exception as e:
            logger.error(f"Error creating SLA policy: {e}")
        return None

    async def list_policies(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        List all SLA policies for a user.

        Args:
            user_id: Owner user ID

        Returns:
            List of policy dicts
        """
        try:
            result = (
                self.supabase.table("sla_policies")
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"Error listing SLA policies: {e}")
            return []

    async def update_policy(
        self,
        policy_id: UUID,
        user_id: UUID,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Update an SLA policy.

        Args:
            policy_id: Policy ID
            user_id: Owner user ID (for verification)
            updates: Fields to update

        Returns:
            Updated policy dict or None
        """
        try:
            # Remove fields that shouldn't be directly updated
            updates.pop("id", None)
            updates.pop("user_id", None)
            updates.pop("created_at", None)
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()

            result = (
                self.supabase.table("sla_policies")
                .update(updates)
                .eq("id", str(policy_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0]
        except Exception as e:
            logger.error(f"Error updating SLA policy: {e}")
        return None

    async def delete_policy(self, policy_id: UUID, user_id: UUID) -> bool:
        """
        Delete an SLA policy.

        Args:
            policy_id: Policy ID
            user_id: Owner user ID (for verification)

        Returns:
            True if successful
        """
        try:
            result = (
                self.supabase.table("sla_policies")
                .delete()
                .eq("id", str(policy_id))
                .eq("user_id", str(user_id))
                .execute()
            )
            return len(result.data or []) > 0
        except Exception as e:
            logger.error(f"Error deleting SLA policy: {e}")
            return False

    async def record_metric(
        self,
        user_id: UUID,
        metric_type: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Record an SLA metric data point.

        Args:
            user_id: Owner user ID
            metric_type: Type of metric (uptime/response_time/error_rate/throughput)
            value: Metric value
            labels: Optional labels dict

        Returns:
            Created metric dict or None
        """
        try:
            metric = {
                "user_id": str(user_id),
                "metric_type": metric_type,
                "value": value,
                "labels": labels or {},
            }
            result = self.supabase.table("sla_metrics").insert(metric).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
        except Exception as e:
            logger.error(f"Error recording SLA metric: {e}")
        return None

    async def check_compliance(
        self, policy_id: UUID, user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Check if current metrics comply with an SLA policy.

        Args:
            policy_id: Policy ID to check
            user_id: Owner user ID

        Returns:
            Compliance result dict with compliant bool, current_value, threshold, etc.
        """
        try:
            # Fetch the policy
            policy_result = (
                self.supabase.table("sla_policies")
                .select("*")
                .eq("id", str(policy_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            if not policy_result.data or len(policy_result.data) == 0:
                return None

            policy = policy_result.data[0]
            metric = policy["metric"]
            threshold = policy["threshold"]
            window_minutes = policy["window_minutes"]

            # Get recent metrics for this metric type within the window
            cutoff = (
                datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
            ).isoformat()
            metrics_result = (
                self.supabase.table("sla_metrics")
                .select("value")
                .eq("user_id", str(user_id))
                .eq("metric_type", metric)
                .gte("created_at", cutoff)
                .execute()
            )

            values = [m["value"] for m in (metrics_result.data or [])]

            if not values:
                return {
                    "policy_id": str(policy_id),
                    "metric": metric,
                    "compliant": True,
                    "current_value": None,
                    "threshold": threshold,
                    "message": "No metrics data available for the specified window",
                }

            # Calculate aggregate based on metric type
            if metric == SLAMetricType.UPTIME.value:
                current_value = sum(1 for v in values if v > 0) / len(values) * 100
                compliant = current_value >= threshold
            elif metric == SLAMetricType.RESPONSE_TIME.value:
                current_value = sum(values) / len(values)
                compliant = current_value <= threshold
            elif metric == SLAMetricType.ERROR_RATE.value:
                current_value = sum(values) / len(values)
                compliant = current_value <= threshold
            elif metric == SLAMetricType.THROUGHPUT.value:
                current_value = sum(values) / len(values)
                compliant = current_value >= threshold
            else:
                current_value = sum(values) / len(values)
                compliant = current_value <= threshold

            return {
                "policy_id": str(policy_id),
                "metric": metric,
                "compliant": compliant,
                "current_value": round(current_value, 4),
                "threshold": threshold,
                "message": "Compliant" if compliant else "SLA violation detected",
            }

        except Exception as e:
            logger.error(f"Error checking SLA compliance: {e}")
            return None

    async def get_dashboard(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get SLA dashboard with aggregated metrics.

        Args:
            user_id: Owner user ID

        Returns:
            Dashboard dict with uptime, response time, error rate, throughput, alerts, compliance
        """
        try:
            # Get uptime over last 24 hours
            cutoff_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
            uptime_metrics = (
                self.supabase.table("sla_metrics")
                .select("value")
                .eq("user_id", str(user_id))
                .eq("metric_type", SLAMetricType.UPTIME.value)
                .gte("created_at", cutoff_24h)
                .execute()
            )
            uptime_values = [m["value"] for m in (uptime_metrics.data or [])]
            uptime_percentage = (
                (sum(1 for v in uptime_values if v > 0) / len(uptime_values) * 100)
                if uptime_values
                else 100.0
            )

            # Get average response time
            rt_metrics = (
                self.supabase.table("sla_metrics")
                .select("value")
                .eq("user_id", str(user_id))
                .eq("metric_type", SLAMetricType.RESPONSE_TIME.value)
                .gte("created_at", cutoff_24h)
                .execute()
            )
            rt_values = [m["value"] for m in (rt_metrics.data or [])]
            avg_response_time_ms = (
                (sum(rt_values) / len(rt_values)) if rt_values else 0.0
            )

            # Get error rate
            er_metrics = (
                self.supabase.table("sla_metrics")
                .select("value")
                .eq("user_id", str(user_id))
                .eq("metric_type", SLAMetricType.ERROR_RATE.value)
                .gte("created_at", cutoff_24h)
                .execute()
            )
            er_values = [m["value"] for m in (er_metrics.data or [])]
            error_rate = (sum(er_values) / len(er_values)) if er_values else 0.0

            # Get throughput
            tp_metrics = (
                self.supabase.table("sla_metrics")
                .select("value")
                .eq("user_id", str(user_id))
                .eq("metric_type", SLAMetricType.THROUGHPUT.value)
                .gte("created_at", cutoff_24h)
                .execute()
            )
            tp_values = [m["value"] for m in (tp_metrics.data or [])]
            throughput_rps = (sum(tp_values) / len(tp_values)) if tp_values else 0.0

            # Count active (unacknowledged) alerts
            alerts_result = (
                self.supabase.table("sla_alerts")
                .select("id", count="exact")
                .eq("user_id", str(user_id))
                .eq("acknowledged", False)
                .execute()
            )
            active_alerts = alerts_result.count or 0

            # Check compliance for all enabled policies
            policies_result = (
                self.supabase.table("sla_policies")
                .select("id")
                .eq("user_id", str(user_id))
                .eq("enabled", True)
                .execute()
            )

            policy_compliance: Dict[str, bool] = {}
            for policy in policies_result.data or []:
                compliance = await self.check_compliance(UUID(policy["id"]), user_id)
                if compliance:
                    policy_compliance[policy["id"]] = compliance["compliant"]

            return SLADashboard(
                uptime_percentage=round(uptime_percentage, 2),
                avg_response_time_ms=round(avg_response_time_ms, 2),
                error_rate=round(error_rate, 4),
                throughput_rps=round(throughput_rps, 2),
                active_alerts=active_alerts,
                policy_compliance=policy_compliance,
            ).to_dict()

        except Exception as e:
            logger.error(f"Error getting SLA dashboard: {e}")
            return SLADashboard(
                uptime_percentage=0.0,
                avg_response_time_ms=0.0,
                error_rate=0.0,
                throughput_rps=0.0,
                active_alerts=0,
                policy_compliance={},
            ).to_dict()

    async def get_alerts(
        self,
        user_id: UUID,
        acknowledged: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get SLA alerts.

        Args:
            user_id: Owner user ID
            acknowledged: Filter by acknowledged status (optional)
            limit: Max results
            offset: Pagination offset

        Returns:
            List of alert dicts
        """
        try:
            query = (
                self.supabase.table("sla_alerts")
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
            )

            if acknowledged is not None:
                query = query.eq("acknowledged", acknowledged)

            query = query.range(offset, offset + limit - 1)
            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting SLA alerts: {e}")
            return []

    async def acknowledge_alert(self, alert_id: UUID, user_id: UUID) -> bool:
        """
        Acknowledge an SLA alert.

        Args:
            alert_id: Alert ID
            user_id: Owner user ID (for verification)

        Returns:
            True if successful
        """
        try:
            result = (
                self.supabase.table("sla_alerts")
                .update(
                    {
                        "acknowledged": True,
                        "acknowledged_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                .eq("id", str(alert_id))
                .eq("user_id", str(user_id))
                .execute()
            )
            return len(result.data or []) > 0
        except Exception as e:
            logger.error(f"Error acknowledging SLA alert: {e}")
            return False

    async def get_uptime_sla(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """
        Get uptime SLA metrics over a time period.

        Args:
            user_id: Owner user ID
            days: Number of days to look back

        Returns:
            Dict with uptime_percentage and daily_data
        """
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            result = (
                self.supabase.table("sla_metrics")
                .select("value, created_at")
                .eq("user_id", str(user_id))
                .eq("metric_type", SLAMetricType.UPTIME.value)
                .gte("created_at", cutoff)
                .order("created_at", desc=False)
                .execute()
            )

            data = result.data or []
            total_points = len(data)
            up_points = sum(1 for m in data if m["value"] > 0)
            uptime_percentage = (
                (up_points / total_points * 100) if total_points > 0 else 100.0
            )

            # Group by day for trend data
            daily_data: Dict[str, List[float]] = {}
            for m in data:
                day = m["created_at"][:10]  # YYYY-MM-DD
                if day not in daily_data:
                    daily_data[day] = []
                daily_data[day].append(m["value"])

            daily_summary = []
            for day, values in sorted(daily_data.items()):
                day_up = sum(1 for v in values if v > 0)
                daily_summary.append(
                    {
                        "date": day,
                        "uptime_percentage": (
                            round(day_up / len(values) * 100, 2) if values else 100.0
                        ),
                        "samples": len(values),
                    }
                )

            return {
                "uptime_percentage": round(uptime_percentage, 2),
                "total_samples": total_points,
                "period_days": days,
                "daily_data": daily_summary,
            }
        except Exception as e:
            logger.error(f"Error getting uptime SLA: {e}")
            return {
                "uptime_percentage": 0.0,
                "total_samples": 0,
                "period_days": days,
                "daily_data": [],
            }

    async def get_response_time_sla(
        self, user_id: UUID, days: int = 30
    ) -> Dict[str, Any]:
        """
        Get response time SLA metrics over a time period.

        Args:
            user_id: Owner user ID
            days: Number of days to look back

        Returns:
            Dict with percentiles and daily averages
        """
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            result = (
                self.supabase.table("sla_metrics")
                .select("value, created_at")
                .eq("user_id", str(user_id))
                .eq("metric_type", SLAMetricType.RESPONSE_TIME.value)
                .gte("created_at", cutoff)
                .order("created_at", desc=False)
                .execute()
            )

            data = result.data or []
            values = sorted([m["value"] for m in data])

            if values:
                p50 = values[len(values) // 2]
                p90 = values[int(len(values) * 0.9)]
                p95 = values[int(len(values) * 0.95)]
                p99 = values[int(len(values) * 0.99)] if len(values) > 1 else values[-1]
                avg = sum(values) / len(values)
            else:
                p50 = p90 = p95 = p99 = avg = 0.0

            # Group by day
            daily_data: Dict[str, List[float]] = {}
            for m in data:
                day = m["created_at"][:10]
                if day not in daily_data:
                    daily_data[day] = []
                daily_data[day].append(m["value"])

            daily_summary = []
            for day, day_values in sorted(daily_data.items()):
                daily_summary.append(
                    {
                        "date": day,
                        "avg_ms": round(sum(day_values) / len(day_values), 2),
                        "p50_ms": (
                            round(sorted(day_values)[len(day_values) // 2], 2)
                            if day_values
                            else 0
                        ),
                        "samples": len(day_values),
                    }
                )

            return {
                "avg_ms": round(avg, 2),
                "p50_ms": round(p50, 2),
                "p90_ms": round(p90, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
                "total_samples": len(values),
                "period_days": days,
                "daily_data": daily_summary,
            }
        except Exception as e:
            logger.error(f"Error getting response time SLA: {e}")
            return {
                "avg_ms": 0.0,
                "p50_ms": 0.0,
                "p90_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
                "total_samples": 0,
                "period_days": days,
                "daily_data": [],
            }

    async def get_error_rate_sla(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """
        Get error rate SLA metrics over a time period.

        Args:
            user_id: Owner user ID
            days: Number of days to look back

        Returns:
            Dict with error rate trend data
        """
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            result = (
                self.supabase.table("sla_metrics")
                .select("value, created_at")
                .eq("user_id", str(user_id))
                .eq("metric_type", SLAMetricType.ERROR_RATE.value)
                .gte("created_at", cutoff)
                .order("created_at", desc=False)
                .execute()
            )

            data = result.data or []
            values = [m["value"] for m in data]

            # Group by day
            daily_data: Dict[str, List[float]] = {}
            for m in data:
                day = m["created_at"][:10]
                if day not in daily_data:
                    daily_data[day] = []
                daily_data[day].append(m["value"])

            daily_summary = []
            for day, day_values in sorted(daily_data.items()):
                daily_summary.append(
                    {
                        "date": day,
                        "error_rate": round(sum(day_values) / len(day_values), 4),
                        "samples": len(day_values),
                    }
                )

            overall_rate = (sum(values) / len(values)) if values else 0.0

            return {
                "error_rate": round(overall_rate, 4),
                "total_samples": len(values),
                "period_days": days,
                "daily_data": daily_summary,
            }
        except Exception as e:
            logger.error(f"Error getting error rate SLA: {e}")
            return {
                "error_rate": 0.0,
                "total_samples": 0,
                "period_days": days,
                "daily_data": [],
            }

    async def _create_alert_if_needed(
        self,
        user_id: UUID,
        policy_id: str,
        metric_type: str,
        current_value: float,
        threshold: float,
        severity: str,
        message: str,
    ) -> Optional[Dict[str, Any]]:
        """Create an alert if one doesn't already exist for this policy+metric."""
        try:
            # Check for existing unacknowledged alert
            existing = (
                self.supabase.table("sla_alerts")
                .select("id")
                .eq("user_id", str(user_id))
                .eq("policy_id", policy_id)
                .eq("metric_type", metric_type)
                .eq("acknowledged", False)
                .limit(1)
                .execute()
            )

            if existing.data and len(existing.data) > 0:
                return None  # Alert already exists

            alert = {
                "user_id": str(user_id),
                "policy_id": policy_id,
                "metric_type": metric_type,
                "current_value": current_value,
                "threshold": threshold,
                "severity": severity,
                "message": message,
            }
            result = self.supabase.table("sla_alerts").insert(alert).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
        except Exception as e:
            logger.error(f"Error creating SLA alert: {e}")
        return None


# Global instance
sla_service = SLAService()

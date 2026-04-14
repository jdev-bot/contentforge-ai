"""
Alert Service for Content Performance Monitoring.

This service handles:
- Checking content metrics against alert rules
- Detecting viral content (sudden engagement spikes)
- Detecting declining engagement
- Triggering alerts when thresholds are crossed
- Managing alert lifecycle
"""

import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Types of content performance alerts."""

    VIRAL = "viral"
    DECLINING = "declining"
    MILESTONE = "milestone"
    ERROR = "error"


class AlertStatus(str, Enum):
    """Status of an alert."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class MetricName(str, Enum):
    """Available content metrics for alerting."""

    VIEWS = "views"
    ENGAGEMENT = "engagement"
    CLICKS = "clicks"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"


class AlertOperator(str, Enum):
    """Comparison operators for alert rules."""

    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUALS = "equals"
    PERCENTAGE_CHANGE = "percentage_change"


class AlertService:
    """Service for managing content performance alerts."""

    # Viral detection thresholds
    VIRAL_VELOCITY_THRESHOLD = 3.0  # 3x normal engagement rate
    VIRAL_MIN_VIEWS = 1000  # Minimum views to consider viral
    VIRAL_TIME_WINDOW_HOURS = 24

    # Declining engagement thresholds
    DECLINING_THRESHOLD = 0.5  # 50% drop from baseline
    DECLINING_TIME_WINDOW_DAYS = 7

    def __init__(self):
        """Initialize the alert service."""
        self._supabase = None

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    @supabase.setter
    def supabase(self, value):
        self._supabase = value

    async def check_content_metrics(
        self, content_id: UUID, user_id: UUID, metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Check content metrics against all active alert rules and thresholds.

        Args:
            content_id: The content ID
            user_id: The user ID
            metrics: Current metrics (views, engagement, clicks, etc.)

        Returns:
            List of triggered alerts
        """
        triggered_alerts = []

        # 1. Check user-defined alert rules
        rule_alerts = await self._check_alert_rules(content_id, user_id, metrics)
        triggered_alerts.extend(rule_alerts)

        # 2. Check for viral content (automatic)
        viral_alert = await self._detect_viral_content(content_id, user_id, metrics)
        if viral_alert:
            triggered_alerts.append(viral_alert)

        # 3. Check for declining engagement (automatic)
        declining_alert = await self._detect_declining_engagement(
            content_id, user_id, metrics
        )
        if declining_alert:
            triggered_alerts.append(declining_alert)

        # 4. Check for milestone achievements
        milestone_alerts = await self._check_milestones(content_id, user_id, metrics)
        triggered_alerts.extend(milestone_alerts)

        # Store metrics history for future comparisons
        await self._store_metrics_history(content_id, user_id, metrics)

        return triggered_alerts

    async def _check_alert_rules(
        self, content_id: UUID, user_id: UUID, metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Check metrics against user-defined alert rules.

        Args:
            content_id: The content ID
            user_id: The user ID
            metrics: Current metrics

        Returns:
            List of triggered rule-based alerts
        """
        triggered = []

        try:
            # Get all active alert rules for the user
            result = (
                self.supabase.table("alert_rules")
                .select("*")
                .eq("user_id", str(user_id))
                .eq("is_enabled", True)
                .execute()
            )

            rules = result.data or []

            for rule in rules:
                metric_name = rule.get("metric_name")
                operator = rule.get("operator")
                threshold = rule.get("threshold_value")

                if metric_name not in metrics:
                    continue

                current_value = metrics[metric_name]
                triggered_alert = None

                # Check if condition is met
                if operator == AlertOperator.GREATER_THAN.value:
                    if current_value > threshold:
                        triggered_alert = self._create_alert_from_rule(
                            rule, content_id, user_id, current_value, threshold
                        )

                elif operator == AlertOperator.LESS_THAN.value:
                    if current_value < threshold:
                        triggered_alert = self._create_alert_from_rule(
                            rule, content_id, user_id, current_value, threshold
                        )

                elif operator == AlertOperator.EQUALS.value:
                    if abs(current_value - threshold) < 0.001:  # Float comparison
                        triggered_alert = self._create_alert_from_rule(
                            rule, content_id, user_id, current_value, threshold
                        )

                elif operator == AlertOperator.PERCENTAGE_CHANGE.value:
                    # Get previous value from history
                    prev_value = await self._get_previous_metric_value(
                        content_id, user_id, metric_name
                    )
                    if prev_value and prev_value > 0:
                        change_pct = (
                            abs((current_value - prev_value) / prev_value) * 100
                        )
                        if change_pct >= threshold:
                            triggered_alert = self._create_alert_from_rule(
                                rule,
                                content_id,
                                user_id,
                                current_value,
                                threshold,
                                extra_message=f"Change: {change_pct:.1f}%",
                            )

                if triggered_alert:
                    # Check for duplicate active alerts
                    if not await self._alert_exists(
                        content_id, user_id, rule.get("alert_type"), metric_name
                    ):
                        saved_alert = await self._save_alert(triggered_alert)
                        if saved_alert:
                            triggered.append(saved_alert)

        except Exception as e:
            logger.error(f"Error checking alert rules: {e}")

        return triggered

    def _create_alert_from_rule(
        self,
        rule: Dict[str, Any],
        content_id: UUID,
        user_id: UUID,
        current_value: float,
        threshold: float,
        extra_message: str = "",
    ) -> Dict[str, Any]:
        """Create an alert dictionary from a rule."""
        alert_type = rule.get("alert_type")
        metric_name = rule.get("metric_name")
        rule_name = rule.get("name")

        message = f"{rule_name}: {metric_name} is {current_value:.1f} (threshold: {threshold:.1f})"
        if extra_message:
            message += f" {extra_message}"

        return {
            "user_id": str(user_id),
            "alert_type": alert_type,
            "content_id": str(content_id),
            "metric_name": metric_name,
            "threshold_value": threshold,
            "current_value": current_value,
            "status": AlertStatus.ACTIVE.value,
            "message": message,
        }

    async def _detect_viral_content(
        self, content_id: UUID, user_id: UUID, metrics: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if content is going viral based on engagement velocity.

        Args:
            content_id: The content ID
            user_id: The user ID
            metrics: Current metrics

        Returns:
            Viral alert if detected, None otherwise
        """
        views = metrics.get(MetricName.VIEWS.value, 0)
        engagement = metrics.get(MetricName.ENGAGEMENT.value, 0)

        # Minimum threshold for viral consideration
        if views < self.VIRAL_MIN_VIEWS:
            return None

        try:
            # Get historical metrics for comparison
            history = await self._get_metrics_history(
                content_id, user_id, hours=self.VIRAL_TIME_WINDOW_HOURS
            )

            if len(history) < 2:
                return None

            # Calculate velocity (engagement rate change)
            recent = history[-1]
            previous = history[0]

            if previous.get("value", 0) > 0:
                velocity = recent.get("value", 0) / previous.get("value", 0)

                if velocity >= self.VIRAL_VELOCITY_THRESHOLD:
                    # Check if we already have an active viral alert for this content
                    if not await self._alert_exists(
                        content_id,
                        user_id,
                        AlertType.VIRAL.value,
                        MetricName.ENGAGEMENT.value,
                    ):
                        alert = {
                            "user_id": str(user_id),
                            "alert_type": AlertType.VIRAL.value,
                            "content_id": str(content_id),
                            "metric_name": MetricName.ENGAGEMENT.value,
                            "threshold_value": self.VIRAL_VELOCITY_THRESHOLD,
                            "current_value": velocity,
                            "status": AlertStatus.ACTIVE.value,
                            "message": f"🔥 Your content is going viral! Engagement increased {velocity:.1f}x in the last {self.VIRAL_TIME_WINDOW_HOURS}h. Views: {int(views):,}",
                        }
                        return await self._save_alert(alert)

        except Exception as e:
            logger.error(f"Error detecting viral content: {e}")

        return None

    async def _detect_declining_engagement(
        self, content_id: UUID, user_id: UUID, metrics: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if content engagement is declining significantly.

        Args:
            content_id: The content ID
            user_id: The user ID
            metrics: Current metrics

        Returns:
            Declining alert if detected, None otherwise
        """
        engagement = metrics.get(MetricName.ENGAGEMENT.value, 0)

        try:
            # Get historical metrics
            history = await self._get_metrics_history(
                content_id, user_id, days=self.DECLINING_TIME_WINDOW_DAYS
            )

            if len(history) < 2:
                return None

            # Calculate average engagement from first half vs second half
            mid_point = len(history) // 2
            first_half = history[:mid_point]
            second_half = history[mid_point:]

            if not first_half or not second_half:
                return None

            first_avg = sum(h.get("value", 0) for h in first_half) / len(first_half)
            second_avg = sum(h.get("value", 0) for h in second_half) / len(second_half)

            if first_avg > 0:
                decline_ratio = second_avg / first_avg

                if decline_ratio <= self.DECLINING_THRESHOLD:
                    # Check if we already have an active declining alert
                    if not await self._alert_exists(
                        content_id,
                        user_id,
                        AlertType.DECLINING.value,
                        MetricName.ENGAGEMENT.value,
                    ):
                        alert = {
                            "user_id": str(user_id),
                            "alert_type": AlertType.DECLINING.value,
                            "content_id": str(content_id),
                            "metric_name": MetricName.ENGAGEMENT.value,
                            "threshold_value": self.DECLINING_THRESHOLD,
                            "current_value": decline_ratio,
                            "status": AlertStatus.ACTIVE.value,
                            "message": f"📉 Engagement declining: {((1-decline_ratio)*100):.0f}% drop over the last {self.DECLINING_TIME_WINDOW_DAYS} days. Consider refreshing this content.",
                        }
                        return await self._save_alert(alert)

        except Exception as e:
            logger.error(f"Error detecting declining engagement: {e}")

        return None

    async def _check_milestones(
        self, content_id: UUID, user_id: UUID, metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Check for milestone achievements (e.g., 1K, 10K, 100K views).

        Args:
            content_id: The content ID
            user_id: The user ID
            metrics: Current metrics

        Returns:
            List of milestone alerts
        """
        milestones = []
        views = metrics.get(MetricName.VIEWS.value, 0)

        # Define milestone thresholds
        milestone_thresholds = [1000, 5000, 10000, 50000, 100000, 500000, 1000000]

        for threshold in milestone_thresholds:
            if views >= threshold:
                # Check if this milestone was already alerted
                if not await self._milestone_alerted(
                    content_id, user_id, MetricName.VIEWS.value, threshold
                ):
                    alert = {
                        "user_id": str(user_id),
                        "alert_type": AlertType.MILESTONE.value,
                        "content_id": str(content_id),
                        "metric_name": MetricName.VIEWS.value,
                        "threshold_value": float(threshold),
                        "current_value": views,
                        "status": AlertStatus.ACTIVE.value,
                        "message": f"🎉 Milestone reached! Your content hit {threshold:,} views!",
                    }
                    saved = await self._save_alert(alert)
                    if saved:
                        milestones.append(saved)

        return milestones

    async def _alert_exists(
        self, content_id: UUID, user_id: UUID, alert_type: str, metric_name: str
    ) -> bool:
        """Check if an active alert already exists for this content/type/metric."""
        try:
            result = (
                self.supabase.table("content_alerts")
                .select("id")
                .eq("user_id", str(user_id))
                .eq("content_id", str(content_id))
                .eq("alert_type", alert_type)
                .eq("metric_name", metric_name)
                .eq("status", AlertStatus.ACTIVE.value)
                .limit(1)
                .execute()
            )

            return len(result.data or []) > 0

        except Exception as e:
            logger.error(f"Error checking alert existence: {e}")
            return False

    async def _milestone_alerted(
        self, content_id: UUID, user_id: UUID, metric_name: str, threshold: float
    ) -> bool:
        """Check if a specific milestone was already alerted."""
        try:
            result = (
                self.supabase.table("content_alerts")
                .select("id")
                .eq("user_id", str(user_id))
                .eq("content_id", str(content_id))
                .eq("alert_type", AlertType.MILESTONE.value)
                .eq("metric_name", metric_name)
                .eq("threshold_value", threshold)
                .limit(1)
                .execute()
            )

            return len(result.data or []) > 0

        except Exception as e:
            logger.error(f"Error checking milestone alert: {e}")
            return False

    async def _save_alert(self, alert: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save an alert to the database and create notification."""
        try:
            # Insert the alert
            result = self.supabase.table("content_alerts").insert(alert).execute()

            if result.data and len(result.data) > 0:
                saved_alert = result.data[0]

                # Create in-app notification
                await self._create_in_app_notification(saved_alert)

                return saved_alert

        except Exception as e:
            logger.error(f"Error saving alert: {e}")

        return None

    async def _create_in_app_notification(self, alert: Dict[str, Any]):
        """Create an in-app notification for an alert."""
        try:
            alert_type = alert.get("alert_type")
            message = alert.get("message", "")

            # Determine notification type and title
            if alert_type == AlertType.VIRAL.value:
                title = "🔥 Viral Content Alert"
                notif_type = "success"
            elif alert_type == AlertType.DECLINING.value:
                title = "📉 Engagement Declining"
                notif_type = "warning"
            elif alert_type == AlertType.MILESTONE.value:
                title = "🎉 Milestone Reached"
                notif_type = "success"
            else:
                title = "Content Alert"
                notif_type = "info"

            notification = {
                "user_id": alert.get("user_id"),
                "alert_id": alert.get("id"),
                "title": title,
                "message": message,
                "type": notif_type,
                "is_read": False,
            }

            self.supabase.table("in_app_notifications").insert(notification).execute()

        except Exception as e:
            logger.error(f"Error creating in-app notification: {e}")

    async def _store_metrics_history(
        self, content_id: UUID, user_id: UUID, metrics: Dict[str, float]
    ):
        """Store current metrics for historical comparison."""
        try:
            for metric_name, value in metrics.items():
                record = {
                    "content_id": str(content_id),
                    "user_id": str(user_id),
                    "metric_name": metric_name,
                    "value": value,
                    "recorded_at": datetime.now(timezone.utc).isoformat(),
                }
                self.supabase.table("alert_metrics_history").insert(record).execute()

        except Exception as e:
            logger.error(f"Error storing metrics history: {e}")

    async def _get_metrics_history(
        self,
        content_id: UUID,
        user_id: UUID,
        hours: Optional[int] = None,
        days: Optional[int] = None,
        metric_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get historical metrics for a content item."""
        try:
            query = (
                self.supabase.table("alert_metrics_history")
                .select("*")
                .eq("content_id", str(content_id))
                .eq("user_id", str(user_id))
                .order("recorded_at", desc=False)
            )

            if metric_name:
                query = query.eq("metric_name", metric_name)

            if hours:
                cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
                query = query.gte("recorded_at", cutoff.isoformat())

            if days:
                cutoff = datetime.now(timezone.utc) - timedelta(days=days)
                query = query.gte("recorded_at", cutoff.isoformat())

            result = query.execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Error getting metrics history: {e}")
            return []

    async def _get_previous_metric_value(
        self, content_id: UUID, user_id: UUID, metric_name: str
    ) -> Optional[float]:
        """Get the most recent previous value for a metric."""
        try:
            result = (
                self.supabase.table("alert_metrics_history")
                .select("value")
                .eq("content_id", str(content_id))
                .eq("user_id", str(user_id))
                .eq("metric_name", metric_name)
                .order("recorded_at", desc=True)
                .limit(1)
                .execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0].get("value")

        except Exception as e:
            logger.error(f"Error getting previous metric value: {e}")

        return None

    async def acknowledge_alert(self, alert_id: UUID, user_id: UUID) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: The alert ID
            user_id: The user ID (for verification)

        Returns:
            True if successful, False otherwise
        """
        try:
            result = (
                self.supabase.table("content_alerts")
                .update(
                    {
                        "status": AlertStatus.ACKNOWLEDGED.value,
                        "acknowledged_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                .eq("id", str(alert_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            return len(result.data or []) > 0

        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False

    async def resolve_alert(self, alert_id: UUID, user_id: UUID) -> bool:
        """
        Mark an alert as resolved.

        Args:
            alert_id: The alert ID
            user_id: The user ID (for verification)

        Returns:
            True if successful, False otherwise
        """
        try:
            result = (
                self.supabase.table("content_alerts")
                .update(
                    {
                        "status": AlertStatus.RESOLVED.value,
                    }
                )
                .eq("id", str(alert_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            return len(result.data or []) > 0

        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False

    async def get_user_alerts(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        alert_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get alerts for a user.

        Args:
            user_id: The user ID
            status: Filter by status (optional)
            alert_type: Filter by type (optional)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of alerts
        """
        try:
            query = (
                self.supabase.table("content_alerts")
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
            )

            if status:
                query = query.eq("status", status)

            if alert_type:
                query = query.eq("alert_type", alert_type)

            query = query.range(offset, offset + limit - 1)

            result = query.execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Error getting user alerts: {e}")
            return []

    async def get_unread_alert_count(self, user_id: UUID) -> int:
        """
        Get count of active (unread) alerts for a user.

        Args:
            user_id: The user ID

        Returns:
            Count of active alerts
        """
        try:
            result = (
                self.supabase.table("content_alerts")
                .select("id", count="exact")
                .eq("user_id", str(user_id))
                .eq("status", AlertStatus.ACTIVE.value)
                .execute()
            )

            return result.count or 0

        except Exception as e:
            logger.error(f"Error getting unread alert count: {e}")
            return 0

    async def get_alert_rules(
        self, user_id: UUID, is_enabled: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get alert rules for a user.

        Args:
            user_id: The user ID
            is_enabled: Filter by enabled status (optional)

        Returns:
            List of alert rules
        """
        try:
            query = (
                self.supabase.table("alert_rules")
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
            )

            if is_enabled is not None:
                query = query.eq("is_enabled", is_enabled)

            result = query.execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Error getting alert rules: {e}")
            return []

    async def create_alert_rule(
        self,
        user_id: UUID,
        name: str,
        alert_type: str,
        metric_name: str,
        operator: str,
        threshold_value: float,
        notification_channels: List[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new alert rule.

        Args:
            user_id: The user ID
            name: Rule name
            alert_type: Type of alert
            metric_name: Metric to monitor
            operator: Comparison operator
            threshold_value: Threshold value
            notification_channels: List of notification channels

        Returns:
            Created rule or None
        """
        try:
            rule = {
                "user_id": str(user_id),
                "name": name,
                "alert_type": alert_type,
                "metric_name": metric_name,
                "operator": operator,
                "threshold_value": threshold_value,
                "is_enabled": True,
                "notification_channels": notification_channels,
            }

            result = self.supabase.table("alert_rules").insert(rule).execute()

            if result.data and len(result.data) > 0:
                return result.data[0]

        except Exception as e:
            logger.error(f"Error creating alert rule: {e}")

        return None

    async def update_alert_rule(
        self, rule_id: UUID, user_id: UUID, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update an alert rule.

        Args:
            rule_id: The rule ID
            user_id: The user ID (for verification)
            updates: Dictionary of fields to update

        Returns:
            Updated rule or None
        """
        try:
            # Remove fields that shouldn't be updated
            updates.pop("id", None)
            updates.pop("user_id", None)
            updates.pop("created_at", None)

            result = (
                self.supabase.table("alert_rules")
                .update(updates)
                .eq("id", str(rule_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0]

        except Exception as e:
            logger.error(f"Error updating alert rule: {e}")

        return None

    async def delete_alert_rule(self, rule_id: UUID, user_id: UUID) -> bool:
        """
        Delete an alert rule.

        Args:
            rule_id: The rule ID
            user_id: The user ID (for verification)

        Returns:
            True if successful, False otherwise
        """
        try:
            result = (
                self.supabase.table("alert_rules")
                .delete()
                .eq("id", str(rule_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            return len(result.data or []) > 0

        except Exception as e:
            logger.error(f"Error deleting alert rule: {e}")
            return False

    async def get_in_app_notifications(
        self, user_id: UUID, is_read: Optional[bool] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get in-app notifications for a user.

        Args:
            user_id: The user ID
            is_read: Filter by read status (optional)
            limit: Maximum number of results

        Returns:
            List of notifications
        """
        try:
            query = (
                self.supabase.table("in_app_notifications")
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
                .limit(limit)
            )

            if is_read is not None:
                query = query.eq("is_read", is_read)

            result = query.execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Error getting in-app notifications: {e}")
            return []

    async def mark_notification_read(
        self, notification_id: UUID, user_id: UUID
    ) -> bool:
        """
        Mark an in-app notification as read.

        Args:
            notification_id: The notification ID
            user_id: The user ID (for verification)

        Returns:
            True if successful, False otherwise
        """
        try:
            result = (
                self.supabase.table("in_app_notifications")
                .update(
                    {
                        "is_read": True,
                        "read_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                .eq("id", str(notification_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            return len(result.data or []) > 0

        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False


# Global instance
alert_service = AlertService()

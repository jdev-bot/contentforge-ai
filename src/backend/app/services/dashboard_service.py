"""
Dashboard Service

Handles custom dashboard and widget management with live data fetching.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.core.supabase import get_supabase_admin_client, get_supabase_client

logger = logging.getLogger(__name__)

VALID_WIDGET_TYPES = [
    "metric_card", "line_chart", "bar_chart", "pie_chart",
    "table", "counter", "recent_list",
]

VALID_DATA_SOURCES = [
    "content_count", "distribution_stats", "quality_scores",
    "sentiment_summary", "team_activity", "usage_stats",
]

VALID_REFRESH_INTERVALS = [30, 60, 300, 900, 1800]  # seconds


class DashboardService:
    """Service for custom dashboards and widgets."""

    def __init__(self):
        self._supabase = None
        self._admin_supabase = None

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    @supabase.setter
    def supabase(self, value):
        self._supabase = value

    @property
    def admin_supabase(self):
        if self._admin_supabase is None:
            self._admin_supabase = get_supabase_admin_client()
        return self._admin_supabase

    # ── Dashboard CRUD ────────────────────────────────────────────

    def list_dashboards(self, user_id: str) -> List[Dict[str, Any]]:
        """List all dashboards for a user."""
        response = (
            self.supabase.table("dashboards")
            .select("id, user_id, name, description, layout_config, is_default, created_at, updated_at")
            .eq("user_id", user_id)
            .order("is_default", desc=True)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []

    def create_dashboard(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        layout_config: Optional[Dict] = None,
        is_default: bool = False,
    ) -> Dict[str, Any]:
        """Create a new dashboard."""
        if is_default:
            self._unset_default_dashboards(user_id)

        payload = {
            "id": str(uuid4()),
            "user_id": user_id,
            "name": name,
            "description": description,
            "layout_config": layout_config or {},
            "is_default": is_default,
        }
        response = self.supabase.table("dashboards").insert(payload).execute()
        return response.data[0] if response.data else payload

    def get_dashboard(self, dashboard_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a dashboard with its widgets."""
        dash_resp = (
            self.supabase.table("dashboards")
            .select("id, user_id, name, description, layout_config, is_default, created_at, updated_at")
            .eq("id", dashboard_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        if not dash_resp.data:
            return None

        widgets_resp = (
            self.supabase.table("dashboard_widgets")
            .select("id, dashboard_id, widget_type, title, data_source, refresh_interval, size, position, config, created_at, updated_at")
            .eq("dashboard_id", dashboard_id)
            .order("position", desc=False)
            .execute()
        )

        dashboard = dash_resp.data
        dashboard["widgets"] = widgets_resp.data or []
        return dashboard

    def update_dashboard(
        self,
        dashboard_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        layout_config: Optional[Dict] = None,
        is_default: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a dashboard."""
        existing = self.get_dashboard(dashboard_id, user_id)
        if not existing:
            return None

        updates: Dict[str, Any] = {}
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if layout_config is not None:
            updates["layout_config"] = layout_config
        if is_default is not None:
            if is_default:
                self._unset_default_dashboards(user_id)
            updates["is_default"] = is_default

        if not updates:
            return existing

        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        response = (
            self.supabase.table("dashboards")
            .update(updates)
            .eq("id", dashboard_id)
            .eq("user_id", user_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def delete_dashboard(self, dashboard_id: str, user_id: str) -> bool:
        """Delete a dashboard and its widgets."""
        existing = self.get_dashboard(dashboard_id, user_id)
        if not existing:
            return False

        # Delete widgets first
        self.supabase.table("dashboard_widgets").delete().eq("dashboard_id", dashboard_id).execute()
        # Delete dashboard
        self.supabase.table("dashboards").delete().eq("id", dashboard_id).eq("user_id", user_id).execute()
        return True

    # ── Widget CRUD ────────────────────────────────────────────────

    def add_widget(
        self,
        dashboard_id: str,
        user_id: str,
        widget_type: str,
        title: str,
        data_source: str,
        refresh_interval: int = 60,
        size: Optional[Dict] = None,
        position: int = 0,
        config: Optional[Dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """Add a widget to a dashboard."""
        existing = self.get_dashboard(dashboard_id, user_id)
        if not existing:
            return None

        if widget_type not in VALID_WIDGET_TYPES:
            raise ValueError(f"Invalid widget type: {widget_type}")
        if data_source not in VALID_DATA_SOURCES:
            raise ValueError(f"Invalid data source: {data_source}")
        if refresh_interval not in VALID_REFRESH_INTERVALS:
            raise ValueError(f"Invalid refresh interval: {refresh_interval}")

        payload = {
            "id": str(uuid4()),
            "dashboard_id": dashboard_id,
            "widget_type": widget_type,
            "title": title,
            "data_source": data_source,
            "refresh_interval": refresh_interval,
            "size": size or {"w": 4, "h": 3},
            "position": position,
            "config": config or {},
        }
        response = self.supabase.table("dashboard_widgets").insert(payload).execute()
        return response.data[0] if response.data else payload

    def update_widget(
        self,
        dashboard_id: str,
        widget_id: str,
        user_id: str,
        widget_type: Optional[str] = None,
        title: Optional[str] = None,
        data_source: Optional[str] = None,
        refresh_interval: Optional[int] = None,
        size: Optional[Dict] = None,
        position: Optional[int] = None,
        config: Optional[Dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a widget's configuration."""
        # Verify ownership via dashboard
        existing = self.get_dashboard(dashboard_id, user_id)
        if not existing:
            return None

        # Verify widget belongs to this dashboard
        widget_resp = (
            self.supabase.table("dashboard_widgets")
            .select("id")
            .eq("id", widget_id)
            .eq("dashboard_id", dashboard_id)
            .maybe_single()
            .execute()
        )
        if not widget_resp.data:
            return None

        updates: Dict[str, Any] = {}
        if widget_type is not None:
            if widget_type not in VALID_WIDGET_TYPES:
                raise ValueError(f"Invalid widget type: {widget_type}")
            updates["widget_type"] = widget_type
        if title is not None:
            updates["title"] = title
        if data_source is not None:
            if data_source not in VALID_DATA_SOURCES:
                raise ValueError(f"Invalid data source: {data_source}")
            updates["data_source"] = data_source
        if refresh_interval is not None:
            if refresh_interval not in VALID_REFRESH_INTERVALS:
                raise ValueError(f"Invalid refresh interval: {refresh_interval}")
            updates["refresh_interval"] = refresh_interval
        if size is not None:
            updates["size"] = size
        if position is not None:
            updates["position"] = position
        if config is not None:
            updates["config"] = config

        if not updates:
            return widget_resp.data

        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        response = (
            self.supabase.table("dashboard_widgets")
            .update(updates)
            .eq("id", widget_id)
            .eq("dashboard_id", dashboard_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def delete_widget(self, dashboard_id: str, widget_id: str, user_id: str) -> bool:
        """Remove a widget from a dashboard."""
        existing = self.get_dashboard(dashboard_id, user_id)
        if not existing:
            return False

        widget_resp = (
            self.supabase.table("dashboard_widgets")
            .delete()
            .eq("id", widget_id)
            .eq("dashboard_id", dashboard_id)
            .execute()
        )
        return bool(widget_resp.data)

    # ── Live Data ──────────────────────────────────────────────────

    def get_dashboard_data(self, dashboard_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get live data for all widgets in a dashboard."""
        dashboard = self.get_dashboard(dashboard_id, user_id)
        if not dashboard:
            return None

        widgets_data = []
        for widget in dashboard.get("widgets", []):
            data = self._fetch_widget_data(widget["data_source"], user_id)
            widgets_data.append({
                "widget_id": widget["id"],
                "widget_type": widget["widget_type"],
                "title": widget["title"],
                "data_source": widget["data_source"],
                "refresh_interval": widget["refresh_interval"],
                "data": data,
            })

        return {
            "dashboard_id": dashboard_id,
            "widgets": widgets_data,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    def _fetch_widget_data(self, data_source: str, user_id: str) -> Dict[str, Any]:
        """Fetch live data for a given data source."""
        try:
            fetcher = getattr(self, f"_fetch_{data_source}", None)
            if fetcher:
                return fetcher(user_id)
            return {"error": f"Unknown data source: {data_source}"}
        except Exception as e:
            logger.error(f"Error fetching {data_source}: {e}")
            return {"error": str(e)}

    def _fetch_content_count(self, user_id: str) -> Dict[str, Any]:
        """Fetch content count data."""
        resp = (
            self.supabase.table("content")
            .select("status")
            .eq("user_id", user_id)
            .execute()
        )
        items = resp.data or []
        by_status: Dict[str, int] = {}
        for item in items:
            s = item.get("status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1

        return {
            "total": len(items),
            "by_status": by_status,
        }

    def _fetch_distribution_stats(self, user_id: str) -> Dict[str, Any]:
        """Fetch distribution statistics."""
        resp = (
            self.supabase.table("distributions")
            .select("platform, status")
            .eq("user_id", user_id)
            .execute()
        )
        items = resp.data or []
        by_platform: Dict[str, int] = {}
        by_status: Dict[str, int] = {}
        for item in items:
            p = item.get("platform", "unknown")
            s = item.get("status", "unknown")
            by_platform[p] = by_platform.get(p, 0) + 1
            by_status[s] = by_status.get(s, 0) + 1

        total = len(items)
        published = by_status.get("published", 0)
        return {
            "total": total,
            "by_platform": by_platform,
            "by_status": by_status,
            "success_rate": round(published / total * 100, 1) if total else 0,
        }

    def _fetch_quality_scores(self, user_id: str) -> Dict[str, Any]:
        """Fetch quality score data."""
        try:
            resp = (
                self.supabase.table("quality_scores")
                .select("score, category")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(100)
                .execute()
            )
            items = resp.data or []
            if not items:
                return {"average": 0, "count": 0, "by_category": {}}

            total_score = sum(i.get("score", 0) for i in items)
            by_category: Dict[str, Any] = {}
            for i in items:
                cat = i.get("category", "uncategorized")
                if cat not in by_category:
                    by_category[cat] = {"scores": [], "average": 0}
                by_category[cat]["scores"].append(i.get("score", 0))

            for cat_data in by_category.values():
                scores = cat_data["scores"]
                cat_data["average"] = round(sum(scores) / len(scores), 1) if scores else 0
                del cat_data["scores"]

            return {
                "average": round(total_score / len(items), 1),
                "count": len(items),
                "by_category": by_category,
            }
        except Exception:
            return {"average": 0, "count": 0, "by_category": {}}

    def _fetch_sentiment_summary(self, user_id: str) -> Dict[str, Any]:
        """Fetch sentiment analysis summary."""
        try:
            resp = (
                self.supabase.table("sentiment_results")
                .select("sentiment, score")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(100)
                .execute()
            )
            items = resp.data or []
            by_sentiment: Dict[str, int] = {}
            scores = []
            for i in items:
                s = i.get("sentiment", "neutral")
                by_sentiment[s] = by_sentiment.get(s, 0) + 1
                if i.get("score") is not None:
                    scores.append(i["score"])

            return {
                "total": len(items),
                "by_sentiment": by_sentiment,
                "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
            }
        except Exception:
            return {"total": 0, "by_sentiment": {}, "average_score": 0}

    def _fetch_team_activity(self, user_id: str) -> Dict[str, Any]:
        """Fetch team activity data."""
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        try:
            resp = (
                self.supabase.table("content")
                .select("id, created_at")
                .eq("user_id", user_id)
                .gte("created_at", seven_days_ago)
                .order("created_at", desc=True)
                .limit(50)
                .execute()
            )
            items = resp.data or []
            return {
                "recent_items_count": len(items),
                "items": items[:10],
                "period_days": 7,
            }
        except Exception:
            return {"recent_items_count": 0, "items": [], "period_days": 7}

    def _fetch_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Fetch usage statistics."""
        try:
            resp = (
                self.supabase.table("usage_tracking")
                .select("event_type, tokens_used, created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(100)
                .execute()
            )
            items = resp.data or []
            total_tokens = sum(i.get("tokens_used", 0) or 0 for i in items)
            by_event: Dict[str, int] = {}
            for i in items:
                et = i.get("event_type", "unknown")
                by_event[et] = by_event.get(et, 0) + 1

            return {
                "total_events": len(items),
                "total_tokens": total_tokens,
                "by_event_type": by_event,
            }
        except Exception:
            return {"total_events": 0, "total_tokens": 0, "by_event_type": {}}

    # ── Helpers ────────────────────────────────────────────────────

    def _unset_default_dashboards(self, user_id: str):
        """Remove is_default from all user dashboards."""
        self.supabase.table("dashboards").update({"is_default": False}).eq("user_id", user_id).eq("is_default", True).execute()


# Singleton instance
dashboard_service = DashboardService()
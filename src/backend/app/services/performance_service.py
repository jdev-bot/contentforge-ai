"""
Content Performance Analytics Service.

Advanced analytics for measuring content impact:
- Engagement metrics (views, shares, comments, conversions)
- Performance scoring per content piece
- Time-series performance data
- Content funnel tracking (create → publish → engage → convert)
- Cohort analysis (group content by publish date, compare performance)
- Attribution modeling (which content drives conversions)
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.cache import cache
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

CACHE_PREFIX = "performance"
CACHE_TTL_SECONDS = 300  # 5 minutes

# Weights for composite performance score
PERFORMANCE_DIMENSIONS = {
    "views": 0.15,
    "shares": 0.20,
    "comments": 0.20,
    "conversions": 0.30,
    "engagement_rate": 0.15,
}

# Funnel stage order
FUNNEL_STAGES = ["created", "published", "engaged", "converted"]


class PerformanceService:
    """Service for content performance analytics."""

    def __init__(self):
        self._supabase = None

    @property
    def supabase(self):
        """Lazy Supabase client init."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    # ------------------------------------------------------------------ #
    #  Event Tracking                                                       #
    # ------------------------------------------------------------------ #

    async def track_event(
        self,
        user_id: UUID,
        content_id: UUID,
        event_type: str,
        value: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record a performance event for a content piece.

        event_type: one of 'view', 'share', 'comment', 'conversion'
        value: numeric value (default 1 for counting events)
        metadata: optional JSON-safe dict with extra context
        """
        if event_type not in ("view", "share", "comment", "conversion"):
            raise ValueError(
                f"Invalid event_type '{event_type}'. Must be view/share/comment/conversion."
            )

        row = {
            "user_id": str(user_id),
            "content_id": str(content_id),
            "event_type": event_type,
            "value": value,
            "metadata": metadata or {},
        }

        result = self.supabase.table("performance_events").insert(row).execute()

        # Invalidate relevant caches
        cache.delete(f"overview:{user_id}", prefix=CACHE_PREFIX)
        cache.delete(f"content:{content_id}", prefix=CACHE_PREFIX)
        cache.delete(f"funnel:{user_id}", prefix=CACHE_PREFIX)
        cache.delete(f"trends:{user_id}", prefix=CACHE_PREFIX)
        cache.delete(f"attribution:{user_id}", prefix=CACHE_PREFIX)

        return result.data[0] if result.data else row

    # ------------------------------------------------------------------ #
    #  Overview                                                             #
    # ------------------------------------------------------------------ #

    async def get_overview(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """
        Overall performance summary across all content for the user.

        Returns total counts, averages, and a performance score.
        """
        cache_key = f"overview:{user_id}:{days}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        since = (datetime.now() - timedelta(days=days)).isoformat()

        # Fetch performance events
        events_result = (
            self.supabase.table("performance_events")
            .select("event_type, value, created_at")
            .eq("user_id", str(user_id))
            .gte("created_at", since)
            .execute()
        )
        events = events_result.data or []

        # Aggregate by event type
        totals = {"views": 0, "shares": 0, "comments": 0, "conversions": 0}
        for ev in events:
            et = ev.get("event_type", "")
            if et in totals:
                totals[et] += ev.get("value", 1)

        # Fetch content count for averages
        content_result = (
            self.supabase.table("content")
            .select("id")
            .eq("user_id", str(user_id))
            .execute()
        )
        total_content = len(content_result.data or [])

        # Compute engagement rate: (shares + comments) / max(views, 1)
        engagement_rate = (totals["shares"] + totals["comments"]) / max(
            totals["views"], 1
        )
        engagement_rate = min(round(engagement_rate, 4), 1.0)

        # Compute composite performance score (0-100)
        performance_score = self._compute_performance_score(
            totals, engagement_rate, total_content
        )

        overview = {
            "total_views": totals["views"],
            "total_shares": totals["shares"],
            "total_comments": totals["comments"],
            "total_conversions": totals["conversions"],
            "total_content": total_content,
            "avg_views_per_content": round(totals["views"] / max(total_content, 1), 2),
            "avg_conversions_per_content": round(
                totals["conversions"] / max(total_content, 1), 2
            ),
            "engagement_rate": engagement_rate,
            "performance_score": performance_score,
            "period_days": days,
        }

        cache.set(cache_key, overview, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return overview

    # ------------------------------------------------------------------ #
    #  Per-Content Metrics                                                  #
    # ------------------------------------------------------------------ #

    async def get_content_metrics(
        self, content_id: UUID, user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Detailed performance metrics for a single content piece.

        Returns views, shares, comments, conversions, score, and event timeline.
        """
        cache_key = f"content:{content_id}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        # Verify content belongs to user
        content_result = (
            self.supabase.table("content")
            .select("id, title, created_at, status")
            .eq("id", str(content_id))
            .eq("user_id", str(user_id))
            .execute()
        )
        if not content_result.data:
            return None

        content_info = content_result.data[0]

        # Fetch all performance events for this content
        events_result = (
            self.supabase.table("performance_events")
            .select("event_type, value, created_at, metadata")
            .eq("content_id", str(content_id))
            .order("created_at", desc=False)
            .execute()
        )
        events = events_result.data or []

        # Aggregate
        totals = {"views": 0, "shares": 0, "comments": 0, "conversions": 0}
        for ev in events:
            et = ev.get("event_type", "")
            if et in totals:
                totals[et] += ev.get("value", 1)

        engagement_rate = (totals["shares"] + totals["comments"]) / max(
            totals["views"], 1
        )
        engagement_rate = min(round(engagement_rate, 4), 1.0)

        performance_score = self._compute_performance_score(totals, engagement_rate, 1)

        # Build daily time-series for this content
        daily_series = self._build_daily_series(events)

        metrics = {
            "content_id": str(content_id),
            "title": content_info.get("title", ""),
            "status": content_info.get("status", ""),
            "created_at": content_info.get("created_at", ""),
            "metrics": totals,
            "engagement_rate": engagement_rate,
            "performance_score": performance_score,
            "event_count": len(events),
            "daily_series": daily_series,
        }

        cache.set(cache_key, metrics, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return metrics

    # ------------------------------------------------------------------ #
    #  Funnel Analysis                                                      #
    # ------------------------------------------------------------------ #

    async def get_funnel(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """
        Content funnel analysis: created → published → engaged → converted.

        Returns counts at each stage and conversion rates between stages.
        """
        cache_key = f"funnel:{user_id}:{days}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        since = (datetime.now() - timedelta(days=days)).isoformat()

        # Stage 1: created (content created in period)
        content_result = (
            self.supabase.table("content")
            .select("id")
            .eq("user_id", str(user_id))
            .gte("created_at", since)
            .execute()
        )
        created_ids = {c["id"] for c in (content_result.data or [])}
        created_count = len(created_ids)

        # Stage 2: published (distributions with status=published)
        dist_result = (
            self.supabase.table("distributions")
            .select("content_id")
            .eq("user_id", str(user_id))
            .eq("status", "published")
            .gte("created_at", since)
            .execute()
        )
        published_ids = {
            d["content_id"] for d in (dist_result.data or []) if d.get("content_id")
        }
        published_count = len(published_ids)

        # Stage 3: engaged (content that has shares or comments)
        events_result = (
            self.supabase.table("performance_events")
            .select("content_id, event_type")
            .eq("user_id", str(user_id))
            .in_("event_type", ["share", "comment"])
            .gte("created_at", since)
            .execute()
        )
        engaged_ids = {e["content_id"] for e in (events_result.data or [])}
        engaged_count = len(engaged_ids)

        # Stage 4: converted (content that has conversion events)
        conv_result = (
            self.supabase.table("performance_events")
            .select("content_id")
            .eq("user_id", str(user_id))
            .eq("event_type", "conversion")
            .gte("created_at", since)
            .execute()
        )
        converted_ids = {c["content_id"] for c in (conv_result.data or [])}
        converted_count = len(converted_ids)

        # Calculate stage-to-stage conversion rates
        stages = {
            "created": created_count,
            "published": published_count,
            "engaged": engaged_count,
            "converted": converted_count,
        }

        stage_order = ["created", "published", "engaged", "converted"]
        conversion_rates = {}
        for i in range(len(stage_order) - 1):
            current = stage_order[i]
            next_stage = stage_order[i + 1]
            current_count = stages[current]
            next_count = stages[next_stage]
            rate = (next_count / current_count) if current_count > 0 else 0.0
            conversion_rates[f"{current}_to_{next_stage}"] = round(rate, 4)

        # Overall funnel conversion
        overall_rate = (converted_count / created_count) if created_count > 0 else 0.0

        funnel_data = {
            "stages": [
                {"name": "created", "count": created_count},
                {"name": "published", "count": published_count},
                {"name": "engaged", "count": engaged_count},
                {"name": "converted", "count": converted_count},
            ],
            "conversion_rates": conversion_rates,
            "overall_conversion_rate": round(overall_rate, 4),
            "period_days": days,
        }

        cache.set(cache_key, funnel_data, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return funnel_data

    # ------------------------------------------------------------------ #
    #  Cohort Analysis                                                      #
    # ------------------------------------------------------------------ #

    async def get_cohort(
        self,
        user_id: UUID,
        cohort_size: str = "week",
        periods: int = 4,
    ) -> Dict[str, Any]:
        """
        Cohort analysis: group content by publish date, compare performance.

        cohort_size: 'day', 'week', or 'month'
        periods: number of cohort periods to analyze
        """
        cache_key = f"cohort:{user_id}:{cohort_size}:{periods}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        # Fetch content with created_at
        content_result = (
            self.supabase.table("content")
            .select("id, created_at")
            .eq("user_id", str(user_id))
            .order("created_at", desc=False)
            .execute()
        )
        all_content = content_result.data or []

        if not all_content:
            result = {"cohorts": [], "cohort_size": cohort_size, "periods": periods}
            cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
            return result

        # Determine time range
        earliest = datetime.fromisoformat(
            all_content[0]["created_at"].replace("Z", "+00:00")
        )
        latest = datetime.fromisoformat(
            all_content[-1]["created_at"].replace("Z", "+00:00")
        )

        # Build cohort buckets
        if cohort_size == "day":
            delta = timedelta(days=1)
        elif cohort_size == "month":
            delta = timedelta(days=30)
        else:  # week
            delta = timedelta(weeks=1)

        cohorts: Dict[str, List[str]] = {}
        for c in all_content:
            c_date = datetime.fromisoformat(c["created_at"].replace("Z", "+00:00"))
            # Find which cohort period this falls into
            periods_back = int((latest - c_date) / delta)
            if periods_back >= periods:
                periods_back = periods - 1
            cohort_label = f"p{periods_back}"
            if cohort_label not in cohorts:
                cohorts[cohort_label] = []
            cohorts[cohort_label].append(c["id"])

        # For each cohort, fetch performance events
        cohort_data = []
        for label in sorted(cohorts.keys()):
            content_ids = cohorts[label]
            if not content_ids:
                continue

            events_result = (
                self.supabase.table("performance_events")
                .select("event_type, value")
                .eq("user_id", str(user_id))
                .in_("content_id", content_ids)
                .execute()
            )
            events = events_result.data or []

            totals = {"views": 0, "shares": 0, "comments": 0, "conversions": 0}
            for ev in events:
                et = ev.get("event_type", "")
                if et in totals:
                    totals[et] += ev.get("value", 1)

            engagement_rate = (totals["shares"] + totals["comments"]) / max(
                totals["views"], 1
            )
            engagement_rate = min(round(engagement_rate, 4), 1.0)

            conversion_rate = totals["conversions"] / max(len(content_ids), 1)
            conversion_rate = min(round(conversion_rate, 4), 1.0)

            cohort_data.append(
                {
                    "cohort": label,
                    "content_count": len(content_ids),
                    "metrics": totals,
                    "engagement_rate": engagement_rate,
                    "conversion_rate": conversion_rate,
                    "avg_views": round(totals["views"] / max(len(content_ids), 1), 2),
                    "avg_conversions": round(
                        totals["conversions"] / max(len(content_ids), 1), 2
                    ),
                }
            )

        result = {
            "cohorts": cohort_data,
            "cohort_size": cohort_size,
            "periods": periods,
        }

        cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return result

    # ------------------------------------------------------------------ #
    #  Attribution Modeling                                                  #
    # ------------------------------------------------------------------ #

    async def get_attribution(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """
        Attribution modeling: which content pieces drive conversions.

        Uses a simple last-touch attribution model, grouping content
        by type and platform to show conversion drivers.
        """
        cache_key = f"attribution:{user_id}:{days}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        since = (datetime.now() - timedelta(days=days)).isoformat()

        # Get conversion events
        conv_result = (
            self.supabase.table("performance_events")
            .select("content_id, value, metadata, created_at")
            .eq("user_id", str(user_id))
            .eq("event_type", "conversion")
            .gte("created_at", since)
            .execute()
        )
        conversions = conv_result.data or []

        if not conversions:
            result = {
                "total_conversions": 0,
                "total_value": 0,
                "by_content": [],
                "by_content_type": [],
                "by_platform": [],
                "top_converters": [],
                "period_days": days,
            }
            cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
            return result

        # Get content details for conversion content_ids
        content_ids = list({c["content_id"] for c in conversions})
        content_result = (
            self.supabase.table("content")
            .select("id, title, source_type, status")
            .in_("id", content_ids)
            .execute()
        )
        content_map = {c["id"]: c for c in (content_result.data or [])}

        # Get distribution info for platform attribution
        dist_result = (
            self.supabase.table("distributions")
            .select("content_id, platform, status")
            .eq("user_id", str(user_id))
            .execute()
        )
        dist_by_content: Dict[str, List[Dict]] = defaultdict(list)
        for d in dist_result.data or []:
            cid = d.get("content_id")
            if cid:
                dist_by_content[cid].append(d)

        # Aggregate conversions by content
        by_content: Dict[str, Dict] = {}
        total_value = 0
        for conv in conversions:
            cid = conv["content_id"]
            val = conv.get("value", 1)
            total_value += val

            if cid not in by_content:
                by_content[cid] = {"conversions": 0, "value": 0}
            by_content[cid]["conversions"] += 1
            by_content[cid]["value"] += val

        # Build by_content_type attribution
        by_type: Dict[str, Dict] = defaultdict(
            lambda: {"conversions": 0, "value": 0, "content_count": 0}
        )
        for cid, data in by_content.items():
            content_info = content_map.get(cid, {})
            source_type = content_info.get("source_type", "unknown")
            by_type[source_type]["conversions"] += data["conversions"]
            by_type[source_type]["value"] += data["value"]
            by_type[source_type]["content_count"] += 1

        # Build by_platform attribution
        by_platform: Dict[str, Dict] = defaultdict(
            lambda: {"conversions": 0, "value": 0}
        )
        for cid, data in by_content.items():
            platforms = [
                d.get("platform", "unknown") for d in dist_by_content.get(cid, [])
            ]
            if not platforms:
                platforms = ["organic"]
            for platform in platforms:
                by_platform[platform]["conversions"] += data["conversions"]
                by_platform[platform]["value"] += data["value"]

        # Top converting content pieces
        top_converters = sorted(
            by_content.items(), key=lambda x: x[1]["value"], reverse=True
        )[:10]
        top_converters_list = []
        for cid, data in top_converters:
            info = content_map.get(cid, {})
            top_converters_list.append(
                {
                    "content_id": cid,
                    "title": info.get("title", "Unknown"),
                    "source_type": info.get("source_type", "unknown"),
                    "conversions": data["conversions"],
                    "value": data["value"],
                }
            )

        result = {
            "total_conversions": len(conversions),
            "total_value": total_value,
            "by_content": [
                {"content_id": cid, **data} for cid, data in by_content.items()
            ],
            "by_content_type": [{"source_type": k, **v} for k, v in by_type.items()],
            "by_platform": [{"platform": k, **v} for k, v in by_platform.items()],
            "top_converters": top_converters_list,
            "period_days": days,
        }

        cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return result

    # ------------------------------------------------------------------ #
    #  Trends Over Time                                                      #
    # ------------------------------------------------------------------ #

    async def get_trends(
        self,
        user_id: UUID,
        days: int = 30,
        granularity: str = "day",
    ) -> Dict[str, Any]:
        """
        Performance trends over time with configurable granularity.

        granularity: 'day', 'week', or 'month'
        """
        cache_key = f"trends:{user_id}:{days}:{granularity}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        since = (datetime.now() - timedelta(days=days)).isoformat()

        events_result = (
            self.supabase.table("performance_events")
            .select("event_type, value, created_at")
            .eq("user_id", str(user_id))
            .gte("created_at", since)
            .order("created_at", desc=False)
            .execute()
        )
        events = events_result.data or []

        # Group events by time bucket
        buckets: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {
                "views": 0,
                "shares": 0,
                "comments": 0,
                "conversions": 0,
            }
        )

        for ev in events:
            try:
                ev_date = datetime.fromisoformat(
                    ev["created_at"].replace("Z", "+00:00")
                )
            except (KeyError, ValueError):
                continue

            if granularity == "month":
                key = ev_date.strftime("%Y-%m")
            elif granularity == "week":
                # ISO week
                key = f"{ev_date.isocalendar()[0]}-W{ev_date.isocalendar()[1]:02d}"
            else:  # day
                key = ev_date.strftime("%Y-%m-%d")

            et = ev.get("event_type", "")
            if et in buckets[key]:
                buckets[key][et] += ev.get("value", 1)

        # Sort buckets and build series
        sorted_keys = sorted(buckets.keys())
        series = []
        for key in sorted_keys:
            data = buckets[key]
            total_engagement = data["shares"] + data["comments"]
            data["total_engagement"] = total_engagement
            series.append({"period": key, **data})

        result = {
            "granularity": granularity,
            "period_days": days,
            "series": series,
            "total_events": len(events),
        }

        cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return result

    # ------------------------------------------------------------------ #
    #  Internal Helpers                                                      #
    # ------------------------------------------------------------------ #

    def _compute_performance_score(
        self,
        totals: Dict[str, int],
        engagement_rate: float,
        content_count: int,
    ) -> int:
        """
        Compute a 0-100 composite performance score.

        Uses weighted dimensions. Since raw counts vary widely,
        we normalise using a logarithmic scale for counts and
        direct value for engagement_rate.
        """
        import math

        def log_normalise(value: int, cap: int = 1000) -> float:
            """Normalise a count to 0-1 using log scale with cap."""
            if value <= 0:
                return 0.0
            capped = min(value, cap)
            return math.log1p(capped) / math.log1p(cap)

        views_norm = log_normalise(totals.get("views", 0), cap=10000)
        shares_norm = log_normalise(totals.get("shares", 0), cap=1000)
        comments_norm = log_normalise(totals.get("comments", 0), cap=1000)
        conversions_norm = log_normalise(totals.get("conversions", 0), cap=500)

        weighted = (
            views_norm * PERFORMANCE_DIMENSIONS["views"]
            + shares_norm * PERFORMANCE_DIMENSIONS["shares"]
            + comments_norm * PERFORMANCE_DIMENSIONS["comments"]
            + conversions_norm * PERFORMANCE_DIMENSIONS["conversions"]
            + engagement_rate * PERFORMANCE_DIMENSIONS["engagement_rate"]
        )

        return max(0, min(100, round(weighted * 100)))

    def _build_daily_series(self, events: List[Dict]) -> List[Dict]:
        """Build daily time-series buckets from events."""
        daily: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {
                "views": 0,
                "shares": 0,
                "comments": 0,
                "conversions": 0,
            }
        )

        for ev in events:
            try:
                ev_date = datetime.fromisoformat(
                    ev["created_at"].replace("Z", "+00:00")
                )
            except (KeyError, ValueError):
                continue
            key = ev_date.strftime("%Y-%m-%d")
            et = ev.get("event_type", "")
            if et in daily[key]:
                daily[key][et] += ev.get("value", 1)

        sorted_keys = sorted(daily.keys())
        return [{"date": k, **daily[k]} for k in sorted_keys]


# Singleton
performance_service = PerformanceService()

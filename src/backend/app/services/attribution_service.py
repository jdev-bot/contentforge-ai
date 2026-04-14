"""
Attribution Modeling Service.

Provides multi-touch attribution analysis:
- Touchpoint recording for content-channel interactions
- Five attribution models: First-Touch, Last-Touch, Linear, Time-Decay, Position-Based
- Channel-level performance aggregation
- Revenue attribution breakdowns
"""
import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.cache import cache
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

CACHE_PREFIX = "attribution"
CACHE_TTL_SECONDS = 300  # 5 minutes


# ── Enums ────────────────────────────────────────────────────────


class AttributionModel(str, Enum):
    """Supported attribution models."""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"


# ── Pydantic Models ──────────────────────────────────────────────


class AttributionTouchpoint(BaseModel):
    """A single touchpoint in the attribution chain."""
    id: str = Field(default="", description="Touchpoint ID")
    content_id: str = Field(..., description="Content piece ID")
    channel: str = Field(..., description="Marketing channel (e.g., organic, email, social)")
    source: str = Field(default="", description="Traffic source (e.g., google, newsletter)")
    campaign: str = Field(default="", description="Campaign name or identifier")
    timestamp: str = Field(default="", description="When the touchpoint occurred")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata")


class AttributionResult(BaseModel):
    """Result of attribution calculation for a single channel/source."""
    channel: str = Field(..., description="Marketing channel")
    source: str = Field(default="", description="Traffic source")
    attribution_weight: float = Field(default=0.0, description="Weight assigned (0-1)")
    revenue_attributed: float = Field(default=0.0, description="Revenue attributed to this channel")
    conversion_count: int = Field(default=0, description="Number of conversions attributed")


class ChannelPerformance(BaseModel):
    """Aggregated channel-level performance."""
    channel: str
    total_touchpoints: int = 0
    total_conversions: int = 0
    attribution_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Weights by attribution model",
    )
    revenue_attributed: Dict[str, float] = Field(
        default_factory=dict,
        description="Revenue by attribution model",
    )


# ── Service ───────────────────────────────────────────────────────


class AttributionService:
    """Service for managing attribution touchpoints and calculating attribution."""

    _supabase = None

    @property
    def supabase(self):
        """Lazy Supabase client initialization."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    # ── Touchpoint Recording ───────────────────────────────────

    async def record_touchpoint(
        self,
        content_id: str,
        channel: str,
        source: str = "",
        campaign: str = "",
        event_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record a touchpoint for content attribution.

        Args:
            content_id: Content piece ID.
            channel: Marketing channel.
            source: Traffic source.
            campaign: Campaign name.
            event_data: Optional metadata.

        Returns:
            Created touchpoint record.
        """
        if not content_id:
            raise ValueError("content_id is required")
        if not channel:
            raise ValueError("channel is required")

        touchpoint_data = {
            "content_id": content_id,
            "channel": channel.strip(),
            "source": source.strip(),
            "campaign": campaign.strip(),
            "event_data": event_data or {},
        }

        result = self.supabase.table("attribution_touchpoints").insert(touchpoint_data).execute()

        # Invalidate caches
        cache.delete(f"touchpoints:{content_id}", prefix=CACHE_PREFIX)
        cache.delete(f"channels", prefix=CACHE_PREFIX)

        return result.data[0] if result.data else touchpoint_data

    async def get_touchpoints(self, content_id: str) -> List[Dict[str, Any]]:
        """
        Get all touchpoints for a content piece.

        Args:
            content_id: Content piece ID.

        Returns:
            List of touchpoint records.
        """
        cache_key = f"touchpoints:{content_id}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        result = (
            self.supabase.table("attribution_touchpoints")
            .select("*")
            .eq("content_id", content_id)
            .order("created_at", desc=False)
            .execute()
        )

        touchpoints = result.data or []
        cache.set(cache_key, touchpoints, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return touchpoints

    # ── Attribution Calculation ────────────────────────────────

    async def calculate_attribution(
        self,
        content_id: str,
        model: str = "first_touch",
    ) -> List[AttributionResult]:
        """
        Calculate attribution for a content piece using the specified model.

        Args:
            content_id: Content piece ID.
            model: Attribution model to use (first_touch, last_touch, linear, time_decay, position_based).

        Returns:
            List of AttributionResult objects.
        """
        cache_key = f"attribution:{content_id}:{model}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return [AttributionResult(**r) for r in cached]

        touchpoints = await self.get_touchpoints(content_id)
        if not touchpoints:
            return []

        # Parse touchpoints into structured objects
        parsed = []
        for tp in touchpoints:
            parsed.append(AttributionTouchpoint(
                id=tp.get("id", ""),
                content_id=tp.get("content_id", content_id),
                channel=tp.get("channel", ""),
                source=tp.get("source", ""),
                campaign=tp.get("campaign", ""),
                timestamp=tp.get("created_at", ""),
                event_data=tp.get("event_data", {}),
            ))

        # Dispatch to the appropriate model
        model_enum = AttributionModel(model)
        if model_enum == AttributionModel.FIRST_TOUCH:
            results = self.first_touch_attribution(parsed)
        elif model_enum == AttributionModel.LAST_TOUCH:
            results = self.last_touch_attribution(parsed)
        elif model_enum == AttributionModel.LINEAR:
            results = self.linear_attribution(parsed)
        elif model_enum == AttributionModel.TIME_DECAY:
            results = self.time_decay_attribution(parsed)
        elif model_enum == AttributionModel.POSITION_BASED:
            results = self.position_based_attribution(parsed)
        else:
            raise ValueError(f"Unsupported attribution model: {model}")

        cache.set(cache_key, [r.model_dump() for r in results], ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return results

    def first_touch_attribution(self, touchpoints: List[AttributionTouchpoint]) -> List[AttributionResult]:
        """
        First-Touch Attribution: 100% credit to the first touchpoint.

        Args:
            touchpoints: List of touchpoints (must be sorted chronologically).

        Returns:
            Attribution results with first touch getting full credit.
        """
        if not touchpoints:
            return []

        first = touchpoints[0]
        return [AttributionResult(
            channel=first.channel,
            source=first.source,
            attribution_weight=1.0,
            revenue_attributed=0.0,
            conversion_count=1,
        )]

    def last_touch_attribution(self, touchpoints: List[AttributionTouchpoint]) -> List[AttributionResult]:
        """
        Last-Touch Attribution: 100% credit to the last touchpoint.

        Args:
            touchpoints: List of touchpoints (must be sorted chronologically).

        Returns:
            Attribution results with last touch getting full credit.
        """
        if not touchpoints:
            return []

        last = touchpoints[-1]
        return [AttributionResult(
            channel=last.channel,
            source=last.source,
            attribution_weight=1.0,
            revenue_attributed=0.0,
            conversion_count=1,
        )]

    def linear_attribution(self, touchpoints: List[AttributionTouchpoint]) -> List[AttributionResult]:
        """
        Linear Attribution: Equal credit to all touchpoints.

        Args:
            touchpoints: List of touchpoints.

        Returns:
            Attribution results with equal weight for all touchpoints.
        """
        if not touchpoints:
            return []

        weight = 1.0 / len(touchpoints)

        # Group by channel+source
        channel_map: Dict[str, AttributionResult] = {}
        for tp in touchpoints:
            key = f"{tp.channel}|{tp.source}"
            if key not in channel_map:
                channel_map[key] = AttributionResult(
                    channel=tp.channel,
                    source=tp.source,
                    attribution_weight=0.0,
                    revenue_attributed=0.0,
                    conversion_count=0,
                )
            channel_map[key].attribution_weight += weight
            channel_map[key].conversion_count += 1

        return list(channel_map.values())

    def time_decay_attribution(
        self,
        touchpoints: List[AttributionTouchpoint],
        decay_rate: float = 0.5,
    ) -> List[AttributionResult]:
        """
        Time-Decay Attribution: Recent touchpoints get more credit.

        Uses exponential decay: weight = decay_rate^((total - index) / total).
        More recent touchpoints (higher index) receive higher weights.

        Args:
            touchpoints: List of touchpoints (chronologically sorted).
            decay_rate: Decay factor (0-1). Lower = stronger recency bias.

        Returns:
            Attribution results with time-decay weights.
        """
        if not touchpoints:
            return []

        n = len(touchpoints)
        weights: List[float] = []

        for i in range(n):
            # More recent touchpoints (higher index) get more weight
            weight = decay_rate ** ((n - 1 - i) / max(n - 1, 1))
            weights.append(weight)

        # Normalize weights to sum to 1.0
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]

        # Group by channel+source
        channel_map: Dict[str, AttributionResult] = {}
        for i, tp in enumerate(touchpoints):
            key = f"{tp.channel}|{tp.source}"
            if key not in channel_map:
                channel_map[key] = AttributionResult(
                    channel=tp.channel,
                    source=tp.source,
                    attribution_weight=0.0,
                    revenue_attributed=0.0,
                    conversion_count=0,
                )
            channel_map[key].attribution_weight += weights[i]
            channel_map[key].conversion_count += 1

        return list(channel_map.values())

    def position_based_attribution(
        self,
        touchpoints: List[AttributionTouchpoint],
        first_weight: float = 0.4,
        last_weight: float = 0.4,
        middle_weight: float = 0.2,
    ) -> List[AttributionResult]:
        """
        Position-Based (U-Shaped) Attribution.

        First and last touchpoints get `first_weight` and `last_weight` respectively.
        Remaining touchpoints share `middle_weight` equally.

        If only one touchpoint, it gets 100% credit.
        If two touchpoints, they get first_weight + last_weight proportionally.

        Args:
            touchpoints: List of touchpoints (chronologically sorted).
            first_weight: Weight for the first touchpoint.
            last_weight: Weight for the last touchpoint.
            middle_weight: Weight shared among middle touchpoints.

        Returns:
            Attribution results with position-based weights.
        """
        if not touchpoints:
            return []

        n = len(touchpoints)

        if n == 1:
            return [AttributionResult(
                channel=touchpoints[0].channel,
                source=touchpoints[0].source,
                attribution_weight=1.0,
                revenue_attributed=0.0,
                conversion_count=1,
            )]

        # Normalize weights to ensure they sum to 1.0
        total = first_weight + last_weight + middle_weight
        first_weight /= total
        last_weight /= total
        middle_weight /= total

        weights: List[float] = []

        if n == 2:
            # Two touchpoints: split proportionally
            weights = [first_weight, last_weight]
        else:
            # First gets first_weight, last gets last_weight
            # Middle ones share middle_weight equally
            middle_share = middle_weight / (n - 2) if n > 2 else 0
            for i in range(n):
                if i == 0:
                    weights.append(first_weight)
                elif i == n - 1:
                    weights.append(last_weight)
                else:
                    weights.append(middle_share)

        # Group by channel+source
        channel_map: Dict[str, AttributionResult] = {}
        for i, tp in enumerate(touchpoints):
            key = f"{tp.channel}|{tp.source}"
            if key not in channel_map:
                channel_map[key] = AttributionResult(
                    channel=tp.channel,
                    source=tp.source,
                    attribution_weight=0.0,
                    revenue_attributed=0.0,
                    conversion_count=0,
                )
            channel_map[key].attribution_weight += weights[i]
            channel_map[key].conversion_count += 1

        return list(channel_map.values())

    # ── Channel Performance ────────────────────────────────────

    async def get_channel_performance(
        self,
        user_id: UUID,
        date_range: int = 30,
    ) -> List[ChannelPerformance]:
        """
        Get aggregated channel-level attribution performance.

        Args:
            user_id: User whose content to analyze.
            date_range: Number of days to include.

        Returns:
            List of ChannelPerformance objects with performance data.
        """
        cache_key = f"channels:{user_id}:{date_range}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return [ChannelPerformance(**c) for c in cached]

        since = (datetime.now() - timedelta(days=date_range)).isoformat()

        # Get user's content IDs
        content_result = (
            self.supabase.table("content")
            .select("id")
            .eq("user_id", str(user_id))
            .execute()
        )
        content_ids = [c["id"] for c in (content_result.data or [])]

        if not content_ids:
            return []

        # Get touchpoints for user's content within date range
        touchpoints_result = (
            self.supabase.table("attribution_touchpoints")
            .select("channel, source, content_id, created_at")
            .in_("content_id", content_ids)
            .gte("created_at", since)
            .order("created_at", desc=False)
            .execute()
        )
        touchpoints = touchpoints_result.data or []

        if not touchpoints:
            return []

        # Aggregate by channel
        channel_data: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_touchpoints": 0,
            "unique_content": set(),
        })

        for tp in touchpoints:
            channel = tp.get("channel", "unknown")
            channel_data[channel]["total_touchpoints"] += 1
            channel_data[channel]["unique_content"].add(tp.get("content_id", ""))

        # Build performance list
        performance = []
        for channel, data in channel_data.items():
            performance.append(ChannelPerformance(
                channel=channel,
                total_touchpoints=data["total_touchpoints"],
                total_conversions=len(data["unique_content"]),
                attribution_weights={},
                revenue_attributed={},
            ))

        cache.set(cache_key, [p.model_dump() for p in performance], ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return performance


# Singleton
attribution_service = AttributionService()
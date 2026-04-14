"""
Funnel Tracking Service.

Provides custom funnel tracking and conversion analytics:
- Funnel definition with ordered steps
- Event tracking at each funnel step
- Step-by-step conversion rate analysis
- Drop-off identification and reporting
- Date-range scoped analytics
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.cache import cache
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

CACHE_PREFIX = "funnel"
CACHE_TTL_SECONDS = 300  # 5 minutes


# ── Pydantic Models ──────────────────────────────────────────────


class FunnelStep(BaseModel):
    """A single step in a funnel."""

    step_id: str = Field(..., description="Unique identifier for the step")
    name: str = Field(..., description="Display name of the step")
    order: int = Field(..., description="Order of the step in the funnel (0-based)")
    description: str = Field(default="", description="Optional description of the step")


class Funnel(BaseModel):
    """A funnel definition with ordered steps."""

    funnel_id: str = Field(..., description="Unique funnel identifier")
    name: str = Field(..., description="Funnel name")
    description: str = Field(default="", description="Funnel description")
    steps: List[FunnelStep] = Field(
        default_factory=list, description="Ordered funnel steps"
    )
    created_at: str = Field(default="", description="Creation timestamp")
    updated_at: str = Field(default="", description="Last update timestamp")


class FunnelConversion(BaseModel):
    """Conversion analytics for a funnel."""

    funnel_id: str
    step_conversions: Dict[str, int] = Field(
        default_factory=dict,
        description="Mapping of step_id to event count",
    )
    total_entered: int = Field(
        default=0, description="Users who entered the first step"
    )
    total_completed: int = Field(
        default=0, description="Users who reached the last step"
    )
    conversion_rate: float = Field(default=0.0, description="Overall conversion rate")
    drop_off_steps: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Steps with highest drop-off rates",
    )
    step_conversion_rates: Dict[str, float] = Field(
        default_factory=dict,
        description="Conversion rate from each step to the next",
    )


class FunnelEventCreate(BaseModel):
    """Request body for tracking a funnel event."""

    step_id: str = Field(..., description="Funnel step ID")
    user_id: str = Field(
        default="", description="Optional user identifier for the event"
    )
    event_data: Dict[str, Any] = Field(
        default_factory=dict, description="Optional event metadata"
    )


# ── Service ───────────────────────────────────────────────────────


class FunnelService:
    """Service for managing funnels and tracking conversion events."""

    _supabase = None

    @property
    def supabase(self):
        """Lazy Supabase client initialization."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    # ── Funnel CRUD ────────────────────────────────────────────

    async def create_funnel(
        self,
        user_id: UUID,
        name: str,
        description: str = "",
        steps: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new funnel definition.

        Args:
            user_id: Owner of the funnel.
            name: Funnel name.
            description: Funnel description.
            steps: List of step dicts with step_id, name, order, description.

        Returns:
            Created funnel record.
        """
        if not name or not name.strip():
            raise ValueError("Funnel name is required")

        steps = steps or []
        # Validate step ordering
        for i, step in enumerate(steps):
            if step.get("order") is None:
                step["order"] = i
            if not step.get("step_id"):
                step["step_id"] = f"step_{i}"

        funnel_data = {
            "user_id": str(user_id),
            "name": name.strip(),
            "description": description,
            "steps": steps,
        }

        result = self.supabase.table("funnels").insert(funnel_data).execute()

        # Invalidate cache
        cache.delete(f"list:{user_id}", prefix=CACHE_PREFIX)

        return result.data[0] if result.data else funnel_data

    async def get_funnel(self, funnel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a funnel by ID.

        Args:
            funnel_id: The funnel identifier.

        Returns:
            Funnel record or None if not found.
        """
        cache_key = f"funnel:{funnel_id}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        result = (
            self.supabase.table("funnels").select("*").eq("id", funnel_id).execute()
        )

        if not result.data:
            return None

        funnel = result.data[0]
        cache.set(cache_key, funnel, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return funnel

    async def list_funnels(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        List all funnels for a user.

        Args:
            user_id: Owner of the funnels.

        Returns:
            List of funnel records.
        """
        cache_key = f"list:{user_id}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return cached

        result = (
            self.supabase.table("funnels")
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=False)
            .execute()
        )

        funnels = result.data or []
        cache.set(cache_key, funnels, ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX)
        return funnels

    async def delete_funnel(self, funnel_id: str) -> bool:
        """
        Delete a funnel and its associated events.

        Args:
            funnel_id: The funnel identifier.

        Returns:
            True if deleted successfully.
        """
        # Delete events first
        self.supabase.table("funnel_events").delete().eq(
            "funnel_id", funnel_id
        ).execute()

        # Delete funnel
        result = self.supabase.table("funnels").delete().eq("id", funnel_id).execute()

        # Invalidate caches
        cache.delete(f"funnel:{funnel_id}", prefix=CACHE_PREFIX)
        cache.delete(f"analytics:{funnel_id}", prefix=CACHE_PREFIX)

        return len(result.data or []) > 0

    # ── Event Tracking ──────────────────────────────────────────

    async def track_event(
        self,
        funnel_id: str,
        step_id: str,
        user_id: str = "",
        event_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Track a conversion event at a specific funnel step.

        Args:
            funnel_id: The funnel this event belongs to.
            step_id: The step within the funnel.
            user_id: Optional user identifier for conversion tracking.
            event_data: Optional metadata for this event.

        Returns:
            Created event record.
        """
        # Verify funnel exists
        funnel = await self.get_funnel(funnel_id)
        if not funnel:
            raise ValueError(f"Funnel {funnel_id} not found")

        # Validate step belongs to funnel
        step_ids = [
            s.get("step_id", s.get("id", "")) for s in (funnel.get("steps") or [])
        ]
        if step_ids and step_id not in step_ids:
            raise ValueError(
                f"Step {step_id} not found in funnel {funnel_id}. "
                f"Available steps: {step_ids}"
            )

        event_record = {
            "funnel_id": funnel_id,
            "step_id": step_id,
            "user_id": user_id or "",
            "event_data": event_data or {},
        }

        result = self.supabase.table("funnel_events").insert(event_record).execute()

        # Invalidate analytics cache for this funnel
        cache.delete(f"analytics:{funnel_id}", prefix=CACHE_PREFIX)

        return result.data[0] if result.data else event_record

    # ── Analytics ───────────────────────────────────────────────

    async def get_analytics(
        self,
        funnel_id: str,
        date_range: int = 30,
    ) -> FunnelConversion:
        """
        Get conversion analytics for a funnel.

        Args:
            funnel_id: The funnel to analyze.
            date_range: Number of days to include in the analysis.

        Returns:
            FunnelConversion with step-by-step conversion rates and drop-off analysis.
        """
        cache_key = f"analytics:{funnel_id}:{date_range}"
        cached = cache.get(cache_key, prefix=CACHE_PREFIX)
        if cached is not None:
            return FunnelConversion(**cached)

        funnel = await self.get_funnel(funnel_id)
        if not funnel:
            raise ValueError(f"Funnel {funnel_id} not found")

        steps = funnel.get("steps", [])
        if not steps:
            return FunnelConversion(funnel_id=funnel_id)

        since = (datetime.now() - timedelta(days=date_range)).isoformat()

        # Fetch all events for this funnel within the date range
        events_result = (
            self.supabase.table("funnel_events")
            .select("step_id, user_id, created_at")
            .eq("funnel_id", funnel_id)
            .gte("created_at", since)
            .order("created_at", desc=False)
            .execute()
        )
        events = events_result.data or []

        # Build step conversions: count of events per step
        step_conversions: Dict[str, int] = {}
        for step in steps:
            step_id = step.get("step_id", step.get("id", ""))
            step_conversions[step_id] = 0

        for event in events:
            step_id = event.get("step_id", "")
            if step_id in step_conversions:
                step_conversions[step_id] += 1

        # Compute unique users per step for conversion rates
        step_users: Dict[str, set] = {sid: set() for sid in step_conversions}
        for event in events:
            sid = event.get("step_id", "")
            uid = event.get("user_id", "")
            if sid in step_users and uid:
                step_users[sid].add(uid)

        # Calculate conversion rates between steps
        ordered_steps = sorted(steps, key=lambda s: s.get("order", 0))
        step_conversion_rates: Dict[str, float] = {}

        for i in range(len(ordered_steps)):
            current_step = ordered_steps[i]
            current_id = current_step.get("step_id", current_step.get("id", ""))

            if i < len(ordered_steps) - 1:
                next_step = ordered_steps[i + 1]
                next_id = next_step.get("step_id", next_step.get("id", ""))

                current_count = len(
                    step_users.get(current_id, set())
                ) or step_conversions.get(current_id, 0)
                next_count = len(
                    step_users.get(next_id, set())
                ) or step_conversions.get(next_id, 0)

                rate = (next_count / current_count) if current_count > 0 else 0.0
                step_conversion_rates[f"{current_id}_to_{next_id}"] = round(rate, 4)

        # Determine total entered and completed
        first_step_id = (
            ordered_steps[0].get("step_id", ordered_steps[0].get("id", ""))
            if ordered_steps
            else ""
        )
        last_step_id = (
            ordered_steps[-1].get("step_id", ordered_steps[-1].get("id", ""))
            if ordered_steps
            else ""
        )

        total_entered = step_conversions.get(first_step_id, 0)
        total_completed = step_conversions.get(last_step_id, 0)
        conversion_rate = (
            (total_completed / total_entered) if total_entered > 0 else 0.0
        )

        # Identify drop-off steps
        drop_off_steps = []
        for i in range(len(ordered_steps) - 1):
            current_step = ordered_steps[i]
            next_step = ordered_steps[i + 1]

            current_id = current_step.get("step_id", current_step.get("id", ""))
            next_id = next_step.get("step_id", next_step.get("id", ""))

            current_count = step_conversions.get(current_id, 0)
            next_count = step_conversions.get(next_id, 0)
            drop_off = current_count - next_count

            if drop_off > 0:
                drop_off_steps.append(
                    {
                        "step_id": current_id,
                        "step_name": current_step.get("name", current_id),
                        "users_entered": current_count,
                        "users_exited": next_count,
                        "drop_off_count": drop_off,
                        "drop_off_rate": (
                            round(drop_off / current_count, 4)
                            if current_count > 0
                            else 0.0
                        ),
                    }
                )

        # Sort drop-offs by rate descending
        drop_off_steps.sort(key=lambda x: x.get("drop_off_rate", 0), reverse=True)

        result = FunnelConversion(
            funnel_id=funnel_id,
            step_conversions=step_conversions,
            total_entered=total_entered,
            total_completed=total_completed,
            conversion_rate=round(conversion_rate, 4),
            drop_off_steps=drop_off_steps,
            step_conversion_rates=step_conversion_rates,
        )

        cache.set(
            cache_key, result.model_dump(), ttl=CACHE_TTL_SECONDS, prefix=CACHE_PREFIX
        )
        return result


# Singleton
funnel_service = FunnelService()

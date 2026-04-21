"""
Batch init endpoint — returns everything the frontend needs on page load in a single request.

This eliminates the N+1 API call pattern where the frontend makes 5+ sequential
requests on every page load (auth/me, projects, content, usage, analytics).

All data is fetched in parallel using asyncio.gather for maximum performance.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.routers.auth import get_auth_user

logger = logging.getLogger(__name__)
router = APIRouter()


class InitContentItem(BaseModel):
    id: str
    project_id: str
    title: str
    source_type: str
    status: str
    created_at: str
    updated_at: str


class InitProjectItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: str
    updated_at: str


class InitUserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    subscription_tier: str = "free"
    monthly_usage_count: int = 0
    monthly_usage_limit: int = 10


class InitUsageSummary(BaseModel):
    monthly_usage_count: int = 0
    monthly_usage_limit: int = 10
    remaining: int = 10
    percentage_used: float = 0.0
    subscription_tier: str = "free"


class InitDashboardKPIs(BaseModel):
    total_content: int = 0
    total_assets: int = 0
    total_distributions: int = 0
    published_distributions: int = 0
    content_growth_30d: int = 0
    asset_growth_30d: int = 0
    distribution_success_rate: float = 0.0


class InitResponse(BaseModel):
    """Aggregated response for frontend init."""
    user: InitUserProfile
    projects: list[InitProjectItem] = []
    content: list[InitContentItem] = []
    usage: InitUsageSummary = Field(default_factory=InitUsageSummary)
    dashboard_kpis: InitDashboardKPIs = Field(default_factory=InitDashboardKPIs)


async def _fetch_user_profile(user) -> InitUserProfile:
    """Fetch user profile with subscription details."""
    import asyncio
    supabase = get_supabase_admin_client()
    profile_data = user.user_metadata or {}

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: supabase.table("profiles")
                .select("subscription_tier, monthly_usage_count, monthly_usage_limit")
                .eq("id", str(user.id))
                .single()
                .execute()
        )
        if result.data:
            return InitUserProfile(
                id=str(user.id),
                email=user.email,
                full_name=profile_data.get("full_name"),
                is_active=True,
                subscription_tier=result.data.get("subscription_tier", "free"),
                monthly_usage_count=result.data.get("monthly_usage_count", 0),
                monthly_usage_limit=result.data.get("monthly_usage_limit", 10),
            )
    except Exception as e:
        logger.debug(f"Init: profile lookup failed: {e}")

    return InitUserProfile(
        id=str(user.id),
        email=user.email,
        full_name=profile_data.get("full_name"),
        is_active=True,
    )


async def _fetch_projects(user_id: str) -> list[InitProjectItem]:
    """Fetch user's projects."""
    import asyncio
    supabase = get_supabase_admin_client()
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: supabase.table("projects")
                .select("id, name, description, is_active, created_at, updated_at")
                .eq("user_id", user_id)
                .order("updated_at", desc=True)
                .limit(50)
                .execute()
        )
        return [InitProjectItem(**p) for p in (result.data or [])]
    except Exception as e:
        logger.debug(f"Init: projects lookup failed: {e}")
        return []


async def _fetch_content(user_id: str) -> list[InitContentItem]:
    """Fetch user's content."""
    import asyncio
    supabase = get_supabase_admin_client()
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: supabase.table("content")
                .select("id, project_id, title, source_type, status, created_at, updated_at")
                .eq("user_id", user_id)
                .order("updated_at", desc=True)
                .limit(50)
                .execute()
        )
        return [InitContentItem(**c) for c in (result.data or [])]
    except Exception as e:
        logger.debug(f"Init: content lookup failed: {e}")
        return []


async def _fetch_usage(user_id: str) -> InitUsageSummary:
    """Fetch usage summary."""
    supabase = get_supabase_admin_client()
    try:
        result = (
            supabase.table("profiles")
            .select("subscription_tier, monthly_usage_count, monthly_usage_limit")
            .eq("id", user_id)
            .single()
            .execute()
        )
        if result.data:
            count = result.data.get("monthly_usage_count", 0)
            limit = result.data.get("monthly_usage_limit", 10)
            return InitUsageSummary(
                monthly_usage_count=count,
                monthly_usage_limit=limit,
                remaining=max(0, limit - count),
                percentage_used=round((count / limit) * 100, 1) if limit > 0 else 0,
                subscription_tier=result.data.get("subscription_tier", "free"),
            )
    except Exception as e:
        logger.debug(f"Init: usage lookup failed: {e}")
    return InitUsageSummary()


async def _fetch_dashboard_kpis(user_id: str) -> InitDashboardKPIs:
    """Fetch dashboard KPIs — optimized to use fewer Supabase queries."""
    supabase = get_supabase_admin_client()
    try:
        # Use a single RPC call or parallel queries
        # Content count + Asset count in parallel
        import asyncio

        def _count_content():
            try:
                result = (
                    supabase.table("content")
                    .select("id", count="exact")
                    .eq("user_id", user_id)
                    .execute()
                )
                return result.count or 0
            except Exception:
                return 0

        def _count_assets():
            try:
                result = (
                    supabase.table("generated_assets")
                    .select("id", count="exact")
                    .eq("user_id", user_id)
                    .execute()
                )
                return result.count or 0
            except Exception:
                return 0

        def _fetch_distributions():
            try:
                result = (
                    supabase.table("distributions")
                    .select("id, status")
                    .eq("user_id", user_id)
                    .execute()
                )
                data = result.data or []
                total = len(data)
                published = len([d for d in data if d.get("status") == "published"])
                return total, published
            except Exception:
                return 0, 0

        # Run all 3 queries in parallel via thread pool
        loop = asyncio.get_event_loop()
        total_content, total_assets, (dist_total, dist_published) = await asyncio.gather(
            loop.run_in_executor(None, _count_content),
            loop.run_in_executor(None, _count_assets),
            loop.run_in_executor(None, _fetch_distributions),
        )

        return InitDashboardKPIs(
            total_content=total_content,
            total_assets=total_assets,
            total_distributions=dist_total,
            published_distributions=dist_published,
            distribution_success_rate=round(
                (dist_published / dist_total) * 100, 1
            ) if dist_total > 0 else 0.0,
        )
    except Exception as e:
        logger.debug(f"Init: dashboard KPIs failed: {e}")
    return InitDashboardKPIs()


@router.get("/init", response_model=InitResponse)
async def get_init(user=Depends(get_auth_user)):
    """
    Batch initialization endpoint.

    Returns everything the frontend needs on page load in a single request:
    - User profile + subscription
    - Projects list
    - Content list
    - Usage summary
    - Dashboard KPIs

    All sub-queries run in parallel via asyncio.gather for maximum performance.
    User profile and usage share a single Supabase query (dedup).
    """
    user_id = str(user.id)

    # Fetch profile + usage together (same table, same row) — avoids duplicate query
    profile_data = await _fetch_user_profile(user)

    # Build usage from profile data we already have (no extra query)
    usage = InitUsageSummary(
        monthly_usage_count=profile_data.monthly_usage_count,
        monthly_usage_limit=profile_data.monthly_usage_limit,
        remaining=max(0, profile_data.monthly_usage_limit - profile_data.monthly_usage_count),
        percentage_used=round(
            (profile_data.monthly_usage_count / profile_data.monthly_usage_limit) * 100, 1
        ) if profile_data.monthly_usage_limit > 0 else 0,
        subscription_tier=profile_data.subscription_tier,
    )

    # Run remaining fetches in parallel
    projects, content, kpis = await asyncio.gather(
        _fetch_projects(user_id),
        _fetch_content(user_id),
        _fetch_dashboard_kpis(user_id),
    )

    return InitResponse(
        user=profile_data,
        projects=projects,
        content=content,
        usage=usage,
        dashboard_kpis=kpis,
    )
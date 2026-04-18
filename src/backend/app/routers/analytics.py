"""
Analytics router for dashboard metrics and reporting.
"""

import asyncio
import csv
import io
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status as http_status
from pydantic import BaseModel, Field

from app.core.cache import cache, CACHE_TTL
from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.routers.auth import get_auth_user

router = APIRouter()


class ContentStatusMetric(BaseModel):
    """Content count by status."""

    status: str
    count: int


class ContentMetricsResponse(BaseModel):
    """Response model for content analytics."""

    total_content: int
    by_status: List[ContentStatusMetric]
    total_views: Optional[int] = None  # Placeholder for future view tracking
    last_30_days_count: int


class AssetTypeMetric(BaseModel):
    """Asset count by type."""

    type: str
    count: int


class AssetPlatformMetric(BaseModel):
    """Asset count by platform."""

    platform: Optional[str]
    count: int


class AssetMetricsResponse(BaseModel):
    """Response model for asset analytics."""

    total_assets: int
    by_type: List[AssetTypeMetric]
    by_platform: List[AssetPlatformMetric]


class DailyUsageMetric(BaseModel):
    """Daily usage counts."""

    date: str
    count: int


class WeeklyUsageMetric(BaseModel):
    """Weekly usage counts."""

    week: str
    count: int


class MonthlyUsageMetric(BaseModel):
    """Monthly usage counts."""

    month: str
    count: int


class UsageMetricsResponse(BaseModel):
    """Response model for usage over time analytics."""

    daily_counts: List[DailyUsageMetric]
    weekly_counts: List[WeeklyUsageMetric]
    monthly_counts: List[MonthlyUsageMetric]
    total_in_period: int
    average_daily: float


class DistributionStatusMetric(BaseModel):
    """Distribution count by status."""

    status: str
    count: int


class PlatformDistributionMetric(BaseModel):
    """Distribution count by platform."""

    platform: str
    count: int
    success_rate: float


class DistributionMetricsResponse(BaseModel):
    """Response model for distribution analytics."""

    total_distributions: int
    by_status: List[DistributionStatusMetric]
    by_platform: List[PlatformDistributionMetric]
    success_rate: float


class KPIDashboardResponse(BaseModel):
    """Response model for dashboard KPIs."""

    total_content: int
    total_assets: int
    total_distributions: int
    published_distributions: int
    content_growth_30d: int
    asset_growth_30d: int
    distribution_success_rate: float


class UserActivityRecord(BaseModel):
    """User activity record for export."""

    timestamp: str
    event_type: str
    details: Optional[str] = None
    tokens_used: Optional[int] = None


@router.get("/analytics/dashboard", response_model=KPIDashboardResponse)
async def get_dashboard_kpis(user=Depends(get_auth_user)):
    """
    Get key performance indicators for the dashboard.
    """
    # Check cache first
    cache_key = f"dashboard_kpis:{user.id}"
    cached = cache.get(cache_key, prefix="analytics")
    if cached is not None:
        return KPIDashboardResponse(**cached)

    supabase = get_supabase_admin_client()

    try:
        # Run all three queries in parallel for better performance
        def fetch_content():
            return supabase.table("content").select("created_at").eq("user_id", str(user.id)).execute()

        def fetch_assets():
            return supabase.table("generated_assets").select("created_at").eq("user_id", str(user.id)).execute()

        def fetch_distributions():
            return supabase.table("distributions").select("status").eq("user_id", str(user.id)).execute()

        content_result, assets_result, distributions_result = await asyncio.gather(
            asyncio.to_thread(fetch_content),
            asyncio.to_thread(fetch_assets),
            asyncio.to_thread(fetch_distributions),
        )

        content_items = content_result.data or []
        total_content = len(content_items)

        # Calculate last 30 days content
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        content_growth_30d = sum(
            1
            for item in content_items
            if datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
            >= thirty_days_ago
        )

        assets = assets_result.data or []
        total_assets = len(assets)

        # Calculate last 30 days assets
        asset_growth_30d = sum(
            1
            for item in assets
            if datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
            >= thirty_days_ago
        )

        distributions = distributions_result.data or []
        total_distributions = len(distributions)

        # Count published and calculate success rate
        published_count = sum(
            1 for d in distributions if d.get("status") == "published"
        )
        failed_count = sum(1 for d in distributions if d.get("status") == "failed")
        completed_count = published_count + failed_count

        success_rate = (
            (published_count / completed_count * 100) if completed_count > 0 else 0.0
        )

        result = KPIDashboardResponse(
            total_content=total_content,
            total_assets=total_assets,
            total_distributions=total_distributions,
            published_distributions=published_count,
            content_growth_30d=content_growth_30d,
            asset_growth_30d=asset_growth_30d,
            distribution_success_rate=round(success_rate, 2),
        )
        # Cache the result
        cache.set(cache_key, result.model_dump(), ttl=CACHE_TTL["analytics"], prefix="analytics")
        return result

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard KPIs: {str(e)}",
        )


@router.get("/analytics/distributions", response_model=DistributionMetricsResponse)
async def get_distribution_metrics(user=Depends(get_auth_user)):
    """
    Get distribution analytics for the current user.

    Returns:
    - total_distributions: Total number of distributions
    - by_status: Breakdown by status
    - by_platform: Breakdown by platform with success rates
    - success_rate: Overall success rate (0-1)
    """
    # Check cache first
    cache_key = f"distribution_metrics:{user.id}"
    cached = cache.get(cache_key, prefix="analytics")
    if cached is not None:
        return DistributionMetricsResponse(**cached)

    supabase = get_supabase_admin_client()

    try:
        # Get all distributions for user
        distributions_result = (
            supabase.table("distributions")
            .select("status, platform")
            .eq("user_id", str(user.id))
            .execute()
        )

        distributions = distributions_result.data or []
        total_distributions = len(distributions)

        # Count by status
        status_counts: Dict[str, int] = {}
        platform_data: Dict[str, Dict[str, int]] = {}

        for dist in distributions:
            # Status counts
            dist_status = dist.get("status", "unknown")
            status_counts[dist_status] = status_counts.get(dist_status, 0) + 1

            # Platform data
            platform = dist.get("platform") or "unknown"
            if platform not in platform_data:
                platform_data[platform] = {"total": 0, "published": 0, "failed": 0}
            platform_data[platform]["total"] += 1
            if dist_status == "published":
                platform_data[platform]["published"] += 1
            elif dist_status == "failed":
                platform_data[platform]["failed"] += 1

        by_status = [
            DistributionStatusMetric(status=k, count=v)
            for k, v in status_counts.items()
        ]

        # Calculate platform success rates
        by_platform = []
        for platform, data in platform_data.items():
            completed = data["published"] + data["failed"]
            success_rate = (
                (data["published"] / completed * 100) if completed > 0 else 0.0
            )
            by_platform.append(
                PlatformDistributionMetric(
                    platform=platform,
                    count=data["total"],
                    success_rate=round(success_rate, 2),
                )
            )

        # Overall success rate
        published_count = sum(
            1 for d in distributions if d.get("status") == "published"
        )
        failed_count = sum(1 for d in distributions if d.get("status") == "failed")
        completed_count = published_count + failed_count
        overall_success_rate = (
            (published_count / completed_count) if completed_count > 0 else 0.0
        )

        result = DistributionMetricsResponse(
            total_distributions=total_distributions,
            by_status=by_status,
            by_platform=by_platform,
            success_rate=round(overall_success_rate, 2),
        )
        # Cache the result
        cache.set(cache_key, result.model_dump(), ttl=CACHE_TTL["analytics"], prefix="analytics")
        return result

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve distribution metrics: {str(e)}",
        )


@router.get("/analytics/content", response_model=ContentMetricsResponse)
async def get_content_metrics(user=Depends(get_auth_user)):
    """
    Get content metrics for the current user.

    Returns:
    - total_content: Total number of content items
    - by_status: Breakdown by status (completed, processing, failed, etc.)
    - total_views: Total views (placeholder for future)
    - last_30_days_count: Content created in last 30 days
    """
    # Check cache first
    cache_key = f"content_metrics:{user.id}"
    cached = cache.get(cache_key, prefix="analytics")
    if cached is not None:
        return ContentMetricsResponse(**cached)

    supabase = get_supabase_admin_client()

    try:
        # Get all content for user
        content_result = (
            supabase.table("content")
            .select("status, created_at")
            .eq("user_id", str(user.id))
            .execute()
        )

        content_items = content_result.data or []
        total_content = len(content_items)

        # Count by status
        status_counts: Dict[str, int] = {}
        for item in content_items:
            item_status = item.get("status", "unknown")
            status_counts[item_status] = status_counts.get(item_status, 0) + 1

        by_status = [
            ContentStatusMetric(status=k, count=v) for k, v in status_counts.items()
        ]

        # Count last 30 days
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        last_30_days_count = sum(
            1
            for item in content_items
            if datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
            >= thirty_days_ago
        )

        result = ContentMetricsResponse(
            total_content=total_content,
            by_status=by_status,
            total_views=None,  # Placeholder for future view tracking
            last_30_days_count=last_30_days_count,
        )
        # Cache the result
        cache.set(cache_key, result.model_dump(), ttl=CACHE_TTL["analytics"], prefix="analytics")
        return result

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve content metrics: {str(e)}",
        )


@router.get("/analytics/assets", response_model=AssetMetricsResponse)
async def get_asset_metrics(user=Depends(get_auth_user)):
    """
    Get asset generation statistics for the current user.

    Returns:
    - total_assets: Total number of generated assets
    - by_type: Breakdown by asset type (thread, social_post, newsletter, etc.)
    - by_platform: Breakdown by platform (twitter, linkedin, etc.)
    """
    # Check cache first
    cache_key = f"asset_metrics:{user.id}"
    cached = cache.get(cache_key, prefix="analytics")
    if cached is not None:
        return AssetMetricsResponse(**cached)

    supabase = get_supabase_admin_client()

    try:
        # Get all assets for user
        assets_result = (
            supabase.table("generated_assets")
            .select("type, platform")
            .eq("user_id", str(user.id))
            .execute()
        )

        assets = assets_result.data or []
        total_assets = len(assets)

        # Count by type
        type_counts: Dict[str, int] = {}
        platform_counts: Dict[str, int] = {}

        for asset in assets:
            # Count by type
            asset_type = asset.get("type", "unknown")
            type_counts[asset_type] = type_counts.get(asset_type, 0) + 1

            # Count by platform
            platform = asset.get("platform") or "none"
            platform_counts[platform] = platform_counts.get(platform, 0) + 1

        by_type = [AssetTypeMetric(type=k, count=v) for k, v in type_counts.items()]
        by_platform = [
            AssetPlatformMetric(platform=k if k != "none" else None, count=v)
            for k, v in platform_counts.items()
        ]

        result = AssetMetricsResponse(
            total_assets=total_assets,
            by_type=by_type,
            by_platform=by_platform,
        )
        # Cache the result
        cache.set(cache_key, result.model_dump(), ttl=CACHE_TTL["analytics"], prefix="analytics")
        return result

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve asset metrics: {str(e)}",
        )


@router.get("/analytics/usage", response_model=UsageMetricsResponse)
async def get_usage_metrics(
    days: int = Query(default=30, ge=7, le=365, description="Number of days to fetch"),
    user=Depends(get_auth_user),
):
    """
    Get usage statistics over time.

    Args:
    - days: Number of days to fetch (7, 30, 90, or custom up to 365)

    Returns:
    - daily_counts: Daily usage counts
    - weekly_counts: Weekly aggregated counts
    - monthly_counts: Monthly aggregated counts
    - total_in_period: Total usage events in the period
    - average_daily: Average daily usage
    """
    # Check cache first
    cache_key = f"usage_metrics:{user.id}:{days}"
    cached = cache.get(cache_key, prefix="analytics")
    if cached is not None:
        return UsageMetricsResponse(**cached)

    supabase = get_supabase_admin_client()

    try:
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        # Get usage tracking data
        usage_result = (
            supabase.table("usage_tracking")
            .select("created_at, event_type")
            .eq("user_id", str(user.id))
            .gte("created_at", start_date.isoformat())
            .execute()
        )

        usage_items = usage_result.data or []

        # Daily counts
        daily_counts: Dict[str, int] = {}
        for i in range(days):
            date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_counts[date] = 0

        # Weekly and monthly aggregations
        weekly_counts: Dict[str, int] = {}
        monthly_counts: Dict[str, int] = {}

        # Count usage by date
        for item in usage_items:
            item_date_str = item.get("created_at", "")[:10]  # Extract YYYY-MM-DD
            if item_date_str in daily_counts:
                daily_counts[item_date_str] = daily_counts.get(item_date_str, 0) + 1

            # Weekly aggregation (ISO week format: YYYY-Www)
            try:
                item_date = datetime.fromisoformat(
                    item.get("created_at", "").replace("Z", "+00:00")
                )
                week_key = item_date.strftime("%Y-W%U")
                weekly_counts[week_key] = weekly_counts.get(week_key, 0) + 1

                # Monthly aggregation
                month_key = item_date.strftime("%Y-%m")
                monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
            except Exception:
                pass

        # Convert daily to sorted list (oldest first)
        sorted_daily_dates = sorted(daily_counts.keys())
        daily_counts_list = [
            DailyUsageMetric(date=date, count=daily_counts[date])
            for date in sorted_daily_dates
        ]

        # Convert weekly to sorted list
        sorted_weekly = sorted(weekly_counts.keys())
        weekly_counts_list = [
            WeeklyUsageMetric(week=week, count=weekly_counts[week])
            for week in sorted_weekly
        ]

        # Convert monthly to sorted list
        sorted_monthly = sorted(monthly_counts.keys())
        monthly_counts_list = [
            MonthlyUsageMetric(month=month, count=monthly_counts[month])
            for month in sorted_monthly
        ]

        total_in_period = len(usage_items)
        average_daily = total_in_period / days if total_in_period > 0 else 0.0

        result = UsageMetricsResponse(
            daily_counts=daily_counts_list,
            weekly_counts=weekly_counts_list,
            monthly_counts=monthly_counts_list,
            total_in_period=total_in_period,
            average_daily=round(average_daily, 2),
        )
        # Cache the result
        cache.set(cache_key, result.model_dump(), ttl=CACHE_TTL["usage_stats"], prefix="analytics")
        return result

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage metrics: {str(e)}",
        )


@router.get("/analytics/export/json")
async def export_user_activity(
    format: str = "csv", days: int = 30, user=Depends(get_auth_user)
):
    """
    Export user activity data.

    Args:
    - format: Export format (currently only "csv" supported)
    - days: Number of days of history to export (default: 30, max: 365)

    Returns CSV file with user activity data including:
    - Timestamp
    - Event type
    - Details
    - Tokens used
    """
    # Validate parameters
    if format.lower() != "csv":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Only CSV format is currently supported",
        )

    if days < 1 or days > 365:
        days = 30

    supabase = get_supabase_admin_client()

    try:
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        # Get content data
        content_result = (
            supabase.table("content")
            .select("created_at, title, source_type, status, word_count")
            .eq("user_id", str(user.id))
            .gte("created_at", start_date.isoformat())
            .execute()
        )

        content_items = content_result.data or []

        # Get asset generation data
        assets_result = (
            supabase.table("generated_assets")
            .select("created_at, type, platform, tokens_used, status")
            .eq("user_id", str(user.id))
            .gte("created_at", start_date.isoformat())
            .execute()
        )

        assets = assets_result.data or []

        # Get usage tracking data
        usage_result = (
            supabase.table("usage_tracking")
            .select("created_at, event_type, tokens_used, metadata")
            .eq("user_id", str(user.id))
            .gte("created_at", start_date.isoformat())
            .execute()
        )

        usage_items = usage_result.data or []

        # Build CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "Timestamp",
                "Activity Type",
                "Event Type",
                "Details",
                "Platform",
                "Status",
                "Tokens Used",
                "Word Count",
            ]
        )

        # Write content entries
        for item in content_items:
            details = f"{item.get('title', 'Untitled')} ({item.get('source_type', 'unknown')})"
            writer.writerow(
                [
                    item.get("created_at", ""),
                    "content",
                    "content_created",
                    details,
                    "",
                    item.get("status", ""),
                    "",
                    item.get("word_count", ""),
                ]
            )

        # Write asset entries
        for item in assets:
            writer.writerow(
                [
                    item.get("created_at", ""),
                    "asset",
                    f"asset_generated_{item.get('type', 'unknown')}",
                    "",
                    item.get("platform", ""),
                    item.get("status", ""),
                    item.get("tokens_used", ""),
                    "",
                ]
            )

        # Write usage entries
        for item in usage_items:
            metadata = item.get("metadata", {}) or {}
            details = str(metadata) if metadata else ""
            writer.writerow(
                [
                    item.get("created_at", ""),
                    "usage",
                    item.get("event_type", ""),
                    details,
                    "",
                    "",
                    item.get("tokens_used", ""),
                    "",
                ]
            )

        # Generate filename
        filename = f"activity_export_{user.id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export user activity: {str(e)}",
        )


@router.get("/analytics/export/json")
async def export_user_activity_json(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to export"),
    user=Depends(get_auth_user),
):
    """
    Export user activity data as JSON.

    Args:
    - days: Number of days of history to export (default: 30, max: 365)

    Returns JSON with user activity data.
    """
    supabase = get_supabase_admin_client()

    try:
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        # Get content data
        content_result = (
            supabase.table("content")
            .select("id, created_at, title, source_type, status, word_count")
            .eq("user_id", str(user.id))
            .gte("created_at", start_date.isoformat())
            .execute()
        )

        content_items = content_result.data or []

        # Get asset generation data
        assets_result = (
            supabase.table("generated_assets")
            .select("id, created_at, type, platform, tokens_used, status")
            .eq("user_id", str(user.id))
            .gte("created_at", start_date.isoformat())
            .execute()
        )

        assets = assets_result.data or []

        # Get usage tracking data
        usage_result = (
            supabase.table("usage_tracking")
            .select("id, created_at, event_type, tokens_used, metadata")
            .eq("user_id", str(user.id))
            .gte("created_at", start_date.isoformat())
            .execute()
        )

        usage_items = usage_result.data or []

        # Build JSON response
        export_data = {
            "export_info": {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "user_id": str(user.id),
                "days_exported": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "content": content_items,
            "assets": assets,
            "usage": usage_items,
            "summary": {
                "total_content": len(content_items),
                "total_assets": len(assets),
                "total_usage_events": len(usage_items),
            },
        }

        # Generate filename
        filename = f"activity_export_{user.id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"

        return Response(
            content=json.dumps(export_data, indent=2, default=str),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export user activity: {str(e)}",
        )


@router.get("/analytics/export")
async def export_analytics(
    format: str = Query(default="csv", description="Export format: csv or json"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to export"),
    user=Depends(get_auth_user),
):
    """Export analytics data in CSV or JSON format.

    Frontend-friendly alias that supports the ?format= query parameter.
    """
    if format.lower() == "json":
        return await export_user_activity_json(days=days, user=user)
    else:
        return await export_user_activity(format="csv", days=days, user=user)

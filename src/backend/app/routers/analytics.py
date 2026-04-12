"""
Analytics router for dashboard metrics and reporting.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Response
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import csv
import io

from app.routers.auth import get_auth_user
from app.core.supabase import get_supabase_client

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


class UsageMetricsResponse(BaseModel):
    """Response model for usage over time analytics."""
    daily_counts: List[DailyUsageMetric]
    total_in_period: int
    average_daily: float


class UserActivityRecord(BaseModel):
    """User activity record for export."""
    timestamp: str
    event_type: str
    details: Optional[str] = None
    tokens_used: Optional[int] = None


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
    supabase = get_supabase_client()
    
    try:
        # Get all content for user
        content_result = supabase.table("content")\
            .select("status, created_at")\
            .eq("user_id", str(user.id))\
            .execute()
        
        content_items = content_result.data or []
        total_content = len(content_items)
        
        # Count by status
        status_counts: Dict[str, int] = {}
        for item in content_items:
            status = item.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        by_status = [ContentStatusMetric(status=k, count=v) for k, v in status_counts.items()]
        
        # Count last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        last_30_days_count = sum(
            1 for item in content_items
            if datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")) >= thirty_days_ago
        )
        
        return ContentMetricsResponse(
            total_content=total_content,
            by_status=by_status,
            total_views=None,  # Placeholder for future view tracking
            last_30_days_count=last_30_days_count,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
    supabase = get_supabase_client()
    
    try:
        # Get all assets for user
        assets_result = supabase.table("generated_assets")\
            .select("type, platform")\
            .eq("user_id", str(user.id))\
            .execute()
        
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
        by_platform = [AssetPlatformMetric(platform=k if k != "none" else None, count=v) 
                      for k, v in platform_counts.items()]
        
        return AssetMetricsResponse(
            total_assets=total_assets,
            by_type=by_type,
            by_platform=by_platform,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve asset metrics: {str(e)}",
        )


@router.get("/analytics/usage", response_model=UsageMetricsResponse)
async def get_usage_metrics(user=Depends(get_auth_user)):
    """
    Get usage statistics over time for the last 30 days.
    
    Returns:
    - daily_counts: Daily usage counts for last 30 days
    - total_in_period: Total usage events in the period
    - average_daily: Average daily usage
    """
    supabase = get_supabase_client()
    
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Get usage tracking data
        usage_result = supabase.table("usage_tracking")\
            .select("created_at")\
            .eq("user_id", str(user.id))\
            .gte("created_at", start_date.isoformat())\
            .execute()
        
        usage_items = usage_result.data or []
        
        # Initialize daily counts for last 30 days
        daily_counts: Dict[str, int] = {}
        for i in range(30):
            date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_counts[date] = 0
        
        # Count usage by date
        for item in usage_items:
            item_date = item.get("created_at", "")[:10]  # Extract YYYY-MM-DD
            if item_date in daily_counts:
                daily_counts[item_date] = daily_counts.get(item_date, 0) + 1
        
        # Convert to sorted list (oldest first)
        sorted_dates = sorted(daily_counts.keys())
        daily_counts_list = [
            DailyUsageMetric(date=date, count=daily_counts[date])
            for date in sorted_dates
        ]
        
        total_in_period = len(usage_items)
        average_daily = total_in_period / 30.0 if total_in_period > 0 else 0.0
        
        return UsageMetricsResponse(
            daily_counts=daily_counts_list,
            total_in_period=total_in_period,
            average_daily=round(average_daily, 2),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage metrics: {str(e)}",
        )


@router.get("/analytics/export")
async def export_user_activity(
    format: str = "csv",
    days: int = 30,
    user=Depends(get_auth_user)
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV format is currently supported",
        )
    
    if days < 1 or days > 365:
        days = 30
    
    supabase = get_supabase_client()
    
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get content data
        content_result = supabase.table("content")\
            .select("created_at, title, source_type, status, word_count")\
            .eq("user_id", str(user.id))\
            .gte("created_at", start_date.isoformat())\
            .execute()
        
        content_items = content_result.data or []
        
        # Get asset generation data
        assets_result = supabase.table("generated_assets")\
            .select("created_at, type, platform, tokens_used, status")\
            .eq("user_id", str(user.id))\
            .gte("created_at", start_date.isoformat())\
            .execute()
        
        assets = assets_result.data or []
        
        # Get usage tracking data
        usage_result = supabase.table("usage_tracking")\
            .select("created_at, event_type, tokens_used, metadata")\
            .eq("user_id", str(user.id))\
            .gte("created_at", start_date.isoformat())\
            .execute()
        
        usage_items = usage_result.data or []
        
        # Build CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Timestamp",
            "Activity Type",
            "Event Type",
            "Details",
            "Platform",
            "Status",
            "Tokens Used",
            "Word Count"
        ])
        
        # Write content entries
        for item in content_items:
            details = f"{item.get('title', 'Untitled')} ({item.get('source_type', 'unknown')})"
            writer.writerow([
                item.get("created_at", ""),
                "content",
                "content_created",
                details,
                "",
                item.get("status", ""),
                "",
                item.get("word_count", "")
            ])
        
        # Write asset entries
        for item in assets:
            writer.writerow([
                item.get("created_at", ""),
                "asset",
                f"asset_generated_{item.get('type', 'unknown')}",
                "",
                item.get("platform", ""),
                item.get("status", ""),
                item.get("tokens_used", ""),
                ""
            ])
        
        # Write usage entries
        for item in usage_items:
            metadata = item.get("metadata", {}) or {}
            details = str(metadata) if metadata else ""
            writer.writerow([
                item.get("created_at", ""),
                "usage",
                item.get("event_type", ""),
                details,
                "",
                "",
                item.get("tokens_used", ""),
                ""
            ])
        
        # Generate filename
        filename = f"activity_export_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export user activity: {str(e)}",
        )

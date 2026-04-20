"""
RSS Feed router for managing RSS feeds and importing content.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from pydantic import BaseModel, Field, HttpUrl

from app.core.rate_limit import rate_limit_dependency
from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.routers.auth import get_auth_user
from app.services.rss_service import rss_service

router = APIRouter()


class RSSFeedCreate(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=255, description="Display name for the RSS feed"
    )
    url: HttpUrl = Field(..., description="URL of the RSS feed")
    fetch_frequency: str = Field(
        default="hourly",
        pattern="^(hourly|daily)$",
        description="How often to fetch: hourly or daily",
    )
    auto_create_content: bool = Field(
        default=False, description="Automatically create content items from new entries"
    )


class RSSFeedUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    fetch_frequency: Optional[str] = Field(None, pattern="^(hourly|daily)$")
    auto_create_content: Optional[bool] = None
    status: Optional[str] = Field(None, pattern="^(active|paused)$")


class RSSFeedResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    url: str
    last_fetched_at: Optional[datetime] = None
    fetch_frequency: str
    auto_create_content: bool
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RSSFeedListResponse(BaseModel):
    feeds: List[RSSFeedResponse]
    total: int


class RSSEntryResponse(BaseModel):
    id: UUID
    feed_id: UUID
    external_id: Optional[str] = None
    title: Optional[str] = None
    link: Optional[str] = None
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    processed: bool
    content_id: Optional[UUID] = None
    created_at: datetime


class RSSEntryListResponse(BaseModel):
    entries: List[RSSEntryResponse]
    total: int
    feed_id: Optional[UUID] = None


class RSSImportResponse(BaseModel):
    success: bool
    content_id: Optional[UUID] = None
    message: str


class RSSFetchResponse(BaseModel):
    success: bool
    entries_fetched: int
    entries_new: int
    message: str


@router.get("/rss/stats")
async def get_rss_stats(user=Depends(get_auth_user)):
    """Return RSS feed statistics for the current user."""
    supabase = get_supabase_admin_client()

    try:
        # Get user's feeds
        feeds_result = (
            supabase.table("rss_feeds")
            .select("id, status")
            .eq("user_id", str(user.id))
            .execute()
        )
        feeds = feeds_result.data or []
        total_feeds = len(feeds)
        active_feeds = sum(1 for f in feeds if f.get("status") == "active")

        feed_ids = [f["id"] for f in feeds]

        if not feed_ids:
            return {
                "total_feeds": 0,
                "active_feeds": 0,
                "total_entries": 0,
                "unimported_entries": 0,
                "recent_entries_count": 0,
            }

        # Total entries
        entries_count_result = (
            supabase.table("rss_entries")
            .select("*", count="exact")
            .in_("feed_id", feed_ids)
            .execute()
        )
        total_entries = entries_count_result.count or 0

        # Unimported entries
        unimported_result = (
            supabase.table("rss_entries")
            .select("*", count="exact")
            .in_("feed_id", feed_ids)
            .eq("processed", False)
            .execute()
        )
        unimported_entries = unimported_result.count or 0

        # Recent entries (last 7 days)
        from datetime import timedelta
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_result = (
            supabase.table("rss_entries")
            .select("*", count="exact")
            .in_("feed_id", feed_ids)
            .gte("published_at", seven_days_ago)
            .execute()
        )
        recent_entries_count = recent_result.count or 0

        return {
            "total_feeds": total_feeds,
            "active_feeds": active_feeds,
            "total_entries": total_entries,
            "unimported_entries": unimported_entries,
            "recent_entries_count": recent_entries_count,
        }

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/rss/settings")
async def get_rss_settings(user=Depends(get_auth_user)):
    """Return the user's RSS settings."""
    supabase = get_supabase_admin_client()

    try:
        result = (
            supabase.table("rss_settings")
            .select("*")
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not result.data:
            # Return defaults if no settings exist yet
            return {
                "auto_import": False,
                "default_project_id": None,
                "notification_enabled": True,
                "notification_new_entries": True,
                "notification_import_errors": True,
            }

        return result.data

    except Exception as e:
        # If table doesn't exist yet, return defaults
        return {
            "auto_import": False,
            "default_project_id": None,
            "notification_enabled": True,
            "notification_new_entries": True,
            "notification_import_errors": True,
        }


@router.patch("/rss/settings")
async def update_rss_settings(
    auto_import: Optional[bool] = None,
    default_project_id: Optional[UUID] = None,
    notification_enabled: Optional[bool] = None,
    notification_new_entries: Optional[bool] = None,
    notification_import_errors: Optional[bool] = None,
    user=Depends(get_auth_user),
):
    """Update the user's RSS settings."""
    supabase = get_supabase_admin_client()

    try:
        update_data = {}
        if auto_import is not None:
            update_data["auto_import"] = auto_import
        if default_project_id is not None:
            update_data["default_project_id"] = str(default_project_id)
        if notification_enabled is not None:
            update_data["notification_enabled"] = notification_enabled
        if notification_new_entries is not None:
            update_data["notification_new_entries"] = notification_new_entries
        if notification_import_errors is not None:
            update_data["notification_import_errors"] = notification_import_errors

        if not update_data:
            return await get_rss_settings(user=user)

        update_data["user_id"] = str(user.id)

        # Upsert settings
        result = (
            supabase.table("rss_settings")
            .upsert(update_data, on_conflict="user_id")
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update RSS settings",
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/rss/entries/bulk-import")
async def bulk_import_entries(
    entry_ids: List[UUID] = Field(..., description="List of RSS entry IDs to import"),
    project_id: Optional[UUID] = None,
    user=Depends(get_auth_user),
):
    """Bulk import RSS entries as content."""
    supabase = get_supabase_admin_client()

    try:
        # Verify ownership of entries through feeds
        feeds_result = (
            supabase.table("rss_feeds")
            .select("id")
            .eq("user_id", str(user.id))
            .execute()
        )
        user_feed_ids = [f["id"] for f in feeds_result.data]

        if not user_feed_ids:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="No RSS feeds found for user",
            )

        # Get specified entries that belong to user's feeds
        entries_result = (
            supabase.table("rss_entries")
            .select("*")
            .in_("id", [str(eid) for eid in entry_ids])
            .in_("feed_id", user_feed_ids)
            .execute()
        )

        entries = entries_result.data or []
        if not entries:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="No matching RSS entries found",
            )

        imported_count = 0
        failed_count = 0
        imported_content_ids = []

        for entry in entries:
            try:
                result = await rss_service.import_entry(
                    entry_id=entry["id"],
                    user_id=str(user.id),
                    project_id=str(project_id) if project_id else None,
                    title=entry.get("title"),
                    content=entry.get("content"),
                    link=entry.get("link"),
                )
                imported_count += 1
                if result.get("content_id"):
                    imported_content_ids.append(result["content_id"])
            except Exception:
                failed_count += 1

        return {
            "success": failed_count == 0,
            "imported_count": imported_count,
            "failed_count": failed_count,
            "content_ids": imported_content_ids,
            "message": f"Imported {imported_count} entries, {failed_count} failed",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/rss/feeds", response_model=RSSFeedResponse, status_code=http_status.HTTP_201_CREATED
)
async def create_feed(
    feed_data: RSSFeedCreate,
    user=Depends(get_auth_user),
    _: None = Depends(rate_limit_dependency),
):
    """Add a new RSS feed for monitoring."""
    supabase = get_supabase_admin_client()

    try:
        # Validate the RSS feed URL by attempting to fetch it
        is_valid, error_msg = await rss_service.validate_feed(str(feed_data.url))
        if not is_valid:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid RSS feed URL: {error_msg}",
            )

        # Create feed record
        data = {
            "user_id": str(user.id),
            "name": feed_data.name,
            "url": str(feed_data.url),
            "fetch_frequency": feed_data.fetch_frequency,
            "auto_create_content": feed_data.auto_create_content,
            "status": "active",
        }

        result = supabase.table("rss_feeds").insert(data).execute()

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create RSS feed",
            )

        # Trigger initial fetch
        from app.tasks.rss import fetch_single_feed_task

        fetch_single_feed_task.delay(result.data[0]["id"], str(user.id))

        return RSSFeedResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/rss/feeds", response_model=RSSFeedListResponse)
async def list_feeds(
    status: Optional[str] = Query(None, pattern="^(active|paused|error)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_auth_user),
):
    """List all RSS feeds for the current user."""
    supabase = get_supabase_admin_client()

    try:
        # Get total count
        count_query = (
            supabase.table("rss_feeds")
            .select("*", count="exact")
            .eq("user_id", str(user.id))
        )
        if status:
            count_query = count_query.eq("status", status)
        count_result = count_query.execute()
        total = count_result.count or 0

        # Get feeds
        query = supabase.table("rss_feeds").select("*").eq("user_id", str(user.id))
        if status:
            query = query.eq("status", status)

        query = query.order("created_at", desc=True).limit(limit).offset(offset)
        result = query.execute()

        return RSSFeedListResponse(
            feeds=[RSSFeedResponse(**f) for f in result.data], total=total
        )

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/rss/feeds/{feed_id}", response_model=RSSFeedResponse)
async def get_feed(feed_id: UUID, user=Depends(get_auth_user)):
    """Get a specific RSS feed by ID."""
    supabase = get_supabase_admin_client()

    try:
        result = (
            supabase.table("rss_feeds")
            .select("*")
            .eq("id", str(feed_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="RSS feed not found",
            )

        return RSSFeedResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.patch("/rss/feeds/{feed_id}", response_model=RSSFeedResponse)
async def update_feed(
    feed_id: UUID, update_data: RSSFeedUpdate, user=Depends(get_auth_user)
):
    """Update an RSS feed configuration."""
    supabase = get_supabase_admin_client()

    try:
        # Verify ownership
        existing = (
            supabase.table("rss_feeds")
            .select("*")
            .eq("id", str(feed_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="RSS feed not found",
            )

        # Build update data
        update_dict = {}
        if update_data.name is not None:
            update_dict["name"] = update_data.name
        if update_data.fetch_frequency is not None:
            update_dict["fetch_frequency"] = update_data.fetch_frequency
        if update_data.auto_create_content is not None:
            update_dict["auto_create_content"] = update_data.auto_create_content
        if update_data.status is not None:
            update_dict["status"] = update_data.status
            # Clear error message when reactivating
            if update_data.status == "active":
                update_dict["error_message"] = None

        if not update_dict:
            return RSSFeedResponse(**existing.data)

        result = (
            supabase.table("rss_feeds")
            .update(update_dict)
            .eq("id", str(feed_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update RSS feed",
            )

        return RSSFeedResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/rss/feeds/{feed_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_feed(feed_id: UUID, user=Depends(get_auth_user)):
    """Remove an RSS feed and all its entries."""
    supabase = get_supabase_admin_client()

    try:
        # Verify ownership
        existing = (
            supabase.table("rss_feeds")
            .select("*")
            .eq("id", str(feed_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="RSS feed not found",
            )

        # Delete the feed (cascades to entries)
        supabase.table("rss_feeds").delete().eq("id", str(feed_id)).execute()

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/rss/feeds/{feed_id}/fetch", response_model=RSSFetchResponse)
async def manual_fetch(feed_id: UUID, user=Depends(get_auth_user)):
    """Manually trigger a fetch for a specific RSS feed."""
    supabase = get_supabase_admin_client()

    try:
        # Verify ownership
        existing = (
            supabase.table("rss_feeds")
            .select("*")
            .eq("id", str(feed_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="RSS feed not found",
            )

        if existing.data.get("status") == "paused":
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot fetch a paused feed. Please activate it first.",
            )

        # Fetch the feed
        result = await rss_service.fetch_feed(str(feed_id), str(user.id))

        return RSSFetchResponse(
            success=result["success"],
            entries_fetched=result["entries_fetched"],
            entries_new=result["entries_new"],
            message=result["message"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/rss/entries", response_model=RSSEntryListResponse)
async def list_entries(
    feed_id: Optional[UUID] = Query(None, description="Filter by feed ID"),
    processed: Optional[bool] = Query(None, description="Filter by processed status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_auth_user),
):
    """List RSS entries for the current user's feeds."""
    supabase = get_supabase_admin_client()

    try:
        # Get user's feed IDs
        feeds_query = (
            supabase.table("rss_feeds").select("id").eq("user_id", str(user.id))
        )
        if feed_id:
            feeds_query = feeds_query.eq("id", str(feed_id))

        feeds_result = feeds_query.execute()
        feed_ids = [f["id"] for f in feeds_result.data]

        if not feed_ids:
            return RSSEntryListResponse(entries=[], total=0, feed_id=feed_id)

        # Get total count
        count_query = (
            supabase.table("rss_entries")
            .select("*", count="exact")
            .in_("feed_id", feed_ids)
        )
        if processed is not None:
            count_query = count_query.eq("processed", processed)
        count_result = count_query.execute()
        total = count_result.count or 0

        # Get entries
        query = supabase.table("rss_entries").select("*").in_("feed_id", feed_ids)
        if processed is not None:
            query = query.eq("processed", processed)

        query = query.order("published_at", desc=True).limit(limit).offset(offset)
        result = query.execute()

        return RSSEntryListResponse(
            entries=[RSSEntryResponse(**e) for e in result.data],
            total=total,
            feed_id=feed_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/rss/entries/{entry_id}", response_model=RSSEntryResponse)
async def get_entry(entry_id: UUID, user=Depends(get_auth_user)):
    """Get a specific RSS entry by ID."""
    supabase = get_supabase_admin_client()

    try:
        # Get entry with feed ownership check
        result = (
            supabase.table("rss_entries")
            .select("*")
            .eq("id", str(entry_id))
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="RSS entry not found",
            )

        # Verify ownership through feed
        feed_result = (
            supabase.table("rss_feeds")
            .select("*")
            .eq("id", result.data["feed_id"])
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not feed_result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="RSS entry not found",
            )

        return RSSEntryResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/rss/entries/{entry_id}/import", response_model=RSSImportResponse)
async def import_entry(
    entry_id: UUID,
    project_id: Optional[UUID] = Query(
        None, description="Optional project ID to associate with"
    ),
    user=Depends(get_auth_user),
):
    """Import an RSS entry as content."""
    supabase = get_supabase_admin_client()

    try:
        # Get entry with feed ownership check
        entry_result = (
            supabase.table("rss_entries")
            .select("*")
            .eq("id", str(entry_id))
            .single()
            .execute()
        )

        if not entry_result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="RSS entry not found",
            )

        entry = entry_result.data

        # Verify ownership through feed
        feed_result = (
            supabase.table("rss_feeds")
            .select("*")
            .eq("id", entry["feed_id"])
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not feed_result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="RSS entry not found",
            )

        # Check if already imported
        if entry.get("processed") and entry.get("content_id"):
            return RSSImportResponse(
                success=True,
                content_id=entry["content_id"],
                message="Entry was already imported",
            )

        # Import the entry
        result = await rss_service.import_entry(
            entry_id=str(entry_id),
            user_id=str(user.id),
            project_id=str(project_id) if project_id else None,
            title=entry.get("title"),
            content=entry.get("content"),
            link=entry.get("link"),
        )

        return RSSImportResponse(
            success=result["success"],
            content_id=result.get("content_id"),
            message=result["message"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/rss/feeds/{feed_id}/import-all", response_model=RSSImportResponse)
async def import_all_unprocessed(
    feed_id: UUID,
    project_id: Optional[UUID] = Query(
        None, description="Optional project ID to associate with"
    ),
    user=Depends(get_auth_user),
):
    """Import all unprocessed entries from a feed as content."""
    supabase = get_supabase_admin_client()

    try:
        # Verify ownership
        feed_result = (
            supabase.table("rss_feeds")
            .select("*")
            .eq("id", str(feed_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not feed_result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="RSS feed not found",
            )

        # Get all unprocessed entries
        entries_result = (
            supabase.table("rss_entries")
            .select("*")
            .eq("feed_id", str(feed_id))
            .eq("processed", False)
            .execute()
        )

        if not entries_result.data:
            return RSSImportResponse(
                success=True, message="No unprocessed entries found"
            )

        # Import each entry
        imported_count = 0
        failed_count = 0

        for entry in entries_result.data:
            try:
                await rss_service.import_entry(
                    entry_id=entry["id"],
                    user_id=str(user.id),
                    project_id=str(project_id) if project_id else None,
                    title=entry.get("title"),
                    content=entry.get("content"),
                    link=entry.get("link"),
                )
                imported_count += 1
            except Exception:
                failed_count += 1

        return RSSImportResponse(
            success=failed_count == 0,
            message=f"Imported {imported_count} entries, {failed_count} failed",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

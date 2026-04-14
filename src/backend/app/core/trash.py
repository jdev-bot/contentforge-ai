"""
Trash/Recycle Bin functionality for ContentForge AI.
Implements soft delete with recovery and permanent deletion.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.core.config import get_settings
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

settings = get_settings()

# Trash retention period in days
TRASH_RETENTION_DAYS = 30


class TrashItem(BaseModel):
    """Represents an item in the trash."""
    id: str
    type: str  # 'content', 'project', 'asset'
    user_id: str
    original_data: dict
    deleted_at: datetime
    expires_at: datetime
    restored_at: Optional[datetime] = None


def soft_delete_content(content_id: str, user_id: str) -> bool:
    """
    Soft delete content by moving it to trash.
    Returns True if successful.
    """
    supabase = get_supabase_client()
    
    try:
        # Get the content first
        result = supabase.table("content").select("*").eq("id", content_id).eq(
            "user_id", user_id
        ).single().execute()
        
        if not result.data:
            return False
        
        content_data = result.data
        
        # Insert into trash
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=TRASH_RETENTION_DAYS)
        
        supabase.table("trash").insert({
            "id": content_id,
            "type": "content",
            "user_id": user_id,
            "original_data": content_data,
            "deleted_at": now.isoformat(),
            "expires_at": expires.isoformat(),
        }).execute()
        
        # Soft delete from content table
        supabase.table("content").update({
            "deleted_at": now.isoformat(),
            "updated_at": now.isoformat()
        }).eq("id", content_id).eq("user_id", user_id).execute()
        
        return True
    except Exception as e:
        logger.error(f"Failed to soft delete content: {e}")
        return False


def soft_delete_project(project_id: str, user_id: str) -> bool:
    """Soft delete a project and all its content."""
    supabase = get_supabase_client()
    
    try:
        # Get project data
        result = supabase.table("projects").select("*").eq("id", project_id).eq(
            "user_id", user_id
        ).single().execute()
        
        if not result.data:
            return False
        
        project_data = result.data
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=TRASH_RETENTION_DAYS)
        
        # Store project in trash
        supabase.table("trash").insert({
            "id": project_id,
            "type": "project",
            "user_id": user_id,
            "original_data": project_data,
            "deleted_at": now.isoformat(),
            "expires_at": expires.isoformat(),
        }).execute()
        
        # Get all content in this project
        content_result = supabase.table("content").select("id").eq(
            "project_id", project_id
        ).eq("user_id", user_id).execute()
        
        # Soft delete all project content
        for item in content_result.data or []:
            soft_delete_content(item["id"], user_id)
        
        # Soft delete project
        supabase.table("projects").update({
            "deleted_at": now.isoformat(),
            "updated_at": now.isoformat()
        }).eq("id", project_id).eq("user_id", user_id).execute()
        
        return True
    except Exception as e:
        logger.error(f"Failed to soft delete project: {e}")
        return False


def restore_from_trash(item_id: str, user_id: str) -> bool:
    """
    Restore an item from trash.
    Returns True if successful.
    """
    supabase = get_supabase_client()
    
    try:
        # Get trash item
        result = supabase.table("trash").select("*").eq("id", item_id).eq(
            "user_id", user_id
        ).single().execute()
        
        if not result.data:
            return False
        
        trash_item = result.data
        item_type = trash_item["type"]
        original_data = trash_item["original_data"]
        
        now = datetime.now(timezone.utc)
        
        if item_type == "content":
            # Restore content
            supabase.table("content").update({
                "deleted_at": None,
                "updated_at": now.isoformat()
            }).eq("id", item_id).eq("user_id", user_id).execute()
        elif item_type == "project":
            # Restore project
            supabase.table("projects").update({
                "deleted_at": None,
                "updated_at": now.isoformat()
            }).eq("id", item_id).eq("user_id", user_id).execute()
        
        # Mark trash item as restored
        supabase.table("trash").update({
            "restored_at": now.isoformat()
        }).eq("id", item_id).eq("user_id", user_id).execute()
        
        return True
    except Exception as e:
        logger.error(f"Failed to restore from trash: {e}")
        return False


def permanently_delete(item_id: str, user_id: str) -> bool:
    """
    Permanently delete an item from trash.
    Returns True if successful.
    """
    supabase = get_supabase_client()
    
    try:
        # Get trash item to determine type
        result = supabase.table("trash").select("type").eq("id", item_id).eq(
            "user_id", user_id
        ).single().execute()
        
        if not result.data:
            return False
        
        item_type = result.data["type"]
        
        if item_type == "content":
            # Delete from content table
            supabase.table("content").delete().eq("id", item_id).eq(
                "user_id", user_id
            ).execute()
        elif item_type == "project":
            # Delete associated assets first
            supabase.table("assets").delete().eq("content_id", item_id).execute()
            # Delete project
            supabase.table("projects").delete().eq("id", item_id).eq(
                "user_id", user_id
            ).execute()
        
        # Delete from trash
        supabase.table("trash").delete().eq("id", item_id).eq("user_id", user_id).execute()
        
        return True
    except Exception as e:
        logger.error(f"Failed to permanently delete: {e}")
        return False


def list_trash(user_id: str, item_type: Optional[str] = None) -> List[dict]:
    """
    List items in trash for a user.
    Optionally filter by type.
    """
    supabase = get_supabase_client()
    
    try:
        query = supabase.table("trash").select("*").eq("user_id", user_id).is_(
            "restored_at", None
        ).order("deleted_at", desc=True)
        
        if item_type:
            query = query.eq("type", item_type)
        
        result = query.execute()
        return result.data or []
    except Exception as e:
        logger.error(f"Failed to list trash: {e}")
        return []


def get_trash_stats(user_id: str) -> dict:
    """Get trash statistics for a user."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("trash").select("type", count="exact").eq(
            "user_id", user_id
        ).is_("restored_at", None).execute()
        
        total = result.count or 0
        
        # Get breakdown by type
        content_count = len(supabase.table("trash").select("id").eq(
            "user_id", user_id
        ).eq("type", "content").is_("restored_at", None).execute().data or [])
        
        project_count = len(supabase.table("trash").select("id").eq(
            "user_id", user_id
        ).eq("type", "project").is_("restored_at", None).execute().data or [])
        
        return {
            "total": total,
            "content_count": content_count,
            "project_count": project_count,
            "retention_days": TRASH_RETENTION_DAYS
        }
    except Exception as e:
        logger.error(f"Failed to get trash stats: {e}")
        return {"total": 0, "content_count": 0, "project_count": 0, "retention_days": TRASH_RETENTION_DAYS}


def cleanup_expired_trash() -> int:
    """
    Clean up trash items that have expired (past retention period).
    Returns number of items cleaned up.
    """
    supabase = get_supabase_client()
    now = datetime.now(timezone.utc).isoformat()
    
    try:
        # Get expired items
        result = supabase.table("trash").select("id, user_id, type").lt(
            "expires_at", now
        ).is_("restored_at", None).execute()
        
        items = result.data or []
        count = 0
        
        for item in items:
            if permanently_delete(item["id"], item["user_id"]):
                count += 1
        
        return count
    except Exception as e:
        logger.error(f"Failed to cleanup expired trash: {e}")
        return 0


def empty_trash(user_id: str) -> int:
    """
    Empty all trash for a user (permanent deletion).
    Returns number of items deleted.
    """
    items = list_trash(user_id)
    count = 0
    
    for item in items:
        if permanently_delete(item["id"], user_id):
            count += 1
    
    return count

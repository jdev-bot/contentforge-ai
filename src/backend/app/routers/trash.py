"""
Trash/Recycle Bin API routes.
Provides endpoints for soft-deleted content management.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.trash import (empty_trash, get_trash_stats, list_trash,
                            permanently_delete, restore_from_trash)
from app.routers.auth import get_auth_user

router = APIRouter()


class TrashItemResponse(BaseModel):
    """Trash item response model."""
    id: str
    type: str
    original_data: dict
    deleted_at: str
    expires_at: str


class TrashStatsResponse(BaseModel):
    """Trash stats response."""
    total: int
    content_count: int
    project_count: int
    retention_days: int


class RestoreResponse(BaseModel):
    """Restore response."""
    message: str
    item_id: str
    restored: bool


class DeleteResponse(BaseModel):
    """Permanent delete response."""
    message: str
    item_id: str
    deleted: bool


class EmptyTrashResponse(BaseModel):
    """Empty trash response."""
    message: str
    items_deleted: int


@router.get("/trash", response_model=List[TrashItemResponse])
async def get_trash(
    item_type: Optional[str] = None,
    user=Depends(get_auth_user)
):
    """
    List items in trash.
    
    Args:
        item_type: Optional filter by type ('content', 'project')
    
    Returns list of trashed items with original data.
    """
    try:
        items = list_trash(str(user.id), item_type=item_type)
        return [
            TrashItemResponse(
                id=item["id"],
                type=item["type"],
                original_data=item["original_data"],
                deleted_at=item["deleted_at"],
                expires_at=item["expires_at"],
            )
            for item in items
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trash: {str(e)}"
        )


@router.get("/trash/stats", response_model=TrashStatsResponse)
async def get_trash_statistics(user=Depends(get_auth_user)):
    """
    Get trash statistics for the current user.
    """
    try:
        stats = get_trash_stats(str(user.id))
        return TrashStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trash stats: {str(e)}"
        )


@router.post("/trash/{item_id}/restore", response_model=RestoreResponse)
async def restore_item(
    item_id: str,
    user=Depends(get_auth_user)
):
    """
    Restore an item from trash back to its original location.
    """
    try:
        success = restore_from_trash(item_id, str(user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in trash"
            )
        
        return RestoreResponse(
            message="Item restored successfully",
            item_id=item_id,
            restored=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restore item: {str(e)}"
        )


@router.delete("/trash/{item_id}", response_model=DeleteResponse)
async def permanently_delete_item(
    item_id: str,
    user=Depends(get_auth_user)
):
    """
    Permanently delete an item from trash.
    This action cannot be undone.
    """
    try:
        success = permanently_delete(item_id, str(user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in trash"
            )
        
        return DeleteResponse(
            message="Item permanently deleted",
            item_id=item_id,
            deleted=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete item: {str(e)}"
        )


@router.post("/trash/empty", response_model=EmptyTrashResponse)
async def empty_user_trash(user=Depends(get_auth_user)):
    """
    Empty all trash for the current user (permanent deletion).
    This action cannot be undone.
    """
    try:
        count = empty_trash(str(user.id))
        
        return EmptyTrashResponse(
            message=f"Trash emptied successfully. {count} items deleted.",
            items_deleted=count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to empty trash: {str(e)}"
        )

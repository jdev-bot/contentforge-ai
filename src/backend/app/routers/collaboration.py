"""
Collaboration REST API router.

Provides HTTP endpoints for querying collaboration state
(edit history, locks, cursors). Real-time editing flows
through the WebSocket channel (app/routers/ws.py).
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.routers.auth import get_auth_user
from app.services.collaboration_service import collaboration_service

logger = logging.getLogger(__name__)

router = APIRouter()


class EditHistoryResponse(BaseModel):
    content_id: str
    version: int
    edits: list


class LockResponse(BaseModel):
    content_id: str
    locked: bool
    holder: Optional[dict] = None


class CursorResponse(BaseModel):
    content_id: str
    cursors: dict


@router.get("/collaboration/{content_id}/history", response_model=EditHistoryResponse)
async def get_edit_history(
    content_id: str,
    limit: int = 50,
    offset: int = 0,
    user=Depends(get_auth_user),
):
    """Get recent edit operations for a content item."""
    edits = collaboration_service.get_edit_history(content_id, limit=limit, offset=offset)
    version = collaboration_service.get_current_version(content_id)
    return EditHistoryResponse(
        content_id=content_id,
        version=version,
        edits=edits,
    )


@router.get("/collaboration/{content_id}/version")
async def get_current_version(
    content_id: str,
    user=Depends(get_auth_user),
):
    """Get the current version number for a content item."""
    return {
        "content_id": content_id,
        "version": collaboration_service.get_current_version(content_id),
    }


@router.get("/collaboration/{content_id}/lock", response_model=LockResponse)
async def get_lock_status(
    content_id: str,
    user=Depends(get_auth_user),
):
    """Get the lock status for a content item."""
    lock_info = collaboration_service.get_lock_info(content_id)
    return LockResponse(
        content_id=content_id,
        locked=lock_info is not None,
        holder=lock_info,
    )


@router.get("/collaboration/{content_id}/cursors", response_model=CursorResponse)
async def get_cursor_positions(
    content_id: str,
    user=Depends(get_auth_user),
):
    """Get all current cursor positions for a content item."""
    cursors = collaboration_service.get_cursors(content_id)
    return CursorResponse(content_id=content_id, cursors=cursors)
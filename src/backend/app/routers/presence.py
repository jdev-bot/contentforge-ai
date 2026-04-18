"""
Presence REST API router.

Provides HTTP endpoints for querying presence state.
Real-time updates flow through the WebSocket channel (app/routers/ws.py).
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from pydantic import BaseModel

from app.routers.auth import get_auth_user
from app.services.presence_service import presence_service

logger = logging.getLogger(__name__)

router = APIRouter()


class PresenceResponse(BaseModel):
    room: str
    users: list
    typing: list


class UserStatusUpdate(BaseModel):
    status: str  # "online", "away", "editing"


@router.get("/presence/{room}", response_model=PresenceResponse)
async def get_room_presence(
    room: str,
    user=Depends(get_auth_user),
):
    """Get current presence state for a room."""
    users = presence_service.get_room_presence(room)
    typing = presence_service.get_typing_users(room)
    return PresenceResponse(room=room, users=users, typing=typing)


@router.get("/presence/{room}/count")
async def get_room_presence_count(
    room: str,
    user=Depends(get_auth_user),
):
    """Get the number of present users in a room."""
    return {"room": room, "count": presence_service.get_room_count(room)}


@router.get("/presence/user/{user_id}/rooms")
async def get_user_rooms(
    user_id: str,
    user=Depends(get_auth_user),
):
    """Get all rooms a user is present in."""
    rooms = presence_service.get_user_rooms(user_id)
    return {"user_id": user_id, "rooms": rooms}

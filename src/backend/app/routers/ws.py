"""
WebSocket router.

Main WebSocket endpoint for real-time communication:
- Authentication via query token
- Room join/leave
- Message routing to appropriate services
"""

import logging
import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from app.core.supabase import get_supabase_client
from app.services.collaboration_service import collaboration_service
from app.services.presence_service import UserStatus, presence_service
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter()


def _authenticate_ws_token(token: str) -> Optional[dict]:
    """
    Validate a Supabase JWT token and return user info.

    Returns a dict with 'id' and 'email' on success, or None.
    """
    if not token:
        return None
    supabase = get_supabase_client()
    try:
        user = supabase.auth.get_user(token)
        if user and user.user:
            return {
                "id": str(user.user.id),
                "email": user.user.email,
                "full_name": (user.user.user_metadata or {}).get("full_name", ""),
            }
    except Exception as exc:
        logger.warning("WebSocket auth failed: %s", exc)
    return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="Supabase JWT token for authentication"),
):
    """
    Main WebSocket endpoint.

    Authentication is performed via the `token` query parameter.
    After successful auth, the client can send JSON messages to:
    - Join/leave rooms
    - Update presence
    - Send edit operations
    - Update cursor position
    - Set typing indicators
    """
    # ── Authenticate ──────────────────────────────────────────────
    user_info = _authenticate_ws_token(token)
    if user_info is None:
        await websocket.close(code=4001, reason="Authentication failed")
        return

    user_id = user_info["id"]
    user_name = user_info.get("full_name", user_info.get("email", ""))
    connection_id = str(uuid.uuid4())

    # ── Accept and register ──────────────────────────────────────
    await websocket.accept()
    accepted = await websocket_manager.connect(connection_id, websocket, user_id)
    if not accepted:
        await websocket.close(code=4002, reason="Connection limit reached")
        return

    # Send welcome message
    await websocket_manager.send_to_connection(
        connection_id,
        {
            "type": "connected",
            "connection_id": connection_id,
            "user_id": user_id,
        },
    )

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            # ── Heartbeat ────────────────────────────────────────
            if msg_type == "pong":
                await websocket_manager.record_pong(connection_id)

            # ── Room management ──────────────────────────────────
            elif msg_type == "room:join":
                room = data.get("room", "")
                if room:
                    joined = await websocket_manager.join_room(connection_id, room)
                    if joined:
                        # Auto-join presence
                        if room.startswith("content:"):
                            await presence_service.join(
                                room, user_id, user_name, UserStatus.ONLINE
                            )
                        await websocket_manager.send_to_connection(
                            connection_id,
                            {
                                "type": "room:joined",
                                "room": room,
                                "members": websocket_manager.get_room_members(room),
                            },
                        )

            elif msg_type == "room:leave":
                room = data.get("room", "")
                if room:
                    await websocket_manager.leave_room(connection_id, room)
                    if room.startswith("content:"):
                        await presence_service.leave(room, user_id)
                    await websocket_manager.send_to_connection(
                        connection_id,
                        {
                            "type": "room:left",
                            "room": room,
                        },
                    )

            # ── Presence ─────────────────────────────────────────
            elif msg_type == "presence:status":
                room = data.get("room", "")
                new_status = data.get("status", "online")
                try:
                    status_enum = UserStatus(new_status)
                    await presence_service.update_status(room, user_id, status_enum)
                except ValueError:
                    await websocket_manager.send_to_connection(
                        connection_id,
                        {
                            "type": "error",
                            "detail": f"Invalid status: {new_status}",
                        },
                    )

            elif msg_type == "presence:typing":
                room = data.get("room", "")
                is_typing = data.get("is_typing", True)
                await presence_service.set_typing(room, user_id, is_typing)

            # ── Collaboration ────────────────────────────────────
            elif msg_type == "collab:lock":
                content_id = data.get("content_id", "")
                result = await collaboration_service.acquire_lock(
                    content_id, user_id, user_name
                )
                await websocket_manager.send_to_connection(
                    connection_id,
                    {
                        "type": "collab:lock_result",
                        "content_id": content_id,
                        **result,
                    },
                )

            elif msg_type == "collab:unlock":
                content_id = data.get("content_id", "")
                released = await collaboration_service.release_lock(content_id, user_id)
                await websocket_manager.send_to_connection(
                    connection_id,
                    {
                        "type": "collab:unlock_result",
                        "content_id": content_id,
                        "released": released,
                    },
                )

            elif msg_type == "collab:edit":
                content_id = data.get("content_id", "")
                operation = data.get("operation", {})
                result = await collaboration_service.apply_edit(
                    content_id=content_id,
                    user_id=user_id,
                    user_name=user_name,
                    operation_type=operation.get("operation_type", "replace"),
                    position=operation.get("position", 0),
                    length=operation.get("length", 0),
                    text=operation.get("text", ""),
                    base_version=operation.get("base_version"),
                )
                await websocket_manager.send_to_connection(
                    connection_id,
                    {
                        "type": "collab:edit_result",
                        "content_id": content_id,
                        **result,
                    },
                )

            elif msg_type == "collab:cursor":
                content_id = data.get("content_id", "")
                cursor = data.get("cursor", {})
                await collaboration_service.update_cursor(
                    content_id,
                    user_id,
                    line=cursor.get("line", 0),
                    col=cursor.get("col", 0),
                )

            # ── Unknown ──────────────────────────────────────────
            else:
                await websocket_manager.send_to_connection(
                    connection_id,
                    {
                        "type": "error",
                        "detail": f"Unknown message type: {msg_type}",
                    },
                )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s (user=%s)", connection_id, user_id)
    except Exception as exc:
        logger.error("WebSocket error for %s: %s", connection_id, exc)
    finally:
        # Clean up: leave all rooms and disconnect
        info = websocket_manager._connections.get(connection_id)
        if info:
            for room in list(info.rooms):
                if room.startswith("content:"):
                    await presence_service.leave(room, user_id)
        await websocket_manager.disconnect(connection_id, reason="client_disconnect")

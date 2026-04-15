"""
Presence Service.

Provides:
- Track which users are viewing/editing which content
- Real-time presence updates via WebSocket
- Typing indicators
- User status (online, away, editing)
- Lazy Supabase init for persistence
"""

import json
import logging
import time
from collections import defaultdict
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)

# Presence TTL — entries older than this are considered stale (seconds)
PRESENCE_TTL = 300  # 5 minutes
TYPING_INDICATOR_TIMEOUT = 5  # seconds before typing indicator expires


class UserStatus(str, Enum):
    ONLINE = "online"
    AWAY = "away"
    EDITING = "editing"


class PresenceService:
    """
    Service for tracking and broadcasting user presence across content rooms.

    Presence state is held in memory for fast access and optionally
    persisted to Supabase for crash recovery.
    """

    _supabase = None

    @property
    def supabase(self):
        """Lazy Supabase client initialization."""
        if self._supabase is None:
            self._supabase = get_supabase_admin_client()
        return self._supabase

    def __init__(self):
        # room_key -> { user_id -> PresenceEntry }
        self._rooms: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        # user_id -> set of rooms
        self._user_rooms: Dict[str, Set[str]] = defaultdict(set)
        # room_key -> { user_id -> last_typing_timestamp }
        self._typing: Dict[str, Dict[str, float]] = defaultdict(dict)

    # ── Presence Tracking ─────────────────────────────────────────

    async def join(
        self,
        room: str,
        user_id: str,
        user_name: str = "",
        status: UserStatus = UserStatus.ONLINE,
    ) -> Dict[str, Any]:
        """
        Mark a user as present in a room and broadcast the join event.
        """
        entry = {
            "user_id": user_id,
            "user_name": user_name,
            "status": status.value,
            "joined_at": time.time(),
            "last_active": time.time(),
        }

        self._rooms[room][user_id] = entry
        self._user_rooms[user_id].add(room)

        # Broadcast presence join to the room
        await websocket_manager.broadcast_to_room(
            room,
            {
                "type": "presence:join",
                "room": room,
                "user_id": user_id,
                "user_name": user_name,
                "status": status.value,
            },
        )

        # Persist to Supabase (best-effort)
        self._persist_presence(room, user_id, entry)

        return entry

    async def leave(self, room: str, user_id: str) -> None:
        """Remove a user from a room and broadcast the leave event."""
        self._rooms[room].pop(user_id, None)
        self._user_rooms[user_id].discard(room)
        self._typing[room].pop(user_id, None)

        # Clean up empty rooms
        if not self._rooms[room]:
            del self._rooms[room]
        if not self._user_rooms[user_id]:
            self._user_rooms.pop(user_id, None)

        await websocket_manager.broadcast_to_room(
            room,
            {
                "type": "presence:leave",
                "room": room,
                "user_id": user_id,
            },
        )

        # Remove from persistence (best-effort)
        self._remove_presence(room, user_id)

    async def update_status(
        self,
        room: str,
        user_id: str,
        status: UserStatus,
    ) -> None:
        """Update a user's status in a room and broadcast the change."""
        entry = self._rooms.get(room, {}).get(user_id)
        if entry is None:
            return

        entry["status"] = status.value
        entry["last_active"] = time.time()

        await websocket_manager.broadcast_to_room(
            room,
            {
                "type": "presence:status",
                "room": room,
                "user_id": user_id,
                "status": status.value,
            },
        )

        # Persist updated status
        self._persist_presence(room, user_id, entry)

    # ── Typing Indicators ────────────────────────────────────────

    async def set_typing(
        self,
        room: str,
        user_id: str,
        is_typing: bool = True,
    ) -> None:
        """Set or clear a typing indicator for a user in a room."""
        if is_typing:
            self._typing[room][user_id] = time.time()
            await websocket_manager.broadcast_to_room(
                room,
                {
                    "type": "presence:typing",
                    "room": room,
                    "user_id": user_id,
                    "is_typing": True,
                },
            )
        else:
            self._typing[room].pop(user_id, None)
            await websocket_manager.broadcast_to_room(
                room,
                {
                    "type": "presence:typing",
                    "room": room,
                    "user_id": user_id,
                    "is_typing": False,
                },
            )

    def get_typing_users(self, room: str) -> List[Dict[str, Any]]:
        """Return users currently typing in a room (within timeout window)."""
        now = time.time()
        typing = self._typing.get(room, {})
        active = []
        expired = []

        for uid, ts in typing.items():
            if now - ts > TYPING_INDICATOR_TIMEOUT:
                expired.append(uid)
            else:
                entry = self._rooms.get(room, {}).get(uid)
                if entry:
                    active.append(
                        {
                            "user_id": uid,
                            "user_name": entry.get("user_name", ""),
                        }
                    )

        # Clean up expired entries
        for uid in expired:
            typing.pop(uid, None)

        return active

    # ── Query ────────────────────────────────────────────────────

    def get_room_presence(self, room: str) -> List[Dict[str, Any]]:
        """Return all present users in a room."""
        self._prune_stale(room)
        entries = list(self._rooms.get(room, {}).values())
        return [
            {
                "user_id": e["user_id"],
                "user_name": e.get("user_name", ""),
                "status": e.get("status", "online"),
                "last_active": e.get("last_active"),
            }
            for e in entries
        ]

    def get_user_rooms(self, user_id: str) -> List[str]:
        """Return all rooms a user is present in."""
        return list(self._user_rooms.get(user_id, set()))

    def get_room_count(self, room: str) -> int:
        """Return the number of present users in a room."""
        return len(self._rooms.get(room, {}))

    # ── Cleanup ──────────────────────────────────────────────────

    def _prune_stale(self, room: str) -> None:
        """Remove entries that have exceeded the presence TTL."""
        now = time.time()
        stale_uids = [
            uid
            for uid, entry in self._rooms.get(room, {}).items()
            if now - entry.get("last_active", 0) > PRESENCE_TTL
        ]
        for uid in stale_uids:
            self._rooms[room].pop(uid, None)
            self._typing[room].pop(uid, None)
            self._user_rooms[uid].discard(room)

    # ── Persistence (best-effort) ────────────────────────────────

    def _persist_presence(self, room: str, user_id: str, entry: Dict[str, Any]) -> None:
        """Upsert presence to Supabase (best-effort, non-blocking)."""
        try:
            data = {
                "room": room,
                "user_id": user_id,
                "user_name": entry.get("user_name", ""),
                "status": entry.get("status", "online"),
                "last_active": entry.get("last_active"),
                "updated_at": time.time(),
            }
            # Upsert on (room, user_id) composite key
            self.supabase.table("presence").upsert(
                data, on_conflict="room,user_id"
            ).execute()
        except Exception as exc:
            logger.debug("Failed to persist presence: %s", exc)

    def _remove_presence(self, room: str, user_id: str) -> None:
        """Remove presence from Supabase (best-effort)."""
        try:
            self.supabase.table("presence").delete().eq("room", room).eq(
                "user_id", user_id
            ).execute()
        except Exception as exc:
            logger.debug("Failed to remove presence: %s", exc)


# Singleton instance
presence_service = PresenceService()

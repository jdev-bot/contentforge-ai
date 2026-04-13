"""
Collaboration Service.

Provides:
- WebSocket endpoint for real-time editing
- Simple operational transform (last-write-wins with conflict detection)
- Cursor position broadcasting
- Edit operations stream
- Content locking for concurrent edits
- Edit history broadcast to collaborators
"""
import asyncio
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from app.core.supabase import get_supabase_client
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)

# Lock TTL — content locks expire after this many seconds of inactivity
CONTENT_LOCK_TTL = 30  # seconds
# Maximum edit history per content item kept in memory
MAX_EDIT_HISTORY = 100


@dataclass
class ContentLock:
    """Tracks who currently holds a lock on a piece of content."""
    user_id: str
    user_name: str
    locked_at: float
    last_renewed: float


@dataclass
class EditOperation:
    """Represents a single edit operation."""
    id: str
    user_id: str
    user_name: str
    content_id: str
    operation_type: str  # "insert", "delete", "replace", "cursor"
    position: int
    length: int = 0
    text: str = ""
    cursor_line: int = 0
    cursor_col: int = 0
    timestamp: float = field(default_factory=time.time)
    version: int = 0


class CollaborationService:
    """
    Service for managing collaborative editing sessions.

    Uses a simple last-write-wins approach with conflict detection.
    Cursor positions and edit operations are broadcast to all
    collaborators in real-time via WebSocket.
    """

    _supabase = None

    @property
    def supabase(self):
        """Lazy Supabase client initialization."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    def __init__(self):
        # content_id -> ContentLock
        self._locks: Dict[str, ContentLock] = {}
        # content_id -> list of EditOperation (in-memory buffer)
        self._edit_history: Dict[str, List[EditOperation]] = defaultdict(list)
        # content_id -> current version number
        self._versions: Dict[str, int] = defaultdict(int)
        # content_id -> { user_id -> cursor position }
        self._cursors: Dict[str, Dict[str, Dict[str, int]]] = defaultdict(dict)

    # ── Content Locking ──────────────────────────────────────────

    async def acquire_lock(
        self,
        content_id: str,
        user_id: str,
        user_name: str = "",
    ) -> Dict[str, Any]:
        """
        Attempt to acquire an edit lock on content.

        Returns a dict with:
          - locked: bool — whether the lock was acquired
          - holder: optional info about who holds the lock if not acquired
        """
        existing = self._locks.get(content_id)
        now = time.time()

        # Expired lock — release it
        if existing and now - existing.last_renewed > CONTENT_LOCK_TTL:
            del self._locks[content_id]
            existing = None

        if existing is None:
            # No lock — acquire it
            lock = ContentLock(
                user_id=user_id,
                user_name=user_name,
                locked_at=now,
                last_renewed=now,
            )
            self._locks[content_id] = lock

            await websocket_manager.broadcast_to_room(
                f"content:{content_id}",
                {
                    "type": "collab:lock_acquired",
                    "content_id": content_id,
                    "user_id": user_id,
                    "user_name": user_name,
                },
            )

            return {"locked": True, "holder": None}

        if existing.user_id == user_id:
            # Same user — renew
            existing.last_renewed = now
            return {"locked": True, "holder": None}

        # Locked by someone else
        return {
            "locked": False,
            "holder": {
                "user_id": existing.user_id,
                "user_name": existing.user_name,
                "locked_at": existing.locked_at,
            },
        }

    async def release_lock(self, content_id: str, user_id: str) -> bool:
        """Release a content lock (only by the holder)."""
        existing = self._locks.get(content_id)
        if existing is None or existing.user_id != user_id:
            return False

        del self._locks[content_id]

        await websocket_manager.broadcast_to_room(
            f"content:{content_id}",
            {
                "type": "collab:lock_released",
                "content_id": content_id,
                "user_id": user_id,
            },
        )

        return True

    async def renew_lock(self, content_id: str, user_id: str) -> bool:
        """Renew a content lock to prevent expiration."""
        existing = self._locks.get(content_id)
        if existing is None or existing.user_id != user_id:
            return False
        existing.last_renewed = time.time()
        return True

    def get_lock_info(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Return lock info for content, or None if unlocked."""
        lock = self._locks.get(content_id)
        if lock is None:
            return None
        now = time.time()
        if now - lock.last_renewed > CONTENT_LOCK_TTL:
            # Expired
            del self._locks[content_id]
            return None
        return {
            "user_id": lock.user_id,
            "user_name": lock.user_name,
            "locked_at": lock.locked_at,
            "last_renewed": lock.last_renewed,
        }

    # ── Edit Operations ──────────────────────────────────────────

    async def apply_edit(
        self,
        content_id: str,
        user_id: str,
        user_name: str,
        operation_type: str,
        position: int,
        length: int = 0,
        text: str = "",
        base_version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Apply an edit operation and broadcast it to collaborators.

        Uses last-write-wins with conflict detection:
        - If base_version is provided and doesn't match current, a conflict is flagged.
        - The edit is still applied (last-write-wins), but the response indicates a conflict.
        """
        self._versions[content_id] += 1
        version = self._versions[content_id]

        op = EditOperation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            user_name=user_name,
            content_id=content_id,
            operation_type=operation_type,
            position=position,
            length=length,
            text=text,
            version=version,
        )

        # Conflict detection
        conflict = False
        if base_version is not None and base_version < version - 1:
            conflict = True

        # Store in history
        self._edit_history[content_id].append(op)
        if len(self._edit_history[content_id]) > MAX_EDIT_HISTORY:
            self._edit_history[content_id] = self._edit_history[content_id][-MAX_EDIT_HISTORY:]

        # Broadcast the edit to collaborators
        room = f"content:{content_id}"
        await websocket_manager.broadcast_to_room(
            room,
            {
                "type": "collab:edit",
                "content_id": content_id,
                "operation": {
                    "id": op.id,
                    "user_id": user_id,
                    "user_name": user_name,
                    "operation_type": operation_type,
                    "position": position,
                    "length": length,
                    "text": text,
                    "version": version,
                },
            },
        )

        # Persist the edit to Supabase (best-effort)
        self._persist_edit(content_id, op)

        return {
            "applied": True,
            "version": version,
            "conflict": conflict,
            "operation_id": op.id,
        }

    # ── Cursor Position ─────────────────────────────────────────

    async def update_cursor(
        self,
        content_id: str,
        user_id: str,
        line: int,
        col: int,
    ) -> None:
        """Update and broadcast a user's cursor position."""
        self._cursors[content_id][user_id] = {"line": line, "col": col}

        room = f"content:{content_id}"
        await websocket_manager.broadcast_to_room(
            room,
            {
                "type": "collab:cursor",
                "content_id": content_id,
                "user_id": user_id,
                "cursor": {"line": line, "col": col},
            },
        )

    def get_cursors(self, content_id: str) -> Dict[str, Dict[str, int]]:
        """Return all cursor positions for a content item."""
        return dict(self._cursors.get(content_id, {}))

    # ── Edit History ────────────────────────────────────────────

    def get_edit_history(
        self,
        content_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Return recent edit operations for a content item."""
        history = self._edit_history.get(content_id, [])
        # Return from newest to oldest within the range
        sliced = list(reversed(history))[offset : offset + limit]
        return [
            {
                "id": op.id,
                "user_id": op.user_id,
                "user_name": op.user_name,
                "operation_type": op.operation_type,
                "position": op.position,
                "length": op.length,
                "text": op.text,
                "version": op.version,
                "timestamp": op.timestamp,
            }
            for op in sliced
        ]

    def get_current_version(self, content_id: str) -> int:
        """Return the current version number for a content item."""
        return self._versions.get(content_id, 0)

    # ── Persistence (best-effort) ────────────────────────────────

    def _persist_edit(self, content_id: str, op: EditOperation) -> None:
        """Persist an edit operation to Supabase."""
        try:
            data = {
                "id": op.id,
                "content_id": content_id,
                "user_id": op.user_id,
                "operation_type": op.operation_type,
                "position": op.position,
                "length": op.length,
                "text": op.text,
                "version": op.version,
                "created_at": time.time(),
            }
            self.supabase.table("collaboration_edits").insert(data).execute()
        except Exception as exc:
            logger.debug("Failed to persist edit: %s", exc)


# Singleton instance
collaboration_service = CollaborationService()
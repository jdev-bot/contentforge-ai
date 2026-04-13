"""
WebSocket Connection Manager.

Provides:
- Room-based connection tracking (per content/project)
- Broadcast to room subscribers
- Heartbeat/ping-pong for connection health
- Graceful disconnect handling
- Connection limit per user
"""
import asyncio
import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)

# Default configuration
MAX_CONNECTIONS_PER_USER = 5
HEARTBEAT_INTERVAL = 30  # seconds
HEARTBEAT_TIMEOUT = 60   # seconds — close if no pong within this window


@dataclass
class ConnectionInfo:
    """Tracks state for a single WebSocket connection."""
    websocket: WebSocket
    user_id: str
    rooms: Set[str] = field(default_factory=set)
    last_pong: float = field(default_factory=time.time)
    connected_at: float = field(default_factory=time.time)


class WebSocketManager:
    """
    Manages WebSocket connections with room-based messaging.

    Rooms are identified by string keys (e.g. "content:<uuid>",
    "project:<uuid>"). A single connection may belong to multiple rooms.
    """

    def __init__(
        self,
        max_connections_per_user: int = MAX_CONNECTIONS_PER_USER,
        heartbeat_interval: int = HEARTBEAT_INTERVAL,
        heartbeat_timeout: int = HEARTBEAT_TIMEOUT,
    ):
        # connection_id -> ConnectionInfo
        self._connections: Dict[str, ConnectionInfo] = {}
        # room_key -> set of connection_ids
        self._rooms: Dict[str, Set[str]] = defaultdict(set)
        # user_id -> set of connection_ids
        self._user_connections: Dict[str, Set[str]] = defaultdict(set)

        self._max_per_user = max_connections_per_user
        self._heartbeat_interval = heartbeat_interval
        self._heartbeat_timeout = heartbeat_timeout

        self._lock = asyncio.Lock()
        self._heartbeat_task: Optional[asyncio.Task] = None

    # ── Lifecycle ─────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the heartbeat monitor (call once at app startup)."""
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info("WebSocketManager heartbeat monitor started")

    async def stop(self) -> None:
        """Stop the heartbeat monitor and close all connections."""
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # Close all connections gracefully
        conn_ids = list(self._connections.keys())
        for cid in conn_ids:
            await self.disconnect(cid, reason="Server shutting down")

        logger.info("WebSocketManager stopped")

    # ── Connect / Disconnect ──────────────────────────────────────

    async def connect(
        self,
        connection_id: str,
        websocket: WebSocket,
        user_id: str,
    ) -> bool:
        """
        Register a new WebSocket connection.

        Returns True if accepted, False if the user has reached the
        connection limit.
        """
        async with self._lock:
            user_conns = self._user_connections[user_id]
            if len(user_conns) >= self._max_per_user:
                logger.warning(
                    "User %s exceeded connection limit (%d)",
                    user_id, self._max_per_user,
                )
                return False

            info = ConnectionInfo(
                websocket=websocket,
                user_id=user_id,
            )
            self._connections[connection_id] = info
            user_conns.add(connection_id)
            logger.info(
                "WebSocket connected: %s (user=%s, total=%d)",
                connection_id, user_id, len(self._connections),
            )
            return True

    async def disconnect(
        self,
        connection_id: str,
        reason: str = "client_disconnect",
    ) -> None:
        """Remove a connection and leave all rooms."""
        async with self._lock:
            info = self._connections.pop(connection_id, None)
            if info is None:
                return

            # Leave all rooms
            for room in list(info.rooms):
                self._rooms[room].discard(connection_id)
                if not self._rooms[room]:
                    del self._rooms[room]

            # Remove from user index
            user_conns = self._user_connections.get(info.user_id, set())
            user_conns.discard(connection_id)
            if not user_conns:
                self._user_connections.pop(info.user_id, None)

            logger.info(
                "WebSocket disconnected: %s (user=%s, reason=%s, remaining=%d)",
                connection_id, info.user_id, reason, len(self._connections),
            )

        # Close the underlying socket outside the lock
        try:
            await info.websocket.close(code=1000, reason=reason)
        except Exception:
            pass

    # ── Room Management ───────────────────────────────────────────

    async def join_room(self, connection_id: str, room: str) -> bool:
        """Add a connection to a room."""
        async with self._lock:
            info = self._connections.get(connection_id)
            if info is None:
                return False
            info.rooms.add(room)
            self._rooms[room].add(connection_id)
            logger.debug("Connection %s joined room %s", connection_id, room)
            return True

    async def leave_room(self, connection_id: str, room: str) -> bool:
        """Remove a connection from a room."""
        async with self._lock:
            info = self._connections.get(connection_id)
            if info is None:
                return False
            info.rooms.discard(room)
            self._rooms[room].discard(connection_id)
            if not self._rooms[room]:
                del self._rooms[room]
            logger.debug("Connection %s left room %s", connection_id, room)
            return True

    # ── Messaging ────────────────────────────────────────────────

    async def broadcast_to_room(
        self,
        room: str,
        message: Dict[str, Any],
        exclude_connection: Optional[str] = None,
    ) -> int:
        """
        Send a JSON message to all connections in a room.

        Returns the number of connections that received the message.
        """
        async with self._lock:
            member_ids = list(self._rooms.get(room, set()))

        sent = 0
        for cid in member_ids:
            if cid == exclude_connection:
                continue
            info = self._connections.get(cid)
            if info is None:
                continue
            try:
                await info.websocket.send_json(message)
                sent += 1
            except Exception as exc:
                logger.warning(
                    "Failed to send to %s in room %s: %s", cid, room, exc
                )
                # Stale connection — schedule cleanup
                await self.disconnect(cid, reason="send_failure")

        return sent

    async def send_to_connection(
        self,
        connection_id: str,
        message: Dict[str, Any],
    ) -> bool:
        """Send a JSON message to a single connection."""
        info = self._connections.get(connection_id)
        if info is None:
            return False
        try:
            await info.websocket.send_json(message)
            return True
        except Exception as exc:
            logger.warning("Failed to send to %s: %s", connection_id, exc)
            await self.disconnect(connection_id, reason="send_failure")
            return False

    # ── Heartbeat ────────────────────────────────────────────────

    async def record_pong(self, connection_id: str) -> None:
        """Record that a pong was received for a connection."""
        info = self._connections.get(connection_id)
        if info:
            info.last_pong = time.time()

    async def _heartbeat_loop(self) -> None:
        """Periodically send pings and evict unresponsive connections."""
        while True:
            try:
                await asyncio.sleep(self._heartbeat_interval)
            except asyncio.CancelledError:
                return

            now = time.time()
            stale_ids: List[str] = []

            async with self._lock:
                for cid, info in list(self._connections.items()):
                    if now - info.last_pong > self._heartbeat_timeout:
                        stale_ids.append(cid)

            for cid in stale_ids:
                logger.warning("Evicting stale connection: %s", cid)
                await self.disconnect(cid, reason="heartbeat_timeout")

            # Send pings to all active connections
            async with self._lock:
                active_ids = list(self._connections.keys())

            for cid in active_ids:
                info = self._connections.get(cid)
                if info is None:
                    continue
                try:
                    await info.websocket.send_json({"type": "ping"})
                except Exception:
                    pass  # Will be cleaned up next cycle

    # ── Query Helpers ─────────────────────────────────────────────

    def get_room_members(self, room: str) -> List[Dict[str, Any]]:
        """Return connection info for all members of a room."""
        members = []
        for cid in self._rooms.get(room, set()):
            info = self._connections.get(cid)
            if info:
                members.append({
                    "connection_id": cid,
                    "user_id": info.user_id,
                    "connected_at": info.connected_at,
                })
        return members

    def get_user_connections(self, user_id: str) -> List[str]:
        """Return connection IDs for a user."""
        return list(self._user_connections.get(user_id, set()))

    def get_room_count(self, room: str) -> int:
        """Return the number of connections in a room."""
        return len(self._rooms.get(room, set()))

    def get_total_connections(self) -> int:
        """Return the total number of active connections."""
        return len(self._connections)


# Singleton instance
websocket_manager = WebSocketManager()
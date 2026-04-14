"""
Comments & Annotations Service.

Provides:
- Inline comments on content (with position/range)
- Thread support (reply to comments)
- Comment resolution (mark as resolved)
- Comment mentions (@user)
- Comment reactions (emoji reactions)
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.supabase import get_supabase_client

# Regex to find @mentions in comment text
MENTION_PATTERN = re.compile(r"@(\w[\w.-]*)")


class CommentsService:
    """Service for managing content comments, threads, mentions, and reactions."""

    _supabase = None

    @property
    def supabase(self):
        """Lazy Supabase client initialization."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    # ── Comment CRUD ──────────────────────────────────────────────

    def create_comment(
        self,
        user_id: UUID,
        content_id: UUID,
        text: str,
        position_start: Optional[int] = None,
        position_end: Optional[int] = None,
        parent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a comment on content.

        Args:
            user_id: Author of the comment.
            content_id: Content being commented on.
            text: Comment text (may include @mentions).
            position_start: Start character offset for inline annotation.
            position_end: End character offset for inline annotation.
            parent_id: Parent comment ID for threaded replies.

        Returns:
            Created comment record with extracted mentions.
        """
        # Validate parent exists and belongs to same content
        if parent_id:
            parent = (
                self.supabase.table("content_comments")
                .select("id, content_id")
                .eq("id", parent_id)
                .single()
                .execute()
            )
            if not parent.data or parent.data["content_id"] != str(content_id):
                raise ValueError("Parent comment does not belong to this content")

        # Validate position range
        if position_start is not None and position_end is not None:
            if position_end < position_start:
                raise ValueError("position_end must be >= position_start")
        if (position_start is None) != (position_end is None):
            raise ValueError(
                "position_start and position_end must both be provided or both omitted"
            )

        # Extract mentions
        mentions = self._extract_mentions(text)

        comment_data = {
            "user_id": str(user_id),
            "content_id": str(content_id),
            "text": text,
            "position_start": position_start,
            "position_end": position_end,
            "parent_id": parent_id,
            "is_resolved": False,
        }

        result = self.supabase.table("content_comments").insert(comment_data).execute()
        comment = result.data[0]

        # Store mentions
        if mentions:
            self._store_mentions(comment["id"], mentions)

        # Enrich response
        comment["mentions"] = mentions
        return comment

    def get_comment(self, comment_id: str, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a single comment by ID (must belong to user's content)."""
        result = (
            self.supabase.table("content_comments")
            .select("*")
            .eq("id", comment_id)
            .eq("user_id", str(user_id))
            .single()
            .execute()
        )
        return result.data

    def list_comments(
        self,
        content_id: UUID,
        user_id: UUID,
        parent_id: Optional[str] = None,
        is_resolved: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        List comments for content.

        When parent_id is None, returns top-level comments only (no replies).
        Set parent_id to a specific comment ID to get its replies.
        """
        query = (
            self.supabase.table("content_comments")
            .select("*")
            .eq("content_id", str(content_id))
        )

        # Scope to user's content (via content ownership)
        content_check = (
            self.supabase.table("content")
            .select("id")
            .eq("id", str(content_id))
            .eq("user_id", str(user_id))
            .single()
            .execute()
        )
        if not content_check.data:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}

        # Thread filtering
        if parent_id is not None:
            query = query.eq("parent_id", parent_id)
        else:
            query = query.is_("parent_id", "null")

        if is_resolved is not None:
            query = query.eq("is_resolved", is_resolved)

        # Count
        count_query = (
            self.supabase.table("content_comments")
            .select("count", count="exact")
            .eq("content_id", str(content_id))
        )
        if parent_id is not None:
            count_query = count_query.eq("parent_id", parent_id)
        else:
            count_query = count_query.is_("parent_id", "null")
        if is_resolved is not None:
            count_query = count_query.eq("is_resolved", is_resolved)
        count_result = count_query.execute()
        total = count_result.count or 0

        offset = (page - 1) * page_size
        result = (
            query.order("created_at").range(offset, offset + page_size - 1).execute()
        )

        # Enrich with mentions
        items = []
        for c in result.data:
            c["mentions"] = self._get_mentions_for_comment(c["id"])
            items.append(c)

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def update_comment(
        self,
        comment_id: str,
        user_id: UUID,
        text: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update comment text (only by author)."""
        # Verify ownership
        existing = (
            self.supabase.table("content_comments")
            .select("id, user_id")
            .eq("id", comment_id)
            .single()
            .execute()
        )
        if not existing.data or existing.data["user_id"] != str(user_id):
            return None

        updates = {"updated_at": datetime.now().isoformat()}
        if text is not None:
            updates["text"] = text
            # Re-extract mentions
            new_mentions = self._extract_mentions(text)
            # Replace mentions
            self.supabase.table("comment_mentions").delete().eq(
                "comment_id", comment_id
            ).execute()
            if new_mentions:
                self._store_mentions(comment_id, new_mentions)
            updates["mentions"] = new_mentions

        result = (
            self.supabase.table("content_comments")
            .update(updates)
            .eq("id", comment_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def delete_comment(self, comment_id: str, user_id: UUID) -> bool:
        """Delete a comment (only by author)."""
        existing = (
            self.supabase.table("content_comments")
            .select("id, user_id")
            .eq("id", comment_id)
            .single()
            .execute()
        )
        if not existing.data or existing.data["user_id"] != str(user_id):
            return False

        # Delete mentions and reactions first
        self.supabase.table("comment_mentions").delete().eq(
            "comment_id", comment_id
        ).execute()
        self.supabase.table("comment_reactions").delete().eq(
            "comment_id", comment_id
        ).execute()
        self.supabase.table("content_comments").delete().eq("id", comment_id).execute()
        return True

    # ── Thread Support ────────────────────────────────────────────

    def get_thread(
        self,
        comment_id: str,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get a comment with all its replies (full thread).

        Returns the parent comment and all nested replies.
        """
        # Get parent
        parent_result = (
            self.supabase.table("content_comments")
            .select("*")
            .eq("id", comment_id)
            .single()
            .execute()
        )
        if not parent_result.data:
            return None

        parent = parent_result.data
        parent["mentions"] = self._get_mentions_for_comment(parent["id"])

        # Get all replies
        replies_result = (
            self.supabase.table("content_comments")
            .select("*")
            .eq("parent_id", comment_id)
            .order("created_at")
            .execute()
        )

        replies = []
        for r in replies_result.data:
            r["mentions"] = self._get_mentions_for_comment(r["id"])
            replies.append(r)

        return {"parent": parent, "replies": replies, "reply_count": len(replies)}

    # ── Resolution ────────────────────────────────────────────────

    def resolve_comment(
        self, comment_id: str, user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Mark a comment as resolved."""
        # Verify user owns the content this comment belongs to
        comment = (
            self.supabase.table("content_comments")
            .select("id, content_id")
            .eq("id", comment_id)
            .single()
            .execute()
        )
        if not comment.data:
            return None

        content = (
            self.supabase.table("content")
            .select("id")
            .eq("id", comment.data["content_id"])
            .eq("user_id", str(user_id))
            .single()
            .execute()
        )
        if not content.data:
            return None

        result = (
            self.supabase.table("content_comments")
            .update(
                {
                    "is_resolved": True,
                    "resolved_at": datetime.now().isoformat(),
                    "resolved_by": str(user_id),
                    "updated_at": datetime.now().isoformat(),
                }
            )
            .eq("id", comment_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def unresolve_comment(
        self, comment_id: str, user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Mark a comment as unresolved (reopen)."""
        comment = (
            self.supabase.table("content_comments")
            .select("id, content_id")
            .eq("id", comment_id)
            .single()
            .execute()
        )
        if not comment.data:
            return None

        content = (
            self.supabase.table("content")
            .select("id")
            .eq("id", comment.data["content_id"])
            .eq("user_id", str(user_id))
            .single()
            .execute()
        )
        if not content.data:
            return None

        result = (
            self.supabase.table("content_comments")
            .update(
                {
                    "is_resolved": False,
                    "resolved_at": None,
                    "resolved_by": None,
                    "updated_at": datetime.now().isoformat(),
                }
            )
            .eq("id", comment_id)
            .execute()
        )
        return result.data[0] if result.data else None

    # ── Mentions ──────────────────────────────────────────────────

    def lookup_mentions(self, username: str) -> List[Dict[str, Any]]:
        """
        Look up users by username prefix for @mention autocomplete.

        Returns matching user records.
        """
        result = (
            self.supabase.table("profiles")
            .select("id, full_name, email")
            .ilike("full_name", f"{username}%")
            .limit(10)
            .execute()
        )
        return result.data

    # ── Reactions ─────────────────────────────────────────────────

    def add_reaction(
        self,
        comment_id: str,
        user_id: UUID,
        emoji: str,
    ) -> Dict[str, Any]:
        """Add an emoji reaction to a comment. Idempotent per user/emoji."""
        # Upsert: same user + same emoji = no duplicate
        existing = (
            self.supabase.table("comment_reactions")
            .select("id")
            .eq("comment_id", comment_id)
            .eq("user_id", str(user_id))
            .eq("emoji", emoji)
            .execute()
        )
        if existing.data:
            return existing.data[0]

        result = (
            self.supabase.table("comment_reactions")
            .insert(
                {
                    "comment_id": comment_id,
                    "user_id": str(user_id),
                    "emoji": emoji,
                }
            )
            .execute()
        )
        return result.data[0]

    def remove_reaction(
        self,
        comment_id: str,
        user_id: UUID,
        emoji: str,
    ) -> bool:
        """Remove an emoji reaction from a comment."""
        result = (
            self.supabase.table("comment_reactions")
            .delete()
            .eq("comment_id", comment_id)
            .eq("user_id", str(user_id))
            .eq("emoji", emoji)
            .execute()
        )
        return bool(result.data)

    def get_reactions(self, comment_id: str) -> List[Dict[str, Any]]:
        """Get all reactions for a comment, grouped by emoji."""
        result = (
            self.supabase.table("comment_reactions")
            .select("emoji, user_id")
            .eq("comment_id", comment_id)
            .execute()
        )
        # Group by emoji
        grouped: Dict[str, List[str]] = {}
        for r in result.data:
            emoji = r["emoji"]
            grouped.setdefault(emoji, []).append(r["user_id"])

        return [
            {"emoji": e, "user_ids": uids, "count": len(uids)}
            for e, uids in grouped.items()
        ]

    # ── Internal ──────────────────────────────────────────────────

    @staticmethod
    def _extract_mentions(text: str) -> List[str]:
        """Extract @mention usernames from comment text."""
        return list(set(MENTION_PATTERN.findall(text)))

    def _store_mentions(self, comment_id: str, mentions: List[str]) -> None:
        """Store mention records for a comment."""
        rows = [{"comment_id": comment_id, "username": m} for m in mentions]
        if rows:
            self.supabase.table("comment_mentions").insert(rows).execute()

    def _get_mentions_for_comment(self, comment_id: str) -> List[str]:
        """Retrieve stored mention usernames for a comment."""
        result = (
            self.supabase.table("comment_mentions")
            .select("username")
            .eq("comment_id", comment_id)
            .execute()
        )
        return [r["username"] for r in result.data]


# Singleton instance
comments_service = CommentsService()

"""
Version History Service

Handles version creation, diff computation, restoration, and auto-versioning for content items.
"""

import difflib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

MAX_VERSIONS_PER_CONTENT = 50


class VersionService:
    """Service for content version history management."""

    def __init__(self):
        self._supabase = None

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    @supabase.setter
    def supabase(self, value):
        self._supabase = value

    def list_versions(
        self,
        content_id: str,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List all versions of a content item, newest first."""
        result = (
            self.supabase.table("content_versions")
            .select("*")
            .eq("content_id", content_id)
            .eq("user_id", user_id)
            .order("version_number", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return result.data or []

    def get_version(
        self,
        content_id: str,
        version_id: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get a specific version by ID."""
        result = (
            self.supabase.table("content_versions")
            .select("*")
            .eq("id", version_id)
            .eq("content_id", content_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return result.data if result.data else None

    def create_version(
        self,
        content_id: str,
        user_id: str,
        title: Optional[str] = None,
        body: Optional[str] = None,
        change_summary: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new version for a content item.
        If title/body not provided, snapshots the current content.
        """
        # Fetch current content if title/body not supplied
        if title is None or body is None:
            content_result = (
                self.supabase.table("content")
                .select("title, original_text")
                .eq("id", content_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            if not content_result.data:
                raise ValueError("Content not found")
            title = title or content_result.data.get("title", "")
            body = body or content_result.data.get("original_text", "")

        # Get next version number
        latest = (
            self.supabase.table("content_versions")
            .select("version_number")
            .eq("content_id", content_id)
            .order("version_number", desc=True)
            .limit(1)
            .execute()
        )
        version_number = (latest.data[0]["version_number"] + 1) if latest.data else 1

        # Compute word count and delta
        current_words = len(body.split()) if body else 0
        word_count_delta = 0
        if version_number > 1:
            prev = (
                self.supabase.table("content_versions")
                .select("body")
                .eq("content_id", content_id)
                .eq("version_number", version_number - 1)
                .single()
                .execute()
            )
            if prev.data and prev.data.get("body"):
                prev_words = len(prev.data["body"].split())
                word_count_delta = current_words - prev_words

        metadata = {
            "change_summary": change_summary or f"Version {version_number}",
            "word_count": current_words,
            "word_count_delta": word_count_delta,
        }

        data = {
            "content_id": content_id,
            "user_id": user_id,
            "version_number": version_number,
            "title": title,
            "body": body,
            "metadata": metadata,
            "created_by": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        result = self.supabase.table("content_versions").insert(data).execute()

        # Prune old versions if over limit
        self._prune_old_versions(content_id, user_id)

        return result.data[0] if result.data else None

    def compute_diff(
        self,
        content_id: str,
        version_id_1: str,
        version_id_2: str,
        user_id: str,
        format: str = "unified",
    ) -> Dict[str, Any]:
        """
        Compute diff between two versions.
        format: "unified" for text diff, "html" for HTML diff.
        """
        v1 = self.get_version(content_id, version_id_1, user_id)
        v2 = self.get_version(content_id, version_id_2, user_id)

        if not v1 or not v2:
            raise ValueError("One or both versions not found")

        text1 = v1.get("body", "") or ""
        text2 = v2.get("body", "") or ""
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)

        if format == "html":
            differ = difflib.HtmlDiff()
            diff_output = differ.make_table(
                lines1,
                lines2,
                fromdesc=f"v{v1['version_number']}",
                todesc=f"v{v2['version_number']}",
            )
        else:
            diff_lines = difflib.unified_diff(
                lines1,
                lines2,
                fromfile=f"v{v1['version_number']}",
                tofile=f"v{v2['version_number']}",
                lineterm="",
            )
            diff_output = "\n".join(diff_lines)

        return {
            "version_1": {
                "id": v1["id"],
                "version_number": v1["version_number"],
                "created_at": v1["created_at"],
            },
            "version_2": {
                "id": v2["id"],
                "version_number": v2["version_number"],
                "created_at": v2["created_at"],
            },
            "format": format,
            "diff": diff_output,
        }

    def restore_version(
        self,
        content_id: str,
        version_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """Restore a previous version as the current content and create a new version record."""
        version = self.get_version(content_id, version_id, user_id)
        if not version:
            raise ValueError("Version not found")

        # Update the content record
        self.supabase.table("content").update(
            {
                "title": version["title"],
                "original_text": version["body"],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", content_id).eq("user_id", user_id).execute()

        # Create a new version reflecting the restoration
        restored_version = self.create_version(
            content_id=content_id,
            user_id=user_id,
            title=version["title"],
            body=version["body"],
            change_summary=f"Restored from version {version['version_number']}",
        )

        return {
            "restored_from_version": version["version_number"],
            "new_version": restored_version,
        }

    def delete_version(
        self,
        content_id: str,
        version_id: str,
        user_id: str,
    ) -> bool:
        """Delete a specific version."""
        result = (
            self.supabase.table("content_versions")
            .delete()
            .eq("id", version_id)
            .eq("content_id", content_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(result.data)

    def auto_version_on_update(
        self,
        content_id: str,
        user_id: str,
        title: str,
        body: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Called when content is updated to automatically create a version snapshot.
        Respects the max versions limit via create_version's pruning.
        """
        return self.create_version(
            content_id=content_id,
            user_id=user_id,
            title=title,
            body=body,
            change_summary="Auto-version on content update",
        )

    def _prune_old_versions(self, content_id: str, user_id: str) -> None:
        """Remove oldest versions exceeding MAX_VERSIONS_PER_CONTENT."""
        count_result = (
            self.supabase.table("content_versions")
            .select("id", count="exact")
            .eq("content_id", content_id)
            .eq("user_id", user_id)
            .execute()
        )
        total = (
            count_result.count
            if hasattr(count_result, "count") and count_result.count
            else len(count_result.data or [])
        )

        if total > MAX_VERSIONS_PER_CONTENT:
            # Get IDs of the oldest versions to delete
            overflow = total - MAX_VERSIONS_PER_CONTENT
            oldest = (
                self.supabase.table("content_versions")
                .select("id")
                .eq("content_id", content_id)
                .eq("user_id", user_id)
                .order("version_number", desc=False)
                .limit(overflow)
                .execute()
            )
            for row in oldest.data or []:
                self.supabase.table("content_versions").delete().eq(
                    "id", row["id"]
                ).execute()


# Global service instance
version_service = VersionService()

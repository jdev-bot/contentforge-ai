"""
RSS Service for fetching and parsing RSS feeds.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

import feedparser
import httpx

from app.core.supabase import get_supabase_admin_client

logger = logging.getLogger(__name__)


class RSSService:
    """Service for RSS feed operations."""

    def __init__(self):
        self.timeout = 30.0  # 30 second timeout for feed fetching

    async def validate_feed(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Validate an RSS feed URL by attempting to fetch and parse it.

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, follow_redirects=True
            ) as client:
                response = await client.get(
                    url, headers={"User-Agent": "ContentForge AI RSS Reader/1.0"}
                )
                response.raise_for_status()

                # Parse the feed
                feed = feedparser.parse(response.text)

                if feed.bozo and feed.bozo_exception:
                    # Some feeds have minor parsing issues but are still valid
                    if hasattr(feed, "entries") and len(feed.entries) > 0:
                        return True, None
                    return False, f"Feed parsing error: {str(feed.bozo_exception)}"

                if not hasattr(feed, "entries"):
                    return False, "No entries found in feed"

                return True, None

        except httpx.HTTPStatusError as e:
            return (
                False,
                f"HTTP error {e.response.status_code}: {e.response.reason_phrase}",
            )
        except httpx.RequestError as e:
            return False, f"Request failed: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    async def fetch_feed(self, feed_id: str, user_id: str) -> Dict[str, Any]:
        """
        Fetch and process an RSS feed.

        Returns:
            Dict with success status, counts, and message
        """
        supabase = get_supabase_admin_client()

        try:
            # Get feed details
            feed_result = (
                supabase.table("rss_feeds")
                .select("*")
                .eq("id", feed_id)
                .single()
                .execute()
            )

            if not feed_result.data:
                return {
                    "success": False,
                    "entries_fetched": 0,
                    "entries_new": 0,
                    "message": "Feed not found",
                }

            feed = feed_result.data
            url = feed["url"]

            # Fetch the feed
            async with httpx.AsyncClient(
                timeout=self.timeout, follow_redirects=True
            ) as client:
                response = await client.get(
                    url, headers={"User-Agent": "ContentForge AI RSS Reader/1.0"}
                )
                response.raise_for_status()

                # Parse the feed
                parsed = feedparser.parse(response.text)

                entries_fetched = len(parsed.entries)
                entries_new = 0

                # Process each entry
                for entry in parsed.entries:
                    try:
                        # Extract entry data
                        external_id = entry.get(
                            "id", entry.get("guid", entry.get("link", ""))
                        )
                        title = entry.get("title", "Untitled")
                        link = entry.get("link", "")

                        # Get content (prefer content, then summary, then description)
                        content = ""
                        if hasattr(entry, "content") and entry.content:
                            content = entry.content[0].value
                        elif hasattr(entry, "summary"):
                            content = entry.summary
                        elif hasattr(entry, "description"):
                            content = entry.description

                        # Parse published date
                        published_at = None
                        if (
                            hasattr(entry, "published_parsed")
                            and entry.published_parsed
                        ):
                            published_at = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                            published_at = datetime(*entry.updated_parsed[:6])

                        # Check if entry already exists
                        existing = (
                            supabase.table("rss_entries")
                            .select("id")
                            .eq("feed_id", feed_id)
                            .eq("external_id", external_id)
                            .execute()
                        )

                        if existing.data:
                            # Entry already exists, skip
                            continue

                        # Insert new entry
                        entry_data = {
                            "feed_id": feed_id,
                            "external_id": external_id,
                            "title": (
                                title[:500] if title else "Untitled"
                            ),  # Limit title length
                            "link": link[:1000] if link else None,  # Limit link length
                            "content": content,
                            "published_at": (
                                published_at.isoformat() if published_at else None
                            ),
                            "processed": False,
                        }

                        supabase.table("rss_entries").insert(entry_data).execute()
                        entries_new += 1

                    except Exception as e:
                        logger.error(f"Error processing RSS entry: {e}")
                        continue

                # Update feed last_fetched_at and clear error
                supabase.table("rss_feeds").update(
                    {
                        "last_fetched_at": datetime.now(timezone.utc).isoformat(),
                        "status": "active",
                        "error_message": None,
                    }
                ).eq("id", feed_id).execute()

                # Auto-create content if enabled
                if feed.get("auto_create_content"):
                    await self._auto_create_content_for_feed(feed_id, user_id, supabase)

                return {
                    "success": True,
                    "entries_fetched": entries_fetched,
                    "entries_new": entries_new,
                    "message": f"Fetched {entries_fetched} entries, {entries_new} new",
                }

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}"
            supabase.table("rss_feeds").update(
                {"status": "error", "error_message": error_msg}
            ).eq("id", feed_id).execute()

            return {
                "success": False,
                "entries_fetched": 0,
                "entries_new": 0,
                "message": error_msg,
            }

        except Exception as e:
            error_msg = f"Fetch error: {str(e)}"
            supabase.table("rss_feeds").update(
                {
                    "status": "error",
                    "error_message": error_msg[:500],  # Limit error message length
                }
            ).eq("id", feed_id).execute()

            logger.error(f"Error fetching RSS feed {feed_id}: {e}")

            return {
                "success": False,
                "entries_fetched": 0,
                "entries_new": 0,
                "message": error_msg,
            }

    async def _auto_create_content_for_feed(self, feed_id: str, user_id: str, supabase):
        """Auto-create content items for unprocessed entries in a feed."""
        try:
            # Get unprocessed entries
            entries_result = (
                supabase.table("rss_entries")
                .select("*")
                .eq("feed_id", feed_id)
                .eq("processed", False)
                .execute()
            )

            for entry in entries_result.data:
                try:
                    await self.import_entry(
                        entry_id=entry["id"],
                        user_id=user_id,
                        project_id=None,
                        title=entry.get("title"),
                        content=entry.get("content"),
                        link=entry.get("link"),
                        supabase=supabase,
                    )
                except Exception as e:
                    logger.error(
                        f"Error auto-creating content for entry {entry['id']}: {e}"
                    )
                    continue

        except Exception as e:
            logger.error(f"Error in auto-create content for feed {feed_id}: {e}")

    async def import_entry(
        self,
        entry_id: str,
        user_id: str,
        project_id: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        link: Optional[str] = None,
        supabase=None,
    ) -> Dict[str, Any]:
        """
        Import an RSS entry as content.

        Returns:
            Dict with success status, content_id, and message
        """
        if supabase is None:
            supabase = get_supabase_admin_client()

        try:
            # Get entry details if not provided
            if not title or not content:
                entry_result = (
                    supabase.table("rss_entries")
                    .select("*")
                    .eq("id", entry_id)
                    .single()
                    .execute()
                )
                if not entry_result.data:
                    return {
                        "success": False,
                        "content_id": None,
                        "message": "Entry not found",
                    }

                entry = entry_result.data
                title = title or entry.get("title", "Untitled")
                content = content or entry.get("content", "")
                link = link or entry.get("link", "")

            # Clean content for word count
            cleaned_content = self._clean_text(content or "")
            word_count = len(cleaned_content.split()) if cleaned_content else 0

            # Create content record
            content_data = {
                "user_id": user_id,
                "title": title[:255] if title else "Untitled",
                "source_type": "rss",
                "source_url": link,
                "original_text": content,
                "word_count": word_count,
                "status": "completed",
            }

            if project_id:
                content_data["project_id"] = project_id

            result = supabase.table("content").insert(content_data).execute()

            if not result.data:
                return {
                    "success": False,
                    "content_id": None,
                    "message": "Failed to create content",
                }

            content_id = result.data[0]["id"]

            # Mark entry as processed
            supabase.table("rss_entries").update(
                {"processed": True, "content_id": content_id}
            ).eq("id", entry_id).execute()

            return {
                "success": True,
                "content_id": content_id,
                "message": "Content created successfully",
            }

        except Exception as e:
            logger.error(f"Error importing RSS entry {entry_id}: {e}")
            return {
                "success": False,
                "content_id": None,
                "message": f"Import error: {str(e)}",
            }

    def _clean_text(self, text: str) -> str:
        """Clean text for word count calculation."""
        import re

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    async def fetch_all_active_feeds(self) -> Dict[str, Any]:
        """
        Fetch all active RSS feeds that are due for fetching.

        Returns:
            Dict with total feeds, processed count, and results
        """
        supabase = get_supabase_admin_client()

        try:
            # Get all active feeds
            feeds_result = (
                supabase.table("rss_feeds").select("*").eq("status", "active").execute()
            )

            if not feeds_result.data:
                return {"total_feeds": 0, "processed": 0, "results": []}

            feeds = feeds_result.data
            results = []
            processed = 0

            for feed in feeds:
                feed_id = feed["id"]
                user_id = feed["user_id"]

                # Check if feed is due for fetching based on frequency
                last_fetched = feed.get("last_fetched_at")
                frequency = feed.get("fetch_frequency", "hourly")

                if last_fetched:
                    last_fetched_dt = datetime.fromisoformat(
                        last_fetched.replace("Z", "+00:00")
                    )
                    minutes_since_fetch = (
                        datetime.now(timezone.utc)
                        - last_fetched_dt.replace(tzinfo=None)
                    ).total_seconds() / 60

                    if frequency == "hourly" and minutes_since_fetch < 60:
                        continue
                    elif (
                        frequency == "daily" and minutes_since_fetch < 1440
                    ):  # 24 hours
                        continue

                # Fetch the feed
                result = await self.fetch_feed(feed_id, user_id)
                results.append({"feed_id": feed_id, "user_id": user_id, **result})
                processed += 1

            return {
                "total_feeds": len(feeds),
                "processed": processed,
                "results": results,
            }

        except Exception as e:
            logger.error(f"Error fetching all active feeds: {e}")
            return {"total_feeds": 0, "processed": 0, "results": [], "error": str(e)}


# Singleton instance
rss_service = RSSService()

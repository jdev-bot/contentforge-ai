"""
Smart Categorization service for ContentForge AI.
Auto-categorizes and tags content using AI, supports content clustering.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.cache import CACHE_TTL, cache
from app.core.supabase import get_supabase_client
from app.services.groq_service import groq_service

logger = logging.getLogger(__name__)


class CategorizationService:
    """Service for intelligent content categorization and tagging."""

    # Predefined categories for classification
    DEFAULT_CATEGORIES = [
        "technology", "business", "marketing", "finance", "health",
        "education", "entertainment", "lifestyle", "science", "politics",
        "sports", "travel", "food", "fashion", "design", "productivity",
        "career", "startups", "ai_ml", "cybersecurity", "sustainability",
    ]

    # Predefined format types
    CONTENT_FORMATS = [
        "how_to", "listicle", "opinion", "case_study", "interview",
        "tutorial", "news", "review", "comparison", "thought_leadership",
        "announcement", "story", "guide", "analysis", "faq",
    ]

    # Predefined industry verticals
    INDUSTRY_VERTICALS = [
        "saas", "ecommerce", "fintech", "healthtech", "edtech",
        "martech", "proptech", "cleantech", "agritech", "legaltech",
        "general", "media", "healthcare", "finance", "education",
        "technology", "real_estate", "automotive", "retail", "manufacturing",
    ]

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

    # ------------------------------------------------------------------
    # Auto-Categorize Content
    # ------------------------------------------------------------------

    async def categorize_content(
        self,
        content_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Auto-categorize a single content item by topic, industry, and format.
        Returns and persists categorization results.
        """
        try:
            # Fetch content
            result = (
                self.supabase.table("content")
                .select("id, title, original_text, category, tags, platform")
                .eq("id", content_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            if not result.data:
                return {"error": "Content not found", "content_id": content_id}

            content = result.data
            content_text = content.get("original_text") or content.get("title", "")

            if not content_text:
                return {"error": "No text content available for categorization", "content_id": content_id}

            # Use AI for categorization
            categorization = await self._ai_categorize(content_text)

            # Save categorization to database
            saved = await self._save_categorization(
                content_id=content_id,
                user_id=user_id,
                categorization=categorization,
            )

            # Update the content record with category and tags
            await self._update_content_metadata(content_id, categorization)

            return saved if saved else categorization

        except Exception as e:
            logger.error(f"Failed to categorize content: {e}")
            return {"error": str(e), "content_id": content_id}

    async def batch_categorize(
        self,
        user_id: str,
        content_ids: Optional[List[str]] = None,
        uncategorized_only: bool = True,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Categorize multiple content items in batch.
        If content_ids is None, processes uncategorized content.
        """
        try:
            # Build query
            query = (
                self.supabase.table("content")
                .select("id, title, original_text, category, tags, platform")
                .eq("user_id", user_id)
            )

            if content_ids:
                query = query.in_("id", content_ids)
            elif uncategorized_only:
                # Content without category or with generic category
                query = query.is_("category", "null").or_("category.eq.uncategorized,category.eq.general,category.eq.")

            query = query.limit(limit)
            result = query.execute()

            content_items = result.data or []
            if not content_items:
                return {
                    "total": 0,
                    "categorized": 0,
                    "results": [],
                }

            # Process each content item
            results = []
            for item in content_items[:20]:  # Limit batch to 20 for AI rate limits
                content_text = item.get("original_text") or item.get("title", "")
                if not content_text:
                    continue

                try:
                    categorization = await self._ai_categorize(content_text)
                    saved = await self._save_categorization(
                        content_id=item["id"],
                        user_id=user_id,
                        categorization=categorization,
                    )
                    await self._update_content_metadata(item["id"], categorization)
                    results.append(saved or categorization)
                except Exception as e:
                    logger.error(f"Failed to categorize content {item['id']}: {e}")
                    continue

            return {
                "total": len(content_items),
                "categorized": len(results),
                "results": results,
            }

        except Exception as e:
            logger.error(f"Batch categorization failed: {e}")
            return {"error": str(e), "total": 0, "categorized": 0, "results": []}

    # ------------------------------------------------------------------
    # Auto-Tag Content
    # ------------------------------------------------------------------

    async def auto_tag_content(
        self,
        content_id: str,
        user_id: str,
        max_tags: int = 10,
    ) -> Dict[str, Any]:
        """
        Auto-tag a content item with relevant keywords using AI.
        Returns and persists tag results.
        """
        try:
            # Fetch content
            result = (
                self.supabase.table("content")
                .select("id, title, original_text, tags")
                .eq("id", content_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            if not result.data:
                return {"error": "Content not found", "content_id": content_id}

            content = result.data
            content_text = content.get("original_text") or content.get("title", "")

            if not content_text:
                return {"error": "No text content available for tagging", "content_id": content_id}

            # Use AI for tagging
            tags = await self._ai_tag(content_text, max_tags)

            # Save tags
            saved = await self._save_tags(
                content_id=content_id,
                user_id=user_id,
                tags=tags,
            )

            # Update content record
            existing_tags = content.get("tags", [])
            if isinstance(existing_tags, str):
                existing_tags = json.loads(existing_tags) if existing_tags else []
            new_tags = list(set(existing_tags + tags.get("tags", [])))
            self.supabase.table("content").update({"tags": new_tags}).eq("id", content_id).execute()

            return saved or tags

        except Exception as e:
            logger.error(f"Failed to auto-tag content: {e}")
            return {"error": str(e), "content_id": content_id}

    async def batch_auto_tag(
        self,
        user_id: str,
        content_ids: Optional[List[str]] = None,
        untagged_only: bool = True,
        max_tags: int = 10,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Auto-tag multiple content items in batch.
        If content_ids is None, processes untagged content.
        """
        try:
            query = (
                self.supabase.table("content")
                .select("id, title, original_text, tags")
                .eq("user_id", user_id)
            )

            if content_ids:
                query = query.in_("id", content_ids)
            elif untagged_only:
                # Content without tags
                query = query.is_("tags", "null").or_("tags.eq.[]")

            query = query.limit(limit)
            result = query.execute()

            content_items = result.data or []
            if not content_items:
                return {"total": 0, "tagged": 0, "results": []}

            results = []
            for item in content_items[:20]:  # Limit batch for AI rate limits
                content_text = item.get("original_text") or item.get("title", "")
                if not content_text:
                    continue

                try:
                    tags = await self._ai_tag(content_text, max_tags)
                    saved = await self._save_tags(
                        content_id=item["id"],
                        user_id=user_id,
                        tags=tags,
                    )
                    # Update content tags
                    existing_tags = item.get("tags", [])
                    if isinstance(existing_tags, str):
                        existing_tags = json.loads(existing_tags) if existing_tags else []
                    new_tags = list(set(existing_tags + tags.get("tags", [])))
                    self.supabase.table("content").update({"tags": new_tags}).eq("id", item["id"]).execute()
                    results.append(saved or tags)
                except Exception as e:
                    logger.error(f"Failed to tag content {item['id']}: {e}")
                    continue

            return {"total": len(content_items), "tagged": len(results), "results": results}

        except Exception as e:
            logger.error(f"Batch auto-tag failed: {e}")
            return {"error": str(e), "total": 0, "tagged": 0, "results": []}

    # ------------------------------------------------------------------
    # Content Clustering
    # ------------------------------------------------------------------

    async def cluster_content(
        self,
        user_id: str,
        cluster_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Cluster user's content into thematic groups using AI.
        Returns cluster assignments and descriptions.
        """
        cache_key = f"clusters:{cluster_count or 'auto'}"
        cached = cache.get(cache_key, prefix=f"categorization:{user_id}")
        if cached is not None:
            return cached

        try:
            # Get user's content
            content_items = await self._get_user_content(user_id, limit=100)

            if not content_items:
                return {"clusters": [], "total_content": 0}

            num_clusters = cluster_count or max(2, min(8, len(content_items) // 5))

            # Prepare content for AI
            content_summaries = []
            for item in content_items[:50]:  # Limit for AI context
                title = item.get("title", "Untitled")
                text = (item.get("original_text") or "")[:200]
                category = item.get("category", "unknown")
                content_summaries.append(f"ID: {item['id']} | Title: {title} | Category: {category} | Excerpt: {text}")

            content_list = "\n".join(content_summaries)

            prompt = f"""Analyze the following content items and cluster them into {num_clusters} thematic groups.

Content Items:
{content_list}

For each cluster provide:
1. A descriptive cluster name (2-4 words)
2. A brief description of the cluster theme
3. The content IDs belonging to this cluster
4. Common topics/keywords in this cluster
5. Suggested category label

Format your response as JSON:
{{
    "clusters": [
        {{
            "cluster_name": "descriptive name",
            "description": "brief description of cluster theme",
            "content_ids": ["id1", "id2"],
            "keywords": ["kw1", "kw2", "kw3"],
            "suggested_category": "category_label"
        }}
    ]
}}"""

            system_prompt = "You are a content organization expert. Group content into meaningful thematic clusters. Return structured JSON."

            result = await groq_service.generate_content(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=3000,
            )

            clusters = self._parse_json_response(result, "clusters")

            response = {
                "clusters": clusters,
                "total_content": len(content_items),
                "num_clusters": len(clusters),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

            # Save cluster results
            try:
                cluster_data = {
                    "user_id": user_id,
                    "cluster_type": "thematic",
                    "clusters": clusters,
                    "total_content": len(content_items),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                self.supabase.table("content_clusters").insert(cluster_data).execute()
            except Exception as e:
                logger.error(f"Failed to save clusters: {e}")

            cache.set(cache_key, response, ttl=CACHE_TTL.get("analytics", 300), prefix=f"categorization:{user_id}")

            return response

        except Exception as e:
            logger.error(f"Content clustering failed: {e}")
            return {"error": str(e), "clusters": [], "total_content": 0}

    # ------------------------------------------------------------------
    # Category & Tag Management (CRUD)
    # ------------------------------------------------------------------

    async def get_content_categorization(
        self,
        content_id: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve the categorization record for a content item."""
        try:
            result = (
                self.supabase.table("content_categorizations")
                .select("*")
                .eq("content_id", content_id)
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get categorization: {e}")
            return None

    async def get_content_tags(
        self,
        content_id: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve the tag record for a content item."""
        try:
            result = (
                self.supabase.table("content_tags")
                .select("*")
                .eq("content_id", content_id)
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get content tags: {e}")
            return None

    async def update_categorization(
        self,
        categorization_id: str,
        user_id: str,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Update a categorization record (e.g., user overrides)."""
        try:
            result = (
                self.supabase.table("content_categorizations")
                .update(updates)
                .eq("id", categorization_id)
                .eq("user_id", user_id)
                .execute()
            )
            if result.data:
                # Invalidate cache
                cache.delete_pattern("", prefix=f"categorization:{user_id}")
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to update categorization: {e}")
            return None

    async def delete_categorization(self, categorization_id: str, user_id: str) -> bool:
        """Delete a categorization record."""
        try:
            result = (
                self.supabase.table("content_categorizations")
                .delete()
                .eq("id", categorization_id)
                .eq("user_id", user_id)
                .execute()
            )
            cache.delete_pattern("", prefix=f"categorization:{user_id}")
            return bool(result.data)
        except Exception as e:
            logger.error(f"Failed to delete categorization: {e}")
            return False

    async def list_categorizations(
        self,
        user_id: str,
        category: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List all categorizations for a user with optional filters."""
        try:
            query = (
                self.supabase.table("content_categorizations")
                .select("*")
                .eq("user_id", user_id)
            )
            if category:
                query = query.eq("category", category)
            if industry:
                query = query.eq("industry", industry)
            query = query.order("created_at", desc=True).limit(limit)
            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to list categorizations: {e}")
            return []

    # ------------------------------------------------------------------
    # Private AI Methods
    # ------------------------------------------------------------------

    async def _ai_categorize(self, content_text: str) -> Dict[str, Any]:
        """Use Groq AI to categorize content."""
        # Truncate for token limits
        text = content_text[:3000]

        prompt = f"""Analyze the following content and categorize it precisely:

Content:
{text}

Provide the following categorization:
1. Primary topic category (one of: {', '.join(self.DEFAULT_CATEGORIES[:10])})
2. Industry vertical (one of: {', '.join(self.INDUSTRY_VERTICALS[:10])})
3. Content format (one of: {', '.join(self.CONTENT_FORMATS[:10])})
4. Sub-topics (2-3 specific sub-topics)
5. Relevance score (0-100, how focused the content is on its primary topic)
6. Target audience description
7. Content tone (professional, casual, educational, persuasive, entertaining)

Format your response as JSON:
{{
    "category": "primary_category",
    "industry": "industry_vertical",
    "format": "content_format",
    "sub_topics": ["subtopic1", "subtopic2"],
    "relevance_score": 85,
    "target_audience": "audience description",
    "tone": "content_tone"
}}"""

        system_prompt = "You are a content classification expert. Analyze content and provide precise categorization. Return structured JSON only."

        result = await groq_service.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1000,
        )

        parsed = self._parse_json_response(result)

        # Ensure sensible defaults
        return {
            "category": parsed.get("category", "general"),
            "industry": parsed.get("industry", "general"),
            "format": parsed.get("format", "how_to"),
            "sub_topics": parsed.get("sub_topics", []),
            "relevance_score": parsed.get("relevance_score", 50),
            "target_audience": parsed.get("target_audience", "General audience"),
            "tone": parsed.get("tone", "professional"),
        }

    async def _ai_tag(self, content_text: str, max_tags: int = 10) -> Dict[str, Any]:
        """Use Groq AI to generate relevant tags for content."""
        text = content_text[:3000]

        prompt = f"""Analyze the following content and generate {max_tags} relevant tags/keywords.

Content:
{text}

Generate tags in these categories:
1. Primary keywords (3-5 main topics)
2. Secondary keywords (3-5 supporting topics)
3. Long-tail keywords (2-3 specific phrases)
4. Entity tags (people, brands, products mentioned)
5. Sentiment tag (positive, negative, neutral, mixed)

Format your response as JSON:
{{
    "tags": ["tag1", "tag2", "tag3", ...],
    "primary_keywords": ["kw1", "kw2", "kw3"],
    "secondary_keywords": ["skw1", "skw2", "skw3"],
    "long_tail_keywords": ["ltkw1", "ltkw2"],
    "entity_tags": ["entity1", "entity2"],
    "sentiment": "sentiment_tag"
}}"""

        system_prompt = "You are an SEO and content tagging expert. Generate precise, relevant tags for content discoverability. Return structured JSON only."

        result = await groq_service.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1000,
        )

        parsed = self._parse_json_response(result)

        # Ensure defaults
        tags = parsed.get("tags", [])
        if not tags:
            # Combine all keyword types into tags
            tags = (
                parsed.get("primary_keywords", [])
                + parsed.get("secondary_keywords", [])
                + parsed.get("long_tail_keywords", [])
            )[:max_tags]

        return {
            "tags": tags[:max_tags],
            "primary_keywords": parsed.get("primary_keywords", []),
            "secondary_keywords": parsed.get("secondary_keywords", []),
            "long_tail_keywords": parsed.get("long_tail_keywords", []),
            "entity_tags": parsed.get("entity_tags", []),
            "sentiment": parsed.get("sentiment", "neutral"),
        }

    # ------------------------------------------------------------------
    # Private Storage Methods
    # ------------------------------------------------------------------

    async def _save_categorization(
        self,
        content_id: str,
        user_id: str,
        categorization: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Save categorization results to database."""
        try:
            data = {
                "content_id": content_id,
                "user_id": user_id,
                "category": categorization.get("category", "general"),
                "industry": categorization.get("industry", "general"),
                "format": categorization.get("format", "how_to"),
                "sub_topics": categorization.get("sub_topics", []),
                "relevance_score": categorization.get("relevance_score", 50),
                "target_audience": categorization.get("target_audience", "General audience"),
                "tone": categorization.get("tone", "professional"),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            result = self.supabase.table("content_categorizations").insert(data).execute()
            cache.delete_pattern("", prefix=f"categorization:{user_id}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to save categorization: {e}")
            return None

    async def _save_tags(
        self,
        content_id: str,
        user_id: str,
        tags: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Save tag results to database."""
        try:
            data = {
                "content_id": content_id,
                "user_id": user_id,
                "tags": tags.get("tags", []),
                "primary_keywords": tags.get("primary_keywords", []),
                "secondary_keywords": tags.get("secondary_keywords", []),
                "long_tail_keywords": tags.get("long_tail_keywords", []),
                "entity_tags": tags.get("entity_tags", []),
                "sentiment": tags.get("sentiment", "neutral"),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            result = self.supabase.table("content_tags").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to save tags: {e}")
            return None

    async def _update_content_metadata(
        self,
        content_id: str,
        categorization: Dict[str, Any],
    ) -> bool:
        """Update the content record with categorized metadata."""
        try:
            update_data = {
                "category": categorization.get("category", "general"),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            self.supabase.table("content").update(update_data).eq("id", content_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update content metadata: {e}")
            return False

    async def _get_user_content(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user's content for clustering analysis."""
        try:
            result = (
                self.supabase.table("content")
                .select("id, title, original_text, category, tags, platform, created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get user content for clustering: {e}")
            return []

    def _parse_json_response(self, response: str, key: Optional[str] = None) -> Any:
        """Parse JSON from Groq AI response, handling markdown code blocks."""
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)

            if key and isinstance(data, dict) and key in data:
                return data[key]

            return data
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            logger.error(f"Failed to parse JSON response: {e}")
            if key == "clusters":
                return []
            return {}


# Singleton instance
categorization_service = CategorizationService()
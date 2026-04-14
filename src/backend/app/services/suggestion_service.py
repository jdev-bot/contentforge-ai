"""
Auto-Suggestions service for ContentForge AI.
Analyzes user content history and patterns to provide AI-powered suggestions
for topics, posting times, and content improvements.
"""
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

from app.core.supabase import get_supabase_client
from app.core.cache import cache, CACHE_TTL
from app.services.groq_service import groq_service


class SuggestionService:
    """Service for generating auto-suggestions based on user content patterns."""

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
    # Content History Analysis
    # ------------------------------------------------------------------

    async def get_user_content_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve user's recent content for pattern analysis."""
        try:
            result = (
                self.supabase.table("content")
                .select("id, title, original_text, category, tags, platform, created_at, updated_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            print(f"Failed to get user content history: {e}")
            return []

    async def get_user_engagement_data(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve user's content engagement/analytics data."""
        try:
            result = (
                self.supabase.table("analytics")
                .select("content_id, views, likes, shares, comments, engagement_rate, recorded_at")
                .eq("user_id", user_id)
                .order("recorded_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            print(f"Failed to get engagement data: {e}")
            return []

    async def get_user_distributions(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve user's content distribution records for posting time analysis."""
        try:
            result = (
                self.supabase.table("distributions")
                .select("id, content_id, platform, status, published_at, engagement_metrics")
                .eq("user_id", user_id)
                .order("published_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            print(f"Failed to get distributions: {e}")
            return []

    # ------------------------------------------------------------------
    # Topic Suggestions
    # ------------------------------------------------------------------

    async def suggest_topics(
        self,
        user_id: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Suggest content topics based on user's content history and performance data.
        Uses Groq AI to generate relevant topic ideas.
        """
        cache_key = f"topics:{limit}"
        cached = cache.get(cache_key, prefix=f"suggestions:{user_id}")
        if cached is not None:
            return cached

        try:
            content_history = await self.get_user_content_history(user_id, limit=30)
            engagement_data = await self.get_user_engagement_data(user_id, limit=50)

            # Build context for AI
            history_summary = self._summarize_content_history(content_history)
            top_performers = self._get_top_performing_content(content_history, engagement_data)

            prompt = f"""Based on the user's content history and performance data, suggest {limit} new content topics they should write about.

User's Content History Summary:
{history_summary}

Top Performing Content:
{top_performers}

Generate {limit} topic suggestions. For each topic provide:
1. A compelling title
2. A brief description (2-3 sentences)
3. The recommended platform (twitter, linkedin, blog, newsletter, instagram, tiktok)
4. The rationale (why this topic fits their audience)
5. Related keywords (3-5)

Format your response as JSON:
{{
    "suggestions": [
        {{
            "title": "topic title",
            "description": "brief description",
            "recommended_platform": "platform",
            "rationale": "why this topic",
            "keywords": ["kw1", "kw2", "kw3"]
        }}
    ]
}}"""

            system_prompt = "You are a content strategy expert. Analyze user patterns and suggest high-value content topics. Return structured JSON."

            result = await groq_service.generate_content(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000,
            )

            suggestions = self._parse_json_response(result, "suggestions")

            # Ensure we return the right number of suggestions
            suggestions = suggestions[:limit]

            # Cache the result
            cache.set(cache_key, suggestions, ttl=CACHE_TTL.get("analytics", 300), prefix=f"suggestions:{user_id}")

            return suggestions

        except Exception as e:
            print(f"Failed to suggest topics: {e}")
            return []

    # ------------------------------------------------------------------
    # Posting Time Suggestions
    # ------------------------------------------------------------------

    async def suggest_posting_times(
        self,
        user_id: str,
        platform: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Suggest optimal posting times based on user's audience engagement data.
        Uses Groq AI to analyze patterns and recommend time slots.
        """
        cache_key = f"posting_times:{platform or 'all'}:{limit}"
        cached = cache.get(cache_key, prefix=f"suggestions:{user_id}")
        if cached is not None:
            return cached

        try:
            distributions = await self.get_user_distributions(user_id, limit=100)
            engagement_data = await self.get_user_engagement_data(user_id, limit=100)

            # Filter by platform if specified
            if platform and distributions:
                distributions = [d for d in distributions if d.get("platform") == platform]

            distribution_summary = self._summarize_distributions(distributions)
            engagement_summary = self._summarize_engagement(engagement_data)

            prompt = f"""Based on the user's publishing history and engagement data, suggest {limit} optimal posting time windows.

Publishing History:
{distribution_summary}

Engagement Summary:
{engagement_summary}

For each suggestion provide:
1. Day of week (e.g., "Tuesday")
2. Time window (e.g., "9:00 AM - 10:00 AM UTC")
3. Recommended platform
4. Expected engagement level (high, medium, low)
5. Reasoning

Format your response as JSON:
{{
    "suggestions": [
        {{
            "day": "Tuesday",
            "time_window": "9:00 AM - 10:00 AM UTC",
            "platform": "linkedin",
            "expected_engagement": "high",
            "reasoning": "why this time"
        }}
    ]
}}"""

            system_prompt = "You are a social media analytics expert. Analyze posting patterns and engagement data to recommend optimal publishing schedules. Return structured JSON."

            result = await groq_service.generate_content(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=1500,
            )

            suggestions = self._parse_json_response(result, "suggestions")
            suggestions = suggestions[:limit]

            cache.set(cache_key, suggestions, ttl=CACHE_TTL.get("analytics", 300), prefix=f"suggestions:{user_id}")

            return suggestions

        except Exception as e:
            print(f"Failed to suggest posting times: {e}")
            return []

    # ------------------------------------------------------------------
    # Content Improvement Suggestions
    # ------------------------------------------------------------------

    async def suggest_content_improvements(
        self,
        user_id: str,
        content_id: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Suggest content improvements based on tone, structure, and keyword analysis.
        If content_id is provided, focuses on that specific content item.
        Otherwise, analyzes recent content and provides general improvements.
        """
        try:
            if content_id:
                # Specific content analysis
                result = (
                    self.supabase.table("content")
                    .select("*")
                    .eq("id", content_id)
                    .eq("user_id", user_id)
                    .single()
                    .execute()
                )
                content_items = [result.data] if result.data else []
            else:
                content_items = await self.get_user_content_history(user_id, limit=10)

            if not content_items:
                return []

            content_text = content_items[0].get("original_text") or content_items[0].get("title", "")
            if not content_text:
                return []

            prompt = f"""Analyze the following content and suggest {limit} specific improvements across these dimensions:
1. Tone - Is the tone consistent? Could it be adjusted for better impact?
2. Structure - Is the content well-organized? Could headings, paragraphs, or flow be improved?
3. Keywords - Are relevant keywords present? Are there keyword gaps?
4. Readability - Is the content easy to read? Could sentences be simplified?
5. Engagement - Could hooks, CTAs, or interactive elements be added?

Content to analyze:
{content_text[:3000]}

For each suggestion, provide:
1. Improvement category (tone, structure, keywords, readability, engagement)
2. Current state description
3. Suggested improvement
4. Priority level (high, medium, low)
5. Example of the improvement applied

Format your response as JSON:
{{
    "suggestions": [
        {{
            "category": "keywords",
            "current_state": "description of current state",
            "suggested_improvement": "what to improve",
            "priority": "high",
            "example": "example of the improvement"
        }}
    ]
}}"""

            system_prompt = "You are an expert content editor and SEO specialist. Provide specific, actionable improvement suggestions. Return structured JSON."

            result = await groq_service.generate_content(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=2500,
            )

            suggestions = self._parse_json_response(result, "suggestions")
            return suggestions[:limit]

        except Exception as e:
            print(f"Failed to suggest content improvements: {e}")
            return []

    # ------------------------------------------------------------------
    # Storage & Retrieval
    # ------------------------------------------------------------------

    async def save_suggestions(
        self,
        user_id: str,
        suggestion_type: str,
        suggestions: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Save generated suggestions to Supabase for later retrieval."""
        try:
            data = {
                "user_id": user_id,
                "suggestion_type": suggestion_type,
                "suggestions": suggestions,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            result = self.supabase.table("auto_suggestions").insert(data).execute()
            if result.data:
                # Invalidate cache when new suggestions are saved
                cache.delete_pattern("", prefix=f"suggestions:{user_id}")
                return result.data[0]
            return None
        except Exception as e:
            print(f"Failed to save suggestions: {e}")
            return None

    async def get_saved_suggestions(
        self,
        user_id: str,
        suggestion_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Retrieve previously saved suggestions from Supabase."""
        try:
            query = (
                self.supabase.table("auto_suggestions")
                .select("*")
                .eq("user_id", user_id)
            )
            if suggestion_type:
                query = query.eq("suggestion_type", suggestion_type)
            query = query.order("created_at", desc=True).limit(limit)
            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Failed to get saved suggestions: {e}")
            return []

    async def delete_suggestion(self, user_id: str, suggestion_id: str) -> bool:
        """Delete a saved suggestion."""
        try:
            result = (
                self.supabase.table("auto_suggestions")
                .delete()
                .eq("id", suggestion_id)
                .eq("user_id", user_id)
                .execute()
            )
            return bool(result.data)
        except Exception as e:
            print(f"Failed to delete suggestion: {e}")
            return False

    # ------------------------------------------------------------------
    # Batch Processing
    # ------------------------------------------------------------------

    async def generate_all_suggestions(
        self,
        user_id: str,
    ) -> Dict[str, Any]:
        """Generate all types of suggestions for a user at once."""
        topics = await self.suggest_topics(user_id, limit=5)
        posting_times = await self.suggest_posting_times(user_id, limit=5)
        improvements = await self.suggest_content_improvements(user_id, limit=5)

        result = {
            "topics": topics,
            "posting_times": posting_times,
            "content_improvements": improvements,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Save each type
        if topics:
            await self.save_suggestions(user_id, "topics", topics)
        if posting_times:
            await self.save_suggestions(user_id, "posting_times", posting_times)
        if improvements:
            await self.save_suggestions(user_id, "content_improvements", improvements)

        return result

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def _summarize_content_history(self, content_history: List[Dict[str, Any]]) -> str:
        """Create a concise summary of user's content history."""
        if not content_history:
            return "No content history available."

        summary_parts = []
        for i, item in enumerate(content_history[:10]):
            title = item.get("title", "Untitled")
            category = item.get("category", "uncategorized")
            tags = item.get("tags", [])
            tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
            platform = item.get("platform", "unknown")
            summary_parts.append(f"{i + 1}. '{title}' (Category: {category}, Platform: {platform}, Tags: {tags_str})")

        return "\n".join(summary_parts)

    def _get_top_performing_content(
        self,
        content_history: List[Dict[str, Any]],
        engagement_data: List[Dict[str, Any]],
    ) -> str:
        """Identify top performing content based on engagement data."""
        if not engagement_data:
            return "No engagement data available."

        # Build engagement lookup
        engagement_by_content: Dict[str, Dict[str, Any]] = {}
        for entry in engagement_data:
            cid = entry.get("content_id")
            if cid:
                rate = entry.get("engagement_rate", 0)
                if cid not in engagement_by_content or rate > engagement_by_content[cid].get("engagement_rate", 0):
                    engagement_by_content[cid] = entry

        # Sort by engagement rate
        top_items = sorted(
            engagement_by_content.values(),
            key=lambda x: float(x.get("engagement_rate", 0)),
            reverse=True,
        )[:5]

        if not top_items:
            return "No top performing content identified."

        lines = []
        for i, item in enumerate(top_items):
            lines.append(
                f"{i + 1}. Content {item.get('content_id', 'unknown')}: "
                f"Engagement rate {item.get('engagement_rate', 0)}, "
                f"Views {item.get('views', 0)}, "
                f"Likes {item.get('likes', 0)}, "
                f"Shares {item.get('shares', 0)}"
            )
        return "\n".join(lines)

    def _summarize_distributions(self, distributions: List[Dict[str, Any]]) -> str:
        """Summarize distribution/publishing history."""
        if not distributions:
            return "No distribution history available."

        lines = []
        for i, d in enumerate(distributions[:10]):
            platform = d.get("platform", "unknown")
            published = d.get("published_at", "unknown")
            status = d.get("status", "unknown")
            metrics = d.get("engagement_metrics", {})
            metrics_str = json.dumps(metrics) if metrics else "N/A"
            lines.append(f"{i + 1}. Platform: {platform}, Published: {published}, Status: {status}, Metrics: {metrics_str}")
        return "\n".join(lines)

    def _summarize_engagement(self, engagement_data: List[Dict[str, Any]]) -> str:
        """Summarize engagement data for AI context."""
        if not engagement_data:
            return "No engagement data available."

        total_views = sum(e.get("views", 0) for e in engagement_data)
        total_likes = sum(e.get("likes", 0) for e in engagement_data)
        total_shares = sum(e.get("shares", 0) for e in engagement_data)
        avg_engagement = sum(e.get("engagement_rate", 0) for e in engagement_data) / len(engagement_data) if engagement_data else 0

        # Group by hour of day for pattern analysis
        hourly: Dict[int, List[float]] = {}
        for e in engagement_data:
            recorded = e.get("recorded_at", "")
            try:
                dt = datetime.fromisoformat(recorded.replace("Z", "+00:00"))
                hour = dt.hour
                hourly.setdefault(hour, []).append(float(e.get("engagement_rate", 0)))
            except (ValueError, AttributeError):
                continue

        peak_hours = sorted(
            hourly.items(),
            key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
            reverse=True,
        )[:5]

        peak_str = ", ".join([f"{h}:00 UTC (avg rate: {sum(rates)/len(rates):.2f})" for h, rates in peak_hours])

        return (
            f"Total views: {total_views}, Total likes: {total_likes}, "
            f"Total shares: {total_shares}, Average engagement rate: {avg_engagement:.2f}\n"
            f"Peak engagement hours: {peak_str if peak_str else 'N/A'}"
        )

    def _parse_json_response(self, response: str, key: str) -> List[Dict[str, Any]]:
        """Parse JSON from Groq AI response, handling markdown code blocks."""
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)

            if isinstance(data, dict) and key in data:
                items = data[key]
                if isinstance(items, list):
                    return items

            if isinstance(data, list):
                return data

            return []
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            print(f"Failed to parse JSON response for key '{key}': {e}")
            return []


# Singleton instance
suggestion_service = SuggestionService()
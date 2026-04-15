"""
Competitor Analysis Service for ContentForge AI.

Provides functionality for:
- Mock competitor data fetching
- Engagement comparison and benchmarking
- Content gap identification
- Topic overlap analysis
- Performance tracking
"""

import logging
import random
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)
from uuid import UUID

from app.core.supabase import get_supabase_admin_client, get_supabase_client


class CompetitorService:
    """Service for competitor analysis and content gap identification."""

    # Mock data for competitor content generation
    MOCK_CONTENT_TEMPLATES = {
        "twitter": [
            "Just published a new article on {topic}! Check it out and let me know your thoughts. 🚀",
            "{topic} is changing the game. Here's why you should pay attention 👇",
            "Thread 🧵: Everything you need to know about {topic} in 10 tweets",
            "Hot take: {topic} is overrated. Here's what actually matters...",
            "The future of {topic} is bright. Excited to see where this goes! ✨",
            "Working on something big in {topic} space. Stay tuned! 🔥",
            "{topic} tip: Consistency beats intensity. Show up every day.",
            "What nobody tells you about {topic}...",
            "Just hit {milestone} followers! Thank you all! 🎉 #{topic}",
            "Question for my audience: What's your biggest challenge with {topic}?",
        ],
        "linkedin": [
            "I'm thrilled to share my insights on {topic}. Over the past year, I've learned that...",
            "3 lessons I learned about {topic} the hard way:\n\n1. ...\n2. ...\n3. ...",
            "The {topic} industry is evolving rapidly. Here's what leaders need to know:",
            "Reflecting on my journey with {topic}. Grateful for the opportunities and challenges.",
            "Why {topic} matters now more than ever. A professional perspective:",
            "Just wrapped up an exciting project focused on {topic}. Key takeaways:",
            "Career advice: Master {topic} and you'll be invaluable in today's market.",
            "The biggest misconception about {topic} in our industry...",
            "Grateful to be recognized for my work in {topic}. Here's what helped me succeed:",
            "Struggling with {topic}? You're not alone. Here's a framework that works:",
        ],
        "instagram": [
            "Living my best {topic} life ✨ #blessed #{topic}",
            "Swipe to see my {topic} journey → Worth it! 🙌",
            "Behind the scenes: How I approach {topic} 💪",
            "{topic} mood ✨ What's your vibe today?",
            "The {topic} community is everything 💯 Love you all!",
            "POV: You're crushing it at {topic} 🔥",
            "Day in the life: {topic} edition 📸",
            "My {topic} setup! Drop a 💙 if you love it",
            "Transforming my {topic} game one day at a time ✨",
            "{topic} tips that actually work 👇 Save this!",
        ],
        "blog": [
            "A Comprehensive Guide to {topic}: Strategies for Success",
            "Why {topic} Should Be Your Priority in 2026",
            "The Complete Beginner's Guide to {topic}",
            "10 {topic} Mistakes You're Probably Making (And How to Fix Them)",
            "How I Improved My {topic} Results by 300%",
            "The Future of {topic}: Trends and Predictions",
            "Case Study: How {topic} Transformed Our Business",
            "{topic} vs {topic_alt}: Which Is Right for You?",
            "Master {topic} in 30 Days: A Step-by-Step Plan",
            "What Experts Won't Tell You About {topic}",
        ],
    }

    MOCK_TOPICS = [
        "content marketing",
        "SEO",
        "social media",
        "branding",
        "AI tools",
        "productivity",
        "leadership",
        "startup growth",
        "personal branding",
        "digital marketing",
        "email marketing",
        "video content",
        "podcasting",
        "webinar marketing",
        "community building",
        "influencer marketing",
        "data analytics",
        "customer experience",
        "automation",
        "storytelling",
    ]

    MOCK_MILESTONES = ["1K", "5K", "10K", "50K", "100K", "500K", "1M"]

    def __init__(self):
        self._supabase = None

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_admin_client()
        return self._supabase

    @supabase.setter
    def supabase(self, value):
        self._supabase = value

    # ============ Mock Data Generation ============

    def _generate_mock_content(
        self, platform: str, handle: str, count: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate realistic mock content for a competitor."""
        templates = self.MOCK_CONTENT_TEMPLATES.get(
            platform, self.MOCK_CONTENT_TEMPLATES["blog"]
        )
        content_list = []

        now = datetime.now(timezone.utc)

        for i in range(count):
            template = random.choice(templates)
            topic = random.choice(self.MOCK_TOPICS)
            topic_alt = random.choice([t for t in self.MOCK_TOPICS if t != topic])
            milestone = random.choice(self.MOCK_MILESTONES)

            content_text = template.format(
                topic=topic, topic_alt=topic_alt, milestone=milestone
            )

            # Generate engagement based on "realistic" patterns
            base_engagement = random.randint(50, 5000)
            likes = int(base_engagement * random.uniform(0.7, 1.0))
            comments = int(base_engagement * random.uniform(0.05, 0.2))
            shares = (
                int(base_engagement * random.uniform(0.1, 0.4))
                if platform in ["twitter", "linkedin", "facebook"]
                else 0
            )
            views = (
                int(likes * random.uniform(5, 20))
                if platform in ["instagram", "tiktok", "youtube"]
                else likes * 3
            )

            engagement_score = likes + (comments * 3) + (shares * 5)

            # Published date (randomly distributed over last 30 days)
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            published_at = now - timedelta(days=days_ago, hours=hours_ago)

            # Extract keywords/topics from content
            words = re.findall(r"\b[a-zA-Z]{4,}\b", content_text.lower())
            keywords = list(set(random.sample(words, min(5, len(words)))))

            content_item = {
                "external_id": f"mock_{platform}_{handle}_{i}_{int(published_at.timestamp())}",
                "content": content_text,
                "content_type": random.choice(["post", "article", "video", "story"]),
                "published_at": published_at.isoformat(),
                "url": f"https://{platform}.com/{handle}/status/{i}",
                "likes": likes,
                "shares": shares,
                "comments": comments,
                "views": views,
                "engagement_score": engagement_score,
                "sentiment": random.choice(
                    ["positive", "neutral", "positive", "positive"]
                ),  # Skew positive
                "topics": [topic],
                "keywords": keywords,
                "analyzed_at": now.isoformat(),
            }
            content_list.append(content_item)

        # Sort by published date descending
        content_list.sort(key=lambda x: x["published_at"], reverse=True)
        return content_list

    def _generate_mock_follower_count(self, platform: str) -> int:
        """Generate a realistic follower count based on platform."""
        ranges = {
            "twitter": (1000, 500000),
            "linkedin": (500, 100000),
            "instagram": (2000, 1000000),
            "youtube": (1000, 2000000),
            "tiktok": (5000, 5000000),
            "facebook": (500, 100000),
            "blog": (100, 50000),
        }
        min_count, max_count = ranges.get(platform, (100, 10000))
        return random.randint(min_count, max_count)

    # ============ Database Operations ============

    async def add_competitor(
        self,
        user_id: str,
        name: str,
        platform: str,
        handle: str,
        description: Optional[str] = None,
        profile_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a new competitor to track."""
        follower_count = self._generate_mock_follower_count(platform)

        competitor_data = {
            "user_id": user_id,
            "name": name,
            "platform": platform,
            "handle": handle,
            "follower_count": follower_count,
            "description": description or f"{name} on {platform}",
            "profile_url": profile_url or f"https://{platform}.com/{handle}",
            "is_active": True,
            "last_synced_at": datetime.now(timezone.utc).isoformat(),
        }

        result = self.supabase.table("competitors").insert(competitor_data).execute()

        if result.data:
            competitor = result.data[0]
            # Generate initial mock content
            await self.refresh_competitor_data(competitor["id"], user_id)
            return competitor

        return None

    async def get_competitors(
        self, user_id: str, platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all competitors for a user."""
        query = (
            self.supabase.table("competitors")
            .select("*")
            .eq("user_id", user_id)
            .eq("is_active", True)
        )

        if platform:
            query = query.eq("platform", platform)

        result = query.order("created_at", desc=True).execute()
        return result.data or []

    async def get_competitor_by_id(
        self, competitor_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific competitor by ID."""
        result = (
            self.supabase.table("competitors")
            .select("*")
            .eq("id", competitor_id)
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    async def remove_competitor(self, competitor_id: str, user_id: str) -> bool:
        """Remove a competitor (soft delete by setting is_active=false)."""
        result = (
            self.supabase.table("competitors")
            .update({"is_active": False})
            .eq("id", competitor_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(result.data)

    async def get_competitor_content(
        self, competitor_id: str, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get content for a specific competitor."""
        # Verify competitor belongs to user
        competitor = await self.get_competitor_by_id(competitor_id, user_id)
        if not competitor:
            return []

        result = (
            self.supabase.table("competitor_content")
            .select("*")
            .eq("competitor_id", competitor_id)
            .order("published_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return result.data or []

    async def refresh_competitor_data(
        self, competitor_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Refresh competitor data by fetching new content."""
        competitor = await self.get_competitor_by_id(competitor_id, user_id)
        if not competitor:
            return {"success": False, "error": "Competitor not found"}

        # Generate new mock content
        new_content = self._generate_mock_content(
            competitor["platform"], competitor["handle"], count=random.randint(5, 15)
        )

        # Insert content (skip duplicates based on external_id)
        inserted_count = 0
        for content_item in new_content:
            content_item["competitor_id"] = competitor_id
            try:
                self.supabase.table("competitor_content").insert(content_item).execute()
                inserted_count += 1
            except Exception:
                # Duplicate or error, skip
                pass

        # Update last_synced_at
        self.supabase.table("competitors").update(
            {"last_synced_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", competitor_id).execute()

        return {
            "success": True,
            "competitor_id": competitor_id,
            "new_content_count": inserted_count,
            "total_content": await self._get_content_count(competitor_id),
        }

    async def _get_content_count(self, competitor_id: str) -> int:
        """Get total content count for a competitor."""
        result = (
            self.supabase.table("competitor_content")
            .select("id", count="exact")
            .eq("competitor_id", competitor_id)
            .execute()
        )
        return result.count or 0

    # ============ Analysis Methods ============

    async def get_performance_analysis(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive performance analysis for user's competitors."""
        competitors = await self.get_competitors(user_id)

        if not competitors:
            return {
                "competitor_count": 0,
                "message": "No competitors tracked yet",
            }

        analysis = {
            "competitor_count": len(competitors),
            "competitors": [],
            "aggregated_metrics": {},
            "platform_breakdown": {},
            "insights": [],
        }

        total_followers = 0
        total_engagement = 0
        total_content = 0

        for comp in competitors:
            # Get recent content stats
            recent_content = (
                self.supabase.table("competitor_content")
                .select("*")
                .eq("competitor_id", comp["id"])
                .gte(
                    "published_at",
                    (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                )
                .execute()
            )

            content_count = len(recent_content.data) if recent_content.data else 0

            # Calculate avg engagement
            if recent_content.data:
                avg_likes = sum(c.get("likes", 0) for c in recent_content.data) / max(
                    content_count, 1
                )
                avg_comments = sum(
                    c.get("comments", 0) for c in recent_content.data
                ) / max(content_count, 1)
                avg_shares = sum(c.get("shares", 0) for c in recent_content.data) / max(
                    content_count, 1
                )
                avg_engagement = (
                    (avg_likes + avg_comments * 3 + avg_shares * 5)
                    / max(comp["follower_count"], 1)
                    * 100
                )
            else:
                avg_engagement = 0

            comp_analysis = {
                "id": comp["id"],
                "name": comp["name"],
                "platform": comp["platform"],
                "handle": comp["handle"],
                "follower_count": comp["follower_count"],
                "content_last_30_days": content_count,
                "avg_engagement_rate": round(avg_engagement, 2),
                "last_synced": comp.get("last_synced_at"),
            }

            analysis["competitors"].append(comp_analysis)

            total_followers += comp["follower_count"]
            total_engagement += avg_engagement
            total_content += content_count

            # Platform breakdown
            platform = comp["platform"]
            if platform not in analysis["platform_breakdown"]:
                analysis["platform_breakdown"][platform] = {
                    "count": 0,
                    "total_followers": 0,
                    "total_content": 0,
                }
            analysis["platform_breakdown"][platform]["count"] += 1
            analysis["platform_breakdown"][platform]["total_followers"] += comp[
                "follower_count"
            ]
            analysis["platform_breakdown"][platform]["total_content"] += content_count

        # Aggregated metrics
        analysis["aggregated_metrics"] = {
            "total_competitor_followers": total_followers,
            "avg_followers_per_competitor": round(
                total_followers / len(competitors), 0
            ),
            "avg_engagement_rate": round(total_engagement / len(competitors), 2),
            "total_content_last_30_days": total_content,
        }

        # Generate insights
        analysis["insights"] = self._generate_insights(
            analysis["competitors"], analysis["aggregated_metrics"]
        )

        return analysis

    def _generate_insights(
        self, competitors: List[Dict], metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable insights from competitor data."""
        insights = []

        if not competitors:
            return insights

        # Sort by engagement rate
        by_engagement = sorted(
            competitors, key=lambda x: x["avg_engagement_rate"], reverse=True
        )
        top_engager = by_engagement[0]

        insights.append(
            {
                "type": "engagement_leader",
                "title": f"{top_engager['name']} has the highest engagement",
                "description": f"Their engagement rate of {top_engager['avg_engagement_rate']}% is leading your tracked competitors.",
                "platform": top_engager["platform"],
                "recommendation": "Study their content strategy to understand what resonates with their audience.",
            }
        )

        # Find most active poster
        by_activity = sorted(
            competitors, key=lambda x: x["content_last_30_days"], reverse=True
        )
        top_poster = by_activity[0]

        insights.append(
            {
                "type": "content_volume",
                "title": f"{top_poster['name']} is most active",
                "description": f"They published {top_poster['content_last_30_days']} pieces of content in the last 30 days.",
                "platform": top_poster["platform"],
                "recommendation": "Consider increasing your posting frequency if quality can be maintained.",
            }
        )

        # Platform diversity insight
        platforms = set(c["platform"] for c in competitors)
        if len(platforms) == 1:
            insights.append(
                {
                    "type": "platform_diversity",
                    "title": "Single platform focus detected",
                    "description": f"All competitors are on {list(platforms)[0]}. Consider diversifying.",
                    "recommendation": "Add competitors from different platforms to get broader insights.",
                }
            )

        return insights

    async def identify_content_gaps(self, user_id: str) -> Dict[str, Any]:
        """Identify content gaps based on competitor analysis."""
        # Get all competitor content from last 60 days
        competitors = await self.get_competitors(user_id)

        if not competitors:
            return {"gaps": [], "message": "No competitors to analyze"}

        # Collect all topics from competitor content
        all_topics = Counter()
        topic_content_counts = {}

        for comp in competitors:
            content_result = (
                self.supabase.table("competitor_content")
                .select("topics")
                .eq("competitor_id", comp["id"])
                .gte(
                    "published_at",
                    (datetime.now(timezone.utc) - timedelta(days=60)).isoformat(),
                )
                .execute()
            )

            for item in content_result.data or []:
                for topic in item.get("topics", []):
                    all_topics[topic] += 1
                    if topic not in topic_content_counts:
                        topic_content_counts[topic] = 0
                    topic_content_counts[topic] += 1

        # Get user's existing content topics (from content table)
        user_topics = set()
        try:
            user_content = (
                self.supabase.table("content")
                .select("keywords")
                .eq("user_id", user_id)
                .execute()
            )
            for item in user_content.data or []:
                for keyword in item.get("keywords", []):
                    user_topics.add(keyword.lower())
        except Exception:
            pass

        # Identify gaps
        gaps = []

        for topic, count in all_topics.most_common(20):
            has_content = topic.lower() in user_topics
            opportunity_score = min(100, int(count * 10 + random.randint(10, 30)))

            if (
                not has_content or count > 3
            ):  # Gap if user has none OR competitors are very active
                gap = {
                    "user_id": user_id,
                    "topic": topic,
                    "category": self._categorize_topic(topic),
                    "competitor_count": count,
                    "user_has_content": has_content,
                    "user_content_count": 1 if has_content else 0,
                    "opportunity_score": opportunity_score,
                    "suggested_action": self._generate_suggestion(topic, has_content),
                    "content_ideas": self._generate_content_ideas(topic),
                    "priority": (
                        "high"
                        if opportunity_score > 70
                        else "medium" if opportunity_score > 40 else "low"
                    ),
                }
                gaps.append(gap)

        # Store gaps in database
        stored_gaps = []
        for gap in gaps[:10]:  # Store top 10
            try:
                result = (
                    self.supabase.table("content_gaps")
                    .upsert(gap, on_conflict="user_id,topic")
                    .execute()
                )
                if result.data:
                    stored_gaps.append(result.data[0])
            except Exception as e:
                # Log but continue
                logger.error(f"Error storing gap: {e}")
                stored_gaps.append(gap)

        return {
            "gaps_analyzed": len(gaps),
            "gaps_stored": len(stored_gaps),
            "gaps": stored_gaps,
        }

    def _categorize_topic(self, topic: str) -> str:
        """Categorize a topic into a broad category."""
        categories = {
            "marketing": ["marketing", "SEO", "content", "social media", "email"],
            "business": ["business", "startup", "leadership", "growth", "strategy"],
            "technology": ["AI", "automation", "tech", "digital", "software"],
            "personal": ["personal branding", "productivity", "career"],
        }

        topic_lower = topic.lower()
        for category, keywords in categories.items():
            if any(kw in topic_lower for kw in keywords):
                return category
        return "general"

    def _generate_suggestion(self, topic: str, has_content: bool) -> str:
        """Generate a suggested action for a content gap."""
        if not has_content:
            return f"Create your first piece of content about {topic}. Your competitors are talking about it."
        return f"Increase content volume about {topic}. Competitors are publishing frequently on this topic."

    def _generate_content_ideas(self, topic: str) -> List[str]:
        """Generate content ideas for a topic."""
        templates = [
            f"The Ultimate Guide to {topic.title()}",
            f"10 {topic.title()} Tips That Actually Work",
            f"Why {topic.title()} Matters in 2026",
            f"{topic.title()}: A Beginner's Guide",
            f"How I Improved My {topic.title()} in 30 Days",
            f"The Biggest {topic.title()} Mistakes to Avoid",
            f"{topic.title()} Trends You Need to Know",
            f"Case Study: {topic.title()} Success Story",
        ]
        return random.sample(templates, min(3, len(templates)))

    async def get_content_gaps(
        self, user_id: str, min_opportunity: int = 0
    ) -> List[Dict[str, Any]]:
        """Get stored content gaps for a user."""
        query = (
            self.supabase.table("content_gaps")
            .select("*")
            .eq("user_id", user_id)
            .eq("is_addressed", False)
        )

        if min_opportunity > 0:
            query = query.gte("opportunity_score", min_opportunity)

        result = query.order("opportunity_score", desc=True).execute()
        return result.data or []

    async def analyze_topic_overlap(self, user_id: str) -> Dict[str, Any]:
        """Analyze topic overlap between user and competitors."""
        competitors = await self.get_competitors(user_id)

        # Get competitor topics
        comp_topics = Counter()
        for comp in competitors:
            content = (
                self.supabase.table("competitor_content")
                .select("topics")
                .eq("competitor_id", comp["id"])
                .execute()
            )
            for item in content.data or []:
                comp_topics.update(item.get("topics", []))

        # Get user topics
        user_topics = Counter()
        try:
            user_content = (
                self.supabase.table("content")
                .select("keywords")
                .eq("user_id", user_id)
                .execute()
            )
            for item in user_content.data or []:
                user_topics.update(item.get("keywords", []))
        except Exception:
            pass

        # Calculate overlap
        overlap = set(comp_topics.keys()) & set(user_topics.keys())
        unique_to_comp = set(comp_topics.keys()) - set(user_topics.keys())
        unique_to_user = set(user_topics.keys()) - set(comp_topics.keys())

        return {
            "competitor_topic_count": len(comp_topics),
            "user_topic_count": len(user_topics),
            "overlap_count": len(overlap),
            "overlap_percentage": round(
                len(overlap) / max(len(comp_topics), 1) * 100, 1
            ),
            "shared_topics": list(overlap),
            "competitor_only_topics": list(unique_to_comp)[:10],
            "user_only_topics": list(unique_to_user)[:10],
            "recommendation": (
                "Focus on competitor-only topics to close content gaps"
                if len(unique_to_comp) > 5
                else "Good topic coverage"
            ),
        }

    async def get_benchmark_comparison(self, user_id: str) -> Dict[str, Any]:
        """Get benchmarking data comparing user to competitors."""
        analysis = await self.get_performance_analysis(user_id)

        if analysis["competitor_count"] == 0:
            return {"message": "No competitors to benchmark against"}

        # Get user's metrics (mock for now - would come from actual user data)
        user_metrics = {
            "follower_count": random.randint(1000, 50000),  # Would be actual user data
            "content_count_30d": random.randint(5, 30),
            "avg_engagement_rate": round(random.uniform(1.5, 5.0), 2),
        }

        comp_metrics = analysis["aggregated_metrics"]

        return {
            "user_metrics": user_metrics,
            "competitor_avg": {
                "follower_count": comp_metrics["avg_followers_per_competitor"],
                "content_per_month": round(
                    comp_metrics["total_content_last_30_days"]
                    / max(analysis["competitor_count"], 1),
                    1,
                ),
                "engagement_rate": comp_metrics["avg_engagement_rate"],
            },
            "comparison": {
                "follower_gap": int(
                    comp_metrics["avg_followers_per_competitor"]
                    - user_metrics["follower_count"]
                ),
                "content_gap": round(
                    comp_metrics["total_content_last_30_days"]
                    / max(analysis["competitor_count"], 1)
                    - user_metrics["content_count_30d"],
                    1,
                ),
                "engagement_comparison": round(
                    user_metrics["avg_engagement_rate"]
                    - comp_metrics["avg_engagement_rate"],
                    2,
                ),
            },
            "percentile": {
                "followers": self._calculate_percentile(
                    user_metrics["follower_count"],
                    [c["follower_count"] for c in analysis["competitors"]],
                ),
                "engagement": self._calculate_percentile(
                    user_metrics["avg_engagement_rate"],
                    [c["avg_engagement_rate"] for c in analysis["competitors"]],
                ),
            },
        }

    def _calculate_percentile(self, value: float, population: List[float]) -> int:
        """Calculate percentile of value within population."""
        if not population:
            return 50
        below = sum(1 for p in population if p < value)
        return int((below / len(population)) * 100)

    async def fetch_all_competitor_data(self) -> Dict[str, Any]:
        """Fetch data for all active competitors (for scheduled tasks)."""
        # Get all active competitors across all users
        result = (
            self.supabase.table("competitors")
            .select("*")
            .eq("is_active", True)
            .execute()
        )
        competitors = result.data or []

        updated_count = 0
        total_new_content = 0

        for comp in competitors:
            try:
                result = await self.refresh_competitor_data(comp["id"], comp["user_id"])
                if result["success"]:
                    updated_count += 1
                    total_new_content += result.get("new_content_count", 0)
            except Exception as e:
                logger.error(f"Error refreshing competitor {comp['id']}: {e}")
                continue

        return {
            "success": True,
            "competitors_updated": updated_count,
            "total_new_content": total_new_content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def generate_gap_analysis_for_all_users(self) -> Dict[str, Any]:
        """Generate content gap analysis for all users with competitors."""
        # Get unique user IDs with competitors
        result = (
            self.supabase.table("competitors")
            .select("user_id")
            .eq("is_active", True)
            .execute()
        )
        user_ids = list(set(item["user_id"] for item in result.data or []))

        processed_count = 0
        total_gaps = 0

        for user_id in user_ids:
            try:
                gap_result = await self.identify_content_gaps(user_id)
                processed_count += 1
                total_gaps += gap_result.get("gaps_stored", 0)
            except Exception as e:
                logger.error(f"Error analyzing gaps for user {user_id}: {e}")
                continue

        return {
            "success": True,
            "users_processed": processed_count,
            "total_gaps_identified": total_gaps,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global service instance
competitor_service = CompetitorService()

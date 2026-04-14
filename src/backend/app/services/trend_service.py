"""
Trend detection and analysis service using AI and mock data.
"""
import json
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from app.core.supabase import get_supabase_client
from app.services.groq_service import groq_service


class TrendService:
    """Service for detecting and analyzing trending topics."""
    
    # Mock trending data sources
    MOCK_KEYWORDS = {
        "tech": [
            "AI", "machine learning", "ChatGPT", "LLM", "generative AI", "OpenAI",
            "API", "automation", "no-code", "low-code", "web3", "blockchain",
            "cloud computing", "serverless", "DevOps", "Kubernetes", "Docker",
            "cybersecurity", "data privacy", "quantum computing", "edge computing",
            "5G", "IoT", "smart home", "virtual reality", "augmented reality",
            "metaverse", "NFT", "crypto", "bitcoin", "ethereum", "DeFi"
        ],
        "business": [
            "startup", "funding", "Series A", "venture capital", "SaaS",
            "productivity", "remote work", "hybrid work", "digital transformation",
            "customer experience", "CX", "user engagement", "retention",
            "growth hacking", "marketing automation", "content strategy",
            "thought leadership", "personal branding", "networking",
            "entrepreneurship", "side hustle", "passive income", "freelancing"
        ],
        "entertainment": [
            "streaming", "Netflix", "Spotify", "podcast", "TikTok", "viral",
            "celebrity", "movie", "TV series", "documentary", "reality TV",
            "music", "concert", "festival", "award show", " Oscars", "Grammy",
            "social media", "influencer", "content creator", "YouTube"
        ],
        "news": [
            "breaking news", "headlines", "politics", "election", "policy",
            "climate change", "environment", "sustainability", "green energy",
            "health", "wellness", "mental health", "fitness", "nutrition",
            "science", "research", "discovery", "space", "NASA"
        ],
        "social": [
            "viral", "trending", "meme", "challenge", "hashtag", "Twitter",
            "Instagram", "LinkedIn", "Facebook", "social media marketing",
            "community building", "engagement", "followers", "algorithm"
        ]
    }
    
    SOURCES = ["twitter", "reddit", "news", "google_trends", "hackernews", "linkedin"]
    
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
    
    async def fetch_mock_trending_data(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch mock trending data from various sources."""
        trends = []
        
        # Select categories to fetch from
        if category and category in self.MOCK_KEYWORDS:
            categories = [category]
        else:
            categories = list(self.MOCK_KEYWORDS.keys())
        
        # Generate mock trends
        for cat in categories:
            keywords = self.MOCK_KEYWORDS[cat]
            num_trends = random.randint(3, 8)
            selected_keywords = random.sample(keywords, min(num_trends, len(keywords)))
            
            for keyword in selected_keywords:
                # Generate realistic trend metrics
                base_mentions = random.randint(1000, 50000)
                velocity = random.uniform(0.5, 10.0)  # mentions per hour growth
                trend_score = random.uniform(50, 100)
                
                trend = {
                    "topic": keyword,
                    "category": cat,
                    "mention_count": base_mentions,
                    "velocity": round(velocity, 2),
                    "trend_score": round(trend_score, 2),
                    "source": random.choice(self.SOURCES),
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                    "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
                    "related_keywords": self._generate_related_keywords(keyword, cat),
                    "sample_content": self._generate_sample_content(keyword, cat),
                }
                trends.append(trend)
        
        return trends
    
    def _generate_related_keywords(self, topic: str, category: str) -> List[str]:
        """Generate related keywords for a topic."""
        related_pool = self.MOCK_KEYWORDS.get(category, [])
        related = [k for k in related_pool if k != topic and len(k) > 3]
        return random.sample(related, min(5, len(related))) if related else []
    
    def _generate_sample_content(self, topic: str, category: str) -> List[Dict[str, str]]:
        """Generate sample content items for a topic."""
        templates = {
            "tech": [
                f"Just tried out the new {topic} feature - mind blown! 🤯",
                f"{topic} is changing how we build software forever",
                f"Can't believe how fast {topic} technology is advancing",
            ],
            "business": [
                f"How {topic} is reshaping the business landscape",
                f"Why every startup should focus on {topic} in 2024",
                f"The {topic} playbook: lessons from successful founders",
            ],
            "entertainment": [
                f"Everyone's talking about {topic} right now 🔥",
                f"This {topic} moment is pure gold",
                f"{topic} trends that are taking over social media",
            ],
            "news": [
                f"Breaking: Major developments in {topic}",
                f"What {topic} means for the future",
                f"Experts weigh in on {topic}",
            ],
            "social": [
                f"This {topic} challenge is everywhere 📈",
                f"How {topic} became the biggest trend of the week",
                f"The {topic} effect on social media engagement",
            ],
        }
        
        content_templates = templates.get(category, templates["tech"])
        return [
            {"source": source, "text": text}
            for source, text in zip(
                random.sample(self.SOURCES, min(len(content_templates), len(self.SOURCES))),
                random.sample(content_templates, len(content_templates))
            )
        ]
    
    async def analyze_trends_with_ai(self, trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use AI to analyze and categorize trending topics."""
        if not trends:
            return []
        
        # Prepare trend data for analysis
        trends_text = "\n".join([
            f"{i+1}. {t['topic']} (Category: {t['category']}, Mentions: {t['mention_count']})"
            for i, t in enumerate(trends[:20])  # Analyze top 20
        ])
        
        prompt = f"""Analyze these trending topics and provide insights:

Trending Topics:
{trends_text}

For each trend, provide:
1. A refined categorization (tech, business, entertainment, news, health, sports, lifestyle)
2. A relevance score (0-100) based on current importance
3. Content opportunities for creators
4. Related emerging subtopics

Format your response as JSON:
{{
    "trends": [
        {{
            "topic": "original topic",
            "refined_category": "category",
            "relevance_score": 85,
            "content_opportunities": ["how-to guide", "opinion piece", "case study"],
            "emerging_subtopics": ["subtopic1", "subtopic2"]
        }}
    ]
}}"""
        
        try:
            system_prompt = "You are a trend analysis expert. Analyze trending topics and provide structured insights in JSON format."
            result = await groq_service.generate_content(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2000,
            )
            
            # Parse AI response
            ai_analysis = self._parse_ai_analysis(result)
            
            # Merge AI analysis with original trends
            enriched_trends = []
            for trend in trends:
                analysis = ai_analysis.get(trend["topic"], {})
                trend.update({
                    "category": analysis.get("refined_category", trend["category"]),
                    "trend_score": analysis.get("relevance_score", trend["trend_score"]),
                    "content_opportunities": analysis.get("content_opportunities", []),
                    "emerging_subtopics": analysis.get("emerging_subtopics", []),
                })
                enriched_trends.append(trend)
            
            return enriched_trends
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return trends
    
    def _parse_ai_analysis(self, result: str) -> Dict[str, Dict]:
        """Parse AI analysis response."""
        analysis = {}
        
        try:
            # Try to extract JSON from the response
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                json_str = result.split("```")[1].strip()
            else:
                json_str = result.strip()
            
            data = json.loads(json_str)
            
            for item in data.get("trends", []):
                topic = item.get("topic", "").lower().strip()
                if topic:
                    analysis[topic] = {
                        "refined_category": item.get("refined_category", "general"),
                        "relevance_score": item.get("relevance_score", 50),
                        "content_opportunities": item.get("content_opportunities", []),
                        "emerging_subtopics": item.get("emerging_subtopics", []),
                    }
        except Exception as e:
            print(f"Failed to parse AI analysis: {e}")
        
        return analysis
    
    async def save_trends_to_db(self, trends: List[Dict[str, Any]]) -> int:
        """Save trending topics to database."""
        if not trends:
            return 0
        
        saved_count = 0
        
        for trend in trends:
            try:
                # Check if trend already exists
                existing = self.supabase.table("trending_topics").select("id").eq("topic", trend["topic"]).execute()
                
                if existing.data:
                    # Update existing trend
                    trend_id = existing.data[0]["id"]
                    update_data = {
                        "trend_score": trend["trend_score"],
                        "mention_count": trend["mention_count"],
                        "velocity": trend["velocity"],
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                    self.supabase.table("trending_topics").update(update_data).eq("id", trend_id).execute()
                else:
                    # Insert new trend
                    insert_data = {
                        "topic": trend["topic"],
                        "category": trend["category"],
                        "trend_score": trend["trend_score"],
                        "mention_count": trend["mention_count"],
                        "velocity": trend["velocity"],
                        "source": trend["source"],
                        "discovered_at": trend["discovered_at"],
                        "expires_at": trend["expires_at"],
                        "related_keywords": trend["related_keywords"],
                        "sample_content": trend["sample_content"],
                    }
                    self.supabase.table("trending_topics").insert(insert_data).execute()
                    saved_count += 1
                    
            except Exception as e:
                print(f"Failed to save trend {trend.get('topic')}: {e}")
                continue
        
        return saved_count
    
    async def get_trending_topics(
        self,
        category: Optional[str] = None,
        limit: int = 20,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Get current trending topics from database."""
        try:
            query = self.supabase.table("trending_topics").select("*")
            
            if category:
                query = query.eq("category", category)
            
            query = query.gte("trend_score", min_score)
            query = query.order("trend_score", desc=True)
            query = query.limit(limit)
            
            result = query.execute()
            return result.data or []
            
        except Exception as e:
            print(f"Failed to get trending topics: {e}")
            return []
    
    async def get_topics_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get trending topics grouped by category."""
        try:
            result = self.supabase.table("trending_topics").select("*").order("trend_score", desc=True).execute()
            
            topics_by_category = {}
            for topic in result.data or []:
                cat = topic.get("category", "uncategorized")
                if cat not in topics_by_category:
                    topics_by_category[cat] = []
                topics_by_category[cat].append(topic)
            
            return topics_by_category
            
        except Exception as e:
            print(f"Failed to get topics by category: {e}")
            return {}
    
    async def get_relevant_topics_for_user(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get topics relevant to user's content history."""
        try:
            # Get user's content topics
            content_result = self.supabase.table("content").select("id, title, tags, category").eq("user_id", user_id).execute()
            
            user_keywords = set()
            for content in content_result.data or []:
                if content.get("title"):
                    user_keywords.update(content["title"].lower().split())
                if content.get("tags"):
                    user_keywords.update([t.lower() for t in content["tags"]])
                if content.get("category"):
                    user_keywords.add(content["category"].lower())
            
            # Get all trending topics
            trends_result = self.supabase.table("trending_topics").select("*").order("trend_score", desc=True).execute()
            
            # Calculate relevance scores
            relevant_topics = []
            for trend in trends_result.data or []:
                relevance = self._calculate_relevance(trend, user_keywords)
                if relevance > 0.3:  # Minimum relevance threshold
                    trend["relevance_score"] = relevance
                    relevant_topics.append(trend)
            
            # Sort by relevance and return top N
            relevant_topics.sort(key=lambda x: x["relevance_score"], reverse=True)
            return relevant_topics[:limit]
            
        except Exception as e:
            print(f"Failed to get relevant topics: {e}")
            return []
    
    def _calculate_relevance(self, trend: Dict, user_keywords: set) -> float:
        """Calculate relevance score between trend and user keywords."""
        if not user_keywords:
            return 0.0
        
        relevance = 0.0
        trend_topic = trend.get("topic", "").lower()
        
        # Direct match
        if trend_topic in user_keywords:
            relevance += 0.5
        
        # Partial matches
        for keyword in user_keywords:
            if keyword in trend_topic or trend_topic in keyword:
                relevance += 0.3
            # Check related keywords
            for related in trend.get("related_keywords", []):
                if keyword in related.lower():
                    relevance += 0.2
        
        # Normalize by trend score
        trend_score = trend.get("trend_score", 0) / 100
        relevance = (relevance + trend_score) / 2
        
        return min(relevance, 1.0)
    
    async def track_topic_for_user(
        self,
        user_id: str,
        topic_id: str,
        relevance_score: float = 0.0
    ) -> bool:
        """Track a topic for a user."""
        try:
            data = {
                "user_id": user_id,
                "topic_id": topic_id,
                "relevance_score": relevance_score,
            }
            
            # Use upsert to handle duplicates
            self.supabase.table("user_topic_interests").upsert(data).execute()
            return True
            
        except Exception as e:
            print(f"Failed to track topic for user: {e}")
            return False
    
    async def get_user_tracked_topics(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all topics tracked by a user."""
        try:
            result = self.supabase.table("user_topic_interests").select(
                "*, trending_topics(*)"
            ).eq("user_id", user_id).execute()
            
            return result.data or []
            
        except Exception as e:
            print(f"Failed to get user tracked topics: {e}")
            return []
    
    async def generate_content_from_trend(
        self,
        topic: str,
        category: str,
        platform: str,
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """Generate content ideas from a trending topic."""
        try:
            prompt = f"""Create {platform} content about the trending topic: "{topic}"

Category: {category}
Tone: {tone}

Generate:
1. A catchy headline/title
2. 3 content angle ideas
3. A complete piece of content optimized for {platform}
4. Relevant hashtags (if applicable)
5. A call-to-action

Format:
HEADLINE: [title]

ANGLES:
- [Angle 1]
- [Angle 2]
- [Angle 3]

CONTENT:
[Full content here]

HASHTAGS:
[hashtags if applicable]

CTA:
[call to action]"""
            
            system_prompt = f"You are an expert content creator specializing in {platform} content. Create engaging, platform-optimized content that leverages trending topics."
            
            result = await groq_service.generate_content(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=2000,
            )
            
            # Parse the result
            content_data = self._parse_generated_content(result)
            content_data["topic"] = topic
            content_data["platform"] = platform
            
            return content_data
            
        except Exception as e:
            print(f"Failed to generate content from trend: {e}")
            return {
                "topic": topic,
                "platform": platform,
                "headline": f"Exploring {topic}",
                "content": f"An interesting look at {topic} and its impact on {category}.",
                "angles": ["Overview", "Analysis", "Future trends"],
                "hashtags": [f"#{topic.replace(' ', '')}", f"#{category}", "#trending"],
                "cta": f"Learn more about {topic}",
            }
    
    def _parse_generated_content(self, result: str) -> Dict[str, Any]:
        """Parse AI-generated content."""
        data = {
            "headline": "",
            "content": "",
            "angles": [],
            "hashtags": [],
            "cta": "",
        }
        
        try:
            # Extract headline
            if "HEADLINE:" in result:
                headline_section = result.split("HEADLINE:")[1].split("ANGLES:")[0] if "ANGLES:" in result else result.split("HEADLINE:")[1]
                data["headline"] = headline_section.strip().split("\n")[0].strip()
            
            # Extract content
            if "CONTENT:" in result:
                content_section = result.split("CONTENT:")[1].split("HASHTAGS:")[0] if "HASHTAGS:" in result else result.split("CONTENT:")[1]
                data["content"] = content_section.strip()
            
            # Extract angles
            if "ANGLES:" in result:
                angles_section = result.split("ANGLES:")[1].split("CONTENT:")[0] if "CONTENT:" in result else result.split("ANGLES:")[1]
                for line in angles_section.split("\n"):
                    line = line.strip()
                    if line.startswith("-") or line.startswith("•"):
                        data["angles"].append(line[1:].strip())
            
            # Extract hashtags
            if "HASHTAGS:" in result:
                hashtags_section = result.split("HASHTAGS:")[1].split("CTA:")[0] if "CTA:" in result else result.split("HASHTAGS:")[1]
                hashtags_text = hashtags_section.strip()
                data["hashtags"] = [h.strip() for h in hashtags_text.split() if h.startswith("#")]
            
            # Extract CTA
            if "CTA:" in result:
                cta_section = result.split("CTA:")[1].strip()
                data["cta"] = cta_section.split("\n")[0].strip()
            
        except Exception as e:
            print(f"Failed to parse generated content: {e}")
            data["content"] = result.strip()
        
        return data
    
    async def update_trending_topics(self) -> Dict[str, Any]:
        """Main method to update trending topics - called by Celery task."""
        try:
            # Fetch mock data
            mock_data = await self.fetch_mock_trending_data()
            
            # Analyze with AI
            enriched_trends = await self.analyze_trends_with_ai(mock_data)
            
            # Save to database
            saved_count = await self.save_trends_to_db(enriched_trends)
            
            # Clean up expired trends
            await self._cleanup_expired_trends()
            
            return {
                "success": True,
                "trends_analyzed": len(enriched_trends),
                "trends_saved": saved_count,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
        except Exception as e:
            print(f"Failed to update trending topics: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
    
    async def _cleanup_expired_trends(self) -> int:
        """Remove expired trending topics."""
        try:
            result = self.supabase.table("trending_topics").delete().lt("expires_at", datetime.now(timezone.utc).isoformat()).execute()
            return len(result.data or [])
        except Exception as e:
            print(f"Failed to cleanup expired trends: {e}")
            return 0
    
    async def get_velocity_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get topics with highest velocity (fastest growing)."""
        try:
            result = self.supabase.table("trending_topics").select("*").order("velocity", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            print(f"Failed to get velocity leaderboard: {e}")
            return []
    
    async def get_trending_insights(self) -> Dict[str, Any]:
        """Get overall trending insights."""
        try:
            # Get all active trends
            result = self.supabase.table("trending_topics").select("*").execute()
            trends = result.data or []
            
            if not trends:
                return {
                    "total_trends": 0,
                    "top_category": None,
                    "avg_velocity": 0,
                    "highest_velocity_topic": None,
                }
            
            # Calculate insights
            categories = {}
            total_velocity = 0
            highest_velocity = 0
            highest_topic = None
            
            for trend in trends:
                cat = trend.get("category", "unknown")
                categories[cat] = categories.get(cat, 0) + 1
                
                velocity = trend.get("velocity", 0)
                total_velocity += velocity
                
                if velocity > highest_velocity:
                    highest_velocity = velocity
                    highest_topic = trend.get("topic")
            
            top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else None
            
            return {
                "total_trends": len(trends),
                "top_category": top_category,
                "avg_velocity": round(total_velocity / len(trends), 2),
                "highest_velocity_topic": highest_topic,
                "category_distribution": categories,
            }
            
        except Exception as e:
            print(f"Failed to get trending insights: {e}")
            return {}


# Singleton instance
trend_service = TrendService()

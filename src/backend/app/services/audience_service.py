"""
Audience Growth Metrics Service

Handles growth analysis, calculations, and insights for audience metrics.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.core.supabase import get_supabase_client, get_supabase_admin_client
from app.services.groq_service import groq_service

logger = logging.getLogger(__name__)


class AudienceService:
    """Service for audience growth metrics and analysis."""
    
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
    
    def record_metric(
        self,
        user_id: str,
        platform: str,
        metric_type: str,
        value: int,
        period: str = "daily",
        recorded_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Record a new audience metric."""
        data = {
            "user_id": user_id,
            "platform": platform,
            "metric_type": metric_type,
            "value": value,
            "period": period,
            "recorded_at": recorded_at or datetime.now(timezone.utc).isoformat()
        }
        
        result = self.supabase.table("audience_metrics").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_growth_metrics(
        self,
        user_id: str,
        platform: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get growth metrics for a user."""
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        query = self.supabase.table("audience_metrics")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("recorded_at", since)\
            .order("recorded_at", desc=True)
        
        if platform:
            query = query.eq("platform", platform)
        
        result = query.execute()
        metrics = result.data or []
        
        # Calculate growth rates
        growth_7d = self._calculate_growth_rate(user_id, platform, 7)
        growth_30d = self._calculate_growth_rate(user_id, platform, 30)
        growth_90d = self._calculate_growth_rate(user_id, platform, 90)
        
        # Get current totals by platform
        current_totals = self._get_current_totals(user_id)
        
        return {
            "metrics": metrics,
            "growth_rates": {
                "7d": growth_7d,
                "30d": growth_30d,
                "90d": growth_90d
            },
            "current_totals": current_totals,
            "platform": platform,
            "period_days": days
        }
    
    def get_platforms_metrics(
        self,
        user_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get metrics grouped by platform."""
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        result = self.supabase.table("audience_metrics")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("recorded_at", since)\
            .execute()
        
        metrics = result.data or []
        
        # Group by platform
        platforms = {}
        for metric in metrics:
            platform = metric.get("platform")
            if platform not in platforms:
                platforms[platform] = {
                    "platform": platform,
                    "metrics": [],
                    "current_followers": 0,
                    "growth_7d": 0,
                    "growth_30d": 0
                }
            platforms[platform]["metrics"].append(metric)
        
        # Calculate current totals and growth for each platform
        for platform in platforms:
            platforms[platform]["current_followers"] = self._get_current_followers(
                user_id, platform
            )
            platforms[platform]["growth_7d"] = self._calculate_follower_growth(
                user_id, platform, 7
            )
            platforms[platform]["growth_30d"] = self._calculate_follower_growth(
                user_id, platform, 30
            )
            # Remove raw metrics list to reduce response size
            del platforms[platform]["metrics"]
        
        return list(platforms.values())
    
    def get_historical_data(
        self,
        user_id: str,
        platform: Optional[str] = None,
        metric_type: str = "followers",
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """Get historical metric data."""
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        query = self.supabase.table("audience_metrics")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("metric_type", metric_type)\
            .gte("recorded_at", since)\
            .order("recorded_at")
        
        if platform:
            query = query.eq("platform", platform)
        
        result = query.execute()
        return result.data or []
    
    def get_latest_snapshot(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get the most recent growth snapshot for a user."""
        result = self.supabase.table("growth_snapshots")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("recorded_at", desc=True)\
            .limit(1)\
            .execute()
        
        return result.data[0] if result.data else None
    
    def calculate_growth_snapshot(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Calculate and store a new growth snapshot."""
        # Calculate metrics
        total_followers = self._get_total_followers(user_id)
        new_followers_7d = self._calculate_follower_growth(user_id, None, 7)
        new_followers_30d = self._calculate_follower_growth(user_id, None, 30)
        engagement_rate = self._calculate_engagement_rate(user_id)
        top_content = self._identify_top_performing_content(user_id)
        
        snapshot = {
            "user_id": user_id,
            "total_followers": total_followers,
            "new_followers_7d": new_followers_7d,
            "new_followers_30d": new_followers_30d,
            "engagement_rate": engagement_rate,
            "top_performing_content": top_content,
            "recorded_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store snapshot
        result = self.supabase.table("growth_snapshots").insert(snapshot).execute()
        return result.data[0] if result.data else snapshot
    
    def generate_insights(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Generate AI-powered insights from audience data."""
        # Get recent metrics
        metrics_data = self.get_growth_metrics(user_id, days=days)
        platforms = self.get_platforms_metrics(user_id, days=days)
        snapshot = self.get_latest_snapshot(user_id)
        
        # Calculate additional insights
        trends = self._analyze_trends(user_id, days)
        comparisons = self._compare_periods(user_id, days)
        predictions = self._predict_growth(user_id)
        
        # Generate AI insights using Groq
        ai_insights = self._generate_ai_insights(
            metrics_data, platforms, trends, comparisons
        )
        
        return {
            "summary": {
                "total_followers": snapshot.get("total_followers", 0) if snapshot else 0,
                "growth_rate_30d": metrics_data.get("growth_rates", {}).get("30d", 0),
                "engagement_rate": snapshot.get("engagement_rate", 0) if snapshot else 0,
            },
            "trends": trends,
            "comparisons": comparisons,
            "predictions": predictions,
            "platforms": platforms,
            "ai_insights": ai_insights,
            "recommendations": self._generate_recommendations(trends, platforms)
        }
    
    def _calculate_growth_rate(
        self,
        user_id: str,
        platform: Optional[str],
        days: int
    ) -> float:
        """Calculate growth rate percentage over a period."""
        current = self._get_followers_at_date(user_id, platform, 0)
        past = self._get_followers_at_date(user_id, platform, days)
        
        if past == 0:
            return 0.0
        
        return round(((current - past) / past) * 100, 2)
    
    def _get_followers_at_date(
        self,
        user_id: str,
        platform: Optional[str],
        days_ago: int
    ) -> int:
        """Get follower count at a specific date."""
        date = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        query = self.supabase.table("audience_metrics")\
            .select("value")\
            .eq("user_id", user_id)\
            .eq("metric_type", "followers")\
            .lte("recorded_at", date.isoformat())\
            .order("recorded_at", desc=True)\
            .limit(1)
        
        if platform:
            query = query.eq("platform", platform)
        
        result = query.execute()
        return result.data[0].get("value", 0) if result.data else 0
    
    def _get_current_followers(
        self,
        user_id: str,
        platform: str
    ) -> int:
        """Get current follower count for a platform."""
        result = self.supabase.table("audience_metrics")\
            .select("value")\
            .eq("user_id", user_id)\
            .eq("platform", platform)\
            .eq("metric_type", "followers")\
            .order("recorded_at", desc=True)\
            .limit(1)\
            .execute()
        
        return result.data[0].get("value", 0) if result.data else 0
    
    def _get_total_followers(
        self,
        user_id: str
    ) -> int:
        """Get total followers across all platforms."""
        result = self.supabase.rpc(
            "get_total_followers",
            {"p_user_id": user_id}
        ).execute()
        
        # Fallback: sum manually if RPC not available
        if not result.data:
            result = self.supabase.table("audience_metrics")\
                .select("platform, value")\
                .eq("user_id", user_id)\
                .eq("metric_type", "followers")\
                .order("recorded_at", desc=True)\
                .execute()
            
            # Get latest value for each platform
            platforms = {}
            for row in result.data or []:
                platform = row.get("platform")
                if platform not in platforms:
                    platforms[platform] = row.get("value", 0)
            
            return sum(platforms.values())
        
        return result.data or 0
    
    def _get_current_totals(
        self,
        user_id: str
    ) -> Dict[str, int]:
        """Get current totals by platform."""
        result = self.supabase.table("audience_metrics")\
            .select("platform, metric_type, value")\
            .eq("user_id", user_id)\
            .order("recorded_at", desc=True)\
            .execute()
        
        totals = {}
        seen = set()
        
        for row in result.data or []:
            key = (row.get("platform"), row.get("metric_type"))
            if key not in seen:
                totals[key] = row.get("value", 0)
                seen.add(key)
        
        return totals
    
    def _calculate_follower_growth(
        self,
        user_id: str,
        platform: Optional[str],
        days: int
    ) -> int:
        """Calculate absolute follower growth over a period."""
        current = self._get_followers_at_date(user_id, platform, 0)
        past = self._get_followers_at_date(user_id, platform, days)
        return current - past
    
    def _calculate_engagement_rate(
        self,
        user_id: str
    ) -> float:
        """Calculate overall engagement rate."""
        since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        
        result = self.supabase.table("audience_metrics")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("metric_type", "engagement_rate")\
            .gte("recorded_at", since)\
            .execute()
        
        metrics = result.data or []
        if not metrics:
            return 0.0
        
        avg_rate = sum(m.get("value", 0) for m in metrics) / len(metrics)
        return round(avg_rate, 2)
    
    def _identify_top_performing_content(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Identify top performing content based on engagement."""
        # Query content with distribution data
        result = self.supabase.table("content")\
            .select("id, title, created_at, distributions(*)")\
            .eq("user_id", user_id)\
            .gte("created_at", (datetime.now(timezone.utc) - timedelta(days=30)).isoformat())\
            .execute()
        
        content_items = result.data or []
        
        # Calculate engagement score for each piece
        scored_content = []
        for item in content_items:
            distributions = item.get("distributions", [])
            if distributions:
                total_engagement = sum(
                    d.get("metrics", {}).get("likes", 0) + 
                    d.get("metrics", {}).get("comments", 0) + 
                    d.get("metrics", {}).get("shares", 0)
                    for d in distributions if d.get("metrics")
                )
                scored_content.append({
                    "content_id": item.get("id"),
                    "title": item.get("title"),
                    "engagement_score": total_engagement,
                    "created_at": item.get("created_at")
                })
        
        # Sort by engagement score
        scored_content.sort(key=lambda x: x["engagement_score"], reverse=True)
        return scored_content[:limit]
    
    def _analyze_trends(
        self,
        user_id: str,
        days: int
    ) -> Dict[str, Any]:
        """Analyze growth trends."""
        historical = self.get_historical_data(user_id, days=days)
        
        if len(historical) < 7:
            return {"trend": "insufficient_data", "direction": "flat"}
        
        # Calculate week-over-week growth
        weekly_totals = {}
        for metric in historical:
            week = metric.get("recorded_at", "")[:10]  # Group by date
            if week not in weekly_totals:
                weekly_totals[week] = 0
            weekly_totals[week] += metric.get("value", 0)
        
        weeks = sorted(weekly_totals.keys())
        if len(weeks) >= 2:
            recent = weekly_totals[weeks[-1]]
            previous = weekly_totals[weeks[-2]]
            
            if recent > previous * 1.1:
                trend = "accelerating"
                direction = "up"
            elif recent > previous:
                trend = "growing"
                direction = "up"
            elif recent < previous * 0.9:
                trend = "declining"
                direction = "down"
            else:
                trend = "stable"
                direction = "flat"
        else:
            trend = "stable"
            direction = "flat"
        
        return {
            "trend": trend,
            "direction": direction,
            "weekly_data": weekly_totals
        }
    
    def _compare_periods(
        self,
        user_id: str,
        days: int
    ) -> Dict[str, Any]:
        """Compare current period to previous period."""
        current_growth = self._calculate_follower_growth(user_id, None, days)
        previous_growth = self._calculate_follower_growth(user_id, None, days * 2) - current_growth
        
        if previous_growth == 0:
            change_percent = 100 if current_growth > 0 else 0
        else:
            change_percent = ((current_growth - previous_growth) / abs(previous_growth)) * 100
        
        return {
            "current_period_growth": current_growth,
            "previous_period_growth": previous_growth,
            "change_percent": round(change_percent, 2),
            "improved": current_growth > previous_growth
        }
    
    def _predict_growth(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Predict future growth based on historical data."""
        growth_30d = self._calculate_follower_growth(user_id, None, 30)
        growth_7d = self._calculate_follower_growth(user_id, None, 7)
        
        # Simple linear projection
        daily_rate_30d = growth_30d / 30
        daily_rate_7d = growth_7d / 7
        
        # Weight recent data more heavily
        weighted_daily_rate = (daily_rate_7d * 0.7) + (daily_rate_30d * 0.3)
        
        current_followers = self._get_total_followers(user_id)
        
        return {
            "projected_30d": round(weighted_daily_rate * 30),
            "projected_90d": round(weighted_daily_rate * 90),
            "projected_followers_30d": round(current_followers + (weighted_daily_rate * 30)),
            "growth_rate": round(weighted_daily_rate, 2),
            "confidence": "medium" if abs(daily_rate_7d - daily_rate_30d) < 10 else "low"
        }
    
    def _generate_ai_insights(
        self,
        metrics_data: Dict[str, Any],
        platforms: List[Dict[str, Any]],
        trends: Dict[str, Any],
        comparisons: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate AI-powered insights using Groq."""
        try:
            # Build prompt for insights
            prompt = f"""Analyze the following audience growth data and provide insights:

Growth Rates:
- 7 days: {metrics_data.get('growth_rates', {}).get('7d', 0)}%
- 30 days: {metrics_data.get('growth_rates', {}).get('30d', 0)}%
- 90 days: {metrics_data.get('growth_rates', {}).get('90d', 0)}%

Platforms: {', '.join([p.get('platform', 'unknown') for p in platforms])}

Trend: {trends.get('trend', 'stable')}
Direction: {trends.get('direction', 'flat')}

Period Comparison:
- Current: {comparisons.get('current_period_growth', 0)} new followers
- Previous: {comparisons.get('previous_period_growth', 0)} new followers
- Change: {comparisons.get('change_percent', 0)}%

Provide a brief summary (2-3 sentences) highlighting the key insight and one actionable recommendation."""
            
            # Use Groq for insights (simplified - return placeholder for now)
            # In production, this would call the actual AI service
            return {
                "summary": f"Your audience is {trends.get('trend', 'stable')} with a {metrics_data.get('growth_rates', {}).get('30d', 0)}% growth rate over the last 30 days.",
                "key_finding": f"Period-over-period growth has {'improved' if comparisons.get('improved') else 'declined'} by {abs(comparisons.get('change_percent', 0))}%.",
                "recommendation": "Focus on consistent posting and engagement to maintain momentum."
            }
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {
                "summary": "Unable to generate AI insights at this time.",
                "key_finding": "",
                "recommendation": ""
            }
    
    def _generate_recommendations(
        self,
        trends: Dict[str, Any],
        platforms: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        trend = trends.get("trend", "stable")
        
        if trend == "declining":
            recommendations.append("Your audience growth is declining. Consider increasing posting frequency or diversifying content types.")
        elif trend == "stable":
            recommendations.append("Your growth is stable. Experiment with new content formats to accelerate growth.")
        elif trend == "accelerating":
            recommendations.append("Great momentum! Double down on your current content strategy.")
        
        # Platform-specific recommendations
        for platform in platforms:
            growth_30d = platform.get("growth_30d", 0)
            if growth_30d < 10:
                recommendations.append(f"{platform.get('platform', 'Unknown')} growth is slow. Review your posting strategy for this platform.")
        
        return recommendations[:3]  # Limit to top 3


# Global service instance
audience_service = AudienceService()

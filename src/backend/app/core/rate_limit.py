"""
Rate limiting and usage tracking middleware.
"""
import time
from typing import Dict, Optional, Literal
from datetime import datetime
from functools import wraps
from collections import defaultdict

from fastapi import Request, HTTPException, status, Depends
from pydantic import BaseModel
from uuid import UUID

from app.core.supabase import get_supabase_client
from app.core.config import get_settings

settings = get_settings()


# In-memory rate limit storage: {user_id: [(timestamp, count), ...]}
# Note: For production, consider using Redis
_rate_limit_store: Dict[str, list] = defaultdict(list)

# Subscription tier limits
SUBSCRIPTION_LIMITS = {
    "free": 10,
    "pro": 100,
    "agency": float("inf"),  # Unlimited
}

class RateLimitConfig:
    """Rate limiting configuration."""
    requests: int = settings.RATE_LIMIT_REQUESTS
    window: int = settings.RATE_LIMIT_WINDOW  # seconds


class UsageStats(BaseModel):
    """User usage statistics model."""
    monthly_usage_count: int
    monthly_usage_limit: int
    remaining: int
    reset_at: Optional[datetime] = None
    subscription_tier: str = "free"


def get_user_subscription_tier(user_id: str) -> str:
    """Get user's subscription tier from database."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("profiles").select(
            "subscription_tier"
        ).eq("id", user_id).single().execute()
        
        if result.data:
            return result.data.get("subscription_tier", "free")
        return "free"
    except Exception:
        return "free"


def get_subscription_limit(tier: str) -> int:
    """Get usage limit for a subscription tier."""
    return SUBSCRIPTION_LIMITS.get(tier.lower(), SUBSCRIPTION_LIMITS["free"])


def check_monthly_reset(user_id: str) -> bool:
    """Check if monthly usage should be reset (first day of month)."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("profiles").select(
            "updated_at, monthly_usage_count"
        ).eq("id", user_id).single().execute()
        
        if not result.data:
            return False
        
        last_updated = result.data.get("updated_at")
        if not last_updated:
            return False
        
        # Parse last updated timestamp
        try:
            last_date = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return False
        
        now = datetime.now(datetime.now().astimezone().tzinfo)
        
        # Check if we're in a new month compared to last update
        if last_date.month != now.month or last_date.year != now.year:
            # Reset usage count
            supabase.table("profiles").update({
                "monthly_usage_count": 0,
                "updated_at": now.isoformat()
            }).eq("id", user_id).execute()
            return True
        
        return False
    except Exception:
        return False


def check_and_increment_usage(user_id: str) -> UsageStats:
    """
    Check user's monthly usage and increment if under limit.
    Returns current usage stats.
    """
    supabase = get_supabase_client()
    
    try:
        # Check for monthly reset first
        check_monthly_reset(user_id)
        
        # Get user's profile with usage data
        result = supabase.table("profiles").select(
            "monthly_usage_count, monthly_usage_limit, subscription_tier"
        ).eq("id", user_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found",
            )
        
        profile = result.data
        subscription_tier = profile.get("subscription_tier", "free")
        
        # Get the limit based on subscription tier
        tier_limit = get_subscription_limit(subscription_tier)
        
        usage_count = profile.get("monthly_usage_count", 0)
        # Use tier limit if monthly_usage_limit is not set or is default
        usage_limit = profile.get("monthly_usage_limit", tier_limit)
        
        # Check if under limit (unlimited tiers have float('inf'))
        if usage_count >= usage_limit and usage_limit != float("inf"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Monthly limit reached. Upgrade to Pro.",
            )
        
        # Increment usage count
        new_count = usage_count + 1
        supabase.table("profiles").update({
            "monthly_usage_count": new_count,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", user_id).execute()
        
        # Log usage
        log_usage_event(user_id, "content_generation", 1)
        
        remaining = float("inf") if usage_limit == float("inf") else max(0, usage_limit - new_count)
        
        return UsageStats(
            monthly_usage_count=new_count,
            monthly_usage_limit=int(usage_limit) if usage_limit != float("inf") else -1,  # -1 indicates unlimited
            remaining=int(remaining) if remaining != float("inf") else -1,
            subscription_tier=subscription_tier,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check usage: {str(e)}",
        )


def log_usage_event(user_id: str, event_type: str, tokens_used: Optional[int] = None):
    """Log a usage event to the usage_logs table."""
    supabase = get_supabase_client()
    
    try:
        log_data = {
            "user_id": user_id,
            "event_type": event_type,
            "tokens_used": tokens_used,
            "created_at": datetime.utcnow().isoformat(),
        }
        supabase.table("usage_logs").insert(log_data).execute()
    except Exception as e:
        # Don't fail the request if logging fails
        print(f"Failed to log usage event: {e}")


def get_user_usage_stats(user_id: str) -> UsageStats:
    """Get current usage statistics for a user."""
    supabase = get_supabase_client()
    
    try:
        # Check for monthly reset
        check_monthly_reset(user_id)
        
        result = supabase.table("profiles").select(
            "monthly_usage_count, monthly_usage_limit, subscription_tier"
        ).eq("id", user_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found",
            )
        
        profile = result.data
        subscription_tier = profile.get("subscription_tier", "free")
        usage_count = profile.get("monthly_usage_count", 0)
        
        # Get the limit based on subscription tier
        tier_limit = get_subscription_limit(subscription_tier)
        usage_limit = profile.get("monthly_usage_limit", tier_limit)
        
        # Handle unlimited
        if usage_limit == float("inf"):
            remaining = -1  # -1 indicates unlimited
            usage_limit_display = -1
        else:
            remaining = max(0, usage_limit - usage_count)
            usage_limit_display = usage_limit
        
        return UsageStats(
            monthly_usage_count=usage_count,
            monthly_usage_limit=usage_limit_display,
            remaining=remaining,
            subscription_tier=subscription_tier,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage stats: {str(e)}",
        )


def get_usage_history(user_id: str, limit: int = 100):
    """Get usage history for a user."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("usage_logs").select("*").eq(
            "user_id", user_id
        ).order("created_at", desc=True).limit(limit).execute()
        
        return result.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage history: {str(e)}",
        )


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, requests: int = 100, window: int = 3600):
        self.requests = requests
        self.window = window
        self._storage: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for given key."""
        now = time.time()
        
        # Clean old entries
        self._storage[key] = [
            timestamp for timestamp in self._storage[key]
            if now - timestamp < self.window
        ]
        
        # Check limit
        if len(self._storage[key]) >= self.requests:
            return False
        
        # Record request
        self._storage[key].append(now)
        return True
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests for key."""
        now = time.time()
        
        # Clean old entries
        self._storage[key] = [
            timestamp for timestamp in self._storage[key]
            if now - timestamp < self.window
        ]
        
        return max(0, self.requests - len(self._storage[key]))


# Global rate limiter instance
rate_limiter = RateLimiter(
    requests=settings.RATE_LIMIT_REQUESTS,
    window=settings.RATE_LIMIT_WINDOW
)


def rate_limit_dependency(request: Request):
    """Dependency for applying rate limiting to endpoints."""
    # Use IP address + user ID (if authenticated) as key
    client_ip = request.client.host if request.client else "unknown"
    
    # Try to get user ID from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)
    key = f"{client_ip}:{user_id}" if user_id else client_ip
    
    if not rate_limiter.is_allowed(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)}
        )
    
    return True


def check_subscription_limit(user_id: str, action: str = "content_creation"):
    """
    Check if user has available usage quota before allowing action.
    Raises HTTPException if limit exceeded.
    
    Args:
        user_id: The user's ID
        action: The action being performed (for logging)
    """
    stats = get_user_usage_stats(user_id)
    
    # Check if limit reached (-1 means unlimited)
    if stats.remaining == 0:
        tier = stats.subscription_tier
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly limit reached. Upgrade to Pro.",
            headers={
                "X-Subscription-Tier": tier,
                "X-Usage-Count": str(stats.monthly_usage_count),
                "X-Usage-Limit": str(stats.monthly_usage_limit) if stats.monthly_usage_limit > 0 else "unlimited",
            }
        )
    
    return stats


def enforce_subscription_limit(request: Request):
    """
    FastAPI dependency to enforce subscription limits on endpoints.
    Use this as a dependency for content creation and asset generation endpoints.
    """
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.replace("Bearer ", "")
    supabase = get_supabase_client()
    
    try:
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = str(user.user.id)
        return check_subscription_limit(user_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check subscription: {str(e)}",
        )


class UsageTrackingMiddleware:
    """
    Middleware to track API usage per user.
    Checks monthly limits before processing requests.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """ASGI middleware interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Only track certain paths
        path = scope.get("path", "")
        if not self._should_track(path):
            await self.app(scope, receive, send)
            return
        
        # Get user from authorization header
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode()
        
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                from app.core.supabase import get_supabase_client
                supabase = get_supabase_client()
                user = supabase.auth.get_user(token)
                
                if user and user.user:
                    user_id = str(user.user.id)
                    
                    # Check usage before proceeding
                    try:
                        check_and_increment_usage(user_id)
                    except HTTPException as e:
                        if e.status_code == 429:
                            # Return 429 response
                            await self._send_error(scope, receive, send, e)
                            return
            except Exception:
                pass  # Continue if auth fails
        
        await self.app(scope, receive, send)
    
    def _should_track(self, path: str) -> bool:
        """Determine if a path should be tracked for usage."""
        # Track content generation endpoints
        tracked_paths = [
            "/api/v1/content",
            "/api/v1/content/",
        ]
        return any(path.startswith(tp) for tp in tracked_paths)
    
    async def _send_error(self, scope, receive, send, error: HTTPException):
        """Send HTTP error response."""
        from starlette.responses import JSONResponse
        response = JSONResponse(
            content={"detail": error.detail},
            status_code=error.status_code
        )
        await response(scope, receive, send)

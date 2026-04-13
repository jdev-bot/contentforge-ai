"""
Rate limit headers middleware.
Adds X-RateLimit headers to all API responses.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.rate_limit import get_user_usage_stats
from app.core.supabase import get_supabase_client


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add rate limit headers to API responses.
    Provides visibility into API usage limits.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Process the request
        response = await call_next(request)
        
        # Only add headers to API routes
        path = request.url.path
        if not path.startswith("/api/"):
            return response
        
        # Try to get user from auth header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                supabase = get_supabase_client()
                user = supabase.auth.get_user(token)
                
                if user and user.user:
                    user_id = str(user.user.id)
                    stats = get_user_usage_stats(user_id)
                    
                    # Add rate limit headers
                    response.headers["X-RateLimit-Limit"] = str(stats.monthly_usage_limit) if stats.monthly_usage_limit > 0 else "unlimited"
                    response.headers["X-RateLimit-Remaining"] = str(stats.remaining) if stats.remaining >= 0 else "unlimited"
                    response.headers["X-RateLimit-Used"] = str(stats.monthly_usage_count)
                    response.headers["X-Subscription-Tier"] = stats.subscription_tier
                    
                    # Add warning header if approaching limit
                    if stats.monthly_usage_limit > 0:
                        usage_pct = (stats.monthly_usage_count / stats.monthly_usage_limit) * 100
                        if usage_pct >= 80:
                            response.headers["X-RateLimit-Warning"] = f"{usage_pct:.0f}%"
            except Exception:
                pass  # Silently fail if auth/user lookup fails
        
        return response

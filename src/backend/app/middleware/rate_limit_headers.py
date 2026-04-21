"""
Rate limit headers middleware.
Adds X-RateLimit headers to all API responses.

PERFORMANCE FIX: Extracts user_id from JWT locally instead of calling
supabase.auth.get_user() on every request. The full auth validation
happens in the route handler — this middleware only needs the user_id
to look up usage stats.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.rate_limit import get_user_usage_stats


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add rate limit headers to API responses.
    Provides visibility into API usage limits.
    """

    async def dispatch(self, request: Request, call_next):
        # Process the request first — auth dependency may set user_id in context
        response = await call_next(request)

        # Only add headers to API routes
        path = request.url.path
        if not path.startswith("/api/"):
            return response

        # Try to get user_id — prefer request context (set by auth dependency),
        # fall back to JWT decode (no network call)
        user_id = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # First: check if the auth dependency already set user_id
            from app.core.request_context import get_request_user_id, decode_jwt_subject
            user_id = get_request_user_id(request)

            if not user_id:
                token = auth_header.replace("Bearer ", "")
                user_id = decode_jwt_subject(token)

        if user_id:
            try:
                stats = get_user_usage_stats(user_id)

                # Add rate limit headers
                response.headers["X-RateLimit-Limit"] = (
                    str(stats.monthly_usage_limit)
                    if stats.monthly_usage_limit > 0
                    else "unlimited"
                )
                response.headers["X-RateLimit-Remaining"] = (
                    str(stats.remaining) if stats.remaining >= 0 else "unlimited"
                )
                response.headers["X-RateLimit-Used"] = str(
                    stats.monthly_usage_count
                )
                response.headers["X-Subscription-Tier"] = stats.subscription_tier

                # Add warning header if approaching limit
                if stats.monthly_usage_limit > 0:
                    usage_pct = (
                        stats.monthly_usage_count / stats.monthly_usage_limit
                    ) * 100
                    if usage_pct >= 80:
                        response.headers["X-RateLimit-Warning"] = (
                            f"{usage_pct:.0f}%"
                        )
            except Exception:
                pass  # Silently fail if usage lookup fails

        return response
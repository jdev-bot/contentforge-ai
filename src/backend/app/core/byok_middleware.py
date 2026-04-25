"""
BYOK (Bring Your Own Key) middleware.

Resolves per-user API keys for every authenticated API request.
There is no platform fallback — AI features only work when the user
has configured their own API key.

This middleware runs early in the request lifecycle, before route handlers.
It extracts the user ID from the JWT and looks up their stored key.
The ai_service reads the context variable, so no changes to existing
service code or router call sites are needed.
"""

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.request_context import decode_jwt_subject, is_jwt_expired
from app.services.llm_service import create_llm_service_for_user, get_user_llm_config
from app.services.ai_service import set_user_llm_service, reset_user_llm_service

logger = logging.getLogger(__name__)

# Paths that don't need BYOK resolution
_SKIP_PREFIXES = ("/api/v1/health", "/docs", "/openapi", "/redoc", "/")


class BYOKMiddleware(BaseHTTPMiddleware):
    """Resolve per-user LLM API keys for each request.

    When a user has a valid API key, it's set in the request context.
    When they don't, the context remains None — AI calls will raise
    NoAPIKeyConfigured with a clear message directing the user to Settings.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip non-API and health/docs routes
        if not path.startswith("/api/") or any(path.startswith(p) for p in _SKIP_PREFIXES):
            return await call_next(request)

        token = None
        user_id = None

        # Extract user ID from JWT without full auth validation
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            jwt_token = auth_header[7:]
            if not is_jwt_expired(jwt_token):
                user_id = decode_jwt_subject(jwt_token)

        if user_id:
            try:
                user_config = await get_user_llm_config(user_id)
                if user_config:
                    svc = create_llm_service_for_user(
                        provider=user_config.get("provider"),
                        api_key=user_config.get("api_key"),
                        base_url=user_config.get("base_url"),
                        model=user_config.get("model"),
                    )
                    token = set_user_llm_service(svc)
                    logger.debug(
                        "BYOK: user %s → provider=%s", user_id, user_config.get("provider")
                    )
                # else: user has no key configured — AI calls will raise NoAPIKeyConfigured
            except Exception as exc:
                logger.warning("BYOK: error resolving key for %s: %s", user_id, exc)

        try:
            response = await call_next(request)
        finally:
            if token is not None:
                reset_user_llm_service(token)

        return response
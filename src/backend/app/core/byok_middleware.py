"""
BYOK (Bring Your Own Key) middleware.

Resolves per-user API keys for every authenticated API request.
There is no platform fallback — AI features only work when the user
has configured their own API key.

This middleware runs early in the request lifecycle, before route handlers.
It extracts the user ID from the JWT and looks up their stored key.
The ai_service reads the context variable, so no changes to existing
service code or router call sites are needed.

IMPORTANT: This middleware uses a pure ASGI implementation instead of
BaseHTTPMiddleware. Starlette's BaseHTTPMiddleware runs call_next() in
a separate anyio task, which breaks ContextVar propagation — values set
in the middleware body (via set_user_llm_service) are NOT visible inside
route handlers. The pure ASGI approach keeps everything in the same
async context, preserving ContextVar values correctly.
"""

import logging

from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.request_context import decode_jwt_subject, is_jwt_expired
from app.services.llm_service import create_llm_service_for_user, get_user_llm_config
from app.services.ai_service import set_user_llm_service, reset_user_llm_service

logger = logging.getLogger(__name__)

# Paths that don't need BYOK resolution
_SKIP_PREFIXES = ("/api/v1/health", "/docs", "/openapi", "/redoc", "/")


class BYOKMiddleware:
    """Resolve per-user LLM API keys for each request.

    When a user has a valid API key, it's set in the request context.
    When they don't, the context remains None — AI calls will raise
    NoAPIKeyConfigured with a clear message directing the user to Settings.

    Uses a pure ASGI implementation to preserve ContextVar propagation.
    BaseHTTPMiddleware's call_next() runs in a separate anyio task,
    which breaks ContextVar — values set before call_next are invisible
    to route handlers.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        # Skip non-API and health/docs routes
        if not path.startswith("/api/") or any(path.startswith(p) for p in _SKIP_PREFIXES):
            await self.app(scope, receive, send)
            return

        # Extract user ID from JWT without full auth validation
        user_id = None
        headers = dict(
            (k.decode("latin-1").lower(), v.decode("latin-1"))
            for k, v in scope.get("headers", [])
        )
        auth_header = headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            jwt_token = auth_header[7:]
            if not is_jwt_expired(jwt_token):
                user_id = decode_jwt_subject(jwt_token)

        ctx_token = None
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
                    ctx_token = set_user_llm_service(svc)
                    logger.debug(
                        "BYOK: user %s → provider=%s", user_id, user_config.get("provider")
                    )
                # else: user has no key configured — AI calls will raise NoAPIKeyConfigured
            except Exception as exc:
                logger.warning("BYOK: error resolving key for %s: %s", user_id, exc)

        try:
            await self.app(scope, receive, send)
        finally:
            if ctx_token is not None:
                reset_user_llm_service(ctx_token)

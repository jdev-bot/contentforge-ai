"""
BYOK (Bring Your Own Key) middleware.

Resolves per-user API keys for every authenticated API request.
There is no platform fallback — AI features only work when the user
has configured their own API key.

This middleware runs early in the request lifecycle, before route handlers.
It extracts the user ID from the JWT and looks up their stored key.

IMPORTANT: This middleware uses a pure ASGI implementation instead of
BaseHTTPMiddleware. Starlette's BaseHTTPMiddleware runs call_next() in
a separate anyio task, which breaks ContextVar propagation — values set
in the middleware body (via set_user_llm_service) are NOT visible inside
route handlers.

However, since other BaseHTTPMiddleware instances in the stack may still
break ContextVar propagation, we ALSO store the LLM service in:
1. scope["state"]["_byok_llm_service"] — survives across task boundaries
2. Module-level _request_llm_services dict — keyed by request ID

The ai_service get_active_llm_service() function checks all three locations.
"""

import logging

from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.request_context import decode_jwt_subject, is_jwt_expired
from app.services.llm_service import create_llm_service_for_user, get_user_llm_config
from app.services.ai_service import (
    set_user_llm_service, reset_user_llm_service,
    set_request_llm_service, clear_request_llm_service,
)

logger = logging.getLogger(__name__)

# Paths that don't need BYOK resolution
_SKIP_PREFIXES = ("/api/v1/health", "/docs", "/openapi", "/redoc", "/")


class BYOKMiddleware:
    """Resolve per-user LLM API keys for each request.

    When a user has a valid API key, it's set in:
    1. ContextVar (may not propagate past BaseHTTPMiddleware)
    2. scope["state"]["_byok_llm_service"] (survives across task boundaries)
    3. Module-level _request_llm_services dict (keyed by ASGI request ID)

    When they don't have a key, AI calls will raise NoAPIKeyConfigured
    with a clear message directing the user to Settings.
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
        request_id = None
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

                    # 1. Set ContextVar (may not survive BaseHTTPMiddleware)
                    ctx_token = set_user_llm_service(svc)

                    # 2. Store in scope state (survives across task boundaries)
                    if "state" not in scope:
                        scope["state"] = {}
                    scope["state"]["_byok_llm_service"] = svc

                    # 3. Store in module-level dict keyed by request ID
                    request_id = headers.get("x-request-id", "") or str(id(scope))
                    set_request_llm_service(request_id, svc)

                    logger.debug(
                        "BYOK: user %s → provider=%s (request_id=%s)",
                        user_id, user_config.get("provider"), request_id,
                    )
                # else: user has no key configured — AI calls will raise NoAPIKeyConfigured
            except Exception as exc:
                logger.warning("BYOK: error resolving key for %s: %s", user_id, exc)

        try:
            await self.app(scope, receive, send)
        finally:
            if ctx_token is not None:
                reset_user_llm_service(ctx_token)
            if request_id is not None:
                clear_request_llm_service(request_id)
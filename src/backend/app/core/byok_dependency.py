"""
BYOK (Bring Your Own Key) dependency for FastAPI.

Resolves per-user API keys for AI requests.
There is no platform fallback — AI features only work when the user
has configured their own API key.

This is a FastAPI Depends() that runs in the same async context as
the route handler, ensuring ContextVar values are visible.

IMPORTANT: The BYOKMiddleware also sets the ContextVar, but Starlette's
BaseHTTPMiddleware runs call_next() in a separate anyio task, which
breaks ContextVar propagation. This dependency serves as a reliable
fallback that re-resolves the LLM service if the ContextVar is empty.
"""

import logging
from typing import Optional

from fastapi import Depends, Request

from app.core.request_context import decode_jwt_subject, is_jwt_expired
from app.services.llm_service import create_llm_service_for_user, get_user_llm_config
from app.services.ai_service import set_user_llm_service, reset_user_llm_service, _user_llm_service

logger = logging.getLogger(__name__)


async def ensure_byok_context(request: Request):
    """FastAPI dependency that ensures BYOK context is set for AI endpoints.

    Checks if the ContextVar is already set (by middleware). If not,
    resolves the user's API key and sets it. This handles the case where
    BaseHTTPMiddleware breaks ContextVar propagation.
    """
    # Check if ContextVar is already set (middleware set it successfully)
    existing_svc = _user_llm_service.get()
    if existing_svc is not None:
        return

    # Check if scope state has it (pure ASGI middleware fallback)
    scope_state = request.scope.get("state", {})
    fallback_svc = scope_state.get("_byok_llm_service") if isinstance(scope_state, dict) else None
    if fallback_svc is not None:
        # Re-set the ContextVar from scope state — this works because
        # we're now running inside the route handler's async context
        ctx_token = set_user_llm_service(fallback_svc)
        request.state._byok_ctx_token = ctx_token
        return

    # Neither ContextVar nor scope state has it — resolve from JWT directly
    auth_header = request.headers.get("authorization", "")
    user_id = None

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
                ctx_token = set_user_llm_service(svc)
                request.state._byok_ctx_token = ctx_token
                logger.debug(
                    "BYOK dependency: user %s → provider=%s (resolved from JWT)",
                    user_id, user_config.get("provider")
                )
        except Exception as exc:
            logger.warning("BYOK dependency: error resolving key for %s: %s", user_id, exc)


async def cleanup_byok_context(request: Request):
    """Clean up BYOK context after the response.

    Resets the ContextVar to prevent leaking between requests.
    """
    ctx_token = getattr(request.state, "_byok_ctx_token", None)
    if ctx_token is not None:
        reset_user_llm_service(ctx_token)
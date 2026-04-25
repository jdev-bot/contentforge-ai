"""
Backward-compatible Groq service shim with BYOK support.

All functionality is provided by :mod:`app.services.llm_service`.
This module re-exports the singleton so that existing imports like:

    from app.services.groq_service import groq_service

continue to work without changes.

BYOK: When a per-user LLM service is set via ``set_user_llm_service()``,
all calls route through that user's own API key instead of the platform default.
New code should import from ``llm_service`` directly.
"""

import contextvars
from typing import Optional

from app.services.llm_service import LLMService, llm_service  # noqa: F401 — re-export

# Context variable for per-request user LLM service
_user_llm_service: contextvars.ContextVar[Optional[LLMService]] = contextvars.ContextVar(
    "_user_llm_service", default=None
)


def set_user_llm_service(svc: Optional[LLMService]) -> contextvars.Token:
    """Set the per-user LLM service for this request context.

    Call this in a router dependency/middleware after resolving the user's API key.
    Pass None to reset to platform default.
    """
    return _user_llm_service.set(svc)


def reset_user_llm_service(token: contextvars.Token) -> None:
    """Reset the per-user LLM service after a request completes."""
    _user_llm_service.reset(token)


def get_active_llm_service() -> LLMService:
    """Return the currently active LLM service (per-user or platform default)."""
    return _user_llm_service.get() or llm_service


class GroqService:
    """Backward-compatible shim — delegates to the active LLM service.

    If a per-user service is set for this request context, it is used;
    otherwise falls back to the platform-default singleton.
    Deprecated: use ``from app.services.llm_service import llm_service`` instead.
    """

    @property
    def _svc(self) -> LLMService:
        return get_active_llm_service()

    # Mirror attributes for any code that reads them directly
    @property
    def api_key(self) -> str:
        return self._svc.api_key

    @property
    def model(self) -> str:
        return self._svc.model

    @property
    def headers(self) -> dict:
        return self._svc.headers

    # --- delegate every public method ---

    async def generate_content(self, *a, **kw):
        return await self._svc.generate_content(*a, **kw)

    async def generate_social_posts(self, *a, **kw):
        return await self._svc.generate_social_posts(*a, **kw)

    async def generate_thread(self, *a, **kw):
        return await self._svc.generate_thread(*a, **kw)

    async def generate_newsletter(self, *a, **kw):
        return await self._svc.generate_newsletter(*a, **kw)

    async def generate_short_video_script(self, *a, **kw):
        return await self._svc.generate_short_video_script(*a, **kw)

    async def rewrite_content(self, *a, **kw):
        return await self._svc.rewrite_content(*a, **kw)

    async def expand_content(self, *a, **kw):
        return await self._svc.expand_content(*a, **kw)

    async def condense_content(self, *a, **kw):
        return await self._svc.condense_content(*a, **kw)

    async def optimize_content(self, *a, **kw):
        return await self._svc.optimize_content(*a, **kw)


# Legacy singleton — keeps `from app.services.groq_service import groq_service` working
groq_service = llm_service
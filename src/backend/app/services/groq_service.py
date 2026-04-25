"""
Backward-compatible Groq service shim with BYOK support.

All functionality is provided by :mod:`app.services.llm_service`.
This module re-exports the singleton so that existing imports like:

    from app.services.groq_service import groq_service

continue to work without changes.

BYOK: When a per-user LLM service is set via ``set_user_llm_service()``,
all calls route through that user's own API key. When no user key is set,
calls raise a clear error — there is no platform fallback key.
"""

import contextvars
import logging
from typing import Optional

from app.services.llm_service import LLMService, llm_service  # noqa: F401 — re-export

logger = logging.getLogger(__name__)

# Context variable for per-request user LLM service
_user_llm_service: contextvars.ContextVar[Optional[LLMService]] = contextvars.ContextVar(
    "_user_llm_service", default=None
)


class NoAPIKeyConfigured(Exception):
    """Raised when no user API key is configured and there's no platform fallback."""
    pass


def set_user_llm_service(svc: Optional[LLMService]) -> contextvars.Token:
    """Set the per-user LLM service for this request context.

    Call this in middleware after resolving the user's API key.
    Pass None to indicate no key is available (calls will raise NoAPIKeyConfigured).
    """
    return _user_llm_service.set(svc)


def reset_user_llm_service(token: contextvars.Token) -> None:
    """Reset the per-user LLM service after a request completes."""
    _user_llm_service.reset(token)


def get_active_llm_service() -> LLMService:
    """Return the currently active LLM service.

    Returns the per-user service if set. Raises NoAPIKeyConfigured
    if no user key is available — there is no platform fallback.
    """
    svc = _user_llm_service.get()
    if svc is not None:
        return svc
    # No user key configured — raise a descriptive error
    raise NoAPIKeyConfigured(
        "No API key configured. Please add your API key in Settings → API Keys. "
        "ContentForge requires your own provider key (Google AI Studio, Groq, etc.) to use AI features."
    )


class GroqService:
    """Backward-compatible shim — delegates to the active LLM service.

    Raises NoAPIKeyConfigured when no user API key is set for the request.
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
        return self._svc.condense_content(*a, **kw)

    async def optimize_content(self, *a, **kw):
        return await self._svc.optimize_content(*a, **kw)


# Legacy singleton — keeps `from app.services.groq_service import groq_service` working
# Note: direct use of groq_service without a user key will raise NoAPIKeyConfigured
groq_service = llm_service
"""
Backward-compatible Groq service shim.

All functionality is now provided by :mod:`app.services.llm_service`.
This module re-exports the singleton so that existing imports like:

    from app.services.groq_service import groq_service

continue to work without changes.  New code should import from
``llm_service`` directly.
"""

from app.services.llm_service import llm_service  # noqa: F401 — re-export


class GroqService:
    """Backward-compatible shim — delegates to LLMService.

    Deprecated: use ``from app.services.llm_service import llm_service`` instead.
    """

    def __init__(self):
        self._svc = llm_service
        # Mirror attributes for any code that reads them directly
        self.api_key = llm_service.api_key
        self.model = llm_service.model
        self.headers = llm_service.headers

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
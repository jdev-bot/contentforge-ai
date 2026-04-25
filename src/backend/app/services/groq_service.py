"""
Backward-compatible re-export module.

All AI service functionality has been moved to :mod:`app.services.ai_service`.
This module re-exports names so that existing imports continue to work:

    from app.services.groq_service import groq_service, GroqService, NoAPIKeyConfigured
    from app.services.groq_service import set_user_llm_service, reset_user_llm_service, get_active_llm_service

New code should import from :mod:`app.services.ai_service` directly:

    from app.services.ai_service import ai_service, AIService, NoAPIKeyConfigured
"""

from app.services.ai_service import (  # noqa: F401
    AIService,
    GroqService,
    NoAPIKeyConfigured,
    ai_service,
    get_active_llm_service,
    groq_service,
    llm_service,
    reset_user_llm_service,
    set_user_llm_service,
)
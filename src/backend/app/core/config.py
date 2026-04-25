"""
Application configuration using Pydantic Settings.
"""

import json
import logging
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = Field(default="ContentForge AI", alias="APP_NAME")
    APP_ENV: str = Field(default="development", alias="APP_ENV")
    DEBUG: bool = Field(default=False, alias="DEBUG")

    # Security
    SECRET_KEY: str = Field(alias="SECRET_KEY")
    ENCRYPTION_KEY: Optional[str] = Field(default=None, alias="ENCRYPTION_KEY")  # for encrypting user API keys at rest
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24 * 7, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )  # 7 days

    # Supabase
    SUPABASE_URL: str = Field(alias="SUPABASE_URL")
    SUPABASE_KEY: str = Field(alias="SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(
        default=None, alias="SUPABASE_SERVICE_ROLE_KEY"
    )

    # AI / LLM Provider — supports google, groq, cerebras, openrouter, or custom
    # New unified config (preferred)
    AI_PROVIDER: str = Field(default="google", alias="AI_PROVIDER")
    AI_API_KEY: Optional[str] = Field(default=None, alias="AI_API_KEY")
    AI_BASE_URL: Optional[str] = Field(default=None, alias="AI_BASE_URL")
    AI_MODEL: Optional[str] = Field(default=None, alias="AI_MODEL")

    # Legacy Groq config — still supported as fallbacks
    GROQ_API_KEY: str = Field(default="", alias="GROQ_API_KEY")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")

    # App URL (used for OpenRouter attribution header)
    APP_URL: str = Field(
        default="https://contentforge-ai-api.onrender.com", alias="APP_URL"
    )

    # Resend
    RESEND_API_KEY: Optional[str] = Field(default=None, alias="RESEND_API_KEY")

    # SMTP (Fallback)
    SMTP_HOST: Optional[str] = Field(default=None, alias="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, alias="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, alias="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")

    # Redis (for Celery)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, alias="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(
        default=None, alias="STRIPE_WEBHOOK_SECRET"
    )

    # CORS — accepts JSON array ("[\"https://...\"]") or comma-separated string ("https://a,https://b")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"], alias="CORS_ORIGINS"
    )

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, alias="RATE_LIMIT_WINDOW")  # 1 hour

    # SSO / OIDC Providers
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(
        default=None, alias="GOOGLE_CLIENT_SECRET"
    )
    MICROSOFT_CLIENT_ID: Optional[str] = Field(
        default=None, alias="MICROSOFT_CLIENT_ID"
    )
    MICROSOFT_CLIENT_SECRET: Optional[str] = Field(
        default=None, alias="MICROSOFT_CLIENT_SECRET"
    )
    OKTA_CLIENT_ID: Optional[str] = Field(default=None, alias="OKTA_CLIENT_ID")
    OKTA_CLIENT_SECRET: Optional[str] = Field(default=None, alias="OKTA_CLIENT_SECRET")
    OKTA_DOMAIN: Optional[str] = Field(default=None, alias="OKTA_DOMAIN")
    SSO_BASE_URL: str = Field(default="http://localhost:3000", alias="SSO_BASE_URL")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from env var — supports JSON array or comma-separated string."""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return ["http://localhost:3000"]
            # Try JSON parse first (e.g. '["https://example.com"]')
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return [parsed]
            except (json.JSONDecodeError, TypeError):
                pass
            # Fall back to comma-separated (e.g. "https://a.com,https://b.com")
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return [v]

    def model_post_init(self, __context):
        """Resolve AI_API_KEY / AI_MODEL from legacy GROQ_* vars when not set."""
        # If AI_API_KEY is not set but GROQ_API_KEY is, fall back
        if not self.AI_API_KEY and self.GROQ_API_KEY:
            self.AI_API_KEY = self.GROQ_API_KEY
        # If AI_MODEL is not set but GROQ_MODEL is (and provider is groq), fall back
        if not self.AI_MODEL and self.AI_PROVIDER == "groq":
            self.AI_MODEL = self.GROQ_MODEL

    class Config:
        env_file = ".env"
        case_sensitive = True
        populate_by_name = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
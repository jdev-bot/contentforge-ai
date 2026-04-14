"""
Application configuration using Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = Field(default="ContentForge AI", alias="APP_NAME")
    APP_ENV: str = Field(default="development", alias="APP_ENV")
    DEBUG: bool = Field(default=False, alias="DEBUG")

    # Security
    SECRET_KEY: str = Field(alias="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24 * 7, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )  # 7 days

    # Supabase
    SUPABASE_URL: str = Field(alias="SUPABASE_URL")
    SUPABASE_KEY: str = Field(alias="SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(
        default=None, alias="SUPABASE_SERVICE_ROLE_KEY"
    )

    # Groq
    GROQ_API_KEY: str = Field(alias="GROQ_API_KEY")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")

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

    # CORS
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

    class Config:
        env_file = ".env"
        case_sensitive = True
        populate_by_name = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

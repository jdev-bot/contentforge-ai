"""
Tests for BYOK API keys router and LLM service per-user resolution.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.core.encryption import encrypt, decrypt, mask_key


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    """Ensure required env vars for app startup."""
    monkeypatch.setenv("ENCRYPTION_KEY", "test-encryption-key-32-bytes!!")


@pytest.fixture
def mock_supabase_admin():
    """Mock Supabase admin client for API key CRUD."""
    with patch("app.routers.api_keys.get_supabase_admin_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user."""
    with patch("app.routers.api_keys.get_auth_user") as mock_auth:
        user = MagicMock()
        user.id = "user-123"
        user.email = "test@example.com"
        mock_auth.return_value = user
        yield mock_auth


@pytest.fixture
def mock_httpx_get():
    """Mock httpx.AsyncClient.get for key validation."""
    with patch("app.routers.api_keys.httpx.AsyncClient") as mock_client_cls:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "model-1"}]}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_cls.return_value = mock_client
        yield mock_client_cls


# ---------------------------------------------------------------------------
# Encryption integration with API key storage
# ---------------------------------------------------------------------------

class TestAPIKeyEncryption:
    """Test that API keys are properly encrypted before storage and masked on retrieval."""

    def test_encrypt_decrypt_api_key_round_trip(self):
        """A real Google API key should encrypt/decrypt correctly."""
        key = "AIzaSyD1234567890abcdefghijklmnopqrstuvwx"
        encrypted = encrypt(key)
        assert encrypted != key
        assert decrypt(encrypted) == key

    def test_mask_key_hides_middle(self):
        """Masked key should not reveal the full key."""
        key = "AIzaSyD1234567890abcdefghijklmnopqrstuvwx"
        masked = mask_key(key)
        assert key not in masked
        assert masked.startswith("AIza")
        assert masked.endswith("uvwx")

    def test_different_keys_different_ciphertext(self):
        """Different plaintexts produce different ciphertexts."""
        e1 = encrypt("key-one")
        e2 = encrypt("key-two")
        assert e1 != e2


# ---------------------------------------------------------------------------
# API key CRUD router tests
# ---------------------------------------------------------------------------

class TestCreateAPIKey:
    """Test POST /api/v1/api-keys endpoint."""

    def test_create_key_validates_provider(self):
        """Invalid provider should be rejected by Pydantic."""
        from app.routers.api_keys import CreateAPIKeyRequest
        with pytest.raises(Exception):
            CreateAPIKeyRequest(
                provider="invalid_provider",
                api_key="sk-test-key-12345",
            )

    def test_create_key_accepts_known_providers(self):
        """All known providers should be accepted."""
        from app.routers.api_keys import CreateAPIKeyRequest, ALLOWED_PROVIDERS
        for provider in ["google", "groq", "cerebras", "openrouter", "custom"]:
            assert provider in ALLOWED_PROVIDERS

    def test_create_key_requires_base_url_for_custom(self):
        """Custom provider must include a base_url."""
        from app.routers.api_keys import CreateAPIKeyRequest
        with pytest.raises(Exception):
            CreateAPIKeyRequest(
                provider="custom",
                api_key="sk-test-key-12345",
            )

    def test_create_key_custom_with_base_url(self):
        """Custom provider with base_url should be valid."""
        from app.routers.api_keys import CreateAPIKeyRequest
        req = CreateAPIKeyRequest(
            provider="custom",
            api_key="sk-test-key-12345",
            base_url="https://my-llm.example.com/v1",
        )
        assert req.provider == "custom"
        assert req.base_url == "https://my-llm.example.com/v1"


class TestAPIKeyValidation:
    """Test key validation against provider endpoints."""

    @pytest.mark.asyncio
    async def test_validate_google_key_success(self):
        """Valid Google key returns is_valid=True."""
        from app.routers.api_keys import validate_key_against_provider
        with patch("app.routers.api_keys.httpx.AsyncClient") as mock_client_cls:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = await validate_key_against_provider("google", "test-key")
            assert result["is_valid"] is True
            assert "response_time_ms" in result

    @pytest.mark.asyncio
    async def test_validate_key_failure_401(self):
        """Invalid key (401) returns is_valid=False."""
        from app.routers.api_keys import validate_key_against_provider
        with patch("app.routers.api_keys.httpx.AsyncClient") as mock_client_cls:
            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = await validate_key_against_provider("groq", "bad-key")
            assert result["is_valid"] is False
            assert "401" in result["message"]

    @pytest.mark.asyncio
    async def test_validate_key_connection_failure(self):
        """Connection failure returns is_valid=False."""
        from app.routers.api_keys import validate_key_against_provider
        with patch("app.routers.api_keys.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = await validate_key_against_provider("google", "test-key")
            assert result["is_valid"] is False
            assert "Connection refused" in result["message"]


# ---------------------------------------------------------------------------
# LLM service per-user resolution tests
# ---------------------------------------------------------------------------

class TestPerUserLLMResolution:
    """Test that BYOK per-user LLM service creation works."""

    def test_create_llm_service_for_user_google(self):
        """Creating a Google per-user service uses the right preset."""
        from app.services.llm_service import create_llm_service_for_user
        svc = create_llm_service_for_user(
            provider="google",
            api_key="test-google-key",
        )
        assert svc.provider == "google"
        assert svc.api_key == "test-google-key"
        assert svc.base_url == "https://generativelanguage.googleapis.com/v1beta/openai"
        assert svc.model == "gemini-2.5-flash"

    def test_create_llm_service_for_user_groq(self):
        """Creating a Groq per-user service uses the right preset."""
        from app.services.llm_service import create_llm_service_for_user
        svc = create_llm_service_for_user(
            provider="groq",
            api_key="test-groq-key",
        )
        assert svc.provider == "groq"
        assert svc.api_key == "test-groq-key"
        assert svc.base_url == "https://api.groq.com/openai/v1"
        assert svc.model == "llama-3.3-70b-versatile"

    def test_create_llm_service_for_user_custom_model(self):
        """Per-user service can override the model."""
        from app.services.llm_service import create_llm_service_for_user
        svc = create_llm_service_for_user(
            provider="google",
            api_key="test-key",
            model="gemini-2.5-pro",
        )
        assert svc.model == "gemini-2.5-pro"

    def test_create_llm_service_for_user_custom_url(self):
        """Custom provider with base_url works."""
        from app.services.llm_service import create_llm_service_for_user
        svc = create_llm_service_for_user(
            provider="custom",
            api_key="test-key",
            base_url="https://my-llm.example.com/v1",
            model="my-custom-model",
        )
        assert svc.provider == "custom"
        assert svc.base_url == "https://my-llm.example.com/v1"
        assert svc.model == "my-custom-model"

    def test_create_llm_service_custom_no_url_raises(self):
        """Custom provider without base_url should raise ValueError."""
        from app.services.llm_service import create_llm_service_for_user
        with pytest.raises(ValueError, match="No base_url"):
            create_llm_service_for_user(
                provider="custom",
                api_key="test-key",
            )


# ---------------------------------------------------------------------------
# Context var (BYOK shim) tests
# ---------------------------------------------------------------------------

class TestBYOKContextVar:
    """Test that the context variable correctly routes to user vs platform LLM."""

    def test_default_returns_platform_service(self):
        """Without a user context, get_active_llm_service returns platform default."""
        from app.services.groq_service import get_active_llm_service, llm_service
        assert get_active_llm_service() is llm_service

    def test_set_user_service_overrides(self):
        """Setting a user service makes get_active_llm_service return it."""
        from app.services.groq_service import (
            set_user_llm_service,
            reset_user_llm_service,
            get_active_llm_service,
        )
        from app.services.llm_service import create_llm_service_for_user

        user_svc = create_llm_service_for_user(
            provider="google",
            api_key="user-google-key",
        )
        token = set_user_llm_service(user_svc)
        try:
            active = get_active_llm_service()
            assert active is user_svc
            assert active.provider == "google"
            assert active.api_key == "user-google-key"
        finally:
            reset_user_llm_service(token)

    def test_reset_restores_platform_service(self):
        """Resetting the context restores the platform default."""
        from app.services.groq_service import (
            set_user_llm_service,
            reset_user_llm_service,
            get_active_llm_service,
            llm_service,
        )
        from app.services.llm_service import create_llm_service_for_user

        user_svc = create_llm_service_for_user(
            provider="groq",
            api_key="user-groq-key",
        )
        token = set_user_llm_service(user_svc)
        reset_user_llm_service(token)
        assert get_active_llm_service() is llm_service
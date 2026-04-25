"""
Tests for LLM service (provider-agnostic, mocked HTTP).
Also verifies the backward-compatible GroqService shim.
"""

import pytest
import httpx
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.llm_service import LLMService, llm_service
from app.services.groq_service import GroqService, groq_service


class TestLLMService:
    """Test provider-agnostic LLM service with mocked HTTP requests."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for LLM service."""
        with patch("app.services.llm_service.get_settings") as mock:
            settings_mock = MagicMock()
            settings_mock.AI_PROVIDER = "groq"
            settings_mock.AI_API_KEY = "test-api-key"
            settings_mock.AI_BASE_URL = None  # use preset
            settings_mock.AI_MODEL = "llama-3.1-8b-instant"
            settings_mock.GROQ_MODEL = "llama-3.1-8b-instant"
            settings_mock.APP_URL = "https://test.example.com"
            mock.return_value = settings_mock
            yield settings_mock

    @pytest.fixture
    def llm_service_instance(self, mock_settings):
        """Create an LLMService instance with mocked settings."""
        return LLMService()

    @pytest.mark.asyncio
    async def test_generate_content_success(self, llm_service_instance):
        """Test successful content generation."""
        expected_content = "This is the generated content."

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": expected_content}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result = await llm_service_instance.generate_content(
                prompt="Generate some content", temperature=0.7, max_tokens=500
            )

            assert result == expected_content

            # Verify the API was called with correct parameters
            call_args = client_instance.post.call_args
            assert call_args[0][0] == "https://api.groq.com/openai/v1/chat/completions"
            assert call_args[1]["json"]["model"] == "llama-3.1-8b-instant"
            assert call_args[1]["json"]["temperature"] == 0.7
            assert call_args[1]["json"]["max_tokens"] == 500

    @pytest.mark.asyncio
    async def test_generate_content_with_system_prompt(self, llm_service_instance):
        """Test content generation with system prompt."""
        expected_content = "Content with system context."

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": expected_content}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result = await llm_service_instance.generate_content(
                prompt="User prompt",
                system_prompt="You are a helpful assistant.",
                temperature=0.5,
            )

            assert result == expected_content

            # Verify messages include system prompt
            call_args = client_instance.post.call_args
            messages = call_args[1]["json"]["messages"]
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[0]["content"] == "You are a helpful assistant."
            assert messages[1]["role"] == "user"

    @pytest.mark.asyncio
    async def test_generate_content_api_error(self, llm_service_instance):
        """Test handling API errors."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rate limit exceeded",
            request=MagicMock(),
            response=MagicMock(status_code=429),
        )

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            with pytest.raises(httpx.HTTPStatusError):
                await llm_service_instance.generate_content(prompt="Test prompt")

    @pytest.mark.asyncio
    async def test_generate_social_posts(self, llm_service_instance):
        """Test generating social media posts."""
        mock_content = """Post 1: Check out this amazing content! #viral

Post 2: This is something you don't want to miss! #mustread

Post 3: Exciting news everyone! #update"""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": mock_content}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result = await llm_service_instance.generate_social_posts(
                content="Original blog post content", platform="twitter", count=3
            )

            assert len(result) == 3
            assert all("Post" in post for post in result)

    @pytest.mark.asyncio
    async def test_generate_thread(self, llm_service_instance):
        """Test generating a thread."""
        mock_content = """1/ Here's the first post in the thread.

2/ This is the second post with more details.

3/ And here's the final post with a CTA."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": mock_content}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result = await llm_service_instance.generate_thread(
                content="Original content for thread", platform="twitter"
            )

            assert len(result) == 3
            assert not any(post.startswith("1/") for post in result)

    @pytest.mark.asyncio
    async def test_generate_newsletter(self, llm_service_instance):
        """Test generating a newsletter."""
        expected_newsletter = """Subject: Weekly Update

Introduction:
Welcome to our weekly newsletter!

Body:
Here's what's new this week...

CTA:
Subscribe now!

Sign-off:
Best regards,
The Team"""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": expected_newsletter}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result = await llm_service_instance.generate_newsletter(
                content="Weekly updates", subject_line="Weekly Update"
            )

            assert "newsletter" in result
            assert result["newsletter"] == expected_newsletter

    @pytest.mark.asyncio
    async def test_generate_short_video_script(self, llm_service_instance):
        """Test generating a short video script."""
        expected_script = """HOOK (0-3s):
Stop scrolling! You need to see this!

CONTENT:
Here's the valuable information...

CTA:
Follow for more!

VISUAL CUES:
- Close-up shot
- Text overlay
- Jump cuts"""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": expected_script}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result = await llm_service_instance.generate_short_video_script(
                content="Content for video script"
            )

            assert "script" in result
            assert result["script"] == expected_script


class TestProviderPresets:
    """Test that provider presets resolve to correct base URLs."""

    @pytest.fixture
    def mock_settings_base(self):
        """Mock settings base — override specific fields per test."""
        with patch("app.services.llm_service.get_settings") as mock:
            settings_mock = MagicMock()
            settings_mock.GROQ_MODEL = "llama-3.3-70b-versatile"
            settings_mock.APP_URL = "https://test.example.com"
            mock.return_value = settings_mock
            yield settings_mock

    def test_google_provider_preset(self, mock_settings_base):
        """Google provider should resolve to generativelanguage.googleapis.com."""
        mock_settings_base.AI_PROVIDER = "google"
        mock_settings_base.AI_API_KEY = "test-google-key"
        mock_settings_base.AI_BASE_URL = None
        mock_settings_base.AI_MODEL = None
        svc = LLMService()
        assert "generativelanguage.googleapis.com" in svc.base_url
        assert svc.model == "gemini-2.5-flash"
        assert svc.provider == "google"

    def test_groq_provider_preset(self, mock_settings_base):
        """Groq provider should resolve to api.groq.com."""
        mock_settings_base.AI_PROVIDER = "groq"
        mock_settings_base.AI_API_KEY = "test-groq-key"
        mock_settings_base.AI_BASE_URL = None
        mock_settings_base.AI_MODEL = None
        svc = LLMService()
        assert "api.groq.com" in svc.base_url
        assert svc.model == "llama-3.3-70b-versatile"

    def test_cerebras_provider_preset(self, mock_settings_base):
        """Cerebras provider should resolve to api.cerebras.ai."""
        mock_settings_base.AI_PROVIDER = "cerebras"
        mock_settings_base.AI_API_KEY = "test-cerebras-key"
        mock_settings_base.AI_BASE_URL = None
        mock_settings_base.AI_MODEL = None
        svc = LLMService()
        assert "api.cerebras.ai" in svc.base_url
        assert svc.model == "llama-3.3-70b"

    def test_openrouter_provider_preset(self, mock_settings_base):
        """OpenRouter provider should resolve to openrouter.ai."""
        mock_settings_base.AI_PROVIDER = "openrouter"
        mock_settings_base.AI_API_KEY = "test-or-key"
        mock_settings_base.AI_BASE_URL = None
        mock_settings_base.AI_MODEL = None
        svc = LLMService()
        assert "openrouter.ai" in svc.base_url
        assert svc.provider == "openrouter"

    def test_custom_base_url_override(self, mock_settings_base):
        """Explicit AI_BASE_URL should override the preset."""
        mock_settings_base.AI_PROVIDER = "groq"
        mock_settings_base.AI_API_KEY = "test-key"
        mock_settings_base.AI_BASE_URL = "https://custom.llm.example.com/v1"
        mock_settings_base.AI_MODEL = "custom-model"
        svc = LLMService()
        assert svc.base_url == "https://custom.llm.llm.example.com/v1" or "custom.llm.example.com" in svc.base_url
        assert svc.model == "custom-model"

    def test_legacy_groq_model_fallback(self, mock_settings_base):
        """When provider is groq and AI_MODEL is not set, GROQ_MODEL should be used."""
        mock_settings_base.AI_PROVIDER = "groq"
        mock_settings_base.AI_API_KEY = "test-key"
        mock_settings_base.AI_BASE_URL = None
        mock_settings_base.AI_MODEL = None
        mock_settings_base.GROQ_MODEL = "llama-3.1-8b-instant"
        svc = LLMService()
        assert svc.model == "llama-3.1-8b-instant"  # GROQ_MODEL wins for groq provider

    def test_google_uses_preset_default_model(self, mock_settings_base):
        """When provider is google and AI_MODEL/GROQ_MODEL not explicitly set, preset default applies."""
        mock_settings_base.AI_PROVIDER = "google"
        mock_settings_base.AI_API_KEY = "test-google-key"
        mock_settings_base.AI_BASE_URL = None
        mock_settings_base.AI_MODEL = None
        mock_settings_base.GROQ_MODEL = "llama-3.3-70b-versatile"  # should be ignored for google
        svc = LLMService()
        assert svc.model == "gemini-2.5-flash"  # Google preset default, not GROQ_MODEL

    def test_unknown_provider_without_base_url_raises(self, mock_settings_base):
        """Unknown provider without AI_BASE_URL should raise ValueError."""
        mock_settings_base.AI_PROVIDER = "unknown_provider"
        mock_settings_base.AI_API_KEY = "test-key"
        mock_settings_base.AI_BASE_URL = None
        mock_settings_base.AI_MODEL = "some-model"
        with pytest.raises(ValueError, match="AI_BASE_URL"):
            LLMService()


class TestGroqServiceShim:
    """Test that the backward-compatible GroqService shim delegates correctly."""

    def test_groq_service_singleton_is_llm_service(self):
        """groq_service singleton should be the same object as llm_service."""
        # Both are the same underlying LLMService singleton
        assert groq_service is llm_service

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for Groq shim test."""
        with patch("app.services.llm_service.get_settings") as mock:
            settings_mock = MagicMock()
            settings_mock.AI_PROVIDER = "groq"
            settings_mock.AI_API_KEY = "test-api-key"
            settings_mock.AI_BASE_URL = None
            settings_mock.AI_MODEL = "llama-3.3-70b-versatile"
            settings_mock.GROQ_MODEL = "llama-3.3-70b-versatile"
            settings_mock.APP_URL = "https://test.example.com"
            mock.return_value = settings_mock
            yield settings_mock

    def test_groq_service_class_delegates(self, mock_settings):
        """GroqService class should delegate all methods to LLMService."""
        svc = GroqService()
        assert svc._svc is llm_service
        assert svc.api_key == llm_service.api_key
        assert svc.model == llm_service.model
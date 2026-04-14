"""
Tests for Groq AI service (mocked).
"""

import pytest
import httpx
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.groq_service import GroqService, groq_service


class TestGroqService:
    """Test Groq AI service with mocked HTTP requests."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for Groq service."""
        with patch("app.services.groq_service.get_settings") as mock:
            settings_mock = MagicMock()
            settings_mock.GROQ_API_KEY = "test-api-key"
            settings_mock.GROQ_MODEL = "llama-3.1-8b-instant"
            mock.return_value = settings_mock
            yield settings_mock

    @pytest.fixture
    def groq_service_instance(self, mock_settings):
        """Create a GroqService instance with mocked settings."""
        return GroqService()

    @pytest.mark.asyncio
    async def test_generate_content_success(self, groq_service_instance):
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

            result = await groq_service_instance.generate_content(
                prompt="Generate some content", temperature=0.7, max_tokens=500
            )

            assert result == expected_content

            # Verify the API was called with correct parameters
            call_args = client_instance.post.call_args
            assert call_args[0][0] == "https://api.groq.com/openai/v1/chat/completions"
            assert call_args[1]["json"]["model"] == "llama-3.3-70b-versatile"
            assert call_args[1]["json"]["temperature"] == 0.7
            assert call_args[1]["json"]["max_tokens"] == 500

    @pytest.mark.asyncio
    async def test_generate_content_with_system_prompt(self, groq_service_instance):
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

            result = await groq_service_instance.generate_content(
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
    async def test_generate_social_posts(self, groq_service_instance):
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

            result = await groq_service_instance.generate_social_posts(
                content="Original blog post content", platform="twitter", count=3
            )

            assert len(result) == 3
            assert all("Post" in post for post in result)

    @pytest.mark.asyncio
    async def test_generate_thread(self, groq_service_instance):
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

            result = await groq_service_instance.generate_thread(
                content="Original content for thread", platform="twitter"
            )

            assert len(result) == 3
            # Should strip the "1/", "2/", etc. prefixes
            assert not any(post.startswith("1/") for post in result)

    @pytest.mark.asyncio
    async def test_generate_newsletter(self, groq_service_instance):
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

            result = await groq_service_instance.generate_newsletter(
                content="Weekly updates", subject_line="Weekly Update"
            )

            assert "newsletter" in result
            assert result["newsletter"] == expected_newsletter

    @pytest.mark.asyncio
    async def test_generate_short_video_script(self, groq_service_instance):
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

            result = await groq_service_instance.generate_short_video_script(
                content="Content for video script"
            )

            assert "script" in result
            assert result["script"] == expected_script

    @pytest.mark.asyncio
    async def test_generate_content_api_error(self, groq_service_instance):
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
                await groq_service_instance.generate_content(prompt="Test prompt")

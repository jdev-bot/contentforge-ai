"""
Tests for AI Editor router and Groq service.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import UUID, uuid4
from fastapi import HTTPException

from app.routers.ai_editor import (
    RewriteRequest,
    ExpandRequest,
    CondenseRequest,
    OptimizeRequest,
    rewrite_content,
    expand_content,
    condense_content,
    optimize_content,
)
from app.services.groq_service import GroqService, groq_service


class TestGroqServiceEditorMethods:
    """Test Groq service editor methods."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for Groq service."""
        with patch("app.services.groq_service.get_settings") as mock:
            settings_mock = MagicMock()
            settings_mock.GROQ_API_KEY = "test-api-key"
            settings_mock.GROQ_MODEL = "llama-3.3-70b-versatile"
            mock.return_value = settings_mock
            yield settings_mock

    @pytest.fixture
    def groq_service_instance(self, mock_settings):
        """Create a GroqService instance with mocked settings."""
        return GroqService()

    @pytest.mark.asyncio
    async def test_rewrite_content_success(self, groq_service_instance):
        """Test successful content rewriting."""
        expected_content = "This is the rewritten content in a professional tone."

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

            result, tokens = await groq_service_instance.rewrite_content(
                content="Original content",
                tone="professional",
                style="persuasive",
            )

            assert result == expected_content
            assert tokens > 0

            # Verify the API was called
            call_args = client_instance.post.call_args
            assert call_args[0][0] == "https://api.groq.com/openai/v1/chat/completions"
            assert call_args[1]["json"]["model"] == "llama-3.3-70b-versatile"

    @pytest.mark.asyncio
    async def test_rewrite_content_different_tones(self, groq_service_instance):
        """Test rewriting with different tones."""
        tones = [
            "casual",
            "witty",
            "formal",
            "friendly",
            "authoritative",
            "enthusiastic",
            "empathetic",
        ]

        for tone in tones:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": f"Rewritten in {tone} tone"}}]
            }

            with patch("httpx.AsyncClient") as mock_client:
                client_instance = MagicMock()
                client_instance.__aenter__ = AsyncMock(return_value=client_instance)
                client_instance.__aexit__ = AsyncMock(return_value=False)
                client_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value = client_instance

                result, tokens = await groq_service_instance.rewrite_content(
                    content="Test content",
                    tone=tone,
                    style="neutral",
                )

                assert f"{tone}" in result.lower() or "rewritten" in result.lower()

    @pytest.mark.asyncio
    async def test_expand_content_success(self, groq_service_instance):
        """Test successful content expansion."""
        original = "Short text."
        expanded = "This is a much longer version of the short text with additional details and elaboration to demonstrate the expansion functionality."

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": expanded}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result, tokens = await groq_service_instance.expand_content(
                content=original,
                target_length=3,
                focus_areas=["examples", "details"],
            )

            assert len(result.split()) > len(original.split())
            assert tokens > 0

    @pytest.mark.asyncio
    async def test_condense_content_success(self, groq_service_instance):
        """Test successful content condensation."""
        original = "This is a very long piece of text that needs to be condensed. It contains many words and sentences that could be shortened while preserving the meaning."
        condensed = "Condensed text preserving meaning."

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": condensed}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result, tokens = await groq_service_instance.condense_content(
                content=original,
                target_percentage=50,
                preserve_key_points=True,
            )

            assert len(result.split()) < len(original.split())
            assert tokens > 0

    @pytest.mark.asyncio
    async def test_optimize_content_success(self, groq_service_instance):
        """Test successful content optimization."""
        optimized_text = "Check out this amazing content! #viral #content #marketing"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": optimized_text}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result = await groq_service_instance.optimize_content(
                content="Original content for social media",
                platform="twitter",
                include_hashtags=True,
                include_cta=True,
            )

            assert "optimized_content" in result
            assert result["platform"] == "twitter"
            assert result["character_count"] > 0
            assert result["word_count"] > 0
            assert result["estimated_tokens"] > 0

    @pytest.mark.asyncio
    async def test_optimize_content_all_platforms(self, groq_service_instance):
        """Test optimization for all supported platforms."""
        platforms = ["twitter", "linkedin", "blog", "newsletter", "instagram", "tiktok"]

        for platform in platforms:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": f"Optimized for {platform}"}}]
            }

            with patch("httpx.AsyncClient") as mock_client:
                client_instance = MagicMock()
                client_instance.__aenter__ = AsyncMock(return_value=client_instance)
                client_instance.__aexit__ = AsyncMock(return_value=False)
                client_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value = client_instance

                result = await groq_service_instance.optimize_content(
                    content="Test content",
                    platform=platform,
                    include_hashtags=True,
                    include_cta=True,
                )

                assert result["platform"] == platform

    @pytest.mark.asyncio
    async def test_editor_methods_api_error(self, groq_service_instance):
        """Test handling API errors in editor methods."""
        import httpx

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
                await groq_service_instance.rewrite_content(
                    content="Test content",
                    tone="professional",
                )


class TestRewriteRequest:
    """Test RewriteRequest model validation."""

    def test_valid_rewrite_request(self):
        """Test valid rewrite request creation."""
        request = RewriteRequest(
            content="This is some content to rewrite.",
            tone="professional",
            style="persuasive",
        )
        assert request.content == "This is some content to rewrite."
        assert request.tone == "professional"
        assert request.style == "persuasive"

    def test_invalid_tone(self):
        """Test validation rejects invalid tone."""
        with pytest.raises(ValueError):
            RewriteRequest(
                content="Test content",
                tone="invalid_tone",
                style="neutral",
            )

    def test_invalid_style(self):
        """Test validation rejects invalid style."""
        with pytest.raises(ValueError):
            RewriteRequest(
                content="Test content",
                tone="professional",
                style="invalid_style",
            )

    def test_content_min_length(self):
        """Test content minimum length validation."""
        with pytest.raises(ValueError):
            RewriteRequest(
                content="Short",
                tone="professional",
                style="neutral",
            )


class TestExpandRequest:
    """Test ExpandRequest model validation."""

    def test_valid_expand_request(self):
        """Test valid expand request creation."""
        request = ExpandRequest(
            content="This is some content to expand with more details.",
            target_length=3,
            focus_areas=["examples", "background"],
        )
        assert request.target_length == 3
        assert request.focus_areas == ["examples", "background"]

    def test_target_length_range(self):
        """Test target length range validation."""
        # Test minimum
        request = ExpandRequest(
            content="Content to expand with more details.",
            target_length=2,
        )
        assert request.target_length == 2

        # Test maximum
        request = ExpandRequest(
            content="Content to expand with more details.",
            target_length=5,
        )
        assert request.target_length == 5

        # Test below minimum
        with pytest.raises(ValueError):
            ExpandRequest(
                content="Content to expand with more details.",
                target_length=1,
            )

        # Test above maximum
        with pytest.raises(ValueError):
            ExpandRequest(
                content="Content to expand with more details.",
                target_length=6,
            )


class TestCondenseRequest:
    """Test CondenseRequest model validation."""

    def test_valid_condense_request(self):
        """Test valid condense request creation."""
        request = CondenseRequest(
            content="This is a longer piece of content that should be condensed down to a shorter form.",
            target_percentage=50,
            preserve_key_points=True,
        )
        assert request.target_percentage == 50
        assert request.preserve_key_points is True

    def test_target_percentage_range(self):
        """Test target percentage range validation."""
        # Test minimum (20%)
        request = CondenseRequest(
            content="Content to condense with more details and longer text.",
            target_percentage=20,
        )
        assert request.target_percentage == 20

        # Test maximum (80%)
        request = CondenseRequest(
            content="Content to condense with more details and longer text.",
            target_percentage=80,
        )
        assert request.target_percentage == 80

        # Test below minimum
        with pytest.raises(ValueError):
            CondenseRequest(
                content="Content to condense with more details and longer text.",
                target_percentage=10,
            )

        # Test above maximum
        with pytest.raises(ValueError):
            CondenseRequest(
                content="Content to condense with more details and longer text.",
                target_percentage=90,
            )


class TestOptimizeRequest:
    """Test OptimizeRequest model validation."""

    def test_valid_optimize_request(self):
        """Test valid optimize request creation."""
        request = OptimizeRequest(
            content="Check out this amazing content!",
            platform="twitter",
            include_hashtags=True,
            include_cta=True,
        )
        assert request.platform == "twitter"
        assert request.include_hashtags is True
        assert request.include_cta is True

    def test_invalid_platform(self):
        """Test validation rejects invalid platform."""
        with pytest.raises(ValueError):
            OptimizeRequest(
                content="Test content for platform",
                platform="invalid_platform",
            )

    def test_valid_platforms(self):
        """Test all valid platforms are accepted."""
        valid_platforms = [
            "twitter",
            "linkedin",
            "blog",
            "newsletter",
            "instagram",
            "tiktok",
        ]

        for platform in valid_platforms:
            request = OptimizeRequest(
                content="Test content for platform",
                platform=platform,
            )
            assert request.platform == platform

    def test_optional_hashtags_cta(self):
        """Test that hashtags and CTA are optional."""
        request = OptimizeRequest(
            content="Test content",
            platform="linkedin",
        )
        assert request.include_hashtags is True  # Default
        assert request.include_cta is True  # Default


class TestEditorEndpoints:
    """Test AI editor API endpoints."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        from unittest.mock import Mock

        user = Mock()
        user.id = uuid4()
        user.email = "test@example.com"
        user.is_active = True
        return user

    @pytest.fixture
    def mock_usage_stats(self):
        """Create mock usage stats."""
        from unittest.mock import Mock

        stats = Mock()
        stats.monthly_usage_count = 10
        stats.monthly_usage_limit = 100
        stats.remaining = 90
        return stats

    @pytest.mark.asyncio
    async def test_rewrite_content_endpoint(self, mock_user, mock_usage_stats):
        """Test rewrite content endpoint."""
        mock_result = "Rewritten content in professional tone"

        with patch("app.routers.ai_editor.check_and_increment_usage") as mock_usage:
            mock_usage.return_value = mock_usage_stats

            with patch.object(
                groq_service, "rewrite_content", return_value=(mock_result, 150)
            ):
                request = RewriteRequest(
                    content="Original content to rewrite",
                    tone="professional",
                    style="persuasive",
                )

                with patch(
                    "app.routers.ai_editor.get_auth_user", return_value=mock_user
                ):
                    with patch(
                        "app.routers.ai_editor.enforce_subscription_limit",
                        return_value=mock_usage_stats,
                    ):
                        response = await rewrite_content(
                            request=request,
                            user=mock_user,
                        )

                        assert response.operation == "rewrite"
                        assert response.rewritten_content == mock_result
                        assert response.tone == "professional"
                        assert response.style == "persuasive"
                        assert response.tokens_used == 150

    @pytest.mark.asyncio
    async def test_expand_content_endpoint(self, mock_user, mock_usage_stats):
        """Test expand content endpoint."""
        original = "Short content"
        expanded = "This is a much longer version of the short content with additional details."

        with patch("app.routers.ai_editor.check_and_increment_usage") as mock_usage:
            mock_usage.return_value = mock_usage_stats

            with patch.object(
                groq_service, "expand_content", return_value=(expanded, 200)
            ):
                request = ExpandRequest(
                    content=original,
                    target_length=3,
                    focus_areas=["details", "examples"],
                )

                response = await expand_content(
                    request=request,
                    user=mock_user,
                )

                assert response.operation == "expand"
                assert response.expanded_content == expanded
                assert response.target_length == 3
                assert response.actual_expansion_ratio > 1.0
                assert response.tokens_used == 200

    @pytest.mark.asyncio
    async def test_condense_content_endpoint(self, mock_user, mock_usage_stats):
        """Test condense content endpoint."""
        original = "This is a long piece of content with many words and sentences."
        condensed = "Condensed version."

        with patch("app.routers.ai_editor.check_and_increment_usage") as mock_usage:
            mock_usage.return_value = mock_usage_stats

            with patch.object(
                groq_service, "condense_content", return_value=(condensed, 100)
            ):
                request = CondenseRequest(
                    content=original,
                    target_percentage=50,
                    preserve_key_points=True,
                )

                response = await condense_content(
                    request=request,
                    user=mock_user,
                )

                assert response.operation == "condense"
                assert response.condensed_content == condensed
                assert response.target_percentage == 50
                assert response.tokens_used == 100

    @pytest.mark.asyncio
    async def test_optimize_content_endpoint(self, mock_user, mock_usage_stats):
        """Test optimize content endpoint."""
        optimized = "Check this out! #viral"

        result_dict = {
            "optimized_content": optimized,
            "platform": "twitter",
            "character_count": len(optimized),
            "word_count": len(optimized.split()),
            "estimated_tokens": 120,
        }

        with patch("app.routers.ai_editor.check_and_increment_usage") as mock_usage:
            mock_usage.return_value = mock_usage_stats

            with patch.object(
                groq_service, "optimize_content", return_value=result_dict
            ):
                request = OptimizeRequest(
                    content="Original content",
                    platform="twitter",
                    include_hashtags=True,
                    include_cta=True,
                )

                response = await optimize_content(
                    request=request,
                    user=mock_user,
                )

                assert response.operation == "optimize"
                assert response.optimized_content == optimized
                assert response.platform == "twitter"
                assert response.character_count > 0
                assert response.word_count > 0
                assert response.tokens_used == 120

    @pytest.mark.asyncio
    async def test_rewrite_content_groq_error(self, mock_user, mock_usage_stats):
        """Test handling Groq service error in rewrite endpoint."""
        import httpx

        with patch("app.routers.ai_editor.check_and_increment_usage") as mock_usage:
            mock_usage.return_value = mock_usage_stats

            with patch.object(
                groq_service,
                "rewrite_content",
                side_effect=httpx.HTTPStatusError(
                    "Rate limit exceeded",
                    request=MagicMock(),
                    response=MagicMock(status_code=429),
                ),
            ):
                request = RewriteRequest(
                    content="Content to rewrite",
                    tone="professional",
                    style="neutral",
                )

                with pytest.raises(HTTPException) as exc_info:
                    await rewrite_content(
                        request=request,
                        user=mock_user,
                    )

                assert exc_info.value.status_code == 500
                assert "Failed to rewrite content" in exc_info.value.detail


class TestIntegrationEditor:
    """Integration tests with mock client."""

    def test_rewrite_endpoint_client(self, client, auth_headers):
        """Test rewrite endpoint via test client."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Rewritten content"}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            response = client.post(
                "/api/v1/ai/edit/rewrite",
                headers=auth_headers,
                json={
                    "content": "Original content to rewrite with enough length",
                    "tone": "professional",
                    "style": "persuasive",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["operation"] == "rewrite"
            assert data["rewritten_content"] == "Rewritten content"
            assert data["tone"] == "professional"
            assert data["style"] == "persuasive"

    def test_expand_endpoint_client(self, client, auth_headers):
        """Test expand endpoint via test client."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Expanded content with much more detail and elaboration"
                    }
                }
            ]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            response = client.post(
                "/api/v1/ai/edit/expand",
                headers=auth_headers,
                json={
                    "content": "Short content to expand",
                    "target_length": 3,
                    "focus_areas": ["details"],
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["operation"] == "expand"
            assert data["target_length"] == 3
            assert data["actual_expansion_ratio"] > 1.0

    def test_condense_endpoint_client(self, client, auth_headers):
        """Test condense endpoint via test client."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Condensed."}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            response = client.post(
                "/api/v1/ai/edit/condense",
                headers=auth_headers,
                json={
                    "content": "This is a very long piece of text with many words that should be condensed down.",
                    "target_percentage": 50,
                    "preserve_key_points": True,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["operation"] == "condense"
            assert data["condensed_content"] == "Condensed."

    def test_optimize_endpoint_client(self, client, auth_headers):
        """Test optimize endpoint via test client."""
        optimized = "Check this out! #viral #content"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": optimized}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = MagicMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            response = client.post(
                "/api/v1/ai/edit/optimize",
                headers=auth_headers,
                json={
                    "content": "Original content for social media platform",
                    "platform": "twitter",
                    "include_hashtags": True,
                    "include_cta": True,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["operation"] == "optimize"
            assert data["platform"] == "twitter"
            assert data["character_count"] == len(optimized)

    def test_rewrite_validation_error(self, client, auth_headers):
        """Test rewrite endpoint validation error."""
        response = client.post(
            "/api/v1/ai/edit/rewrite",
            headers=auth_headers,
            json={
                "content": "Short",  # Too short
                "tone": "professional",
                "style": "neutral",
            },
        )

        assert response.status_code == 422

    def test_optimize_validation_error(self, client, auth_headers):
        """Test optimize endpoint validation error."""
        response = client.post(
            "/api/v1/ai/edit/optimize",
            headers=auth_headers,
            json={
                "content": "Content to optimize",
                "platform": "invalid_platform",
            },
        )

        assert response.status_code == 422

    def test_condense_validation_error(self, client, auth_headers):
        """Test condense endpoint validation error."""
        response = client.post(
            "/api/v1/ai/edit/condense",
            headers=auth_headers,
            json={
                "content": "Short text",  # Too short
                "target_percentage": 50,
            },
        )

        assert response.status_code == 422

    def test_expand_validation_error(self, client, auth_headers):
        """Test expand endpoint validation error."""
        response = client.post(
            "/api/v1/ai/edit/expand",
            headers=auth_headers,
            json={
                "content": "Content to expand",
                "target_length": 10,  # Too high
            },
        )

        assert response.status_code == 422

    def test_editor_history_endpoint(self, client, auth_headers):
        """Test editor history endpoint."""
        # Setup mock history data
        mock_history = [
            {
                "id": "history-1",
                "user_id": "test-user-id-123",
                "content_id": "content-1",
                "operation": "rewrite",
                "original_preview": "Original...",
                "result_preview": "Rewritten...",
                "tokens_used": 150,
                "created_at": "2024-01-01T00:00:00Z",
            }
        ]

        with patch("app.routers.ai_editor.get_supabase_client") as mock_supabase:
            mock_client = MagicMock()
            mock_query = MagicMock()
            mock_query.select = MagicMock(return_value=mock_query)
            mock_query.eq = MagicMock(return_value=mock_query)
            mock_query.order = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_query.execute = MagicMock(return_value=MagicMock(data=mock_history))
            mock_client.table = MagicMock(return_value=mock_query)
            mock_supabase.return_value = mock_client

            response = client.get(
                "/api/v1/ai/edit/history",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["operation"] == "rewrite"
            assert data[0]["tokens_used"] == 150

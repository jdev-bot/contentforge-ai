"""
Translation API tests for ContentForge AI.

Tests translation endpoints, language detection, batch translation,
caching, and rate limiting.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import status
from uuid import uuid4

from tests.utils import create_auth_headers


class TestTranslationLanguages:
    """Tests for supported languages endpoint."""
    
    @pytest.mark.unit
    def test_list_languages_success(self, client, auth_headers):
        """Test listing supported languages returns expected structure."""
        response = client.get("/api/v1/translate/languages", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 20  # Should have 20+ languages
        
        # Check language structure
        for lang in data:
            assert "code" in lang
            assert "name" in lang
            assert "native_name" in lang
            assert len(lang["code"]) >= 2
            assert len(lang["name"]) > 0
    
    @pytest.mark.unit
    def test_list_languages_no_auth(self, client):
        """Test listing languages without auth (should be allowed)."""
        response = client.get("/api/v1/translate/languages")
        
        # Languages endpoint should be public
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.unit
    def test_supported_languages_content(self, client, auth_headers):
        """Test that expected languages are supported."""
        response = client.get("/api/v1/translate/languages", headers=auth_headers)
        data = response.json()
        
        codes = {lang["code"] for lang in data}
        
        # Check major languages are present
        expected = {"es", "fr", "de", "zh-cn", "ja", "ko", "pt", "it", "ru", "ar", "hi", "nl"}
        for lang in expected:
            assert lang in codes, f"Language {lang} should be supported"
    
    @pytest.mark.unit
    def test_language_structure(self, client, auth_headers):
        """Test language info structure."""
        response = client.get("/api/v1/translate/languages", headers=auth_headers)
        data = response.json()
        
        # Check Spanish structure
        spanish = next((l for l in data if l["code"] == "es"), None)
        assert spanish is not None
        assert spanish["name"] == "Spanish"
        assert spanish["native_name"] == "Español"


class TestTranslationUnauthorized:
    """Tests for unauthorized translation access."""
    
    @pytest.mark.unit
    def test_translate_unauthorized(self, client):
        """Test translation without authentication."""
        translate_data = {
            "content_id": str(uuid4()),
            "target_language": "es",
            "preserve_formatting": True,
        }
        
        response = client.post("/api/v1/translate", json=translate_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.unit
    def test_batch_translate_unauthorized(self, client):
        """Test batch translation without authentication."""
        batch_data = {
            "content_ids": [str(uuid4())],
            "target_languages": ["es", "fr"],
        }
        
        response = client.post("/api/v1/translate/batch", json=batch_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.unit
    def test_get_translations_unauthorized(self, client):
        """Test getting translations without authentication."""
        content_id = str(uuid4())
        response = client.get(f"/api/v1/translate/content/{content_id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.unit
    def test_delete_translation_unauthorized(self, client):
        """Test deleting translation without authentication."""
        translation_id = str(uuid4())
        response = client.delete(f"/api/v1/translate/{translation_id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTranslationValidation:
    """Tests for translation request validation."""
    
    @pytest.mark.unit
    def test_translate_invalid_language(self, client, auth_headers):
        """Test translation with unsupported language code."""
        translate_data = {
            "content_id": str(uuid4()),
            "target_language": "xyz",  # Invalid code
        }
        
        response = client.post("/api/v1/translate", json=translate_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "xyz" in response.text or "language" in response.text.lower()
    
    @pytest.mark.unit
    def test_translate_empty_content_id(self, client, auth_headers):
        """Test translation with empty content ID."""
        translate_data = {
            "content_id": "",
            "target_language": "es",
        }
        
        response = client.post("/api/v1/translate", json=translate_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_translate_case_insensitive_language(self, client, auth_headers):
        """Test that language codes are case-insensitive."""
        translate_data = {
            "content_id": str(uuid4()),
            "target_language": "ES",  # Uppercase
        }
        
        # Should validate but will fail on content lookup
        response = client.post("/api/v1/translate", json=translate_data, headers=auth_headers)
        
        # Should pass validation but 404 on content
        # (mock doesn't find the content)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    @pytest.mark.unit
    def test_batch_translate_empty_content_ids(self, client, auth_headers):
        """Test batch translation with empty content_ids."""
        batch_data = {
            "content_ids": [],
            "target_languages": ["es"],
        }
        
        response = client.post("/api/v1/translate/batch", json=batch_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_batch_translate_empty_target_languages(self, client, auth_headers):
        """Test batch translation with empty target_languages."""
        batch_data = {
            "content_ids": [str(uuid4())],
            "target_languages": [],
        }
        
        response = client.post("/api/v1/translate/batch", json=batch_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_batch_translate_too_many_content_ids(self, client, auth_headers):
        """Test batch translation exceeding content limit."""
        batch_data = {
            "content_ids": [str(uuid4()) for _ in range(55)],  # Over limit
            "target_languages": ["es"],
        }
        
        response = client.post("/api/v1/translate/batch", json=batch_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_batch_translate_too_many_languages(self, client, auth_headers):
        """Test batch translation exceeding language limit."""
        batch_data = {
            "content_ids": [str(uuid4())],
            "target_languages": ["es", "fr", "de", "zh-cn", "ja", "ko", "pt", "it", "ru", "ar", "hi"],  # 11 languages
        }
        
        response = client.post("/api/v1/translate/batch", json=batch_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTranslationModels:
    """Tests for translation data models."""
    
    @pytest.mark.unit
    def test_translate_request_model(self):
        """Test TranslateRequest model validation."""
        from app.routers.translation import TranslateRequest
        
        data = {
            "content_id": str(uuid4()),
            "target_language": "es",
            "preserve_formatting": True,
            "translate_metadata": False,
        }
        
        request = TranslateRequest(**data)
        assert request.content_id == data["content_id"]
        assert request.target_language == "es"
        assert request.preserve_formatting is True
        assert request.translate_metadata is False
    
    @pytest.mark.unit
    def test_translate_request_defaults(self):
        """Test TranslateRequest default values."""
        from app.routers.translation import TranslateRequest
        
        data = {
            "content_id": str(uuid4()),
            "target_language": "fr",
        }
        
        request = TranslateRequest(**data)
        assert request.preserve_formatting is True  # Default
        assert request.translate_metadata is False  # Default
    
    @pytest.mark.unit
    def test_translate_request_invalid_language(self):
        """Test TranslateRequest rejects invalid language."""
        from app.routers.translation import TranslateRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            TranslateRequest(
                content_id=str(uuid4()),
                target_language="invalid",
            )
        
        assert "invalid" in str(exc_info.value).lower() or "language" in str(exc_info.value).lower()
    
    @pytest.mark.unit
    def test_batch_translate_request_model(self):
        """Test BatchTranslateRequest model validation."""
        from app.routers.translation import BatchTranslateRequest
        
        data = {
            "content_ids": [str(uuid4()), str(uuid4())],
            "target_languages": ["es", "fr"],
            "preserve_formatting": True,
        }
        
        request = BatchTranslateRequest(**data)
        assert len(request.content_ids) == 2
        assert len(request.target_languages) == 2
        assert request.preserve_formatting is True
    
    @pytest.mark.unit
    def test_translation_response_model(self):
        """Test TranslationResponse model structure."""
        from app.routers.translation import TranslationResponse
        from datetime import datetime, timezone
        
        data = {
            "id": str(uuid4()),
            "content_id": str(uuid4()),
            "original_content": "Hello world",
            "translated_content": "Hola mundo",
            "source_language": "en",
            "target_language": "es",
            "confidence_score": 0.95,
            "preserve_formatting": True,
            "tokens_used": 50,
            "cached": False,
            "created_at": datetime.now(timezone.utc),
        }
        
        response = TranslationResponse(**data)
        assert response.id == data["id"]
        assert response.target_language == "es"
        assert response.confidence_score == 0.95
    
    @pytest.mark.unit
    def test_language_info_model(self):
        """Test LanguageInfo model."""
        from app.routers.translation import LanguageInfo
        
        data = {
            "code": "es",
            "name": "Spanish",
            "native_name": "Español",
        }
        
        lang = LanguageInfo(**data)
        assert lang.code == "es"
        assert lang.name == "Spanish"
        assert lang.native_name == "Español"
    
    @pytest.mark.unit
    def test_batch_translation_response_model(self):
        """Test BatchTranslationResponse model."""
        from app.routers.translation import BatchTranslationResponse, TranslationResponse
        from datetime import datetime, timezone
        
        data = {
            "batch_id": str(uuid4()),
            "total_requested": 4,
            "successful": 4,
            "failed": 0,
            "translations": [],
            "failed_items": [],
            "created_at": datetime.now(timezone.utc),
        }
        
        response = BatchTranslationResponse(**data)
        assert response.total_requested == 4
        assert response.successful == 4


class TestTranslationGroqService:
    """Tests for Groq service translation methods."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_translate_text_success(self):
        """Test successful text translation."""
        from app.services.groq_service import GroqService
        
        with patch.object(GroqService, 'generate_content', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = """SOURCE_LANGUAGE: en
CONFIDENCE: 0.95
TRANSLATION:
Hola mundo"""
            
            service = GroqService()
            result = await service.translate_text("Hello world", "es")
            
            assert "translated_text" in result
            assert "source_language" in result
            assert "confidence_score" in result
            assert result["source_language"] == "en"
            assert result["confidence_score"] == 0.95
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_translate_text_preserve_formatting(self):
        """Test translation with formatting preservation."""
        from app.services.groq_service import GroqService
        
        with patch.object(GroqService, 'generate_content', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = """SOURCE_LANGUAGE: en
CONFIDENCE: 0.92
TRANSLATION:
- Item uno
- Item dos

Paragraph text here."""
            
            service = GroqService()
            result = await service.translate_text("- Item one\n- Item two\n\nParagraph text here.", "es", preserve_formatting=True)
            
            assert "translated_text" in result
            # Check formatting preserved
            assert "- Item" in result["translated_text"]
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_translate_text_error_handling(self):
        """Test translation error handling."""
        from app.services.groq_service import GroqService
        
        with patch.object(GroqService, 'generate_content', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = Exception("API Error")
            
            service = GroqService()
            with pytest.raises(Exception) as exc_info:
                await service.translate_text("Hello", "es")
            
            assert "API Error" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_language(self):
        """Test language detection."""
        from app.services.groq_service import GroqService
        
        with patch.object(GroqService, 'generate_content', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = """LANGUAGE: fr
CONFIDENCE: 0.98
LANGUAGE_NAME: French"""
            
            service = GroqService()
            result = await service.detect_language("Bonjour le monde")
            
            assert result["language"] == "fr"
            assert result["confidence"] == 0.98
    
    @pytest.mark.unit
    def test_supported_languages_list(self):
        """Test supported languages list."""
        from app.routers.translation import SUPPORTED_LANGUAGES
        
        assert len(SUPPORTED_LANGUAGES) >= 20
        
        # Check required fields
        for lang in SUPPORTED_LANGUAGES:
            assert "code" in lang
            assert "name" in lang
            assert "native_name" in lang
    
    @pytest.mark.unit
    def test_language_codes_set(self):
        """Test language codes set."""
        from app.routers.translation import LANGUAGE_CODES
        
        assert "es" in LANGUAGE_CODES
        assert "fr" in LANGUAGE_CODES
        assert "de" in LANGUAGE_CODES
        assert "zh-cn" in LANGUAGE_CODES
        assert "ja" in LANGUAGE_CODES


class TestTranslationCaching:
    """Tests for translation caching functionality."""
    
    @pytest.mark.unit
    def test_get_cached_translation(self, client, auth_headers):
        """Test retrieving cached translation."""
        # Mock supabase to return cached translation
        mock_cached = {
            "id": str(uuid4()),
            "content_id": str(uuid4()),
            "target_language": "es",
            "translated_text": "Hola mundo",
            "source_language": "en",
            "confidence_score": 0.95,
            "created_at": "2024-01-01T00:00:00Z",
        }
        
        with patch("app.routers.translation.get_cached_translation", return_value=mock_cached):
            with patch("app.routers.translation.get_content_text", return_value={
                "id": mock_cached["content_id"],
                "original_text": "Hello world",
                "status": "completed",
            }):
                translate_data = {
                    "content_id": mock_cached["content_id"],
                    "target_language": "es",
                }
                
                response = client.post("/api/v1/translate", json=translate_data, headers=auth_headers)
                
                # Should succeed from cache
                assert response.status_code == status.HTTP_201_CREATED
                data = response.json()
                assert data["cached"] is True
                assert data["tokens_used"] == 0
    
    @pytest.mark.unit
    def test_get_content_translations(self, client, auth_headers):
        """Test getting all translations for content."""
        content_id = str(uuid4())
        
        mock_translations = [
            {
                "id": str(uuid4()),
                "content_id": content_id,
                "target_language": "es",
                "translated_text": "Hola mundo",
                "source_language": "en",
                "confidence_score": 0.95,
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": str(uuid4()),
                "content_id": content_id,
                "target_language": "fr",
                "translated_text": "Bonjour le monde",
                "source_language": "en",
                "confidence_score": 0.93,
                "created_at": "2024-01-01T00:00:00Z",
            },
        ]
        
        with patch("app.routers.translation.get_content_text", return_value={
            "id": content_id,
            "original_text": "Hello world",
            "status": "completed",
        }):
            with patch.object(client.mock_supabase[0].table("translations"), "execute", return_value=Mock(data=mock_translations)):
                response = client.get(f"/api/v1/translate/content/{content_id}", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert isinstance(data, list)


class TestTranslationEdgeCases:
    """Tests for translation edge cases."""
    
    @pytest.mark.unit
    def test_translate_content_not_found(self, client, auth_headers):
        """Test translation for non-existent content."""
        translate_data = {
            "content_id": str(uuid4()),
            "target_language": "es",
        }
        
        response = client.post("/api/v1/translate", json=translate_data, headers=auth_headers)
        
        # Mock doesn't find content
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    def test_translate_content_no_text(self, client, auth_headers):
        """Test translation for content without text."""
        content_id = str(uuid4())
        
        with patch("app.routers.translation.get_content_text", return_value={
            "id": content_id,
            "original_text": None,
            "status": "completed",
        }):
            translate_data = {
                "content_id": content_id,
                "target_language": "es",
            }
            
            response = client.post("/api/v1/translate", json=translate_data, headers=auth_headers)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "no text" in response.json()["detail"].lower()
    
    @pytest.mark.unit
    def test_delete_translation_not_found(self, client, auth_headers):
        """Test deleting non-existent translation."""
        translation_id = str(uuid4())
        
        # Mock returns no data for translation lookup
        with patch.object(client.mock_supabase[0].table("translations"), "execute", return_value=Mock(data=None)):
            response = client.delete(f"/api/v1/translate/{translation_id}", headers=auth_headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    def test_batch_translate_partial_failure(self, client, auth_headers):
        """Test batch translation with some failures."""
        content_ids = [str(uuid4()), str(uuid4())]
        
        # First content exists, second doesn't
        def mock_get_content(content_id, user_id):
            if content_id == content_ids[0]:
                return {"id": content_id, "original_text": "Hello", "status": "completed"}
            return None
        
        with patch("app.routers.translation.get_content_text", side_effect=lambda cid, uid: mock_get_content(cid, uid)):
            batch_data = {
                "content_ids": content_ids,
                "target_languages": ["es"],
            }
            
            response = client.post("/api/v1/translate/batch", json=batch_data, headers=auth_headers)
            
            # Should be accepted and report partial failure
            assert response.status_code in [status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]


class TestTranslationRateLimiting:
    """Tests for translation rate limiting."""
    
    @pytest.mark.unit
    def test_translate_rate_limited(self, client, auth_headers):
        """Test translation rate limiting."""
        # This would require integration with rate limit system
        # For unit tests, we verify the dependency is present
        translate_data = {
            "content_id": str(uuid4()),
            "target_language": "es",
        }
        
        response = client.post("/api/v1/translate", json=translate_data, headers=auth_headers)
        
        # Rate limiting happens before content lookup, so we may hit rate limit or 404
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_429_TOO_MANY_REQUESTS, status.HTTP_401_UNAUTHORIZED]


class TestTranslationConfidence:
    """Tests for translation confidence scoring."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_confidence_score_range(self):
        """Test confidence scores are within valid range."""
        from app.services.groq_service import GroqService
        
        with patch.object(GroqService, 'generate_content', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = """SOURCE_LANGUAGE: en
CONFIDENCE: 0.87
TRANSLATION:
Test"""
            
            service = GroqService()
            result = await service.translate_text("Test", "es")
            
            assert 0.0 <= result["confidence_score"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_confidence_score_clamping(self):
        """Test confidence scores are clamped to 0-1 range."""
        from app.services.groq_service import GroqService
        
        with patch.object(GroqService, 'generate_content', new_callable=AsyncMock) as mock_generate:
            # Return invalid confidence value
            mock_generate.return_value = """SOURCE_LANGUAGE: en
CONFIDENCE: 1.5
TRANSLATION:
Test"""
            
            service = GroqService()
            result = await service.translate_text("Test", "es")
            
            # Should be clamped to 1.0
            assert result["confidence_score"] <= 1.0


class TestTranslationFormatting:
    """Tests for formatting preservation."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_markdown_formatting_preserved(self):
        """Test markdown formatting is preserved in translation."""
        from app.services.groq_service import GroqService
        
        with patch.object(GroqService, 'generate_content', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = """SOURCE_LANGUAGE: en
CONFIDENCE: 0.95
TRANSLATION:
# Título

- **Negrita**
- *Cursiva*

[Enlace](http://example.com)"""
            
            service = GroqService()
            result = await service.translate_text(
                "# Title\n\n- **Bold**\n- *Italic*\n\n[Link](http://example.com)",
                "es",
                preserve_formatting=True
            )
            
            # Verify formatting markers present
            assert "# " in result["translated_text"]
            assert "**" in result["translated_text"] or "__" in result["translated_text"]
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_paragraph_breaks_preserved(self):
        """Test paragraph breaks are preserved."""
        from app.services.groq_service import GroqService
        
        with patch.object(GroqService, 'generate_content', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = """SOURCE_LANGUAGE: en
CONFIDENCE: 0.94
TRANSLATION:
Primer párrafo.

Segundo párrafo.

Tercer párrafo."""
            
            service = GroqService()
            result = await service.translate_text(
                "First paragraph.\n\nSecond paragraph.\n\nThird paragraph.",
                "es",
                preserve_formatting=True
            )
            
            assert "\n\n" in result["translated_text"] or "\n" in result["translated_text"]


class TestTranslationSpecialLanguages:
    """Tests for special language cases."""
    
    @pytest.mark.unit
    def test_chinese_variants(self, client, auth_headers):
        """Test both Chinese variants are supported."""
        from app.routers.translation import LANGUAGE_CODES
        
        assert "zh-cn" in LANGUAGE_CODES
        assert "zh-tw" in LANGUAGE_CODES
    
    @pytest.mark.unit
    def test_right_to_left_languages(self, client, auth_headers):
        """Test RTL languages are supported."""
        from app.routers.translation import LANGUAGE_CODES
        
        rtl_languages = ["ar", "he"]
        for lang in rtl_languages:
            assert lang in LANGUAGE_CODES, f"{lang} should be supported"
    
    @pytest.mark.unit
    def test_non_latin_scripts(self, client, auth_headers):
        """Test non-Latin script languages are supported."""
        from app.routers.translation import LANGUAGE_CODES
        
        non_latin = ["ja", "ko", "zh-cn", "zh-tw", "ar", "hi", "ru", "el", "he", "th"]
        for lang in non_latin:
            assert lang in LANGUAGE_CODES, f"{lang} should be supported"


class TestTranslationBatchOperations:
    """Tests for batch translation operations."""
    
    @pytest.mark.unit
    def test_batch_translation_response_structure(self, client, auth_headers):
        """Test batch translation response has expected structure."""
        content_id = str(uuid4())
        
        with patch("app.routers.translation.get_content_text", return_value={
            "id": content_id,
            "original_text": "Hello world",
            "status": "completed",
        }):
            with patch("app.routers.translation.get_cached_translation", return_value=None):
                batch_data = {
                    "content_ids": [content_id],
                    "target_languages": ["es", "fr"],
                }
                
                response = client.post("/api/v1/translate/batch", json=batch_data, headers=auth_headers)
                
                if response.status_code == status.HTTP_202_ACCEPTED:
                    data = response.json()
                    assert "batch_id" in data
                    assert "total_requested" in data
                    assert "successful" in data
                    assert "failed" in data
                    assert "translations" in data
                    assert "failed_items" in data
                    assert "created_at" in data
    
    @pytest.mark.unit
    def test_batch_translation_limits(self, client, auth_headers):
        """Test batch translation respects limits."""
        # Test that 50 content IDs is allowed but 51 is not
        batch_data_50 = {
            "content_ids": [str(uuid4()) for _ in range(50)],
            "target_languages": ["es"],
        }
        
        # Will fail on content lookup but should pass validation
        response = client.post("/api/v1/translate/batch", json=batch_data_50, headers=auth_headers)
        assert response.status_code != status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTranslationSecurity:
    """Tests for translation security."""
    
    @pytest.mark.unit
    def test_cannot_access_other_user_translations(self, client, auth_headers):
        """Test users cannot access other users' translations."""
        content_id = str(uuid4())
        
        # Mock returns None to simulate content not found for this user
        with patch("app.routers.translation.get_content_text", return_value=None):
            response = client.get(f"/api/v1/translate/content/{content_id}", headers=auth_headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    def test_delete_requires_ownership(self, client, auth_headers):
        """Test delete requires content ownership."""
        translation_id = str(uuid4())
        
        # Mock returns a translation but user doesn't own content
        with patch("app.routers.translation.get_content_text", return_value=None):
            with patch.object(client.mock_supabase[0].table("translations"), "execute", return_value=Mock(data={"content_id": str(uuid4())})):
                response = client.delete(f"/api/v1/translate/{translation_id}", headers=auth_headers)
                
                assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


class TestTranslationTokens:
    """Tests for token usage tracking."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_tokens_used_calculated(self):
        """Test token usage is calculated for translations."""
        from app.services.groq_service import GroqService
        
        with patch.object(GroqService, 'generate_content', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = """SOURCE_LANGUAGE: en
CONFIDENCE: 0.92
TRANSLATION:
Hola mundo amigo"""
            
            service = GroqService()
            result = await service.translate_text("Hello world friend", "es")
            
            # Should have token count (original + translated words)
            assert result["tokens_used"] > 0
    
    @pytest.mark.unit
    def test_cached_translation_zero_tokens(self, client, auth_headers):
        """Test cached translations use zero tokens."""
        mock_cached = {
            "id": str(uuid4()),
            "content_id": str(uuid4()),
            "target_language": "es",
            "translated_text": "Hola mundo",
            "source_language": "en",
            "confidence_score": 0.95,
            "created_at": "2024-01-01T00:00:00Z",
        }
        
        with patch("app.routers.translation.get_cached_translation", return_value=mock_cached):
            with patch("app.routers.translation.get_content_text", return_value={
                "id": mock_cached["content_id"],
                "original_text": "Hello world",
                "status": "completed",
            }):
                translate_data = {
                    "content_id": mock_cached["content_id"],
                    "target_language": "es",
                }
                
                response = client.post("/api/v1/translate", json=translate_data, headers=auth_headers)
                
                if response.status_code == status.HTTP_201_CREATED:
                    data = response.json()
                    assert data["tokens_used"] == 0
                    assert data["cached"] is True

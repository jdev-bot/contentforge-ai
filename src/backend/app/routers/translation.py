"""
Translation router for multi-language content translation API.

Provides endpoints for translating content, listing supported languages,
and batch translation operations.
"""
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from uuid import UUID

from app.core.rate_limit import check_and_increment_usage, enforce_subscription_limit, UsageStats
from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.groq_service import groq_service

router = APIRouter()


# =============================================================================
# SUPPORTED LANGUAGES
# =============================================================================

SUPPORTED_LANGUAGES = [
    {"code": "es", "name": "Spanish", "native_name": "Español"},
    {"code": "fr", "name": "French", "native_name": "Français"},
    {"code": "de", "name": "German", "native_name": "Deutsch"},
    {"code": "zh-cn", "name": "Chinese Simplified", "native_name": "简体中文"},
    {"code": "zh-tw", "name": "Chinese Traditional", "native_name": "繁體中文"},
    {"code": "ja", "name": "Japanese", "native_name": "日本語"},
    {"code": "ko", "name": "Korean", "native_name": "한국어"},
    {"code": "pt", "name": "Portuguese", "native_name": "Português"},
    {"code": "it", "name": "Italian", "native_name": "Italiano"},
    {"code": "ru", "name": "Russian", "native_name": "Русский"},
    {"code": "ar", "name": "Arabic", "native_name": "العربية"},
    {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
    {"code": "nl", "name": "Dutch", "native_name": "Nederlands"},
    {"code": "pl", "name": "Polish", "native_name": "Polski"},
    {"code": "tr", "name": "Turkish", "native_name": "Türkçe"},
    {"code": "vi", "name": "Vietnamese", "native_name": "Tiếng Việt"},
    {"code": "th", "name": "Thai", "native_name": "ไทย"},
    {"code": "sv", "name": "Swedish", "native_name": "Svenska"},
    {"code": "da", "name": "Danish", "native_name": "Dansk"},
    {"code": "no", "name": "Norwegian", "native_name": "Norsk"},
    {"code": "fi", "name": "Finnish", "native_name": "Suomi"},
    {"code": "cs", "name": "Czech", "native_name": "Čeština"},
    {"code": "el", "name": "Greek", "native_name": "Ελληνικά"},
    {"code": "he", "name": "Hebrew", "native_name": "עברית"},
]

LANGUAGE_CODES = {lang["code"] for lang in SUPPORTED_LANGUAGES}


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class TranslateRequest(BaseModel):
    """Request model for single content translation."""
    content_id: str = Field(..., description="UUID of the content to translate")
    target_language: str = Field(..., description="Target language code (e.g., 'es', 'fr', 'de')")
    preserve_formatting: bool = Field(default=True, description="Preserve original formatting (paragraphs, lists, etc.)")
    translate_metadata: bool = Field(default=False, description="Also translate content metadata like title")
    
    @validator('target_language')
    def validate_target_language(cls, v):
        """Validate target language is supported."""
        if v.lower() not in LANGUAGE_CODES:
            valid_codes = ", ".join(sorted(LANGUAGE_CODES))
            raise ValueError(f"Unsupported language code '{v}'. Supported: {valid_codes}")
        return v.lower()


class BatchTranslateRequest(BaseModel):
    """Request model for batch translation of multiple contents."""
    content_ids: List[str] = Field(..., min_items=1, max_items=50, description="List of content IDs to translate")
    target_languages: List[str] = Field(..., min_items=1, max_items=10, description="List of target language codes")
    preserve_formatting: bool = Field(default=True, description="Preserve original formatting")
    
    @validator('target_languages')
    def validate_target_languages(cls, v):
        """Validate all target languages are supported."""
        invalid = [lang for lang in v if lang.lower() not in LANGUAGE_CODES]
        if invalid:
            valid_codes = ", ".join(sorted(LANGUAGE_CODES))
            raise ValueError(f"Unsupported language codes: {', '.join(invalid)}. Supported: {valid_codes}")
        return [lang.lower() for lang in v]


class LanguageInfo(BaseModel):
    """Information about a supported language."""
    code: str
    name: str
    native_name: str


class TranslationResponse(BaseModel):
    """Response model for translation operations."""
    id: str
    content_id: str
    original_content: str
    translated_content: str
    source_language: str = Field(default="en", description="Detected or provided source language code")
    target_language: str
    confidence_score: float = Field(ge=0.0, le=1.0, description="Translation confidence (0-1)")
    preserve_formatting: bool
    tokens_used: int
    cached: bool = Field(default=False, description="Whether result was retrieved from cache")
    created_at: datetime


class BatchTranslationResponse(BaseModel):
    """Response model for batch translation operations."""
    batch_id: str
    total_requested: int
    successful: int
    failed: int
    translations: List[TranslationResponse]
    failed_items: List[Dict[str, Any]]
    created_at: datetime


class TranslationStatusResponse(BaseModel):
    """Response model for translation status check."""
    translation_id: str
    content_id: str
    target_language: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    progress: Optional[int] = None  # Percentage complete
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_cached_translation(content_id: str, target_language: str) -> Optional[Dict[str, Any]]:
    """Check if a cached translation exists."""
    supabase = get_supabase_client()
    try:
        result = supabase.table("translations") \
            .select("*") \
            .eq("content_id", content_id) \
            .eq("target_language", target_language) \
            .single() \
            .execute()
        
        if result.data:
            return result.data
        return None
    except Exception:
        return None


def save_translation_to_cache(
    content_id: str,
    target_language: str,
    source_language: str,
    translated_text: str,
    confidence_score: float,
) -> str:
    """Save translation to database cache."""
    supabase = get_supabase_client()
    try:
        data = {
            "content_id": content_id,
            "target_language": target_language,
            "source_language": source_language,
            "translated_text": translated_text,
            "confidence_score": confidence_score,
        }
        
        # Use upsert to handle unique constraint
        result = supabase.table("translations") \
            .upsert(data, on_conflict="content_id,target_language") \
            .execute()
        
        if result.data:
            return result.data[0]["id"]
        return str(UUID())
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to cache translation: {e}")
        return str(UUID())


def get_content_text(content_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch content text and metadata from database."""
    supabase = get_supabase_client()
    try:
        result = supabase.table("content") \
            .select("id, title, original_text, source_type, status") \
            .eq("id", content_id) \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if result.data:
            return result.data
        return None
    except Exception:
        return None


# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.get("/translate/languages", response_model=List[LanguageInfo])
async def list_supported_languages():
    """
    List all supported translation languages.
    
    Returns a list of language codes, names, and native names.
    """
    return [LanguageInfo(**lang) for lang in SUPPORTED_LANGUAGES]


@router.post("/translate", response_model=TranslationResponse, status_code=status.HTTP_201_CREATED)
async def translate_content(
    request: TranslateRequest,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Translate content to a target language.
    
    - Automatically detects source language
    - Caches translations for repeated use
    - Supports formatting preservation
    """
    # Check and increment usage
    usage_stats = check_and_increment_usage(str(user.id))
    
    # Fetch the content
    content = get_content_text(request.content_id, str(user.id))
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content with ID '{request.content_id}' not found or access denied",
        )
    
    if not content.get("original_text"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content has no text to translate",
        )
    
    original_text = content["original_text"]
    
    # Check cache first
    cached = get_cached_translation(request.content_id, request.target_language)
    if cached:
        return TranslationResponse(
            id=cached["id"],
            content_id=request.content_id,
            original_content=original_text,
            translated_content=cached["translated_text"],
            source_language=cached.get("source_language", "en"),
            target_language=cached["target_language"],
            confidence_score=cached.get("confidence_score", 0.95),
            preserve_formatting=request.preserve_formatting,
            tokens_used=0,  # Cached, no tokens used
            cached=True,
            created_at=cached.get("created_at", datetime.now(timezone.utc)),
        )
    
    try:
        # Perform translation using Groq
        result = await groq_service.translate_text(
            text=original_text,
            target_language=request.target_language,
            preserve_formatting=request.preserve_formatting,
        )
        
        translated_text = result["translated_text"]
        detected_source = result.get("source_language", "en")
        confidence = result.get("confidence_score", 0.9)
        tokens_used = result.get("tokens_used", 0)
        
        # Cache the translation
        translation_id = save_translation_to_cache(
            content_id=request.content_id,
            target_language=request.target_language,
            source_language=detected_source,
            translated_text=translated_text,
            confidence_score=confidence,
        )
        
        return TranslationResponse(
            id=translation_id,
            content_id=request.content_id,
            original_content=original_text,
            translated_content=translated_text,
            source_language=detected_source,
            target_language=request.target_language,
            confidence_score=confidence,
            preserve_formatting=request.preserve_formatting,
            tokens_used=tokens_used,
            cached=False,
            created_at=datetime.now(timezone.utc),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}",
        )


@router.post("/translate/batch", response_model=BatchTranslationResponse, status_code=status.HTTP_202_ACCEPTED)
async def batch_translate(
    request: BatchTranslateRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit)
):
    """
    Translate multiple content items to multiple languages in batch.
    
    - Processes up to 50 content items
    - Supports up to 10 target languages
    - Returns accepted status and processes in background
    """
    from uuid import uuid4
    
    batch_id = str(uuid4())
    total_requested = len(request.content_ids) * len(request.target_languages)
    
    # Validate all content exists before starting
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    invalid_content_ids = []
    for content_id in request.content_ids:
        content = get_content_text(content_id, user_id)
        if not content:
            invalid_content_ids.append(content_id)
    
    if invalid_content_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content not found: {', '.join(invalid_content_ids[:5])}" + 
                   ("..." if len(invalid_content_ids) > 5 else ""),
        )
    
    # Check usage limits for all translations
    # Each (content, language) pair counts as one usage
    for _ in range(total_requested):
        check_and_increment_usage(user_id)
    
    # Process translations
    translations = []
    failed_items = []
    
    for content_id in request.content_ids:
        content = get_content_text(content_id, user_id)
        if not content or not content.get("original_text"):
            failed_items.append({
                "content_id": content_id,
                "error": "Content has no text to translate",
            })
            continue
        
        original_text = content["original_text"]
        
        for target_lang in request.target_languages:
            try:
                # Check cache first
                cached = get_cached_translation(content_id, target_lang)
                if cached:
                    translations.append(TranslationResponse(
                        id=cached["id"],
                        content_id=content_id,
                        original_content=original_text[:200] + "..." if len(original_text) > 200 else original_text,
                        translated_content=cached["translated_text"][:200] + "..." if len(cached["translated_text"]) > 200 else cached["translated_text"],
                        source_language=cached.get("source_language", "en"),
                        target_language=target_lang,
                        confidence_score=cached.get("confidence_score", 0.95),
                        preserve_formatting=request.preserve_formatting,
                        tokens_used=0,
                        cached=True,
                        created_at=datetime.now(timezone.utc),
                    ))
                    continue
                
                # Perform translation
                result = await groq_service.translate_text(
                    text=original_text,
                    target_language=target_lang,
                    preserve_formatting=request.preserve_formatting,
                )
                
                translated_text = result["translated_text"]
                detected_source = result.get("source_language", "en")
                confidence = result.get("confidence_score", 0.9)
                tokens_used = result.get("tokens_used", 0)
                
                # Cache the translation
                translation_id = save_translation_to_cache(
                    content_id=content_id,
                    target_language=target_lang,
                    source_language=detected_source,
                    translated_text=translated_text,
                    confidence_score=confidence,
                )
                
                translations.append(TranslationResponse(
                    id=translation_id,
                    content_id=content_id,
                    original_content=original_text[:200] + "..." if len(original_text) > 200 else original_text,
                    translated_content=translated_text[:200] + "..." if len(translated_text) > 200 else translated_text,
                    source_language=detected_source,
                    target_language=target_lang,
                    confidence_score=confidence,
                    preserve_formatting=request.preserve_formatting,
                    tokens_used=tokens_used,
                    cached=False,
                    created_at=datetime.now(timezone.utc),
                ))
                
            except Exception as e:
                failed_items.append({
                    "content_id": content_id,
                    "target_language": target_lang,
                    "error": str(e),
                })
    
    return BatchTranslationResponse(
        batch_id=batch_id,
        total_requested=total_requested,
        successful=len(translations),
        failed=len(failed_items),
        translations=translations,
        failed_items=failed_items,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/translate/content/{content_id}", response_model=List[TranslationResponse])
async def get_content_translations(
    content_id: str,
    user=Depends(get_auth_user)
):
    """
    Get all translations for a specific content item.
    
    Returns cached translations for the content in all available languages.
    """
    # Verify content exists and user has access
    content = get_content_text(content_id, str(user.id))
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content with ID '{content_id}' not found or access denied",
        )
    
    supabase = get_supabase_client()
    try:
        result = supabase.table("translations") \
            .select("*") \
            .eq("content_id", content_id) \
            .execute()
        
        return [
            TranslationResponse(
                id=item["id"],
                content_id=content_id,
                original_content=content["original_text"][:200] + "..." if len(content.get("original_text", "")) > 200 else content.get("original_text", ""),
                translated_content=item["translated_text"][:200] + "..." if len(item["translated_text"]) > 200 else item["translated_text"],
                source_language=item.get("source_language", "en"),
                target_language=item["target_language"],
                confidence_score=item.get("confidence_score", 0.9),
                preserve_formatting=True,
                tokens_used=0,
                cached=True,
                created_at=item.get("created_at", datetime.now(timezone.utc)),
            )
            for item in result.data
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch translations: {str(e)}",
        )


@router.delete("/translate/{translation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_translation(
    translation_id: str,
    user=Depends(get_auth_user)
):
    """
    Delete a cached translation.
    
    Only the content owner can delete translations.
    """
    supabase = get_supabase_client()
    
    try:
        # First verify the translation exists and get content info
        result = supabase.table("translations") \
            .select("content_id") \
            .eq("id", translation_id) \
            .single() \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Translation with ID '{translation_id}' not found",
            )
        
        # Verify user owns the content
        content = get_content_text(result.data["content_id"], str(user.id))
        if not content:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this translation",
            )
        
        # Delete the translation
        supabase.table("translations") \
            .delete() \
            .eq("id", translation_id) \
            .execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete translation: {str(e)}",
        )

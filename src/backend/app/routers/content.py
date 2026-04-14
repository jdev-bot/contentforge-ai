"""
Content router with full implementation.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, HttpUrl

from app.core.rate_limit import (
    UsageStats,
    check_and_increment_usage,
    enforce_subscription_limit,
    rate_limit_dependency,
)
from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.extraction_service import content_extraction_service
from app.services.groq_service import groq_service

logger = logging.getLogger(__name__)

from app.core.trash import soft_delete_content

router = APIRouter()


class ContentSource(BaseModel):
    type: str  # "url", "youtube", "upload", "text"
    url: Optional[HttpUrl] = None
    text: Optional[str] = None
    file_path: Optional[str] = None


class ContentCreate(BaseModel):
    title: str
    source: ContentSource
    project_id: UUID


class ContentResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    title: str
    source_type: str
    source_url: Optional[str] = None
    original_text: Optional[str] = None
    word_count: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime


class GeneratedAsset(BaseModel):
    id: UUID
    content_id: UUID
    user_id: UUID
    type: str
    platform: Optional[str] = None
    content: str
    tokens_used: Optional[int] = None
    status: str
    created_at: datetime


@router.post(
    "/content", response_model=ContentResponse, status_code=status.HTTP_201_CREATED
)
async def create_content(
    content_data: ContentCreate,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Create new content from a source and extract text."""
    supabase = get_supabase_client()

    try:
        # Check and increment usage after validation but before processing
        usage_stats = check_and_increment_usage(str(user.id))

        # Extract text based on source type
        original_text = None
        source_url = None
        word_count = None

        if content_data.source.type == "url" and content_data.source.url:
            source_url = str(content_data.source.url)
            original_text = await content_extraction_service.extract_from_url(
                source_url
            )

        elif content_data.source.type == "youtube" and content_data.source.url:
            source_url = str(content_data.source.url)
            # Extract video ID from URL
            video_id = None
            if "v=" in source_url:
                video_id = source_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in source_url:
                video_id = source_url.split("youtu.be/")[1].split("?")[0]

            if video_id:
                original_text = await content_extraction_service.extract_from_youtube(
                    video_id
                )

        elif content_data.source.type == "text":
            original_text = content_data.source.text

        # Clean and calculate word count
        if original_text:
            cleaned_text = content_extraction_service.clean_text(original_text)
            word_count = len(cleaned_text.split())

        # Create content record
        data = {
            "project_id": str(content_data.project_id),
            "user_id": str(user.id),
            "title": content_data.title,
            "source_type": content_data.source.type,
            "source_url": source_url,
            "original_text": original_text,
            "word_count": word_count,
            "status": "completed" if original_text else "failed",
        }

        result = supabase.table("content").insert(data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create content",
            )

        return ContentResponse(**result.data[0])

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/content", response_model=List[ContentResponse])
async def list_content(
    project_id: Optional[UUID] = None,
    status: Optional[str] = None,
    user=Depends(get_auth_user),
):
    """List all content for the current user."""
    supabase = get_supabase_client()

    try:
        query = supabase.table("content").select("*").eq("user_id", str(user.id))

        if project_id:
            query = query.eq("project_id", str(project_id))
        if status:
            query = query.eq("status", status)

        query = query.order("created_at", desc=True)

        result = query.execute()

        return [ContentResponse(**c) for c in result.data]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(content_id: UUID, user=Depends(get_auth_user)):
    """Get specific content."""
    supabase = get_supabase_client()

    try:
        result = (
            supabase.table("content")
            .select("*")
            .eq("id", str(content_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            )

        return ContentResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/content/{content_id}/generate", response_model=List[GeneratedAsset])
async def generate_assets(
    content_id: UUID,
    user=Depends(get_auth_user),
    _: UsageStats = Depends(enforce_subscription_limit),
):
    """Generate repurposed assets from content using Groq AI."""
    # Check and increment usage before processing
    usage_stats = check_and_increment_usage(str(user.id))

    supabase = get_supabase_client()

    try:
        # Get the content
        content_result = (
            supabase.table("content")
            .select("*")
            .eq("id", str(content_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not content_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            )

        content = content_result.data
        original_text = content.get("original_text")

        if not original_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No content text available for generation",
            )

        # Generate various assets using Groq
        assets_to_create = []

        # Generate Twitter/X threads
        try:
            threads = await groq_service.generate_thread(original_text, "twitter")
            for i, thread_post in enumerate(threads):
                assets_to_create.append(
                    {
                        "content_id": str(content_id),
                        "user_id": str(user.id),
                        "type": "thread",
                        "platform": "twitter",
                        "content": thread_post,
                        "status": "generated",
                    }
                )
        except Exception as e:
            logger.error(f"Error generating threads: {e}")

        # Generate LinkedIn posts
        try:
            linkedin_posts = await groq_service.generate_social_posts(
                original_text, "linkedin", count=2
            )
            for post in linkedin_posts:
                assets_to_create.append(
                    {
                        "content_id": str(content_id),
                        "user_id": str(user.id),
                        "type": "social_post",
                        "platform": "linkedin",
                        "content": post,
                        "status": "generated",
                    }
                )
        except Exception as e:
            logger.error(f"Error generating LinkedIn posts: {e}")

        # Generate Newsletter
        try:
            newsletter_result = await groq_service.generate_newsletter(original_text)
            assets_to_create.append(
                {
                    "content_id": str(content_id),
                    "user_id": str(user.id),
                    "type": "newsletter",
                    "platform": None,
                    "content": newsletter_result.get("newsletter", ""),
                    "status": "generated",
                }
            )
        except Exception as e:
            logger.error(f"Error generating newsletter: {e}")

        # Generate video script
        try:
            video_result = await groq_service.generate_short_video_script(original_text)
            assets_to_create.append(
                {
                    "content_id": str(content_id),
                    "user_id": str(user.id),
                    "type": "video_script",
                    "platform": None,
                    "content": video_result.get("script", ""),
                    "status": "generated",
                }
            )
        except Exception as e:
            logger.error(f"Error generating video script: {e}")

        # Insert all assets
        created_assets = []
        if assets_to_create:
            result = (
                supabase.table("generated_assets").insert(assets_to_create).execute()
            )
            created_assets = [GeneratedAsset(**a) for a in result.data]

        # Update content status
        supabase.table("content").update({"status": "completed"}).eq(
            "id", str(content_id)
        ).execute()

        return created_assets

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/content/{content_id}/assets", response_model=List[GeneratedAsset])
async def list_assets(content_id: UUID, user=Depends(get_auth_user)):
    """List generated assets for content."""
    supabase = get_supabase_client()

    try:
        result = (
            supabase.table("generated_assets")
            .select("*")
            .eq("content_id", str(content_id))
            .eq("user_id", str(user.id))
            .order("created_at", desc=True)
            .execute()
        )

        return [GeneratedAsset(**a) for a in result.data]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), user=Depends(get_auth_user)):
    """Upload a file (audio/video)."""
    # TODO: Implement file upload to R2
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="File upload not yet implemented",
    )


@router.delete("/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: UUID, user=Depends(get_auth_user), permanent: bool = False
):
    """
    Delete content (soft delete by default).

    Args:
        content_id: The content ID to delete
        permanent: If True, permanently delete. Otherwise soft delete to trash.
    """
    supabase = get_supabase_client()

    try:
        if permanent:
            # Permanent delete
            existing = (
                supabase.table("content")
                .select("*")
                .eq("id", str(content_id))
                .eq("user_id", str(user.id))
                .single()
                .execute()
            )

            if not existing.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found",
                )

            # Delete related assets first
            supabase.table("generated_assets").delete().eq(
                "content_id", str(content_id)
            ).execute()

            # Delete content
            supabase.table("content").delete().eq("id", str(content_id)).execute()
        else:
            # Soft delete to trash
            success = soft_delete_content(str(content_id), str(user.id))
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found",
                )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

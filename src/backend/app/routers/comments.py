"""
Comments & Annotations API Router.

Provides endpoints for:
- CRUD on content comments (with inline position/range)
- Thread support (reply to comments)
- Comment resolution (resolve/unresolve)
- @mention lookup
- Emoji reactions
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.routers.auth import get_auth_user
from app.services.comments_service import comments_service

router = APIRouter()


# ── Request / Response Models ──────────────────────────────────────

class CommentCreate(BaseModel):
    """Create a new comment."""
    text: str = Field(..., min_length=1, description="Comment text (supports @mentions)")
    position_start: Optional[int] = Field(None, ge=0, description="Start character offset for inline annotation")
    position_end: Optional[int] = Field(None, ge=0, description="End character offset for inline annotation")
    parent_id: Optional[str] = Field(None, description="Parent comment ID for threaded replies")


class CommentUpdate(BaseModel):
    """Update comment text."""
    text: str = Field(..., min_length=1, description="Updated comment text")


class CommentResponse(BaseModel):
    """Response model for a comment."""
    id: str
    user_id: str
    content_id: str
    text: str
    position_start: Optional[int]
    position_end: Optional[int]
    parent_id: Optional[str]
    is_resolved: bool
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    mentions: List[str] = []


class CommentListResponse(BaseModel):
    """Paginated list of comments."""
    items: List[CommentResponse]
    total: int
    page: int
    page_size: int


class ThreadResponse(BaseModel):
    """A comment thread (parent + replies)."""
    parent: CommentResponse
    replies: List[CommentResponse]
    reply_count: int


class ReactionAdd(BaseModel):
    """Add a reaction to a comment."""
    emoji: str = Field(..., min_length=1, max_length=10, description="Emoji to react with")


class ReactionResponse(BaseModel):
    """A single reaction group."""
    emoji: str
    user_ids: List[str]
    count: int


class MentionLookupResponse(BaseModel):
    """User mention lookup result."""
    id: str
    full_name: Optional[str]
    email: Optional[str]


# ── Comment CRUD ───────────────────────────────────────────────────

@router.post("/content/{content_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    content_id: UUID,
    body: CommentCreate,
    user=Depends(get_auth_user),
):
    """Create a comment on content. Supports inline annotations and threaded replies."""
    try:
        comment = comments_service.create_comment(
            user_id=user.id,
            content_id=content_id,
            text=body.text,
            position_start=body.position_start,
            position_end=body.position_end,
            parent_id=body.parent_id,
        )
        return CommentResponse(**comment)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comment: {exc}",
        )


@router.get("/content/{content_id}/comments", response_model=CommentListResponse)
async def list_comments(
    content_id: UUID,
    parent_id: Optional[str] = Query(None, description="Get replies to a specific comment"),
    is_resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user=Depends(get_auth_user),
):
    """
    List comments for content.

    By default returns top-level comments only.
    Set parent_id to get replies to a specific comment.
    """
    try:
        result = comments_service.list_comments(
            content_id=content_id,
            user_id=user.id,
            parent_id=parent_id,
            is_resolved=is_resolved,
            page=page,
            page_size=page_size,
        )
        return CommentListResponse(
            items=[CommentResponse(**c) for c in result["items"]],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get("/content/comments/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: str,
    user=Depends(get_auth_user),
):
    """Get a single comment by ID."""
    comment = comments_service.get_comment(comment_id, user.id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    comment["mentions"] = comments_service._get_mentions_for_comment(comment_id)
    return CommentResponse(**comment)


@router.put("/content/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    body: CommentUpdate,
    user=Depends(get_auth_user),
):
    """Update a comment (author only)."""
    updated = comments_service.update_comment(
        comment_id=comment_id,
        user_id=user.id,
        text=body.text,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or not authorized",
        )
    return CommentResponse(**updated)


@router.delete("/content/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    user=Depends(get_auth_user),
):
    """Delete a comment (author only)."""
    deleted = comments_service.delete_comment(comment_id, user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or not authorized",
        )


# ── Thread ─────────────────────────────────────────────────────────

@router.get("/content/comments/{comment_id}/thread", response_model=ThreadResponse)
async def get_comment_thread(
    comment_id: str,
    user=Depends(get_auth_user),
):
    """Get a comment with all its replies (full thread)."""
    thread = comments_service.get_thread(comment_id, user.id)
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    return ThreadResponse(
        parent=CommentResponse(**thread["parent"]),
        replies=[CommentResponse(**r) for r in thread["replies"]],
        reply_count=thread["reply_count"],
    )


# ── Resolution ─────────────────────────────────────────────────────

@router.put("/content/comments/{comment_id}/resolve", response_model=CommentResponse)
async def resolve_comment(
    comment_id: str,
    user=Depends(get_auth_user),
):
    """Mark a comment as resolved (content owner only)."""
    resolved = comments_service.resolve_comment(comment_id, user.id)
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or not authorized to resolve",
        )
    resolved["mentions"] = comments_service._get_mentions_for_comment(comment_id)
    return CommentResponse(**resolved)


@router.put("/content/comments/{comment_id}/unresolve", response_model=CommentResponse)
async def unresolve_comment(
    comment_id: str,
    user=Depends(get_auth_user),
):
    """Reopen a resolved comment (content owner only)."""
    unresolved = comments_service.unresolve_comment(comment_id, user.id)
    if not unresolved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or not authorized to unresolve",
        )
    unresolved["mentions"] = comments_service._get_mentions_for_comment(comment_id)
    return CommentResponse(**unresolved)


# ── Mentions ───────────────────────────────────────────────────────

@router.get("/comments/mentions/lookup", response_model=List[MentionLookupResponse])
async def lookup_mentions(
    q: str = Query(..., min_length=1, description="Username prefix to search"),
    user=Depends(get_auth_user),
):
    """Look up users by username prefix for @mention autocomplete."""
    results = comments_service.lookup_mentions(q)
    return [MentionLookupResponse(**r) for r in results]


# ── Reactions ──────────────────────────────────────────────────────

@router.post("/content/comments/{comment_id}/reactions", response_model=Dict[str, Any])
async def add_reaction(
    comment_id: str,
    body: ReactionAdd,
    user=Depends(get_auth_user),
):
    """Add an emoji reaction to a comment. Idempotent per user/emoji."""
    try:
        reaction = comments_service.add_reaction(
            comment_id=comment_id,
            user_id=user.id,
            emoji=body.emoji,
        )
        return reaction
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add reaction: {exc}",
        )


@router.delete("/content/comments/{comment_id}/reactions", status_code=status.HTTP_204_NO_CONTENT)
async def remove_reaction(
    comment_id: str,
    emoji: str = Query(..., description="Emoji to remove"),
    user=Depends(get_auth_user),
):
    """Remove an emoji reaction from a comment."""
    comments_service.remove_reaction(
        comment_id=comment_id,
        user_id=user.id,
        emoji=emoji,
    )


@router.get("/content/comments/{comment_id}/reactions", response_model=List[ReactionResponse])
async def get_reactions(
    comment_id: str,
    user=Depends(get_auth_user),
):
    """Get all reactions for a comment, grouped by emoji."""
    reactions = comments_service.get_reactions(comment_id)
    return [ReactionResponse(**r) for r in reactions]
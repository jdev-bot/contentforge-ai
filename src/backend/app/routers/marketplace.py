"""
Template Marketplace API Router.

Provides endpoints for:
- Template CRUD (list, search, get, create, update, delete, publish, unpublish)
- Categories and tags
- Ratings and reviews
- Template installation/usage tracking
- Featured and trending templates
- Template versioning
- Author profiles
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.routers.auth import get_auth_user
from app.services.marketplace_service import marketplace_service

router = APIRouter()


# ── Request / Response Models ──────────────────────────────────────


class TemplateCreate(BaseModel):
    """Create a new marketplace template."""
    name: str = Field(..., min_length=1, max_length=200, description="Template name")
    description: str = Field(..., min_length=1, description="Template description")
    category: str = Field(..., min_length=1, description="Template category ID")
    content: str = Field(..., min_length=1, description="Template content/structure")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    platforms: List[str] = Field(default_factory=list, description="Compatible platforms")
    preview_image_url: Optional[str] = Field(None, description="Preview image URL")
    version: str = Field("1.0.0", description="Initial version")
    is_published: bool = Field(False, description="Whether to publish immediately")


class TemplateUpdate(BaseModel):
    """Update a marketplace template."""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    preview_image_url: Optional[str] = None
    version: Optional[str] = None
    change_summary: Optional[str] = Field(None, description="Summary of changes for version history")


class TemplateResponse(BaseModel):
    """Marketplace template response."""
    id: str
    author_id: str
    name: str
    description: str
    category: str
    content: str
    tags: List[str]
    platforms: List[str]
    preview_image_url: Optional[str] = None
    version: str
    latest_version: str
    is_published: bool
    is_featured: bool
    install_count: int
    avg_rating: float
    rating_count: int
    review_count: int
    published_at: Optional[str] = None
    created_at: str
    updated_at: str
    author: Optional[Dict[str, Any]] = None


class TemplateListResponse(BaseModel):
    """Paginated list of templates."""
    templates: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int


class CategoryResponse(BaseModel):
    """Marketplace category."""
    id: str
    name: str
    icon: str
    description: str
    template_count: int


class TagResponse(BaseModel):
    """Popular tag with count."""
    name: str
    count: int


class RatingCreate(BaseModel):
    """Rate a template."""
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5 stars)")
    review: Optional[str] = Field(None, max_length=2000, description="Written review")


class RatingResponse(BaseModel):
    """Template rating/review."""
    id: str
    template_id: str
    user_id: str
    rating: int
    review: Optional[str] = None
    created_at: str
    updated_at: str
    user: Optional[Dict[str, Any]] = None


class RatingListResponse(BaseModel):
    """Paginated list of ratings."""
    ratings: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int


class InstallResponse(BaseModel):
    """Template install result."""
    message: str
    template_id: str
    already_installed: bool


class AuthorProfileResponse(BaseModel):
    """Author marketplace profile."""
    id: str
    full_name: str
    email: str
    avatar_url: Optional[str] = None
    template_count: int
    published_count: int
    total_installs: int
    avg_rating: float
    joined_at: str


class VersionResponse(BaseModel):
    """Template version."""
    id: str
    template_id: str
    version: str
    change_summary: str
    author_id: str
    created_at: str


# ── Template CRUD ──────────────────────────────────────────────────


@router.get("/marketplace/templates", response_model=TemplateListResponse)
async def list_marketplace_templates(
    category: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    search: Optional[str] = None,
    author_id: Optional[str] = None,
    featured: Optional[bool] = None,
    sort: str = Query("newest", description="Sort: newest, popular, rating, featured"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List marketplace templates with search, filter, and pagination."""
    tag_list = tags.split(",") if tags else None
    result = marketplace_service.list_templates(
        category=category,
        tags=tag_list,
        search=search,
        author_id=author_id,
        is_featured=featured,
        sort_by=sort,
        limit=limit,
        offset=offset,
    )
    return TemplateListResponse(**result)


@router.get("/marketplace/templates/featured", response_model=List[Dict[str, Any]])
async def get_featured_templates(limit: int = Query(6, ge=1, le=20)):
    """Get featured templates."""
    return marketplace_service.get_featured_templates(limit=limit)


@router.get("/marketplace/templates/trending", response_model=List[Dict[str, Any]])
async def get_trending_templates(limit: int = Query(10, ge=1, le=50)):
    """Get trending templates (most installed)."""
    return marketplace_service.get_trending_templates(limit=limit)


@router.get("/marketplace/templates/{template_id}", response_model=Dict[str, Any])
async def get_marketplace_template(template_id: str):
    """Get a single marketplace template."""
    template = marketplace_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return template


@router.post("/marketplace/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_marketplace_template(body: TemplateCreate, user=Depends(get_auth_user)):
    """Create a new marketplace template."""
    try:
        template = marketplace_service.create_template(
            author_id=str(user.id),
            name=body.name,
            description=body.description,
            category=body.category,
            content=body.content,
            tags=body.tags,
            platforms=body.platforms,
            preview_image_url=body.preview_image_url,
            version=body.version,
            is_published=body.is_published,
        )
        return TemplateResponse(
            id=template["id"],
            author_id=template["author_id"],
            name=template["name"],
            description=template["description"],
            category=template["category"],
            content=template["content"],
            tags=template.get("tags", []),
            platforms=template.get("platforms", []),
            preview_image_url=template.get("preview_image_url"),
            version=template["version"],
            latest_version=template.get("latest_version", template["version"]),
            is_published=template.get("is_published", False),
            is_featured=template.get("is_featured", False),
            install_count=template.get("install_count", 0),
            avg_rating=template.get("avg_rating", 0.0),
            rating_count=template.get("rating_count", 0),
            review_count=template.get("review_count", 0),
            published_at=template.get("published_at"),
            created_at=template["created_at"],
            updated_at=template["updated_at"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {exc}",
        )


@router.patch("/marketplace/templates/{template_id}", response_model=TemplateResponse)
async def update_marketplace_template(template_id: str, body: TemplateUpdate, user=Depends(get_auth_user)):
    """Update a marketplace template (author only)."""
    fields = body.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    try:
        updated = marketplace_service.update_template(template_id, str(user.id), **fields)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        return TemplateResponse(
            id=updated["id"],
            author_id=updated["author_id"],
            name=updated["name"],
            description=updated["description"],
            category=updated["category"],
            content=updated["content"],
            tags=updated.get("tags", []),
            platforms=updated.get("platforms", []),
            preview_image_url=updated.get("preview_image_url"),
            version=updated["version"],
            latest_version=updated.get("latest_version", updated["version"]),
            is_published=updated.get("is_published", False),
            is_featured=updated.get("is_featured", False),
            install_count=updated.get("install_count", 0),
            avg_rating=updated.get("avg_rating", 0.0),
            rating_count=updated.get("rating_count", 0),
            review_count=updated.get("review_count", 0),
            published_at=updated.get("published_at"),
            created_at=updated["created_at"],
            updated_at=updated["updated_at"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.delete("/marketplace/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_marketplace_template(template_id: str, user=Depends(get_auth_user)):
    """Delete a marketplace template (author only, unpublished only)."""
    try:
        deleted = marketplace_service.delete_template(template_id, str(user.id))
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/marketplace/templates/{template_id}/publish", response_model=Dict[str, Any])
async def publish_template(template_id: str, user=Depends(get_auth_user)):
    """Publish a template to the marketplace."""
    try:
        result = marketplace_service.publish_template(template_id, str(user.id))
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.post("/marketplace/templates/{template_id}/unpublish", response_model=Dict[str, Any])
async def unpublish_template(template_id: str, user=Depends(get_auth_user)):
    """Unpublish a template from the marketplace."""
    try:
        result = marketplace_service.unpublish_template(template_id, str(user.id))
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


# ── Categories & Tags ──────────────────────────────────────────────


@router.get("/marketplace/categories", response_model=List[CategoryResponse])
async def list_marketplace_categories():
    """List all marketplace categories with template counts."""
    return marketplace_service.list_categories()


@router.get("/marketplace/tags", response_model=List[TagResponse])
async def list_popular_tags(limit: int = Query(20, ge=1, le=100)):
    """List popular tags with usage counts."""
    return marketplace_service.list_popular_tags(limit=limit)


# ── Ratings & Reviews ──────────────────────────────────────────────


@router.post("/marketplace/templates/{template_id}/ratings", response_model=Dict[str, Any])
async def rate_template(template_id: str, body: RatingCreate, user=Depends(get_auth_user)):
    """Rate a template (1-5 stars, optional review)."""
    try:
        result = marketplace_service.rate_template(
            template_id=template_id,
            user_id=str(user.id),
            rating=body.rating,
            review=body.review,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/marketplace/templates/{template_id}/ratings", response_model=RatingListResponse)
async def get_template_ratings(
    template_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get ratings and reviews for a template."""
    return marketplace_service.get_template_ratings(
        template_id=template_id,
        limit=limit,
        offset=offset,
    )


@router.delete("/marketplace/ratings/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(rating_id: str, user=Depends(get_auth_user)):
    """Delete a rating (only by the user who created it)."""
    deleted = marketplace_service.delete_rating(rating_id, str(user.id))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")


# ── Installation / Usage Tracking ──────────────────────────────────


@router.post("/marketplace/templates/{template_id}/install", response_model=InstallResponse)
async def install_template(template_id: str, user=Depends(get_auth_user)):
    """Install a template (tracks usage)."""
    try:
        result = marketplace_service.install_template(template_id, str(user.id))
        return InstallResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/marketplace/installs", response_model=List[Dict[str, Any]])
async def get_user_installs(user=Depends(get_auth_user)):
    """Get templates installed by the current user."""
    return marketplace_service.get_user_installs(str(user.id))


# ── Versioning ─────────────────────────────────────────────────────


@router.get("/marketplace/templates/{template_id}/versions", response_model=List[Dict[str, Any]])
async def get_template_versions(template_id: str):
    """Get version history for a template."""
    return marketplace_service.get_template_versions(template_id)


@router.get("/marketplace/templates/{template_id}/versions/{version}", response_model=Dict[str, Any])
async def get_template_version(template_id: str, version: str):
    """Get a specific version of a template."""
    result = marketplace_service.get_template_version(template_id, version)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template version not found")
    return result


# ── Author Profile ─────────────────────────────────────────────────


@router.get("/marketplace/authors/{author_id}", response_model=AuthorProfileResponse)
async def get_author_profile(author_id: str):
    """Get an author's marketplace profile."""
    profile = marketplace_service.get_author_profile(author_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return AuthorProfileResponse(**profile)


@router.get("/marketplace/authors/{author_id}/templates", response_model=TemplateListResponse)
async def get_author_templates(
    author_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get templates by a specific author."""
    return marketplace_service.get_author_templates(author_id, limit=limit, offset=offset)
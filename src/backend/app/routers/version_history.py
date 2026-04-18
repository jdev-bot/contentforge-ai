"""
Version History router — endpoints for listing, creating, diffing, restoring, and deleting content versions.

Route order matters: specific paths (like /diff) must come before parameterized paths (like /{version_id}).
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status as http_status
from pydantic import BaseModel

from app.routers.auth import get_auth_user
from app.services.version_service import version_service

router = APIRouter()


class VersionResponse(BaseModel):
    id: str
    content_id: str
    version_number: int
    title: Optional[str] = None
    body: Optional[str] = None
    metadata: Optional[dict] = None
    created_by: str
    created_at: datetime


class VersionCreate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    change_summary: Optional[str] = None


class DiffResponse(BaseModel):
    version_1: dict
    version_2: dict
    format: str
    diff: str


class RestoreResponse(BaseModel):
    restored_from_version: int
    new_version: Optional[dict] = None


# ── Specific paths BEFORE parameterized paths ──


@router.get("/content/{content_id}/versions/diff", response_model=DiffResponse)
async def diff_versions(
    content_id: UUID,
    v1: UUID = Query(..., description="First version ID"),
    v2: UUID = Query(..., description="Second version ID"),
    format: str = Query("unified", pattern="^(unified|html)$"),
    user=Depends(get_auth_user),
):
    """Get diff between two versions."""
    try:
        result = version_service.compute_diff(
            content_id=str(content_id),
            version_id_1=str(v1),
            version_id_2=str(v2),
            user_id=str(user.id),
            format=format,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ── Parameterized paths ──


@router.get("/content/{content_id}/versions", response_model=List[VersionResponse])
async def list_versions(
    content_id: UUID,
    user=Depends(get_auth_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all versions of a content item."""
    try:
        versions = version_service.list_versions(
            content_id=str(content_id),
            user_id=str(user.id),
            limit=limit,
            offset=offset,
        )
        return versions
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/content/{content_id}/versions/{version_id}", response_model=VersionResponse
)
async def get_version(
    content_id: UUID,
    version_id: UUID,
    user=Depends(get_auth_user),
):
    """Get a specific version of a content item."""
    try:
        version = version_service.get_version(
            content_id=str(content_id),
            version_id=str(version_id),
            user_id=str(user.id),
        )
        if not version:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Version not found",
            )
        return version
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/content/{content_id}/versions",
    response_model=VersionResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def create_version(
    content_id: UUID,
    version_data: VersionCreate,
    user=Depends(get_auth_user),
):
    """Create a new version (manual savepoint)."""
    try:
        version = version_service.create_version(
            content_id=str(content_id),
            user_id=str(user.id),
            title=version_data.title,
            body=version_data.body,
            change_summary=version_data.change_summary,
        )
        if not version:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create version",
            )
        return version
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/content/{content_id}/versions/{version_id}/restore",
    response_model=RestoreResponse,
)
async def restore_version(
    content_id: UUID,
    version_id: UUID,
    user=Depends(get_auth_user),
):
    """Restore a previous version as the current content."""
    try:
        result = version_service.restore_version(
            content_id=str(content_id),
            version_id=str(version_id),
            user_id=str(user.id),
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/content/{content_id}/versions/{version_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
)
async def delete_version(
    content_id: UUID,
    version_id: UUID,
    user=Depends(get_auth_user),
):
    """Delete a specific version."""
    try:
        deleted = version_service.delete_version(
            content_id=str(content_id),
            version_id=str(version_id),
            user_id=str(user.id),
        )
        if not deleted:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Version not found",
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

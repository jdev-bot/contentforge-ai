"""
Projects router with Supabase integration.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.core.cache import cache, CACHE_TTL
from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user

router = APIRouter()


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    brand_voice: Optional[dict] = None
    target_platforms: Optional[List[str]] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    brand_voice: Optional[dict] = None
    target_platforms: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool = True


@router.post(
    "/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED
)
async def create_project(project: ProjectCreate, user=Depends(get_auth_user)):
    """Create a new project."""
    supabase = get_supabase_client()

    try:
        # Insert project
        data = {
            "user_id": str(user.id),
            "name": project.name,
            "description": project.description,
            "brand_voice": project.brand_voice or {},
            "target_platforms": project.target_platforms or [],
        }

        result = supabase.table("projects").insert(data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project",
            )

        created_project = result.data[0]

        # Invalidate project caches for this user
        cache.delete("projects", prefix=f"user:{user.id}")
        cache.delete_pattern("project_", prefix=f"user:{user.id}")

        return ProjectResponse(**created_project)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(user=Depends(get_auth_user), is_active: Optional[bool] = None):
    """List all projects for the current user."""
    # Check cache first
    cache_key = f"projects:{is_active}"
    cached = cache.get(cache_key, prefix=f"user:{user.id}")
    if cached is not None:
        return [ProjectResponse(**p) for p in cached]

    supabase = get_supabase_client()

    try:
        query = supabase.table("projects").select("*").eq("user_id", str(user.id))

        if is_active is not None:
            query = query.eq("is_active", is_active)

        query = query.order("created_at", desc=True)

        result = query.execute()

        project_list = [ProjectResponse(**p) for p in result.data]
        # Cache the result
        cache.set(cache_key, [p.model_dump() for p in project_list], ttl=CACHE_TTL["project_list"], prefix=f"user:{user.id}")
        return project_list

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, user=Depends(get_auth_user)):
    """Get a specific project."""
    # Check cache first
    cache_key = f"project_detail:{project_id}"
    cached = cache.get(cache_key, prefix=f"user:{user.id}")
    if cached is not None:
        return ProjectResponse(**cached)

    supabase = get_supabase_client()

    try:
        result = (
            supabase.table("projects")
            .select("*")
            .eq("id", str(project_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        project_item = ProjectResponse(**result.data)
        # Cache the result
        cache.set(cache_key, project_item.model_dump(), ttl=CACHE_TTL["project_list"], prefix=f"user:{user.id}")
        return project_item

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID, project: ProjectUpdate, user=Depends(get_auth_user)
):
    """Update a project."""
    supabase = get_supabase_client()

    try:
        # Check if project exists and belongs to user
        existing = (
            supabase.table("projects")
            .select("*")
            .eq("id", str(project_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        # Build update data
        update_data = {}
        if project.name is not None:
            update_data["name"] = project.name
        if project.description is not None:
            update_data["description"] = project.description
        if project.brand_voice is not None:
            update_data["brand_voice"] = project.brand_voice
        if project.target_platforms is not None:
            update_data["target_platforms"] = project.target_platforms
        if project.is_active is not None:
            update_data["is_active"] = project.is_active

        if not update_data:
            return ProjectResponse(**existing.data)

        result = (
            supabase.table("projects")
            .update(update_data)
            .eq("id", str(project_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project",
            )

        # Invalidate project caches for this user
        cache.delete("projects", prefix=f"user:{user.id}")
        cache.delete_pattern("project_", prefix=f"user:{user.id}")

        return ProjectResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, user=Depends(get_auth_user)):
    """Delete a project (soft delete)."""
    supabase = get_supabase_client()

    try:
        # Soft delete by setting is_active to false
        result = (
            supabase.table("projects")
            .update({"is_active": False})
            .eq("id", str(project_id))
            .eq("user_id", str(user.id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        # Invalidate project caches for this user
        cache.delete("projects", prefix=f"user:{user.id}")
        cache.delete_pattern("project_", prefix=f"user:{user.id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

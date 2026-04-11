"""
Projects router.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

router = APIRouter()


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool = True


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate):
    """Create a new project."""
    # TODO: Implement with Supabase
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Project creation not yet implemented",
    )


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects():
    """List all projects for the current user."""
    # TODO: Implement with Supabase
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Project listing not yet implemented",
    )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID):
    """Get a specific project."""
    # TODO: Implement with Supabase
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Project retrieval not yet implemented",
    )


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: UUID, project: ProjectUpdate):
    """Update a project."""
    # TODO: Implement with Supabase
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Project update not yet implemented",
    )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID):
    """Delete a project."""
    # TODO: Implement with Supabase
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Project deletion not yet implemented",
    )

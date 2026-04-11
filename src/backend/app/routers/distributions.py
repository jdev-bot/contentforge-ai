"""
Distributions router.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

router = APIRouter()


class DistributionBase(BaseModel):
    asset_id: UUID
    platform: str  # "twitter", "linkedin", "instagram", "email", "blog"
    scheduled_at: Optional[datetime] = None


class DistributionCreate(DistributionBase):
    pass


class DistributionResponse(DistributionBase):
    id: UUID
    status: str  # "pending", "scheduled", "publishing", "published", "failed"
    published_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


@router.post("/distributions", response_model=DistributionResponse, status_code=status.HTTP_201_CREATED)
async def create_distribution(distribution: DistributionCreate):
    """Schedule a new distribution."""
    # TODO: Implement with n8n workflow
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Distribution creation not yet implemented",
    )


@router.get("/distributions", response_model=List[DistributionResponse])
async def list_distributions(status: Optional[str] = None):
    """List all distributions."""
    # TODO: Implement with Supabase
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Distribution listing not yet implemented",
    )


@router.post("/distributions/{distribution_id}/publish")
async def publish_now(distribution_id: UUID):
    """Publish a distribution immediately."""
    # TODO: Trigger n8n workflow immediately
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Publish not yet implemented",
    )


@router.delete("/distributions/{distribution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_distribution(distribution_id: UUID):
    """Cancel a scheduled distribution."""
    # TODO: Implement with Supabase + n8n
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Cancel distribution not yet implemented",
    )

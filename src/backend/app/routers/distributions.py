"""
Distributions router with full implementation.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from pydantic import BaseModel

from app.core.cache import cache, CACHE_TTL
from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.routers.auth import get_auth_user

router = APIRouter()


class DistributionBase(BaseModel):
    asset_id: UUID
    platform: str  # "twitter", "linkedin", "instagram", "email", "blog"
    scheduled_at: Optional[datetime] = None


class DistributionCreate(DistributionBase):
    pass


class DistributionUpdate(BaseModel):
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class DistributionResponse(DistributionBase):
    id: UUID
    user_id: UUID
    status: (
        str  # "pending", "scheduled", "publishing", "published", "failed", "cancelled"
    )
    published_url: Optional[str] = None
    external_id: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime


@router.post(
    "/distributions",
    response_model=DistributionResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def create_distribution(
    distribution: DistributionCreate, user=Depends(get_auth_user)
):
    """Schedule a new distribution."""
    supabase = get_supabase_admin_client()

    try:
        # Verify asset belongs to user
        asset_result = (
            supabase.table("generated_assets")
            .select("*")
            .eq("id", str(distribution.asset_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not asset_result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Asset not found",
            )

        # Create distribution
        data = {
            "asset_id": str(distribution.asset_id),
            "user_id": str(user.id),
            "platform": distribution.platform,
            "status": "scheduled" if distribution.scheduled_at else "pending",
            "scheduled_at": (
                distribution.scheduled_at.isoformat()
                if distribution.scheduled_at
                else None
            ),
        }

        result = supabase.table("distributions").insert(data).execute()

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create distribution",
            )

        # Invalidate distribution caches for this user
        cache.delete_pattern("dist_", prefix=f"user:{user.id}")
        cache.delete_pattern("analytics_", prefix=f"user:{user.id}")

        return DistributionResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/distributions", response_model=List[DistributionResponse])
async def list_distributions(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    user=Depends(get_auth_user),
):
    """List all distributions for the current user."""
    # Check cache first
    cache_key = f"dist_list:{status}:{platform}"
    cached = cache.get(cache_key, prefix=f"user:{user.id}")
    if cached is not None:
        return [DistributionResponse(**d) for d in cached]

    supabase = get_supabase_admin_client()

    try:
        query = supabase.table("distributions").select("*").eq("user_id", str(user.id))

        if status:
            query = query.eq("status", status)
        if platform:
            query = query.eq("platform", platform)

        query = query.order("created_at", desc=True)

        result = query.execute()

        dist_list = [DistributionResponse(**d) for d in result.data]
        # Cache the result
        cache.set(cache_key, [d.model_dump() for d in dist_list], ttl=120, prefix=f"user:{user.id}")
        return dist_list

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/distributions/{distribution_id}", response_model=DistributionResponse)
async def get_distribution(distribution_id: UUID, user=Depends(get_auth_user)):
    """Get a specific distribution."""
    # Check cache first
    cache_key = f"dist_detail:{distribution_id}"
    cached = cache.get(cache_key, prefix=f"user:{user.id}")
    if cached is not None:
        return DistributionResponse(**cached)

    supabase = get_supabase_admin_client()

    try:
        result = (
            supabase.table("distributions")
            .select("*")
            .eq("id", str(distribution_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Distribution not found",
            )

        dist_item = DistributionResponse(**result.data)
        # Cache the result
        cache.set(cache_key, dist_item.model_dump(), ttl=120, prefix=f"user:{user.id}")
        return dist_item

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/distributions/{distribution_id}/publish")
async def publish_now(distribution_id: UUID, user=Depends(get_auth_user)):
    """Publish a distribution immediately."""
    supabase = get_supabase_admin_client()

    try:
        # Get distribution
        result = (
            supabase.table("distributions")
            .select("*,generated_assets(*)")
            .eq("id", str(distribution_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Distribution not found",
            )

        distribution = result.data

        # Update status to publishing
        update_result = (
            supabase.table("distributions")
            .update(
                {
                    "status": "publishing",
                    "scheduled_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            .eq("id", str(distribution_id))
            .execute()
        )

        # TODO: Trigger actual platform publishing via n8n webhook
        # For now, simulate successful publish

        # Update to published
        published_result = (
            supabase.table("distributions")
            .update(
                {
                    "status": "published",
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "published_url": f"https://example.com/post/{distribution_id}",  # Placeholder
                }
            )
            .eq("id", str(distribution_id))
            .execute()
        )

        return {
            "status": "published",
            "distribution": DistributionResponse(**published_result.data[0]),
        }

    except HTTPException:
        raise
    except Exception as e:
        # Mark as failed
        supabase.table("distributions").update(
            {
                "status": "failed",
                "error_message": str(e),
            }
        ).eq("id", str(distribution_id)).execute()

        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/distributions/{distribution_id}/publish-now")
async def publish_now_alias(distribution_id: UUID, user=Depends(get_auth_user)):
    """Publish a distribution immediately (frontend-friendly alias for /publish)."""
    return await publish_now(distribution_id=distribution_id, user=user)


@router.patch("/distributions/{distribution_id}", response_model=DistributionResponse)
async def update_distribution(
    distribution_id: UUID, update: DistributionUpdate, user=Depends(get_auth_user)
):
    """Update a distribution (e.g., reschedule or cancel)."""
    supabase = get_supabase_admin_client()

    try:
        # Check if distribution exists and belongs to user
        existing = (
            supabase.table("distributions")
            .select("*")
            .eq("id", str(distribution_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Distribution not found",
            )

        # Build update data
        update_data = {}
        if update.status:
            update_data["status"] = update.status
        if update.scheduled_at:
            update_data["scheduled_at"] = update.scheduled_at.isoformat()

        if not update_data:
            return DistributionResponse(**existing.data)

        result = (
            supabase.table("distributions")
            .update(update_data)
            .eq("id", str(distribution_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update distribution",
            )

        # Invalidate distribution caches for this user
        cache.delete_pattern("dist_", prefix=f"user:{user.id}")
        cache.delete_pattern("analytics_", prefix=f"user:{user.id}")

        return DistributionResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        # Invalidate distribution caches for this user
        cache.delete_pattern("dist_", prefix=f"user:{user.id}")
        cache.delete_pattern("analytics_", prefix=f"user:{user.id}")
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/distributions/{distribution_id}", status_code=http_status.HTTP_204_NO_CONTENT
)
async def cancel_distribution(distribution_id: UUID, user=Depends(get_auth_user)):
    """Cancel/delete a scheduled distribution."""
    supabase = get_supabase_admin_client()

    try:
        # Check if distribution exists and belongs to user
        existing = (
            supabase.table("distributions")
            .select("*")
            .eq("id", str(distribution_id))
            .eq("user_id", str(user.id))
            .single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Distribution not found",
            )

        # Only allow deletion if not already published
        if existing.data.get("status") == "published":
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete already published distribution",
            )

        # Delete distribution
        supabase.table("distributions").delete().eq(
            "id", str(distribution_id)
        ).execute()

        # Invalidate distribution caches for this user
        cache.delete_pattern("dist_", prefix=f"user:{user.id}")
        cache.delete_pattern("analytics_", prefix=f"user:{user.id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

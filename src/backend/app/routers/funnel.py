"""
Funnel Tracking router.

Provides endpoints for:
- Creating, reading, listing, and deleting funnels
- Tracking events at funnel steps
- Retrieving funnel conversion analytics
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from pydantic import BaseModel, Field

from app.routers.auth import get_auth_user
from app.services.funnel_service import funnel_service

router = APIRouter()


# ── Request / Response Models ─────────────────────────────────


class FunnelStepInput(BaseModel):
    """Input model for a funnel step."""

    step_id: str = Field(..., description="Unique identifier for the step")
    name: str = Field(..., description="Display name of the step")
    order: int = Field(..., description="Order of the step in the funnel")
    description: str = Field(default="", description="Optional description of the step")


class CreateFunnelRequest(BaseModel):
    """Request body for creating a funnel."""

    name: str = Field(..., min_length=1, max_length=200, description="Funnel name")
    description: str = Field(
        default="", max_length=1000, description="Funnel description"
    )
    steps: List[FunnelStepInput] = Field(
        default_factory=list, description="Funnel steps"
    )


class TrackEventRequest(BaseModel):
    """Request body for tracking a funnel event."""

    step_id: str = Field(..., description="Funnel step ID")
    user_id: str = Field(default="", description="Optional user identifier")
    event_data: Dict[str, Any] = Field(
        default_factory=dict, description="Optional event metadata"
    )


class FunnelStepResponse(BaseModel):
    """Response model for a funnel step."""

    step_id: str
    name: str
    order: int
    description: str = ""


class FunnelResponse(BaseModel):
    """Response model for a funnel."""

    id: str
    name: str
    description: str = ""
    steps: List[FunnelStepResponse] = []
    created_at: str = ""
    updated_at: str = ""


class FunnelListResponse(BaseModel):
    """Response model for listing funnels."""

    funnels: List[FunnelResponse]
    total: int


class DropOffStep(BaseModel):
    """Drop-off information for a funnel step."""

    step_id: str
    step_name: str
    users_entered: int
    users_exited: int
    drop_off_count: int
    drop_off_rate: float


class FunnelAnalyticsResponse(BaseModel):
    """Response model for funnel analytics."""

    funnel_id: str
    step_conversions: Dict[str, int]
    total_entered: int
    total_completed: int
    conversion_rate: float
    drop_off_steps: List[DropOffStep]
    step_conversion_rates: Dict[str, float]


class TrackEventResponse(BaseModel):
    """Response after tracking a funnel event."""

    id: Optional[str] = None
    funnel_id: str
    step_id: str
    user_id: str = ""
    event_data: Dict[str, Any] = {}
    message: str = "Event tracked successfully"


# ── Endpoints ────────────────────────────────────────────────


@router.post(
    "/funnels", response_model=FunnelResponse, status_code=http_status.HTTP_201_CREATED
)
async def create_funnel(
    body: CreateFunnelRequest,
    user=Depends(get_auth_user),
):
    """
    Create a new funnel definition.

    Requires authenticated user. Steps will be ordered as provided.
    """
    try:
        steps_data = [s.model_dump() for s in body.steps]
        result = await funnel_service.create_funnel(
            user_id=user.id,
            name=body.name,
            description=body.description,
            steps=steps_data,
        )
        steps = result.get("steps", [])
        return FunnelResponse(
            id=result.get("id", ""),
            name=result.get("name", body.name),
            description=result.get("description", body.description),
            steps=[FunnelStepResponse(**s) for s in steps],
            created_at=result.get("created_at", ""),
            updated_at=result.get("updated_at", ""),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create funnel: {str(e)}",
        )


@router.get("/funnels", response_model=FunnelListResponse)
async def list_funnels(
    user=Depends(get_auth_user),
):
    """
    List all funnels for the authenticated user.
    """
    try:
        funnels = await funnel_service.list_funnels(user_id=user.id)
        funnel_responses = []
        for f in funnels:
            steps = f.get("steps", [])
            funnel_responses.append(
                FunnelResponse(
                    id=f.get("id", ""),
                    name=f.get("name", ""),
                    description=f.get("description", ""),
                    steps=[FunnelStepResponse(**s) for s in steps],
                    created_at=f.get("created_at", ""),
                    updated_at=f.get("updated_at", ""),
                )
            )
        return FunnelListResponse(
            funnels=funnel_responses,
            total=len(funnel_responses),
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list funnels: {str(e)}",
        )


@router.get("/funnels/{funnel_id}", response_model=FunnelResponse)
async def get_funnel(
    funnel_id: str,
    user=Depends(get_auth_user),
):
    """
    Get a specific funnel by ID.
    """
    try:
        funnel = await funnel_service.get_funnel(funnel_id)
        if not funnel:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Funnel {funnel_id} not found",
            )
        steps = funnel.get("steps", [])
        return FunnelResponse(
            id=funnel.get("id", ""),
            name=funnel.get("name", ""),
            description=funnel.get("description", ""),
            steps=[FunnelStepResponse(**s) for s in steps],
            created_at=funnel.get("created_at", ""),
            updated_at=funnel.get("updated_at", ""),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve funnel: {str(e)}",
        )


@router.post("/funnels/{funnel_id}/events", response_model=TrackEventResponse)
async def track_funnel_event(
    funnel_id: str,
    body: TrackEventRequest,
    user=Depends(get_auth_user),
):
    """
    Track a conversion event at a specific funnel step.
    """
    try:
        result = await funnel_service.track_event(
            funnel_id=funnel_id,
            step_id=body.step_id,
            user_id=body.user_id or str(user.id),
            event_data=body.event_data,
        )
        return TrackEventResponse(
            id=result.get("id"),
            funnel_id=funnel_id,
            step_id=body.step_id,
            user_id=body.user_id or str(user.id),
            event_data=body.event_data,
            message="Event tracked successfully",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track event: {str(e)}",
        )


@router.get("/funnels/{funnel_id}/analytics", response_model=FunnelAnalyticsResponse)
async def get_funnel_analytics(
    funnel_id: str,
    days: int = Query(
        default=30, ge=1, le=365, description="Number of days to analyze"
    ),
    user=Depends(get_auth_user),
):
    """
    Get conversion analytics for a funnel.

    Returns step-by-step conversion rates and drop-off analysis.
    """
    try:
        conversion = await funnel_service.get_analytics(
            funnel_id=funnel_id,
            date_range=days,
        )
        return FunnelAnalyticsResponse(
            funnel_id=conversion.funnel_id,
            step_conversions=conversion.step_conversions,
            total_entered=conversion.total_entered,
            total_completed=conversion.total_completed,
            conversion_rate=conversion.conversion_rate,
            drop_off_steps=[DropOffStep(**d) for d in conversion.drop_off_steps],
            step_conversion_rates=conversion.step_conversion_rates,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics: {str(e)}",
        )


@router.delete("/funnels/{funnel_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_funnel(
    funnel_id: str,
    user=Depends(get_auth_user),
):
    """
    Delete a funnel and all its associated events.
    """
    try:
        deleted = await funnel_service.delete_funnel(funnel_id)
        if not deleted:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Funnel {funnel_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete funnel: {str(e)}",
        )

"""
Attribution Modeling router.

Provides endpoints for:
- Recording marketing touchpoints
- Calculating attribution using various models
- Viewing channel performance
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.routers.auth import get_auth_user
from app.services.attribution_service import AttributionModel, attribution_service

router = APIRouter()


# ── Request / Response Models ─────────────────────────────────


class RecordTouchpointRequest(BaseModel):
    """Request body for recording a touchpoint."""

    content_id: str = Field(..., description="Content piece ID")
    channel: str = Field(
        ..., description="Marketing channel (e.g., organic, email, social)"
    )
    source: str = Field(
        default="", description="Traffic source (e.g., google, newsletter)"
    )
    campaign: str = Field(default="", description="Campaign name or identifier")
    event_data: Dict[str, Any] = Field(
        default_factory=dict, description="Optional metadata"
    )


class TouchpointResponse(BaseModel):
    """Response model for a touchpoint."""

    id: str = ""
    content_id: str
    channel: str
    source: str = ""
    campaign: str = ""
    created_at: str = ""
    event_data: Dict[str, Any] = {}


class AttributionResultResponse(BaseModel):
    """Response model for attribution result."""

    channel: str
    source: str = ""
    attribution_weight: float = 0.0
    revenue_attributed: float = 0.0
    conversion_count: int = 0


class CalculateAttributionRequest(BaseModel):
    """Request body for calculating attribution."""

    content_id: str = Field(..., description="Content piece ID")
    model: str = Field(
        default="first_touch",
        description="Attribution model: first_touch, last_touch, linear, time_decay, position_based",
    )


class ChannelPerformanceResponse(BaseModel):
    """Response model for channel performance."""

    channel: str
    total_touchpoints: int = 0
    total_conversions: int = 0
    attribution_weights: Dict[str, float] = {}
    revenue_attributed: Dict[str, float] = {}


class TouchpointListResponse(BaseModel):
    """Response model for listing touchpoints."""

    touchpoints: List[TouchpointResponse]
    total: int


# ── Endpoints ────────────────────────────────────────────────


@router.post(
    "/attribution/touchpoints",
    response_model=TouchpointResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_touchpoint(
    body: RecordTouchpointRequest,
    user=Depends(get_auth_user),
):
    """
    Record a marketing touchpoint for content attribution.
    """
    try:
        result = await attribution_service.record_touchpoint(
            content_id=body.content_id,
            channel=body.channel,
            source=body.source,
            campaign=body.campaign,
            event_data=body.event_data,
        )
        return TouchpointResponse(
            id=result.get("id", ""),
            content_id=result.get("content_id", body.content_id),
            channel=result.get("channel", body.channel),
            source=result.get("source", body.source),
            campaign=result.get("campaign", body.campaign),
            created_at=result.get("created_at", ""),
            event_data=result.get("event_data", body.event_data),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record touchpoint: {str(e)}",
        )


@router.get(
    "/attribution/touchpoints/{content_id}", response_model=TouchpointListResponse
)
async def get_touchpoints(
    content_id: str,
    user=Depends(get_auth_user),
):
    """
    Get all touchpoints for a content piece.
    """
    try:
        touchpoints = await attribution_service.get_touchpoints(content_id)
        tp_responses = [
            TouchpointResponse(
                id=tp.get("id", ""),
                content_id=tp.get("content_id", content_id),
                channel=tp.get("channel", ""),
                source=tp.get("source", ""),
                campaign=tp.get("campaign", ""),
                created_at=tp.get("created_at", ""),
                event_data=tp.get("event_data", {}),
            )
            for tp in touchpoints
        ]
        return TouchpointListResponse(
            touchpoints=tp_responses,
            total=len(tp_responses),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve touchpoints: {str(e)}",
        )


@router.post("/attribution/calculate", response_model=List[AttributionResultResponse])
async def calculate_attribution(
    body: CalculateAttributionRequest,
    user=Depends(get_auth_user),
):
    """
    Calculate attribution for a content piece using the specified model.

    Supported models: first_touch, last_touch, linear, time_decay, position_based
    """
    # Validate model
    valid_models = [m.value for m in AttributionModel]
    if body.model not in valid_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model '{body.model}'. Must be one of: {', '.join(valid_models)}",
        )

    try:
        results = await attribution_service.calculate_attribution(
            content_id=body.content_id,
            model=body.model,
        )
        return [
            AttributionResultResponse(
                channel=r.channel,
                source=r.source,
                attribution_weight=round(r.attribution_weight, 4),
                revenue_attributed=r.revenue_attributed,
                conversion_count=r.conversion_count,
            )
            for r in results
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate attribution: {str(e)}",
        )


@router.get("/attribution/channels", response_model=List[ChannelPerformanceResponse])
async def get_channel_performance(
    days: int = Query(
        default=30, ge=1, le=365, description="Number of days to analyze"
    ),
    user=Depends(get_auth_user),
):
    """
    Get aggregated channel-level attribution performance.

    Returns touchpoint counts and conversion data per channel.
    """
    try:
        performance = await attribution_service.get_channel_performance(
            user_id=user.id,
            date_range=days,
        )
        return [
            ChannelPerformanceResponse(
                channel=p.channel,
                total_touchpoints=p.total_touchpoints,
                total_conversions=p.total_conversions,
                attribution_weights=p.attribution_weights,
                revenue_attributed=p.revenue_attributed,
            )
            for p in performance
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve channel performance: {str(e)}",
        )

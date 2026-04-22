"""
A/B Testing Router for ContentForge AI.

Provides endpoints for:
- Creating and managing experiments
- Recording and retrieving experiment results
- Pausing, resuming, and stopping experiments
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from pydantic import BaseModel, Field

from app.core.supabase import get_supabase_admin_client
from app.routers.auth import get_auth_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================


class CreateExperimentRequest(BaseModel):
    """Request model for creating an A/B test experiment."""

    name: str = Field(..., min_length=1, max_length=255, description="Experiment name")
    content_id: Optional[str] = Field(None, description="Associated content ID")
    variant_a: str = Field(..., min_length=1, description="Control variant text")
    variant_b: str = Field(..., min_length=1, description="Test variant text")
    platform: str = Field(
        default="twitter",
        description="Target platform: twitter, linkedin, facebook, email",
    )
    duration_days: int = Field(
        default=7, ge=1, le=90, description="Experiment duration in days"
    )


class UpdateExperimentRequest(BaseModel):
    """Request model for updating an experiment (pause, resume, stop)."""

    status: Optional[str] = Field(
        None, description="New status: draft, running, paused, completed, stopped"
    )
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class RecordResultRequest(BaseModel):
    """Request model for recording a result for an experiment variant."""

    variant: str = Field(..., description="Which variant: a or b")
    impressions: int = Field(default=0, ge=0)
    engagements: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)


class ExperimentResponse(BaseModel):
    """Response model for an experiment."""

    id: UUID
    user_id: UUID
    name: str
    content_id: Optional[str]
    variant_a: str
    variant_b: str
    platform: str
    status: str
    duration_days: int
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ExperimentDetailResponse(ExperimentResponse):
    """Extended experiment response with results."""

    variant_a_results: Optional[Dict[str, Any]] = None
    variant_b_results: Optional[Dict[str, Any]] = None
    winner: Optional[str] = None
    confidence: Optional[float] = None


class ExperimentListResponse(BaseModel):
    """Response model for listing experiments."""

    experiments: List[ExperimentResponse]
    total: int


class ExperimentResultResponse(BaseModel):
    """Response model for experiment results/stats."""

    experiment_id: UUID
    variant_a: Dict[str, Any]
    variant_b: Dict[str, Any]
    winner: Optional[str] = None
    confidence: Optional[float] = None
    total_results: int


class ResultRecordResponse(BaseModel):
    """Response after recording a result."""

    success: bool
    message: str


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/ab-testing/experiments",
    response_model=ExperimentResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def create_experiment(
    request: CreateExperimentRequest,
    user=Depends(get_auth_user),
):
    """Create a new A/B test experiment."""
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    valid_platforms = ["twitter", "linkedin", "facebook", "email"]
    if request.platform not in valid_platforms:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}",
        )

    new_experiment = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": request.name,
        "content_id": request.content_id,
        "variant_a": request.variant_a,
        "variant_b": request.variant_b,
        "platform": request.platform,
        "status": "draft",
        "duration_days": request.duration_days,
        "started_at": None,
        "ended_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    result = supabase.table("ab_experiments").insert(new_experiment).execute()

    if not result.data:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create experiment",
        )

    return result.data[0]


@router.get("/ab-testing/experiments", response_model=ExperimentListResponse)
async def list_experiments(
    status: Optional[str] = Query(None, description="Filter by status"),
    user=Depends(get_auth_user),
):
    """List all experiments for the current user, optionally filtered by status."""
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    query = (
        supabase.table("ab_experiments")
        .select("*", count="exact")
        .eq("user_id", user_id)
    )

    if status:
        valid_statuses = ["draft", "running", "paused", "completed", "stopped"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )
        query = query.eq("status", status)

    query = query.order("created_at", desc=True)

    result = query.execute()

    return ExperimentListResponse(
        experiments=result.data or [], total=result.count or len(result.data or [])
    )


@router.get(
    "/ab-testing/experiments/{experiment_id}", response_model=ExperimentDetailResponse
)
async def get_experiment(experiment_id: UUID, user=Depends(get_auth_user)):
    """Get a specific experiment with aggregated results."""
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    result = (
        supabase.table("ab_experiments")
        .select("*")
        .eq("id", str(experiment_id))
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    experiment = result.data

    # Get aggregated results
    results_resp = (
        supabase.table("ab_experiment_results")
        .select("*")
        .eq("experiment_id", str(experiment_id))
        .execute()
    )

    results_data = results_resp.data or []

    # Aggregate variant results
    variant_a_stats: Dict[str, Any] = {
        "impressions": 0, "engagements": 0, "clicks": 0
    }
    variant_b_stats: Dict[str, Any] = {
        "impressions": 0, "engagements": 0, "clicks": 0
    }

    for r in results_data:
        variant = r.get("variant", "")
        stats = variant_a_stats if variant == "a" else variant_b_stats
        stats["impressions"] += r.get("impressions", 0)
        stats["engagements"] += r.get("engagements", 0)
        stats["clicks"] += r.get("clicks", 0)

    # Compute derived metrics
    for stats in [variant_a_stats, variant_b_stats]:
        imp = stats["impressions"] or 1
        stats["engagementRate"] = round((stats["engagements"] / imp) * 100, 2)
        stats["clickRate"] = round((stats["clicks"] / imp) * 100, 2)

    # Determine winner and confidence (simple heuristic)
    winner = None
    confidence = None
    a_rate = variant_a_stats.get("engagementRate", 0)
    b_rate = variant_b_stats.get("engagementRate", 0)
    if a_rate > 0 or b_rate > 0:
        diff = abs(a_rate - b_rate)
        avg = (a_rate + b_rate) / 2 or 1
        confidence = round(min(diff / avg, 1.0), 2)
        if a_rate > b_rate:
            winner = "A"
        elif b_rate > a_rate:
            winner = "B"
        else:
            winner = "tie"
            confidence = 0.5

    return ExperimentDetailResponse(
        **{k: experiment[k] for k in experiment},
        variant_a_results=variant_a_stats,
        variant_b_results=variant_b_stats,
        winner=winner,
        confidence=confidence,
    )


@router.patch(
    "/ab-testing/experiments/{experiment_id}", response_model=ExperimentResponse
)
async def update_experiment(
    experiment_id: UUID,
    request: UpdateExperimentRequest,
    user=Depends(get_auth_user),
):
    """Update an experiment — pause, resume, stop, or rename."""
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    # Check existence
    existing = (
        supabase.table("ab_experiments")
        .select("*")
        .eq("id", str(experiment_id))
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    update_data: Dict[str, Any] = {
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    if request.status is not None:
        valid_statuses = ["draft", "running", "paused", "completed", "stopped"]
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )
        update_data["status"] = request.status

        # Set timestamps based on status transitions
        now_iso = datetime.now(timezone.utc).isoformat()
        if request.status == "running" and not existing.data.get("started_at"):
            update_data["started_at"] = now_iso
        if request.status in ("completed", "stopped"):
            update_data["ended_at"] = now_iso

    if request.name is not None:
        update_data["name"] = request.name

    result = (
        supabase.table("ab_experiments")
        .update(update_data)
        .eq("id", str(experiment_id))
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update experiment",
        )

    return result.data[0]


@router.post(
    "/ab-testing/experiments/{experiment_id}/results",
    response_model=ResultRecordResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def record_result(
    experiment_id: UUID,
    request: RecordResultRequest,
    user=Depends(get_auth_user),
):
    """Record a result for an experiment variant."""
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    # Verify experiment exists and belongs to user
    experiment = (
        supabase.table("ab_experiments")
        .select("id, status")
        .eq("id", str(experiment_id))
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not experiment.data:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    if experiment.data["status"] not in ("running", "draft"):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Cannot record results for an experiment that is not running or in draft",
        )

    if request.variant not in ("a", "b"):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Variant must be 'a' or 'b'",
        )

    new_result = {
        "id": str(uuid.uuid4()),
        "experiment_id": str(experiment_id),
        "user_id": user_id,
        "variant": request.variant,
        "impressions": request.impressions,
        "engagements": request.engagements,
        "clicks": request.clicks,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    insert_result = (
        supabase.table("ab_experiment_results").insert(new_result).execute()
    )

    if not insert_result.data:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record result",
        )

    return ResultRecordResponse(success=True, message="Result recorded successfully")


@router.get(
    "/ab-testing/experiments/{experiment_id}/results",
    response_model=ExperimentResultResponse,
)
async def get_experiment_results(
    experiment_id: UUID,
    user=Depends(get_auth_user),
):
    """Get aggregated results/stats for an experiment."""
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    # Verify experiment exists
    experiment = (
        supabase.table("ab_experiments")
        .select("id")
        .eq("id", str(experiment_id))
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not experiment.data:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    # Fetch all results
    results_resp = (
        supabase.table("ab_experiment_results")
        .select("*")
        .eq("experiment_id", str(experiment_id))
        .execute()
    )

    results_data = results_resp.data or []

    variant_a: Dict[str, Any] = {
        "impressions": 0, "engagements": 0, "clicks": 0
    }
    variant_b: Dict[str, Any] = {
        "impressions": 0, "engagements": 0, "clicks": 0
    }

    for r in results_data:
        variant = r.get("variant", "")
        stats = variant_a if variant == "a" else variant_b
        stats["impressions"] += r.get("impressions", 0)
        stats["engagements"] += r.get("engagements", 0)
        stats["clicks"] += r.get("clicks", 0)

    for stats in [variant_a, variant_b]:
        imp = stats["impressions"] or 1
        stats["engagementRate"] = round((stats["engagements"] / imp) * 100, 2)
        stats["clickRate"] = round((stats["clicks"] / imp) * 100, 2)

    winner = None
    confidence = None
    a_rate = variant_a.get("engagementRate", 0)
    b_rate = variant_b.get("engagementRate", 0)
    if a_rate > 0 or b_rate > 0:
        diff = abs(a_rate - b_rate)
        avg = (a_rate + b_rate) / 2 or 1
        confidence = round(min(diff / avg, 1.0), 2)
        if a_rate > b_rate:
            winner = "A"
        elif b_rate > a_rate:
            winner = "B"
        else:
            winner = "tie"
            confidence = 0.5

    return ExperimentResultResponse(
        experiment_id=experiment_id,
        variant_a=variant_a,
        variant_b=variant_b,
        winner=winner,
        confidence=confidence,
        total_results=len(results_data),
    )


@router.delete(
    "/ab-testing/experiments/{experiment_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
)
async def delete_experiment(experiment_id: UUID, user=Depends(get_auth_user)):
    """Delete an experiment and its results."""
    supabase = get_supabase_admin_client()
    user_id = str(user.id)

    # Verify existence
    existing = (
        supabase.table("ab_experiments")
        .select("id")
        .eq("id", str(experiment_id))
        .eq("user_id", user_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    # Delete results first (FK)
    supabase.table("ab_experiment_results").delete().eq(
        "experiment_id", str(experiment_id)
    ).execute()

    # Delete experiment
    supabase.table("ab_experiments").delete().eq(
        "id", str(experiment_id)
    ).eq("user_id", user_id).execute()

    return None
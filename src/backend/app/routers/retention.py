"""
Data Retention API Router.

Provides endpoints for:
- CRUD on retention policies
- Apply retention (archive/delete expired content)
- Compliance reporting (GDPR Art. 5)
- Audit trail
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.routers.auth import get_auth_user
from app.services.retention_service import retention_service

router = APIRouter()


# ── Request / Response Models ──────────────────────────────────────

class RetentionPolicyCreate(BaseModel):
    """Create a new retention policy."""
    content_type: str = Field(..., description="Content type this policy applies to")
    archive_after_days: int = Field(..., gt=0, description="Days before content is auto-archived")
    delete_after_days: Optional[int] = Field(None, description="Days before content is auto-deleted (must be >= archive_after_days)")
    description: Optional[str] = Field(None, description="Human-readable description")
    is_active: bool = Field(True, description="Whether the policy is active")


class RetentionPolicyUpdate(BaseModel):
    """Update a retention policy (all fields optional)."""
    content_type: Optional[str] = None
    archive_after_days: Optional[int] = Field(None, gt=0)
    delete_after_days: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RetentionPolicyResponse(BaseModel):
    """Response model for a retention policy."""
    id: str
    user_id: str
    content_type: str
    archive_after_days: int
    delete_after_days: Optional[int]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RetentionPolicyListResponse(BaseModel):
    """Paginated list of retention policies."""
    items: List[RetentionPolicyResponse]
    total: int
    page: int
    page_size: int


class RetentionApplyRequest(BaseModel):
    """Request body for apply-retention endpoint."""
    content_type: Optional[str] = Field(None, description="Apply only to this content type (optional)")


class RetentionApplyResponse(BaseModel):
    """Response model for apply-retention."""
    archived: int
    deleted: int
    policies_applied: int
    message: str


class ComplianceRecommendation(BaseModel):
    """A compliance recommendation."""
    text: str


class ComplianceReportResponse(BaseModel):
    """GDPR Article 5 compliance report."""
    report_generated_at: str
    gdpr_article: str
    compliance_score: int
    total_content: int
    content_by_status: Dict[str, int]
    content_by_type: Dict[str, int]
    active_policies: int
    inactive_policies: int
    content_covered_by_policy: int
    content_without_policy: List[str]
    audit_trail_last_30_days: Dict[str, int]
    recommendations: List[str]


# ── Endpoints ──────────────────────────────────────────────────────

@router.post("/retention/policies", response_model=RetentionPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_retention_policy(
    body: RetentionPolicyCreate,
    user=Depends(get_auth_user),
):
    """Create a new retention policy for a content type."""
    try:
        policy = retention_service.create_policy(
            user_id=user.id,
            content_type=body.content_type,
            archive_after_days=body.archive_after_days,
            delete_after_days=body.delete_after_days,
            description=body.description,
            is_active=body.is_active,
        )
        return RetentionPolicyResponse(**policy)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create retention policy: {exc}",
        )


@router.get("/retention/policies", response_model=RetentionPolicyListResponse)
async def list_retention_policies(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user=Depends(get_auth_user),
):
    """List retention policies for the authenticated user."""
    try:
        result = retention_service.list_policies(
            user_id=user.id,
            content_type=content_type,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )
        return RetentionPolicyListResponse(
            items=[RetentionPolicyResponse(**p) for p in result["items"]],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get("/retention/policies/{policy_id}", response_model=RetentionPolicyResponse)
async def get_retention_policy(
    policy_id: str,
    user=Depends(get_auth_user),
):
    """Get a single retention policy by ID."""
    policy = retention_service.get_policy(policy_id, user.id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retention policy not found",
        )
    return RetentionPolicyResponse(**policy)


@router.put("/retention/policies/{policy_id}", response_model=RetentionPolicyResponse)
async def update_retention_policy(
    policy_id: str,
    body: RetentionPolicyUpdate,
    user=Depends(get_auth_user),
):
    """Update a retention policy (partial update)."""
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )
    try:
        updated = retention_service.update_policy(
            policy_id=policy_id,
            user_id=user.id,
            **updates,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Retention policy not found",
            )
        return RetentionPolicyResponse(**updated)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update retention policy: {exc}",
        )


@router.delete("/retention/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_retention_policy(
    policy_id: str,
    user=Depends(get_auth_user),
):
    """Delete a retention policy."""
    deleted = retention_service.delete_policy(policy_id, user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retention policy not found",
        )


@router.post("/retention/apply", response_model=RetentionApplyResponse)
async def apply_retention(
    body: RetentionApplyRequest = RetentionApplyRequest(),
    user=Depends(get_auth_user),
):
    """
    Apply retention policies: archive and/or delete expired content.

    Optionally scope to a single content_type.
    """
    try:
        result = retention_service.apply_retention(
            user_id=user.id,
            content_type=body.content_type,
        )
        return RetentionApplyResponse(
            archived=result["archived"],
            deleted=result["deleted"],
            policies_applied=result["policies_applied"],
            message=(
                f"Retention applied: {result['archived']} archived, "
                f"{result['deleted']} deleted across "
                f"{result['policies_applied']} policies."
            ),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply retention: {exc}",
        )


@router.get("/retention/compliance", response_model=ComplianceReportResponse)
async def get_compliance_report(
    user=Depends(get_auth_user),
):
    """
    Generate a GDPR Article 5(1)(e) compliance report.

    Covers storage limitation, policy coverage, and audit trail.
    """
    try:
        report = retention_service.get_compliance_report(user_id=user.id)
        return ComplianceReportResponse(**report)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate compliance report: {exc}",
        )


class RetentionAuditEntryResponse(BaseModel):
    """Response model for a retention audit entry."""
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Optional[str] = None
    created_at: datetime


class RetentionAuditListResponse(BaseModel):
    """Paginated list of audit entries."""
    items: List[RetentionAuditEntryResponse]
    total: int
    page: int
    page_size: int


@router.get("/retention/audit", response_model=RetentionAuditListResponse)
async def get_retention_audit_trail(
    action: Optional[str] = Query(None, description="Filter by action type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user=Depends(get_auth_user),
):
    """Get the retention audit trail for the authenticated user."""
    try:
        result = retention_service.get_audit_trail(
            user_id=user.id,
            action=action,
            page=page,
            page_size=page_size,
        )
        return RetentionAuditListResponse(
            items=[RetentionAuditEntryResponse(**e) for e in result["items"]],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
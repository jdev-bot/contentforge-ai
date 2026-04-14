"""
Report scheduling router with generation and download endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user
from app.services.report_service import (
    VALID_FORMATS,
    VALID_REPORT_TYPES,
    report_service,
)

router = APIRouter()


# ── Pydantic Models ─────────────────────────────────────────────────


class ReportCreate(BaseModel):
    """Create a new scheduled report."""

    name: str = Field(..., min_length=1, max_length=200)
    report_type: str = Field(..., description="Type of report to generate")
    schedule: str = Field(..., description="Cron schedule expression")
    format: str = Field("html", description="Output format: pdf, html, csv")
    description: Optional[str] = Field(None, max_length=500)
    recipients: Optional[List[EmailStr]] = Field(None, description="Email recipients")
    filters: Optional[Dict[str, Any]] = Field(None, description="Report filters")


class ReportUpdate(BaseModel):
    """Update a scheduled report."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    report_type: Optional[str] = None
    schedule: Optional[str] = None
    format: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    recipients: Optional[List[EmailStr]] = None
    filters: Optional[Dict[str, Any]] = None


# ── Report Endpoints ────────────────────────────────────────────────


@router.get("/reports")
async def list_reports(user=Depends(get_auth_user)):
    """List all scheduled reports for the authenticated user."""
    try:
        reports = report_service.list_reports(user.id)
        return reports
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reports: {str(e)}",
        )


@router.post("/reports", status_code=status.HTTP_201_CREATED)
async def create_report(report: ReportCreate, user=Depends(get_auth_user)):
    """Create a new scheduled report."""
    try:
        if report.report_type not in VALID_REPORT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid report type. Valid types: {', '.join(VALID_REPORT_TYPES)}",
            )
        if report.format not in VALID_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid format. Valid formats: {', '.join(VALID_FORMATS)}",
            )

        result = report_service.create_report(
            user_id=user.id,
            name=report.name,
            report_type=report.report_type,
            schedule=report.schedule,
            format=report.format,
            description=report.description,
            recipients=report.recipients,
            filters=report.filters,
        )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create report: {str(e)}",
        )


@router.get("/reports/{report_id}")
async def get_report(report_id: str, user=Depends(get_auth_user)):
    """Get a scheduled report configuration."""
    report = report_service.get_report(report_id, user.id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return report


@router.put("/reports/{report_id}")
async def update_report(
    report_id: str, report: ReportUpdate, user=Depends(get_auth_user)
):
    """Update a scheduled report configuration."""
    try:
        if report.report_type and report.report_type not in VALID_REPORT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid report type. Valid types: {', '.join(VALID_REPORT_TYPES)}",
            )
        if report.format and report.format not in VALID_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid format. Valid formats: {', '.join(VALID_FORMATS)}",
            )

        result = report_service.update_report(
            report_id=report_id,
            user_id=user.id,
            name=report.name,
            description=report.description,
            report_type=report.report_type,
            schedule=report.schedule,
            format=report.format,
            recipients=report.recipients,
            filters=report.filters,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update report: {str(e)}",
        )


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_id: str, user=Depends(get_auth_user)):
    """Delete a scheduled report."""
    deleted = report_service.delete_report(report_id, user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )


@router.post("/reports/{report_id}/generate")
async def generate_report(report_id: str, user=Depends(get_auth_user)):
    """Generate a report now (on-demand)."""
    try:
        result = report_service.generate_report(report_id, user.id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


@router.get("/reports/{report_id}/history")
async def get_report_history(report_id: str, user=Depends(get_auth_user)):
    """Get generation history for a report."""
    history = report_service.get_report_history(report_id, user.id)
    return history


@router.get("/reports/{report_id}/download/{run_id}")
async def download_report(report_id: str, run_id: str, user=Depends(get_auth_user)):
    """Download a generated report file."""
    result = report_service.download_report(report_id, run_id, user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report run not found",
        )
    return result

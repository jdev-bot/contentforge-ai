"""
User management router for GDPR compliance and account operations.
"""
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.routers.auth import get_auth_user

router = APIRouter()


class AccountDeletionResponse(BaseModel):
    message: str
    deleted_at: Optional[str] = None
    grace_period_ends: Optional[str] = None


class DataExportResponse(BaseModel):
    export_id: str
    user_data: Dict[str, Any]
    generated_at: str
    expires_at: str


class UserDataSummary(BaseModel):
    profile: Dict[str, Any]
    content_count: int
    assets_count: int
    projects_count: int
    distributions_count: int
    organizations: List[Dict[str, Any]]


def serialize_datetime(obj):
    """Helper to serialize datetime objects for JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@router.get("/user/export-data", response_model=DataExportResponse)
async def export_user_data(user=Depends(get_auth_user)):
    """
    Export all user data as JSON for GDPR data portability.
    Returns comprehensive data including profile, content, projects, assets, and distributions.
    """
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    try:
        # Get user profile data
        profile_result = supabase.table("profiles").select("*").eq("id", user_id).execute()
        profile = profile_result.data[0] if profile_result.data else {}
        
        # Get content items
        content_result = supabase.table("content").select("*").eq("user_id", user_id).execute()
        content_items = content_result.data or []
        
        # Get projects
        projects_result = supabase.table("projects").select("*").eq("user_id", user_id).execute()
        projects = projects_result.data or []
        
        # Get content IDs for assets query
        content_ids = [item["id"] for item in content_items]
        assets = []
        if content_ids:
            assets_result = supabase.table("assets").select("*").in_("content_id", content_ids).execute()
            assets = assets_result.data or []
        
        # Get distributions
        distributions_result = supabase.table("distributions").select("*").eq("user_id", user_id).execute()
        distributions = distributions_result.data or []
        
        # Get organizations
        org_members_result = supabase.table("organization_members").select("*").eq("user_id", user_id).execute()
        org_members = org_members_result.data or []
        
        organizations = []
        for member in org_members:
            org_id = member.get("org_id")
            if org_id:
                org_result = supabase.table("organizations").select("*").eq("id", org_id).execute()
                if org_result.data:
                    org_data = org_result.data[0]
                    org_data["membership_role"] = member.get("role")
                    organizations.append(org_data)
        
        # Get usage statistics
        usage_result = supabase.table("usage_logs").select("*").eq("user_id", user_id).execute()
        usage_logs = usage_result.data or []
        
        # Compile export data
        export_data = {
            "export_metadata": {
                "user_id": user_id,
                "email": user.email,
                "export_date": datetime.now(timezone.utc).isoformat(),
                "version": "1.0",
            },
            "profile": {
                "id": user_id,
                "email": user.email,
                "full_name": profile.get("full_name"),
                "created_at": profile.get("created_at"),
                "updated_at": profile.get("updated_at"),
                "subscription_tier": profile.get("subscription_tier", "free"),
                "monthly_usage_count": profile.get("monthly_usage_count", 0),
            },
            "content": content_items,
            "projects": projects,
            "assets": assets,
            "distributions": distributions,
            "organizations": organizations,
            "usage_logs": usage_logs,
        }
        
        # Generate unique export ID
        export_id = f"export_{user_id}_{int(datetime.now(timezone.utc).timestamp())}"
        
        return DataExportResponse(
            export_id=export_id,
            user_data=export_data,
            generated_at=datetime.now(timezone.utc).isoformat(),
            expires_at=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export user data: {str(e)}",
        )


@router.delete("/user/account", response_model=AccountDeletionResponse)
async def delete_user_account(user=Depends(get_auth_user)):
    """
    Soft delete user account with 30-day grace period (GDPR-compliant).
    
    The account is marked as deleted but retained for 30 days to allow recovery.
    After the grace period, data is permanently deleted.
    """
    supabase = get_supabase_client()
    admin_client = get_supabase_admin_client()
    user_id = str(user.id)
    
    try:
        # Check if already scheduled for deletion
        existing = supabase.table("deletion_requests").select("*").eq("user_id", user_id).execute()
        if existing.data:
            # Already scheduled, return existing info
            deletion = existing.data[0]
            return AccountDeletionResponse(
                message="Account deletion already scheduled",
                deleted_at=deletion.get("created_at"),
                grace_period_ends=deletion.get("scheduled_deletion_at"),
            )
        
        # Calculate deletion date (30 days from now)
        deletion_date = datetime.now(timezone.utc) + timedelta(days=30)
        
        # Create deletion request record
        deletion_request = {
            "user_id": user_id,
            "email": user.email,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "scheduled_deletion_at": deletion_date.isoformat(),
            "status": "pending",
            "content_deleted": False,
            "projects_deleted": False,
            "assets_deleted": False,
        }
        
        supabase.table("deletion_requests").insert(deletion_request).execute()
        
        # Mark user as pending deletion in profiles
        supabase.table("profiles").update({
            "deletion_pending": True,
            "deletion_scheduled_at": deletion_date.isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", user_id).execute()
        
        # Note: Actual data deletion happens after grace period via scheduled job
        # For now, we just mark the account
        
        return AccountDeletionResponse(
            message="Account scheduled for deletion. You have 30 days to restore your account by logging in.",
            deleted_at=datetime.now(timezone.utc).isoformat(),
            grace_period_ends=deletion_date.isoformat(),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule account deletion: {str(e)}",
        )


@router.post("/user/account/restore")
async def restore_user_account(user=Depends(get_auth_user)):
    """
    Restore a user account that was scheduled for deletion (within grace period).
    """
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    try:
        # Check if there's a pending deletion request
        deletion_result = supabase.table("deletion_requests").select("*").eq("user_id", user_id).eq("status", "pending").execute()
        
        if not deletion_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pending deletion request found for this account",
            )
        
        # Cancel the deletion
        supabase.table("deletion_requests").update({
            "status": "cancelled",
            "cancelled_at": datetime.now(timezone.utc).isoformat(),
        }).eq("user_id", user_id).eq("status", "pending").execute()
        
        # Restore the profile
        supabase.table("profiles").update({
            "deletion_pending": False,
            "deletion_scheduled_at": None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", user_id).execute()
        
        return {"message": "Account restored successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restore account: {str(e)}",
        )


@router.get("/user/deletion-status")
async def get_deletion_status(user=Depends(get_auth_user)):
    """
    Check the status of an account deletion request.
    """
    supabase = get_supabase_client()
    user_id = str(user.id)
    
    try:
        deletion_result = supabase.table("deletion_requests").select("*").eq("user_id", user_id).order("requested_at", desc=True).limit(1).execute()
        
        if not deletion_result.data:
            return {
                "deletion_scheduled": False,
                "message": "No deletion request found",
            }
        
        deletion = deletion_result.data[0]
        return {
            "deletion_scheduled": deletion.get("status") == "pending",
            "status": deletion.get("status"),
            "requested_at": deletion.get("requested_at"),
            "scheduled_deletion_at": deletion.get("scheduled_deletion_at"),
            "days_remaining": max(0, 30 - (datetime.now(timezone.utc) - datetime.fromisoformat(deletion.get("requested_at").replace("Z", "+00:00"))).days),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deletion status: {str(e)}",
        )

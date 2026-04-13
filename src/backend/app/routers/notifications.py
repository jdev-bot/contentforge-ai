"""
Notifications router for email preferences and settings.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any

from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user

router = APIRouter()


class EmailPreferencesUpdate(BaseModel):
    """Email preferences update model."""
    marketing_emails: bool = Field(default=True, description="Receive marketing and promotional emails")
    usage_alerts: bool = Field(default=True, description="Receive usage limit alerts")
    weekly_digest: bool = Field(default=True, description="Receive weekly usage summaries")
    feature_announcements: bool = Field(default=True, description="Receive new feature announcements")
    invoice_receipts: bool = Field(default=True, description="Receive invoice receipts")
    digest_frequency: str = Field(default="weekly", description="Digest frequency: daily, weekly, monthly")


class EmailPreferencesResponse(BaseModel):
    """Email preferences response model."""
    marketing_emails: bool
    usage_alerts: bool
    weekly_digest: bool
    feature_announcements: bool
    invoice_receipts: bool
    digest_frequency: str
    updated_at: str = None


@router.get("/notifications/preferences", response_model=EmailPreferencesResponse)
async def get_email_preferences(user=Depends(get_auth_user)):
    """Get current user's email notification preferences."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("profiles").select(
            "email_preferences, updated_at"
        ).eq("id", str(user.id)).single().execute()
        
        if result.data and result.data.get("email_preferences"):
            prefs = result.data["email_preferences"]
            return EmailPreferencesResponse(
                marketing_emails=prefs.get("marketing_emails", True),
                usage_alerts=prefs.get("usage_alerts", True),
                weekly_digest=prefs.get("weekly_digest", True),
                feature_announcements=prefs.get("feature_announcements", True),
                invoice_receipts=prefs.get("invoice_receipts", True),
                digest_frequency=prefs.get("digest_frequency", "weekly"),
                updated_at=result.data.get("updated_at"),
            )
        
        # Return defaults if no preferences set
        return EmailPreferencesResponse(
            marketing_emails=True,
            usage_alerts=True,
            weekly_digest=True,
            feature_announcements=True,
            invoice_receipts=True,
            digest_frequency="weekly",
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch preferences: {str(e)}"
        )


@router.patch("/notifications/preferences", response_model=EmailPreferencesResponse)
async def update_email_preferences(
    preferences: EmailPreferencesUpdate,
    user=Depends(get_auth_user)
):
    """Update email notification preferences."""
    supabase = get_supabase_client()
    
    try:
        # Update profile with new preferences
        prefs_dict = preferences.model_dump()
        
        result = supabase.table("profiles").update({
            "email_preferences": prefs_dict,
            "updated_at": "now()"
        }).eq("id", str(user.id)).execute()
        
        # Return updated preferences
        return EmailPreferencesResponse(
            **prefs_dict,
            updated_at="now()",
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.get("/notifications/history")
async def get_email_history(
    limit: int = 20,
    offset: int = 0,
    user=Depends(get_auth_user)
):
    """Get email history for current user."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("email_tracking").select("*").eq(
            "user_id", str(user.id)
        ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        return {
            "emails": result.data if result.data else [],
            "total": len(result.data) if result.data else 0,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch email history: {str(e)}"
        )


@router.post("/notifications/unsubscribe")
async def unsubscribe_from_all(user=Depends(get_auth_user)):
    """Unsubscribe from all non-essential emails."""
    supabase = get_supabase_client()
    
    try:
        # Set all marketing preferences to False
        result = supabase.table("profiles").update({
            "email_preferences": {
                "marketing_emails": False,
                "usage_alerts": True,  # Keep critical alerts
                "weekly_digest": False,
                "feature_announcements": False,
                "invoice_receipts": True,  # Keep receipts
                "digest_frequency": "weekly",
            },
            "unsubscribed_at": "now()",
            "updated_at": "now()"
        }).eq("id", str(user.id)).execute()
        
        return {"message": "Successfully unsubscribed from marketing emails"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to unsubscribe: {str(e)}"
        )


@router.post("/notifications/resubscribe")
async def resubscribe(user=Depends(get_auth_user)):
    """Resubscribe to all emails."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("profiles").update({
            "email_preferences": {
                "marketing_emails": True,
                "usage_alerts": True,
                "weekly_digest": True,
                "feature_announcements": True,
                "invoice_receipts": True,
                "digest_frequency": "weekly",
            },
            "unsubscribed_at": None,
            "updated_at": "now()"
        }).eq("id", str(user.id)).execute()
        
        return {"message": "Successfully resubscribed to all emails"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to resubscribe: {str(e)}"
        )


# Webhook for managing unsubscribe links
@router.get("/notifications/unsubscribe/{token}")
async def unsubscribe_via_token(token: str):
    """Handle unsubscribe via token (from email links)."""
    # In production, verify token and identify user
    # For now, this is a placeholder that redirects to settings
    return {
        "message": "Please log in to manage your notification preferences",
        "redirect_url": "/settings/notifications"
    }

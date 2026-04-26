"""
API Keys router — BYOK (Bring Your Own Key) management.

Users add, list, validate, and delete their own LLM provider API keys.
Keys are stored encrypted at rest and never returned unmasked.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.config import get_settings
from app.core.encryption import decrypt, encrypt, mask_key
from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.routers.auth import get_auth_user
from app.services.llm_service import PROVIDER_PRESETS

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_PROVIDERS = list(PROVIDER_PRESETS.keys()) + ["custom"]


# ============================================================================
# Request / Response Models
# ============================================================================

class CreateAPIKeyRequest(BaseModel):
    """Request to add a new API key."""
    provider: str = Field(..., description="LLM provider name")
    api_key: str = Field(..., min_length=8, description="Plain-text API key (encrypted before storage)")
    base_url: Optional[str] = Field(None, description="Custom base URL (required for 'custom' provider)")
    model: Optional[str] = Field(None, description="Custom model name override")
    label: Optional[str] = Field(None, max_length=100, description="Friendly label for this key")

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v):
        v = v.lower().strip()
        if v not in ALLOWED_PROVIDERS:
            raise ValueError(f"Unsupported provider. Choose from: {', '.join(ALLOWED_PROVIDERS)}")
        return v

    @model_validator(mode="after")
    def validate_base_url_for_custom(self):
        if self.provider == "custom" and not self.base_url:
            raise ValueError("base_url is required when provider is 'custom'")
        return self


class APIKeyResponse(BaseModel):
    """Response model — never includes the raw key."""
    id: str
    provider: str
    masked_key: str
    base_url: Optional[str]
    model: Optional[str]
    label: Optional[str]
    is_valid: bool
    last_validated_at: Optional[str]
    created_at: str
    updated_at: str


class ValidateResponse(BaseModel):
    """Response from key validation."""
    is_valid: bool
    message: str
    provider: str
    response_time_ms: Optional[float] = None


# ============================================================================
# Helpers
# ============================================================================

async def validate_key_against_provider(provider: str, api_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
    """Test an API key against the provider's models endpoint.

    Returns {is_valid, message, response_time_ms}.
    """
    import time as _time

    preset = PROVIDER_PRESETS.get(provider, {})
    models_url = base_url.rstrip("/") + "/models" if base_url else preset.get("models_url")

    if not models_url:
        return {"is_valid": False, "message": f"No models endpoint for provider '{provider}'", "response_time_ms": None}

    # Provider-specific auth headers
    headers: Dict[str, str] = {}
    params: Optional[Dict[str, str]] = None

    if provider == "google":
        # Google AI Studio / Gemini API uses x-goog-api-key header
        # and also accepts key as query param
        headers["x-goog-api-key"] = api_key
        params = {"key": api_key}
    elif provider == "openrouter":
        headers["Authorization"] = f"Bearer {api_key}"
        headers["HTTP-Referer"] = "https://contentforge.ai"
        headers["X-Title"] = "ContentForge AI"
    else:
        # Groq, Cerebras, and custom providers use Bearer auth
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        start = _time.time()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                models_url,
                headers=headers,
                params=params,
            )
        elapsed = round((_time.time() - start) * 1000, 2)

        if resp.status_code == 200:
            return {"is_valid": True, "message": f"{provider} API key is valid", "response_time_ms": elapsed}
        else:
            return {
                "is_valid": False,
                "message": f"API returned status {resp.status_code}",
                "response_time_ms": elapsed,
            }
    except Exception as exc:
        return {"is_valid": False, "message": f"Connection failed: {exc}", "response_time_ms": None}


def row_to_response(row: Dict) -> APIKeyResponse:
    """Convert a Supabase row dict to a masked APIKeyResponse."""
    raw_key = ""
    try:
        raw_key = decrypt(row["encrypted_key"])
    except Exception:
        pass  # decryption failure = corrupted key

    return APIKeyResponse(
        id=str(row["id"]),
        provider=row["provider"],
        masked_key=mask_key(raw_key) if raw_key else "***corrupted***",
        base_url=row.get("base_url"),
        model=row.get("model"),
        label=row.get("label"),
        is_valid=row.get("is_valid", False),
        last_validated_at=row.get("last_validated_at"),
        created_at=row.get("created_at", ""),
        updated_at=row.get("updated_at", ""),
    )


# ============================================================================
# Endpoints
# ============================================================================

@router.post("", response_model=APIKeyResponse, status_code=http_status.HTTP_201_CREATED)
async def create_api_key(
    request: CreateAPIKeyRequest,
    user=Depends(get_auth_user),
):
    """Add a new API key for the authenticated user.

    The key is validated against the provider before saving.
    One key per provider per user (upsert behavior).
    """
    user_id = str(user.id)

    # Validate the key works before saving
    validation = await validate_key_against_provider(
        request.provider, request.api_key, request.base_url
    )

    encrypted = encrypt(request.api_key)
    now = datetime.now(timezone.utc).isoformat()

    # Upsert: one key per provider per user
    admin = get_supabase_admin_client()
    upsert_data = {
        "user_id": user_id,
        "provider": request.provider,
        "encrypted_key": encrypted,
        "base_url": request.base_url,
        "model": request.model,
        "label": request.label,
        "is_valid": validation["is_valid"],
        "last_validated_at": now,
        "updated_at": now,
    }

    result = admin.table("api_keys").upsert(
        upsert_data,
        on_conflict="user_id,provider",
    ).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save API key")

    return row_to_response(result.data[0])


@router.get("", response_model=List[APIKeyResponse])
async def list_api_keys(user=Depends(get_auth_user)):
    """List all API keys for the authenticated user (masked)."""
    user_id = str(user.id)
    admin = get_supabase_admin_client()

    result = admin.table("api_keys").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()

    return [row_to_response(row) for row in (result.data or [])]


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: str,
    user=Depends(get_auth_user),
):
    """Get a specific API key by ID (masked)."""
    user_id = str(user.id)
    admin = get_supabase_admin_client()

    result = admin.table("api_keys").select("*").eq("id", key_id).eq("user_id", user_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="API key not found")

    return row_to_response(result.data[0])


@router.delete("/{key_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    user=Depends(get_auth_user),
):
    """Delete an API key."""
    user_id = str(user.id)
    admin = get_supabase_admin_client()

    # Verify ownership
    check = admin.table("api_keys").select("id").eq("id", key_id).eq("user_id", user_id).execute()
    if not check.data:
        raise HTTPException(status_code=404, detail="API key not found")

    admin.table("api_keys").delete().eq("id", key_id).eq("user_id", user_id).execute()


@router.post("/{key_id}/validate", response_model=ValidateResponse)
async def validate_api_key(
    key_id: str,
    user=Depends(get_auth_user),
):
    """Re-validate an existing API key and update its status."""
    user_id = str(user.id)
    admin = get_supabase_admin_client()

    result = admin.table("api_keys").select("*").eq("id", key_id).eq("user_id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="API key not found")

    row = result.data[0]
    try:
        raw_key = decrypt(row["encrypted_key"])
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to decrypt stored key")

    validation = await validate_key_against_provider(row["provider"], raw_key, row.get("base_url"))

    now = datetime.now(timezone.utc).isoformat()
    admin.table("api_keys").update({
        "is_valid": validation["is_valid"],
        "last_validated_at": now,
        "updated_at": now,
    }).eq("id", key_id).execute()

    return ValidateResponse(
        is_valid=validation["is_valid"],
        message=validation["message"],
        provider=row["provider"],
        response_time_ms=validation.get("response_time_ms"),
    )
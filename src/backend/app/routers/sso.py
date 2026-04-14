"""
SSO / OIDC API Router.

Provides endpoints for:
- Provider configuration CRUD (admin)
- Initiate SSO login (redirect user to IdP)
- Handle SSO callback (exchange code, provision/link user)
- List/unlink SSO identities for current user
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.routers.auth import get_auth_user
from app.services.sso_service import sso_service

router = APIRouter()


# ── Request / Response Models ──────────────────────────────────────


class ProviderCreate(BaseModel):
    """Create a new SSO provider configuration."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Provider short name (google, microsoft, okta, custom)",
    )
    display_name: str = Field(..., min_length=1, description="Human-readable name")
    client_id: str = Field(..., min_length=1, description="OIDC client ID")
    client_secret: str = Field(..., min_length=1, description="OIDC client secret")
    discovery_url: Optional[str] = Field(
        None, description="OIDC discovery document URL"
    )
    authorization_url: Optional[str] = Field(
        None, description="Override authorization endpoint"
    )
    token_url: Optional[str] = Field(None, description="Override token endpoint")
    userinfo_url: Optional[str] = Field(None, description="Override userinfo endpoint")
    scopes: str = Field("openid email profile", description="OIDC scopes")
    domain: Optional[str] = Field(None, description="Tenant/domain for provider")
    is_active: bool = Field(True, description="Whether provider is enabled")


class ProviderUpdate(BaseModel):
    """Update an SSO provider configuration."""

    display_name: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    discovery_url: Optional[str] = None
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    userinfo_url: Optional[str] = None
    scopes: Optional[str] = None
    domain: Optional[str] = None
    is_active: Optional[bool] = None


class ProviderResponse(BaseModel):
    """SSO provider configuration response."""

    id: str
    name: str
    display_name: str
    client_id: str
    # client_secret intentionally omitted from response
    discovery_url: Optional[str] = None
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    userinfo_url: Optional[str] = None
    scopes: str
    domain: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str


class SSOInitiateRequest(BaseModel):
    """Request to initiate SSO login."""

    provider: str = Field(
        ..., min_length=1, description="Provider name (google, microsoft, okta, custom)"
    )
    redirect_uri: str = Field(..., description="Callback URI for the SSO flow")
    link_user: bool = Field(
        False, description="If true, link SSO to existing authenticated account"
    )


class SSOInitiateResponse(BaseModel):
    """Response with the authorization URL to redirect the user to."""

    authorization_url: str
    state: str


class SSOCallbackRequest(BaseModel):
    """SSO callback with authorization code."""

    state: str = Field(..., description="State token from login initiation")
    code: str = Field(..., description="Authorization code from IdP")


class SSOCallbackResponse(BaseModel):
    """Result of SSO callback processing."""

    action: str  # "login", "register", "linked"
    user_id: str
    email: str
    full_name: Optional[str] = None
    is_new_user: bool


class SSOIdentityResponse(BaseModel):
    """An SSO identity linked to a user."""

    id: str
    provider: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    created_at: str


# ── Provider Configuration CRUD ────────────────────────────────────


@router.get("/sso/providers", response_model=List[ProviderResponse])
async def list_providers(user=Depends(get_auth_user)):
    """List all SSO provider configurations."""
    providers = sso_service.list_providers()
    # Strip client_secret from responses
    return [
        ProviderResponse(
            id=p["id"],
            name=p["name"],
            display_name=p["display_name"],
            client_id=p["client_id"],
            discovery_url=p.get("discovery_url"),
            authorization_url=p.get("authorization_url"),
            token_url=p.get("token_url"),
            userinfo_url=p.get("userinfo_url"),
            scopes=p.get("scopes", "openid email profile"),
            domain=p.get("domain"),
            is_active=p.get("is_active", True),
            created_at=p["created_at"],
            updated_at=p["updated_at"],
        )
        for p in providers
    ]


@router.get("/sso/providers/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: str, user=Depends(get_auth_user)):
    """Get a single SSO provider configuration."""
    provider = sso_service.get_provider(provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found"
        )
    return ProviderResponse(
        id=provider["id"],
        name=provider["name"],
        display_name=provider["display_name"],
        client_id=provider["client_id"],
        discovery_url=provider.get("discovery_url"),
        authorization_url=provider.get("authorization_url"),
        token_url=provider.get("token_url"),
        userinfo_url=provider.get("userinfo_url"),
        scopes=provider.get("scopes", "openid email profile"),
        domain=provider.get("domain"),
        is_active=provider.get("is_active", True),
        created_at=provider["created_at"],
        updated_at=provider["updated_at"],
    )


@router.post(
    "/sso/providers",
    response_model=ProviderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_provider(body: ProviderCreate, user=Depends(get_auth_user)):
    """Create a new SSO provider configuration."""
    try:
        provider = sso_service.create_provider(
            name=body.name,
            display_name=body.display_name,
            client_id=body.client_id,
            client_secret=body.client_secret,
            discovery_url=body.discovery_url,
            authorization_url=body.authorization_url,
            token_url=body.token_url,
            userinfo_url=body.userinfo_url,
            scopes=body.scopes,
            domain=body.domain,
            is_active=body.is_active,
        )
        return ProviderResponse(
            id=provider["id"],
            name=provider["name"],
            display_name=provider["display_name"],
            client_id=provider["client_id"],
            discovery_url=provider.get("discovery_url"),
            authorization_url=provider.get("authorization_url"),
            token_url=provider.get("token_url"),
            userinfo_url=provider.get("userinfo_url"),
            scopes=provider.get("scopes", "openid email profile"),
            domain=provider.get("domain"),
            is_active=provider.get("is_active", True),
            created_at=provider["created_at"],
            updated_at=provider["updated_at"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create provider: {exc}",
        )


@router.patch("/sso/providers/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: str, body: ProviderUpdate, user=Depends(get_auth_user)
):
    """Update an SSO provider configuration."""
    fields = body.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    updated = sso_service.update_provider(provider_id, **fields)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found"
        )
    return ProviderResponse(
        id=updated["id"],
        name=updated["name"],
        display_name=updated["display_name"],
        client_id=updated["client_id"],
        discovery_url=updated.get("discovery_url"),
        authorization_url=updated.get("authorization_url"),
        token_url=updated.get("token_url"),
        userinfo_url=updated.get("userinfo_url"),
        scopes=updated.get("scopes", "openid email profile"),
        domain=updated.get("domain"),
        is_active=updated.get("is_active", True),
        created_at=updated["created_at"],
        updated_at=updated["updated_at"],
    )


@router.delete("/sso/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(provider_id: str, user=Depends(get_auth_user)):
    """Delete an SSO provider configuration."""
    deleted = sso_service.delete_provider(provider_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found"
        )


# ── SSO Login Flow ────────────────────────────────────────────────


@router.post("/sso/login", response_model=SSOInitiateResponse)
async def initiate_sso_login(
    body: SSOInitiateRequest, user=Depends(get_auth_user) if True else None
):
    """
    Initiate SSO login.

    If `link_user` is true, the current authenticated user's account will be
    linked to the SSO identity after successful authentication.
    """
    link_user_id = None
    if body.link_user:
        # User must be authenticated to link
        link_user_id = user.id

    try:
        result = sso_service.initiate_login(
            provider_name=body.provider,
            redirect_uri=body.redirect_uri,
            link_user_id=link_user_id,
        )
        return SSOInitiateResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate SSO login: {exc}",
        )


@router.post("/sso/login/public", response_model=SSOInitiateResponse)
async def initiate_sso_login_public(body: SSOInitiateRequest):
    """
    Initiate SSO login without requiring authentication.
    Used for initial SSO login where user has no session yet.
    """
    try:
        result = sso_service.initiate_login(
            provider_name=body.provider,
            redirect_uri=body.redirect_uri,
            link_user_id=None,
        )
        return SSOInitiateResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate SSO login: {exc}",
        )


@router.post("/sso/callback", response_model=SSOCallbackResponse)
async def sso_callback(body: SSOCallbackRequest):
    """
    Handle SSO callback after IdP authentication.
    Exchanges the authorization code for tokens, provisions/links user,
    and returns user info.
    """
    try:
        result = sso_service.handle_callback(
            state=body.state,
            code=body.code,
        )
        return SSOCallbackResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SSO callback failed: {exc}",
        )


# ── SSO Identity Management ──────────────────────────────────────


@router.get("/sso/identities", response_model=List[SSOIdentityResponse])
async def list_user_identities(user=Depends(get_auth_user)):
    """List SSO identities linked to the current user."""
    identities = sso_service.list_user_identities(str(user.id))
    return [SSOIdentityResponse(**i) for i in identities]


@router.delete("/sso/identities/{identity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_identity(identity_id: str, user=Depends(get_auth_user)):
    """Unlink an SSO identity from the current user."""
    deleted = sso_service.unlink_identity(identity_id, str(user.id))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Identity not found or not authorized to unlink",
        )


# ── Available SSO Providers (public) ─────────────────────────────


class AvailableProvider(BaseModel):
    """Public provider info (no secrets)."""

    name: str
    display_name: str
    is_active: bool


@router.get("/sso/available", response_model=List[AvailableProvider])
async def list_available_providers():
    """List available SSO providers (public endpoint, no auth required)."""
    providers = sso_service.list_providers()
    return [
        AvailableProvider(
            name=p["name"],
            display_name=p["display_name"],
            is_active=p.get("is_active", True),
        )
        for p in providers
        if p.get("is_active", True)
    ]

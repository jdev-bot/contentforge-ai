"""
SAML 2.0 API Router.

Provides endpoints for:
- SAML IdP provider configuration CRUD (admin)
- SP-initiated SSO login (redirect to IdP)
- SAML ACS (Assertion Consumer Service) callback
- Single Logout (SLO) initiation and response
- SAML identity management (list, unlink)
- Attribute mapping configuration
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.routers.auth import get_auth_user
from app.services.saml_service import saml_service

router = APIRouter()


# ── Request / Response Models ──────────────────────────────────────


class SAMLProviderCreate(BaseModel):
    """Create a new SAML IdP provider configuration."""
    name: str = Field(..., min_length=1, max_length=100, description="Provider short name (okta, onelogin, azure-ad, custom)")
    display_name: str = Field(..., min_length=1, description="Human-readable name")
    entity_id: str = Field(..., min_length=1, description="IdP Entity ID")
    sso_url: str = Field(..., description="IdP SSO URL (SingleSignOnService)")
    slo_url: Optional[str] = Field(None, description="IdP SLO URL (SingleLogoutService)")
    metadata_url: Optional[str] = Field(None, description="IdP Metadata URL (auto-fetch configuration)")
    metadata_xml: Optional[str] = Field(None, description="Raw IdP metadata XML (overrides metadata_url)")
    certificate: Optional[str] = Field(None, description="IdP X.509 signing certificate (PEM or base64)")
    attribute_mapping: Optional[Dict[str, str]] = Field(None, description="SAML attribute to local field mapping")
    org_id: Optional[str] = Field(None, description="Organization ID if org-scoped")
    is_active: bool = Field(True, description="Whether provider is enabled")


class SAMLProviderUpdate(BaseModel):
    """Update a SAML IdP provider configuration."""
    display_name: Optional[str] = None
    entity_id: Optional[str] = None
    sso_url: Optional[str] = None
    slo_url: Optional[str] = None
    metadata_url: Optional[str] = None
    metadata_xml: Optional[str] = None
    certificate: Optional[str] = None
    attribute_mapping: Optional[Dict[str, str]] = None
    org_id: Optional[str] = None
    is_active: Optional[bool] = None


class SAMLProviderResponse(BaseModel):
    """SAML provider configuration response."""
    id: str
    name: str
    display_name: str
    entity_id: str
    sso_url: str
    slo_url: Optional[str] = None
    metadata_url: Optional[str] = None
    # certificate and metadata_xml intentionally omitted from response
    attribute_mapping: Optional[Dict[str, str]] = None
    org_id: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str


class SAMLMetadataURLRequest(BaseModel):
    """Request to fetch and parse IdP metadata from URL."""
    metadata_url: str = Field(..., description="URL to the IdP metadata XML")


class SAMLMetadataResponse(BaseModel):
    """Parsed IdP metadata."""
    entity_id: str
    sso_url: str
    slo_url: Optional[str] = None
    certificate: Optional[str] = None
    metadata_xml: str


class SAMLLoginRequest(BaseModel):
    """Request to initiate SP-initiated SAML SSO login."""
    provider_id: str = Field(..., description="SAML provider ID")
    redirect_uri: str = Field(..., description="Assertion Consumer Service URL")
    relay_state: Optional[str] = Field(None, description="RelayState to pass through the flow")


class SAMLLoginResponse(BaseModel):
    """Response with the IdP login redirect URL."""
    login_url: str
    state: str
    saml_request_id: str


class SAMLAcsRequest(BaseModel):
    """SAML Assertion Consumer Service callback."""
    state: str = Field(..., description="State token from login initiation")
    saml_response: str = Field(..., description="Base64-encoded SAML Response from IdP")


class SAMLAcsResponse(BaseModel):
    """Result of SAML ACS processing."""
    action: str  # "login", "register"
    user_id: str
    email: str
    full_name: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None
    is_new_user: bool


class SAMLLogoutRequest(BaseModel):
    """Request to initiate SAML SLO."""
    provider_id: str = Field(..., description="SAML provider ID")
    name_id: str = Field(..., description="User's NameID from SAML assertion")
    session_index: Optional[str] = Field(None, description="Session index from assertion")
    redirect_uri: Optional[str] = Field(None, description="Post-logout redirect URI")


class SAMLLogoutResponse(BaseModel):
    """Response with SLO redirect URL."""
    logout_url: str
    state: str
    saml_request_id: str


class SAMLIdentityResponse(BaseModel):
    """A SAML identity linked to a user."""
    id: str
    provider_id: str
    name_id: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    created_at: str


# ── Provider Configuration CRUD ────────────────────────────────────


@router.get("/saml/providers", response_model=List[SAMLProviderResponse])
async def list_saml_providers(user=Depends(get_auth_user), org_id: Optional[str] = None):
    """List all SAML provider configurations."""
    providers = saml_service.list_providers(org_id=org_id)
    return [
        SAMLProviderResponse(
            id=p["id"],
            name=p["name"],
            display_name=p["display_name"],
            entity_id=p["entity_id"],
            sso_url=p["sso_url"],
            slo_url=p.get("slo_url"),
            metadata_url=p.get("metadata_url"),
            attribute_mapping=_parse_json_field(p.get("attribute_mapping")),
            org_id=p.get("org_id"),
            is_active=p.get("is_active", True),
            created_at=p["created_at"],
            updated_at=p["updated_at"],
        )
        for p in providers
    ]


@router.get("/saml/providers/{provider_id}", response_model=SAMLProviderResponse)
async def get_saml_provider(provider_id: str, user=Depends(get_auth_user)):
    """Get a single SAML provider configuration."""
    provider = saml_service.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SAML provider not found")
    return SAMLProviderResponse(
        id=provider["id"],
        name=provider["name"],
        display_name=provider["display_name"],
        entity_id=provider["entity_id"],
        sso_url=provider["sso_url"],
        slo_url=provider.get("slo_url"),
        metadata_url=provider.get("metadata_url"),
        attribute_mapping=_parse_json_field(provider.get("attribute_mapping")),
        org_id=provider.get("org_id"),
        is_active=provider.get("is_active", True),
        created_at=provider["created_at"],
        updated_at=provider["updated_at"],
    )


@router.post("/saml/providers", response_model=SAMLProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_saml_provider(body: SAMLProviderCreate, user=Depends(get_auth_user)):
    """Create a new SAML IdP provider configuration."""
    try:
        provider = saml_service.create_provider(
            name=body.name,
            display_name=body.display_name,
            entity_id=body.entity_id,
            sso_url=body.sso_url,
            slo_url=body.slo_url,
            metadata_url=body.metadata_url,
            metadata_xml=body.metadata_xml,
            certificate=body.certificate,
            attribute_mapping=body.attribute_mapping,
            org_id=body.org_id,
            is_active=body.is_active,
        )
        return SAMLProviderResponse(
            id=provider["id"],
            name=provider["name"],
            display_name=provider["display_name"],
            entity_id=provider["entity_id"],
            sso_url=provider["sso_url"],
            slo_url=provider.get("slo_url"),
            metadata_url=provider.get("metadata_url"),
            attribute_mapping=_parse_json_field(provider.get("attribute_mapping")),
            org_id=provider.get("org_id"),
            is_active=provider.get("is_active", True),
            created_at=provider["created_at"],
            updated_at=provider["updated_at"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create SAML provider: {exc}",
        )


@router.patch("/saml/providers/{provider_id}", response_model=SAMLProviderResponse)
async def update_saml_provider(provider_id: str, body: SAMLProviderUpdate, user=Depends(get_auth_user)):
    """Update a SAML provider configuration."""
    fields = body.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    updated = saml_service.update_provider(provider_id, **fields)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SAML provider not found")
    return SAMLProviderResponse(
        id=updated["id"],
        name=updated["name"],
        display_name=updated["display_name"],
        entity_id=updated["entity_id"],
        sso_url=updated["sso_url"],
        slo_url=updated.get("slo_url"),
        metadata_url=updated.get("metadata_url"),
        attribute_mapping=_parse_json_field(updated.get("attribute_mapping")),
        org_id=updated.get("org_id"),
        is_active=updated.get("is_active", True),
        created_at=updated["created_at"],
        updated_at=updated["updated_at"],
    )


@router.delete("/saml/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saml_provider(provider_id: str, user=Depends(get_auth_user)):
    """Delete a SAML provider configuration."""
    deleted = saml_service.delete_provider(provider_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SAML provider not found")


# ── Metadata Fetch & Parse ────────────────────────────────────────


@router.post("/saml/metadata/fetch", response_model=SAMLMetadataResponse)
async def fetch_saml_metadata(body: SAMLMetadataURLRequest, user=Depends(get_auth_user)):
    """Fetch and parse IdP metadata from a URL."""
    try:
        metadata_xml = saml_service._fetch_idp_metadata(body.metadata_url)
        parsed = saml_service._parse_idp_metadata(metadata_xml)
        return SAMLMetadataResponse(
            entity_id=parsed.get("entity_id", ""),
            sso_url=parsed.get("sso_url", ""),
            slo_url=parsed.get("slo_url"),
            certificate=parsed.get("certificate"),
            metadata_xml=metadata_xml,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch/parse IdP metadata: {exc}",
        )


# ── Attribute Mapping ─────────────────────────────────────────────


class AttributeMappingUpdate(BaseModel):
    attribute_mapping: Dict[str, str] = Field(..., description="SAML attribute name to local field mapping")


@router.patch("/saml/providers/{provider_id}/attribute-mapping", response_model=SAMLProviderResponse)
async def update_attribute_mapping(provider_id: str, body: AttributeMappingUpdate, user=Depends(get_auth_user)):
    """Update attribute mapping for a SAML provider."""
    updated = saml_service.update_provider(provider_id, attribute_mapping=body.attribute_mapping)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SAML provider not found")
    return SAMLProviderResponse(
        id=updated["id"],
        name=updated["name"],
        display_name=updated["display_name"],
        entity_id=updated["entity_id"],
        sso_url=updated["sso_url"],
        slo_url=updated.get("slo_url"),
        metadata_url=updated.get("metadata_url"),
        attribute_mapping=_parse_json_field(updated.get("attribute_mapping")),
        org_id=updated.get("org_id"),
        is_active=updated.get("is_active", True),
        created_at=updated["created_at"],
        updated_at=updated["updated_at"],
    )


# ── SSO Login Flow ────────────────────────────────────────────────


@router.post("/saml/login", response_model=SAMLLoginResponse)
async def initiate_saml_login(body: SAMLLoginRequest, user=Depends(get_auth_user) if False else None):
    """Initiate SP-initiated SAML SSO login."""
    try:
        result = saml_service.initiate_sso_login(
            provider_id=body.provider_id,
            redirect_uri=body.redirect_uri,
            relay_state=body.relay_state,
        )
        return SAMLLoginResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate SAML login: {exc}",
        )


@router.post("/saml/login/public", response_model=SAMLLoginResponse)
async def initiate_saml_login_public(body: SAMLLoginRequest):
    """Initiate SAML SSO login without requiring authentication."""
    try:
        result = saml_service.initiate_sso_login(
            provider_id=body.provider_id,
            redirect_uri=body.redirect_uri,
            relay_state=body.relay_state,
        )
        return SAMLLoginResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate SAML login: {exc}",
        )


@router.post("/saml/acs", response_model=SAMLAcsResponse)
async def saml_acs(body: SAMLAcsRequest):
    """
    SAML Assertion Consumer Service endpoint.
    Processes the SAMLResponse from the IdP after authentication.
    """
    try:
        result = saml_service.process_assertion(
            state=body.state,
            saml_response=body.saml_response,
        )
        return SAMLAcsResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SAML ACS processing failed: {exc}",
        )


# ── Single Logout (SLO) ────────────────────────────────────────────


@router.post("/saml/logout", response_model=SAMLLogoutResponse)
async def initiate_saml_logout(body: SAMLLogoutRequest, user=Depends(get_auth_user)):
    """Initiate SAML Single Logout."""
    try:
        result = saml_service.initiate_slo(
            provider_id=body.provider_id,
            name_id=body.name_id,
            session_index=body.session_index,
            redirect_uri=body.redirect_uri,
        )
        return SAMLLogoutResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate SAML logout: {exc}",
        )


@router.post("/saml/logout/response")
async def saml_logout_response(saml_response: str = ""):
    """Handle SAML LogoutResponse from the IdP."""
    result = saml_service.handle_slo_response(saml_response=saml_response)
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SAML logout failed")
    return {"message": "Logged out successfully", "status": result["status"]}


# ── SAML Identity Management ──────────────────────────────────────


@router.get("/saml/identities", response_model=List[SAMLIdentityResponse])
async def list_user_saml_identities(user=Depends(get_auth_user)):
    """List SAML identities linked to the current user."""
    identities = saml_service.list_user_identities(str(user.id))
    return [SAMLIdentityResponse(**i) for i in identities]


@router.delete("/saml/identities/{identity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_saml_identity(identity_id: str, user=Depends(get_auth_user)):
    """Unlink a SAML identity from the current user."""
    deleted = saml_service.unlink_identity(identity_id, str(user.id))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Identity not found or not authorized to unlink",
        )


# ── Available SAML Providers (public) ─────────────────────────────


class AvailableSAMLProvider(BaseModel):
    """Public SAML provider info (no secrets)."""
    id: str
    name: str
    display_name: str
    is_active: bool


@router.get("/saml/available", response_model=List[AvailableSAMLProvider])
async def list_available_saml_providers(org_id: Optional[str] = None):
    """List available SAML providers (public endpoint, no auth required)."""
    providers = saml_service.list_providers(org_id=org_id)
    return [
        AvailableSAMLProvider(
            id=p["id"],
            name=p["name"],
            display_name=p["display_name"],
            is_active=p.get("is_active", True),
        )
        for p in providers
        if p.get("is_active", True)
    ]


# ── Helper ─────────────────────────────────────────────────────────


def _parse_json_field(value: Any) -> Any:
    """Parse a JSON string field, returning the original value if not a string."""
    if isinstance(value, str):
        import json
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
    return value
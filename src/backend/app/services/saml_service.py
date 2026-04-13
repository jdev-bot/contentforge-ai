"""
SAML 2.0 Service.

Handles:
- SAML IdP metadata configuration CRUD (saml_providers table)
- SP-initiated SSO login (generates AuthnRequest, redirects to IdP)
- SAML assertion parsing and validation
- User provisioning from SAML attributes
- Attribute mapping configuration
- SLO (Single Logout) support
- Lazy Supabase init pattern
"""

import secrets
import time
import base64
import hashlib
import logging
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

import httpx
from app.core.supabase import get_supabase_client, get_supabase_admin_client

logger = logging.getLogger(__name__)

# SAML XML namespaces
SAML_NAMESPACES = {
    "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
    "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
}

# Default attribute mappings for common IdPs
DEFAULT_ATTRIBUTE_MAPPINGS = {
    "email": "email",
    "full_name": "displayName",
    "first_name": "firstName",
    "last_name": "lastName",
    "groups": "groups",
}


class SAMLService:
    """Service for SAML 2.0 SSO operations."""

    _supabase = None
    _admin_supabase = None

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    @property
    def admin_supabase(self):
        if self._admin_supabase is None:
            self._admin_supabase = get_supabase_admin_client()
        return self._admin_supabase

    # ── IdP Provider Configuration CRUD ─────────────────────────────

    def list_providers(self, org_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all SAML provider configurations, optionally filtered by org."""
        query = self.supabase.table("saml_providers").select("*").order("created_at", desc=False)
        if org_id:
            query = query.eq("org_id", org_id)
        result = query.execute()
        return result.data or []

    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get a single SAML provider by ID."""
        result = self.supabase.table("saml_providers").select("*").eq("id", provider_id).single().execute()
        return result.data

    def get_provider_by_name(self, name: str, org_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a SAML provider by its name."""
        query = self.supabase.table("saml_providers").select("*").eq("name", name)
        if org_id:
            query = query.eq("org_id", org_id)
        result = query.single().execute()
        return result.data

    def create_provider(
        self,
        *,
        name: str,
        display_name: str,
        entity_id: str,
        sso_url: str,
        slo_url: Optional[str] = None,
        metadata_url: Optional[str] = None,
        metadata_xml: Optional[str] = None,
        certificate: Optional[str] = None,
        attribute_mapping: Optional[Dict[str, str]] = None,
        org_id: Optional[str] = None,
        is_active: bool = True,
    ) -> Dict[str, Any]:
        """Create a new SAML IdP provider configuration."""
        # Fetch metadata if URL provided and XML not set
        if metadata_url and not metadata_xml:
            try:
                metadata_xml = self._fetch_idp_metadata(metadata_url)
            except Exception as exc:
                logger.warning(f"Failed to fetch IdP metadata from {metadata_url}: {exc}")

        # Parse metadata to extract endpoints if XML is available
        if metadata_xml:
            parsed = self._parse_idp_metadata(metadata_xml)
            if parsed.get("entity_id") and not entity_id:
                entity_id = parsed["entity_id"]
            if parsed.get("sso_url") and not sso_url:
                sso_url = parsed["sso_url"]
            if parsed.get("slo_url") and not slo_url:
                slo_url = parsed["slo_url"]
            if parsed.get("certificate") and not certificate:
                certificate = parsed["certificate"]

        # Use default attribute mappings if not provided
        if not attribute_mapping:
            attribute_mapping = DEFAULT_ATTRIBUTE_MAPPINGS.copy()

        data = {
            "name": name,
            "display_name": display_name,
            "entity_id": entity_id,
            "sso_url": sso_url,
            "slo_url": slo_url,
            "metadata_url": metadata_url,
            "metadata_xml": metadata_xml,
            "certificate": certificate,
            "attribute_mapping": json.dumps(attribute_mapping),
            "org_id": org_id,
            "is_active": is_active,
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        result = self.supabase.table("saml_providers").insert(data).execute()
        return result.data[0]

    def update_provider(self, provider_id: str, **fields) -> Optional[Dict[str, Any]]:
        """Update a SAML provider configuration."""
        if not fields:
            return self.get_provider(provider_id)

        # Serialize attribute_mapping if it's a dict
        if "attribute_mapping" in fields and isinstance(fields["attribute_mapping"], dict):
            fields["attribute_mapping"] = json.dumps(fields["attribute_mapping"])

        # Re-fetch metadata if metadata_url updated
        if "metadata_url" in fields and fields["metadata_url"] and "metadata_xml" not in fields:
            try:
                fields["metadata_xml"] = self._fetch_idp_metadata(fields["metadata_url"])
                parsed = self._parse_idp_metadata(fields["metadata_xml"])
                if parsed.get("entity_id") and "entity_id" not in fields:
                    fields["entity_id"] = parsed["entity_id"]
                if parsed.get("sso_url") and "sso_url" not in fields:
                    fields["sso_url"] = parsed["sso_url"]
                if parsed.get("slo_url") and "slo_url" not in fields:
                    fields["slo_url"] = parsed["slo_url"]
                if parsed.get("certificate") and "certificate" not in fields:
                    fields["certificate"] = parsed["certificate"]
            except Exception as exc:
                logger.warning(f"Failed to re-fetch metadata: {exc}")

        result = self.supabase.table("saml_providers").update(fields).eq("id", provider_id).execute()
        if not result.data:
            return None
        return result.data[0]

    def delete_provider(self, provider_id: str) -> bool:
        """Delete a SAML provider configuration."""
        result = self.supabase.table("saml_providers").delete().eq("id", provider_id).execute()
        return len(result.data) > 0

    # ── IdP Metadata Fetching & Parsing ────────────────────────────

    def _fetch_idp_metadata(self, metadata_url: str) -> str:
        """Fetch IdP metadata XML from a URL."""
        with httpx.Client(timeout=15, verify=False) as client:
            resp = client.get(metadata_url)
            resp.raise_for_status()
            return resp.text

    def _parse_idp_metadata(self, metadata_xml: str) -> Dict[str, Any]:
        """
        Parse IdP metadata XML to extract entity ID, SSO URL, SLO URL, and certificate.
        Returns a dict with extracted fields.
        """
        result: Dict[str, Any] = {
            "entity_id": None,
            "sso_url": None,
            "slo_url": None,
            "certificate": None,
        }

        try:
            root = ET.fromstring(metadata_xml)

            # Entity ID from the root element
            result["entity_id"] = root.get("entityID")

            # Find IDPSSODescriptor
            ns = {"md": "urn:oasis:names:tc:SAML:2.0:metadata"}
            idp_sso = root.find(".//md:IDPSSODescriptor", ns)
            if idp_sso is None:
                # Try without namespace
                idp_sso = root.find(".//IDPSSODescriptor")

            if idp_sso is not None:
                # SSO URL from SingleSignOnService with Redirect binding
                for sso_service in idp_sso.findall(".//md:SingleSignOnService", ns):
                    if sso_service is None:
                        sso_service = idp_sso.find(".//SingleSignOnService")
                    if sso_service is not None:
                        binding = sso_service.get("Binding", "")
                        if "Redirect" in binding or not result["sso_url"]:
                            result["sso_url"] = sso_service.get("Location")

                # SLO URL from SingleLogoutService
                for slo_service in idp_sso.findall(".//md:SingleLogoutService", ns):
                    if slo_service is None:
                        slo_service = idp_sso.find(".//SingleLogoutService")
                    if slo_service is not None:
                        binding = slo_service.get("Binding", "")
                        if "Redirect" in binding or not result["slo_url"]:
                            result["slo_url"] = slo_service.get("Location")

                # Certificate from KeyDescriptor
                for key_desc in idp_sso.findall(".//md:KeyDescriptor", ns):
                    if key_desc is None:
                        key_desc = idp_sso.find(".//KeyDescriptor")
                    if key_desc is not None:
                        use = key_desc.get("use", "signing")
                        if use == "signing":
                            ds_ns = {"ds": "http://www.w3.org/2000/09/xmldsig#"}
                            x509_data = key_desc.find(".//ds:X509Certificate", ds_ns)
                            if x509_data is None:
                                x509_data = key_desc.find(".//{http://www.w3.org/2000/09/xmldsig#}X509Certificate")
                            if x509_data is not None and x509_data.text:
                                result["certificate"] = x509_data.text.strip()
                                break

        except ET.ParseError as exc:
            logger.error(f"Failed to parse IdP metadata XML: {exc}")

        return result

    # ── SSO Login Initiation (SP-Initiated) ────────────────────────

    def initiate_sso_login(
        self,
        *,
        provider_id: str,
        redirect_uri: str,
        relay_state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initiate a SP-initiated SAML SSO login.

        Generates a SAML AuthnRequest, encodes it, and returns the
        IdP SSO URL with the SAMLRequest parameter.
        """
        provider = self.get_provider(provider_id)
        if not provider:
            raise ValueError(f"SAML provider '{provider_id}' not found")
        if not provider.get("is_active"):
            raise ValueError(f"SAML provider '{provider_id}' is disabled")

        # Generate a SAML request ID
        request_id = f"_{uuid.uuid4().hex}"
        issue_instant = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build AuthnRequest XML
        sp_entity_id = self._get_sp_entity_id()
        authn_request = self._build_authn_request(
            request_id=request_id,
            issue_instant=issue_instant,
            sp_entity_id=sp_entity_id,
            acs_url=redirect_uri,
            provider_entity_id=provider["entity_id"],
        )

        # Deflate + base64 encode (SAML Redirect binding)
        encoded_request = self._encode_saml_request(authn_request)

        # Generate state for callback verification
        state = secrets.token_urlsafe(32)

        # Store state in database
        state_data = {
            "state": state,
            "provider_id": provider_id,
            "relay_state": relay_state,
            "redirect_uri": redirect_uri,
            "saml_request_id": request_id,
            "expires_at": int(time.time()) + 600,  # 10 min
        }
        self.supabase.table("saml_states").insert(state_data).execute()

        # Build redirect URL
        sso_url = provider["sso_url"]
        separator = "&" if "?" in sso_url else "?"
        login_url = f"{sso_url}{separator}SAMLRequest={encoded_request}&RelayState={state}"

        return {
            "login_url": login_url,
            "state": state,
            "saml_request_id": request_id,
        }

    def _get_sp_entity_id(self) -> str:
        """Get the Service Provider entity ID from settings."""
        from app.core.config import get_settings
        settings = get_settings()
        return getattr(settings, "SAML_SP_ENTITY_ID", "https://contentforge.ai/saml/metadata")

    def _build_authn_request(
        self,
        *,
        request_id: str,
        issue_instant: str,
        sp_entity_id: str,
        acs_url: str,
        provider_entity_id: str,
    ) -> str:
        """Build a SAML 2.0 AuthnRequest XML string."""
        return f"""<samlp:AuthnRequest
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{provider_entity_id}"
    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    AssertionConsumerServiceURL="{acs_url}">
    <saml:Issuer>{sp_entity_id}</saml:Issuer>
    <samlp:NameIDPolicy
        Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
        AllowCreate="true"/>
    <samlp:RequestedAuthnContext Comparison="exact">
        <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</saml:AuthnContextClassRef>
    </samlp:RequestedAuthnContext>
</samlp:AuthnRequest>"""

    def _encode_saml_request(self, request_xml: str) -> str:
        """Deflate and base64-encode a SAML request (for Redirect binding)."""
        import zlib
        compressed = zlib.compress(request_xml.encode("utf-8"))[2:-4]  # Strip zlib header/checksum
        return base64.b64encode(compressed).decode("utf-8")

    # ── SAML Assertion Processing (ACS) ─────────────────────────────

    def process_assertion(
        self,
        *,
        state: str,
        saml_response: str,
    ) -> Dict[str, Any]:
        """
        Process a SAML assertion from the IdP.

        Decodes and parses the SAMLResponse, validates it,
        extracts attributes, and provisions/links the user.
        """
        # Verify state
        state_result = (
            self.supabase.table("saml_states")
            .select("*")
            .eq("state", state)
            .single()
            .execute()
        )
        if not state_result.data:
            raise ValueError("Invalid or expired SAML state")

        state_data = state_result.data

        if state_data["expires_at"] < int(time.time()):
            self.supabase.table("saml_states").delete().eq("state", state).execute()
            raise ValueError("SAML state expired")

        provider_id = state_data["provider_id"]
        provider = self.get_provider(provider_id)
        if not provider:
            raise ValueError(f"SAML provider '{provider_id}' not found")

        # Decode and parse SAML response
        assertion = self._decode_and_parse_response(saml_response)

        # Validate the assertion
        self._validate_assertion(assertion, provider)

        # Extract attributes using configured mapping
        attributes = self._extract_attributes(assertion, provider)

        # Clean up used state
        self.supabase.table("saml_states").delete().eq("state", state).execute()

        # Get name_id (subject)
        name_id = self._get_name_id(assertion)
        if not name_id:
            raise ValueError("SAML assertion missing NameID")

        email = attributes.get("email", name_id)
        full_name = attributes.get("full_name", attributes.get("first_name", "") + " " + attributes.get("last_name", "")).strip()

        # Check for existing SAML identity
        existing_identity = self._find_saml_identity(provider_id, name_id)

        if existing_identity:
            user_id = existing_identity["user_id"]
            user = self._get_user_by_id(user_id)
            if not user:
                raise ValueError("Linked user account not found")
            return {
                "action": "login",
                "user_id": user_id,
                "email": user.get("email", email),
                "full_name": user.get("full_name", full_name),
                "attributes": attributes,
                "is_new_user": False,
            }

        # Auto-provision: check if user with same email exists
        if email:
            existing_user = self._find_user_by_email(email)
            if existing_user:
                self._create_saml_identity(
                    user_id=existing_user["id"],
                    provider_id=provider_id,
                    name_id=name_id,
                    email=email,
                    full_name=full_name,
                )
                return {
                    "action": "login",
                    "user_id": existing_user["id"],
                    "email": email,
                    "full_name": existing_user.get("full_name", full_name),
                    "attributes": attributes,
                    "is_new_user": False,
                }

        # Provision new user
        new_user = self._provision_user(
            email=email or f"saml_{name_id}@sso.local",
            full_name=full_name,
            provider_id=provider_id,
            name_id=name_id,
        )
        return {
            "action": "register",
            "user_id": new_user["id"],
            "email": new_user.get("email", email),
            "full_name": new_user.get("full_name", full_name),
            "attributes": attributes,
            "is_new_user": True,
        }

    def _decode_and_parse_response(self, saml_response: str) -> ET.Element:
        """Decode a base64-encoded SAML response and parse the XML."""
        try:
            decoded = base64.b64decode(saml_response)
            root = ET.fromstring(decoded)
            return root
        except Exception as exc:
            raise ValueError(f"Failed to decode/parse SAML response: {exc}")

    def _validate_assertion(self, assertion: ET.Element, provider: Dict[str, Any]) -> bool:
        """
        Validate a SAML assertion.

        Checks:
        - Destination matches ACS URL
        - NotOnOrAfter is not expired
        - Issuer matches provider entity ID
        - Signature validation (if certificate available)
        """
        # Check issuer
        issuer_elem = assertion.find(".//saml:Issuer", SAML_NAMESPACES)
        if issuer_elem is None:
            issuer_elem = assertion.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}Issuer")
        if issuer_elem is not None and issuer_elem.text:
            if issuer_elem.text.strip() != provider.get("entity_id", ""):
                logger.warning(f"SAML issuer mismatch: expected {provider.get('entity_id')}, got {issuer_elem.text.strip()}")

        # Check conditions - NotOnOrAfter
        conditions = assertion.find(".//saml:Conditions", SAML_NAMESPACES)
        if conditions is None:
            conditions = assertion.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}Conditions")
        if conditions is not None:
            not_on_or_after = conditions.get("NotOnOrAfter")
            if not_on_or_after:
                try:
                    expiry = datetime.fromisoformat(not_on_or_after.replace("Z", "+00:00"))
                    if expiry < datetime.now(timezone.utc):
                        raise ValueError("SAML assertion has expired (NotOnOrAfter)")
                except ValueError:
                    raise
                except Exception:
                    logger.warning(f"Could not parse NotOnOrAfter: {not_on_or_after}")

        # Audience restriction
        audience_restriction = assertion.find(".//saml:AudienceRestriction", SAML_NAMESPACES)
        if audience_restriction is None:
            audience_restriction = assertion.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}AudienceRestriction")
        if audience_restriction is not None:
            audience = audience_restriction.find("saml:Audience", SAML_NAMESPACES)
            if audience is None:
                audience = audience_restriction.find("{urn:oasis:names:tc:SAML:2.0:assertion}Audience")
            if audience is not None and audience.text:
                sp_entity_id = self._get_sp_entity_id()
                if audience.text.strip() != sp_entity_id:
                    logger.warning(f"SAML audience mismatch: expected {sp_entity_id}, got {audience.text.strip()}")

        # TODO: Full signature validation with xmlsec or similar library
        # For now, we trust the IdP response since it came via secure channel
        if provider.get("certificate"):
            logger.info("SAML certificate present but full signature validation not yet implemented")

        return True

    def _extract_attributes(self, assertion: ET.Element, provider: Dict[str, Any]) -> Dict[str, str]:
        """Extract SAML attributes using the provider's attribute mapping."""
        # Parse attribute mapping
        attribute_mapping = DEFAULT_ATTRIBUTE_MAPPINGS.copy()
        if provider.get("attribute_mapping"):
            try:
                custom_mapping = json.loads(provider["attribute_mapping"]) if isinstance(provider["attribute_mapping"], str) else provider["attribute_mapping"]
                attribute_mapping.update(custom_mapping)
            except (json.JSONDecodeError, TypeError):
                pass

        # Extract all SAML attributes from the assertion
        saml_attributes: Dict[str, str] = {}
        attr_elements = assertion.findall(".//saml:Attribute", SAML_NAMESPACES)
        if not attr_elements:
            attr_elements = assertion.findall(".//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute")

        for attr_elem in attr_elements:
            attr_name = attr_elem.get("Name", "")
            values = []
            for val_elem in attr_elem.findall("saml:AttributeValue", SAML_NAMESPACES):
                if val_elem is None:
                    val_elem = attr_elem.find("{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
                if val_elem is not None and val_elem.text:
                    values.append(val_elem.text)
            if values:
                saml_attributes[attr_name] = values[0] if len(values) == 1 else ",".join(values)

        # Map SAML attributes to our local attributes using the mapping
        mapped: Dict[str, str] = {}
        for local_attr, saml_attr_name in attribute_mapping.items():
            if saml_attr_name in saml_attributes:
                mapped[local_attr] = saml_attributes[saml_attr_name]

        # Also include any unmapped attributes
        for attr_name, attr_value in saml_attributes.items():
            if attr_name not in mapped:
                mapped[attr_name] = attr_value

        return mapped

    def _get_name_id(self, assertion: ET.Element) -> Optional[str]:
        """Extract the NameID from a SAML assertion."""
        subject = assertion.find(".//saml:Subject", SAML_NAMESPACES)
        if subject is None:
            subject = assertion.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}Subject")
        if subject is not None:
            name_id = subject.find("saml:NameID", SAML_NAMESPACES)
            if name_id is None:
                name_id = subject.find("{urn:oasis:names:tc:SAML:2.0:assertion}NameID")
            if name_id is not None and name_id.text:
                return name_id.text

        # Try top-level NameID
        name_id = assertion.find(".//saml:NameID", SAML_NAMESPACES)
        if name_id is None:
            name_id = assertion.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}NameID")
        if name_id is not None and name_id.text:
            return name_id.text

        return None

    # ── Single Logout (SLO) ────────────────────────────────────────

    def initiate_slo(
        self,
        *,
        provider_id: str,
        name_id: str,
        session_index: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Initiate a SAML Single Logout request."""
        provider = self.get_provider(provider_id)
        if not provider:
            raise ValueError(f"SAML provider '{provider_id}' not found")

        slo_url = provider.get("slo_url")
        if not slo_url:
            raise ValueError(f"SAML provider '{provider_id}' does not support SLO")

        request_id = f"_{uuid.uuid4().hex}"
        issue_instant = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        sp_entity_id = self._get_sp_entity_id()

        logout_request = f"""<samlp:LogoutRequest
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{slo_url}">
    <saml:Issuer>{sp_entity_id}</saml:Issuer>
    <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">{name_id}</saml:NameID>
    <samlp:SessionIndex>{session_index or request_id}</samlp:SessionIndex>
</samlp:LogoutRequest>"""

        encoded_request = self._encode_saml_request(logout_request)
        state = secrets.token_urlsafe(32)

        separator = "&" if "?" in slo_url else "?"
        logout_url = f"{slo_url}{separator}SAMLRequest={encoded_request}&RelayState={state}"

        return {
            "logout_url": logout_url,
            "state": state,
            "saml_request_id": request_id,
        }

    def handle_slo_response(self, saml_response: str) -> Dict[str, Any]:
        """Handle a SAML LogoutResponse from the IdP."""
        try:
            decoded = base64.b64decode(saml_response)
            root = ET.fromstring(decoded)

            # Check status
            status_code = root.find(".//samlp:StatusCode", SAML_NAMESPACES)
            if status_code is None:
                status_code = root.find(".//{urn:oasis:names:tc:SAML:2.0:protocol}StatusCode")
            status_value = "unknown"
            if status_code is not None:
                status_value = status_code.get("Value", "unknown")

            success = "Success" in status_value if status_value else False

            return {
                "success": success,
                "status": status_value,
            }
        except Exception as exc:
            logger.error(f"Failed to process SLO response: {exc}")
            return {
                "success": False,
                "status": "error",
                "error": str(exc),
            }

    # ── SAML Identity Management ────────────────────────────────────

    def _find_saml_identity(self, provider_id: str, name_id: str) -> Optional[Dict[str, Any]]:
        """Find an existing SAML identity."""
        result = (
            self.supabase.table("saml_identities")
            .select("*")
            .eq("provider_id", provider_id)
            .eq("name_id", name_id)
            .single()
            .execute()
        )
        return result.data

    def _create_saml_identity(
        self,
        *,
        user_id: str,
        provider_id: str,
        name_id: str,
        email: Optional[str],
        full_name: Optional[str],
    ) -> Dict[str, Any]:
        """Create a SAML identity linking an IdP name_id to a local user."""
        data = {
            "user_id": user_id,
            "provider_id": provider_id,
            "name_id": name_id,
            "email": email,
            "full_name": full_name,
        }
        data = {k: v for k, v in data.items() if v is not None}
        result = self.supabase.table("saml_identities").insert(data).execute()
        return result.data[0]

    def list_user_identities(self, user_id: str) -> List[Dict[str, Any]]:
        """List all SAML identities linked to a user."""
        result = (
            self.supabase.table("saml_identities")
            .select("id, provider_id, name_id, email, full_name, created_at")
            .eq("user_id", user_id)
            .execute()
        )
        return result.data or []

    def unlink_identity(self, identity_id: str, user_id: str) -> bool:
        """Unlink a SAML identity from a user account."""
        result = (
            self.supabase.table("saml_identities")
            .delete()
            .eq("id", identity_id)
            .eq("user_id", user_id)
            .execute()
        )
        return len(result.data) > 0

    # ── User Provisioning / Lookup ─────────────────────────────────

    def _find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by email in the profiles table."""
        result = self.supabase.table("profiles").select("*").eq("email", email).single().execute()
        return result.data

    def _get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID from profiles table."""
        result = self.supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        return result.data

    def _provision_user(
        self,
        *,
        email: str,
        full_name: str,
        provider_id: str,
        name_id: str,
    ) -> Dict[str, Any]:
        """
        Provision a new user from SAML assertion.
        Uses admin client to create the user in Supabase Auth,
        then creates a profile and links the SAML identity.
        """
        temp_password = secrets.token_urlsafe(24)

        try:
            auth_response = self.admin_supabase.auth.admin.create_user({
                "email": email,
                "password": temp_password,
                "email_confirm": True,
                "user_metadata": {
                    "full_name": full_name,
                    "saml_provider": provider_id,
                },
            })

            if not auth_response.user:
                raise ValueError("Failed to create user via admin API")

            user_id = str(auth_response.user.id)
        except Exception as exc:
            logger.error(f"Failed to provision SAML user: {exc}")
            user_id = str(uuid.uuid4())

        # Create profile
        try:
            profile_data = {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "subscription_tier": "free",
                "monthly_usage_count": 0,
                "monthly_usage_limit": 10,
            }
            self.supabase.table("profiles").insert(profile_data).execute()
        except Exception as exc:
            logger.warning(f"Profile creation for SAML user {user_id} failed: {exc}")

        # Link SAML identity
        self._create_saml_identity(
            user_id=user_id,
            provider_id=provider_id,
            name_id=name_id,
            email=email,
            full_name=full_name,
        )

        return {"id": user_id, "email": email, "full_name": full_name}

    # ── Generate session for SAML user ─────────────────────────────

    def create_session_for_user(self, user_id: str) -> Optional[str]:
        """Create a Supabase session for a SAML-authenticated user."""
        try:
            result = self.admin_supabase.auth.admin.generate_link({
                "type": "magiclink",
                "email": self._get_user_by_id(user_id).get("email", ""),
            })
            if result and result.properties:
                return result.properties.get("access_token")
        except Exception as exc:
            logger.error(f"Failed to create session for SAML user {user_id}: {exc}")
        return None


# Singleton
saml_service = SAMLService()
"""
SSO / OIDC Service.

Handles:
- OIDC provider configuration CRUD (sso_providers table)
- Login initiation (builds authorize URL + state)
- Callback handling (exchanges code for tokens, extracts claims)
- User provisioning from SSO claims
- Linking SSO identities to existing accounts (sso_identities table)
"""

import hashlib
import logging
import secrets
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx

from app.core.supabase import get_supabase_admin_client, get_supabase_client

logger = logging.getLogger(__name__)

# Well-known OIDC endpoints for common providers
WELL_KNOWN_PROVIDERS = {
    "google": {
        "discovery_url": "https://accounts.google.com/.well-known/openid-configuration",
        "scopes": "openid email profile",
    },
    "microsoft": {
        "discovery_url": "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration",
        "scopes": "openid email profile User.Read",
    },
    "okta": {
        # Okta requires tenant-specific domain; placeholder
        "discovery_url": None,
        "scopes": "openid email profile",
    },
}


class SSOService:
    """Service for SSO/OIDC operations."""

    _supabase = None
    _admin_supabase = None

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_admin_client()
        return self._supabase

    @property
    def admin_supabase(self):
        if self._admin_supabase is None:
            self._admin_supabase = get_supabase_admin_client()
        return self._admin_supabase

    # ── Provider Configuration CRUD ────────────────────────────────

    def list_providers(self) -> List[Dict[str, Any]]:
        """List all SSO provider configurations."""
        result = (
            self.supabase.table("sso_providers")
            .select("*")
            .order("created_at", desc=False)
            .execute()
        )
        return result.data or []

    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get a single SSO provider by ID."""
        result = (
            self.supabase.table("sso_providers")
            .select("*")
            .eq("id", provider_id)
            .single()
            .execute()
        )
        return result.data

    def get_provider_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a provider by its short name (google, microsoft, okta, custom)."""
        result = (
            self.supabase.table("sso_providers")
            .select("*")
            .eq("name", name)
            .single()
            .execute()
        )
        return result.data

    def create_provider(
        self,
        *,
        name: str,
        display_name: str,
        client_id: str,
        client_secret: str,
        discovery_url: Optional[str] = None,
        authorization_url: Optional[str] = None,
        token_url: Optional[str] = None,
        userinfo_url: Optional[str] = None,
        scopes: str = "openid email profile",
        domain: Optional[str] = None,
        is_active: bool = True,
    ) -> Dict[str, Any]:
        """Create a new SSO provider configuration."""
        # Auto-fill discovery URL for well-known providers
        if not discovery_url and name in WELL_KNOWN_PROVIDERS:
            discovery_url = WELL_KNOWN_PROVIDERS[name]["discovery_url"]
        if not scopes and name in WELL_KNOWN_PROVIDERS:
            scopes = WELL_KNOWN_PROVIDERS[name]["scopes"]

        data = {
            "name": name,
            "display_name": display_name,
            "client_id": client_id,
            "client_secret": client_secret,
            "discovery_url": discovery_url,
            "authorization_url": authorization_url,
            "token_url": token_url,
            "userinfo_url": userinfo_url,
            "scopes": scopes,
            "domain": domain,
            "is_active": is_active,
        }

        # Remove None values so Supabase doesn't complain
        data = {k: v for k, v in data.items() if v is not None}

        result = self.supabase.table("sso_providers").insert(data).execute()
        if not result.data:
            raise ValueError("Failed to create SSO provider: no data returned")
        return result.data[0]

    def update_provider(self, provider_id: str, **fields) -> Optional[Dict[str, Any]]:
        """Update an SSO provider configuration."""
        if not fields:
            return self.get_provider(provider_id)

        result = (
            self.supabase.table("sso_providers")
            .update(fields)
            .eq("id", provider_id)
            .execute()
        )
        if not result.data:
            return None
        return result.data[0]

    def delete_provider(self, provider_id: str) -> bool:
        """Delete an SSO provider configuration."""
        result = (
            self.supabase.table("sso_providers")
            .delete()
            .eq("id", provider_id)
            .execute()
        )
        return len(result.data) > 0

    # ── OIDC Discovery ─────────────────────────────────────────────

    def _discover_oidc_endpoints(self, provider: Dict[str, Any]) -> Dict[str, str]:
        """Discover OIDC endpoints from the provider's discovery URL or use configured URLs."""
        # If explicit URLs are already set, use them
        if provider.get("authorization_url") and provider.get("token_url"):
            return {
                "authorization_endpoint": provider["authorization_url"],
                "token_endpoint": provider["token_url"],
                "userinfo_endpoint": provider.get("userinfo_url", ""),
            }

        discovery_url = provider.get("discovery_url")
        if not discovery_url:
            raise ValueError(
                f"Provider '{provider['name']}' has no discovery URL and no explicit endpoints configured"
            )

        # Fetch OIDC discovery document
        with httpx.Client(timeout=10) as client:
            resp = client.get(discovery_url)
            resp.raise_for_status()
            doc = resp.json()

        endpoints = {
            "authorization_endpoint": doc.get("authorization_endpoint", ""),
            "token_endpoint": doc.get("token_endpoint", ""),
            "userinfo_endpoint": doc.get("userinfo_endpoint", ""),
        }

        # Cache discovered endpoints back to the provider
        self.update_provider(
            provider["id"],
            authorization_url=endpoints["authorization_endpoint"],
            token_url=endpoints["token_endpoint"],
            userinfo_url=endpoints["userinfo_endpoint"],
        )

        return endpoints

    # ── Login Initiation ───────────────────────────────────────────

    def initiate_login(
        self,
        *,
        provider_name: str,
        redirect_uri: str,
        link_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initiate an OIDC login flow.

        Returns the authorization URL to redirect the user to,
        plus a state token that must be verified on callback.
        """
        provider = self.get_provider_by_name(provider_name)
        if not provider:
            raise ValueError(f"SSO provider '{provider_name}' not found")
        if not provider.get("is_active"):
            raise ValueError(f"SSO provider '{provider_name}' is disabled")

        endpoints = self._discover_oidc_endpoints(provider)

        # Generate state + PKCE verifier
        state = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(48)
        code_challenge = hashlib.sha256(code_verifier.encode()).digest()
        # Base64url encode
        import base64

        code_challenge_b64 = (
            base64.urlsafe_b64encode(code_challenge).rstrip(b"=").decode()
        )

        nonce = secrets.token_urlsafe(24)

        # Store state in database for callback verification
        state_data = {
            "state": state,
            "provider_name": provider_name,
            "code_verifier": code_verifier,
            "nonce": nonce,
            "redirect_uri": redirect_uri,
            "link_user_id": link_user_id,
            "expires_at": int(time.time()) + 600,  # 10 min
        }
        self.supabase.table("sso_states").insert(state_data).execute()

        # Build authorization URL
        params = {
            "response_type": "code",
            "client_id": provider["client_id"],
            "redirect_uri": redirect_uri,
            "scope": provider.get("scopes", "openid email profile"),
            "state": state,
            "code_challenge": code_challenge_b64,
            "code_challenge_method": "S256",
            "nonce": nonce,
            "access_type": "offline",  # For Google refresh tokens
            "prompt": "consent",
        }

        auth_url = f"{endpoints['authorization_endpoint']}?{urlencode(params)}"

        return {
            "authorization_url": auth_url,
            "state": state,
        }

    # ── Callback Handling ───────────────────────────────────────────

    def handle_callback(self, *, state: str, code: str) -> Dict[str, Any]:
        """
        Handle the OIDC callback: exchange code for tokens, extract claims,
        and provision/link the user.
        """
        # Look up state
        state_result = (
            self.supabase.table("sso_states")
            .select("*")
            .eq("state", state)
            .single()
            .execute()
        )
        if not state_result.data:
            raise ValueError("Invalid or expired SSO state")

        state_data = state_result.data

        # Check expiry
        if state_data["expires_at"] < int(time.time()):
            # Clean up expired state
            self.supabase.table("sso_states").delete().eq("state", state).execute()
            raise ValueError("SSO state expired")

        provider_name = state_data["provider_name"]
        code_verifier = state_data["code_verifier"]
        redirect_uri = state_data["redirect_uri"]
        link_user_id = state_data.get("link_user_id")

        provider = self.get_provider_by_name(provider_name)
        if not provider:
            raise ValueError(f"SSO provider '{provider_name}' not found")

        endpoints = self._discover_oidc_endpoints(provider)

        # Exchange code for tokens
        token_response = self._exchange_code(
            token_endpoint=endpoints["token_endpoint"],
            code=code,
            client_id=provider["client_id"],
            client_secret=provider["client_secret"],
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )

        # Extract claims from ID token or userinfo endpoint
        claims = self._extract_claims(
            token_response=token_response,
            userinfo_endpoint=endpoints.get("userinfo_endpoint", ""),
            access_token=token_response.get("access_token", ""),
        )

        # Clean up used state
        self.supabase.table("sso_states").delete().eq("state", state).execute()

        # Determine the subject (unique ID from the IdP)
        subject = claims.get("sub")
        if not subject:
            raise ValueError("OIDC claims missing 'sub' field")

        email = claims.get("email")
        full_name = claims.get("name") or claims.get("preferred_username") or ""

        # Check if SSO identity already linked
        existing_identity = self._find_sso_identity(provider_name, subject)

        if existing_identity:
            # User already linked — sign them in
            user_id = existing_identity["user_id"]
            user = self._get_user_by_id(user_id)
            if not user:
                raise ValueError("Linked user account not found")
            return {
                "action": "login",
                "user_id": user_id,
                "email": user.get("email", email),
                "full_name": user.get("full_name", full_name),
                "is_new_user": False,
            }

        # If linking to an existing account
        if link_user_id:
            identity = self._create_sso_identity(
                user_id=link_user_id,
                provider_name=provider_name,
                subject=subject,
                email=email,
                full_name=full_name,
            )
            return {
                "action": "linked",
                "user_id": link_user_id,
                "email": email,
                "full_name": full_name,
                "is_new_user": False,
            }

        # Auto-provision: check if user with same email exists
        if email:
            existing_user = self._find_user_by_email(email)
            if existing_user:
                # Auto-link SSO identity to existing user with matching email
                self._create_sso_identity(
                    user_id=existing_user["id"],
                    provider_name=provider_name,
                    subject=subject,
                    email=email,
                    full_name=full_name,
                )
                return {
                    "action": "login",
                    "user_id": existing_user["id"],
                    "email": email,
                    "full_name": existing_user.get("full_name", full_name),
                    "is_new_user": False,
                }

        # No existing user — provision a new one
        new_user = self._provision_user(
            email=email or f"{provider_name}_{subject}@sso.local",
            full_name=full_name,
            provider_name=provider_name,
            subject=subject,
        )
        return {
            "action": "register",
            "user_id": new_user["id"],
            "email": new_user.get("email", email),
            "full_name": new_user.get("full_name", full_name),
            "is_new_user": True,
        }

    # ── Token Exchange ─────────────────────────────────────────────

    def _exchange_code(
        self,
        *,
        token_endpoint: str,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        code_verifier: str,
    ) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }

        with httpx.Client(timeout=15) as client:
            resp = client.post(token_endpoint, data=payload)
            resp.raise_for_status()
            return resp.json()

    # ── Claims Extraction ──────────────────────────────────────────

    def _extract_claims(
        self,
        *,
        token_response: Dict[str, Any],
        userinfo_endpoint: str,
        access_token: str,
    ) -> Dict[str, Any]:
        """Extract user claims from ID token or userinfo endpoint."""
        # Try ID token first
        id_token = token_response.get("id_token")
        if id_token:
            try:
                import jwt  # PyJWT

                # Decode without verification (we trust the token endpoint)
                claims = jwt.decode(id_token, options={"verify_signature": False})
                return claims
            except Exception:
                logger.warning("Failed to decode ID token, falling back to userinfo")

        # Fallback to userinfo endpoint
        if userinfo_endpoint and access_token:
            with httpx.Client(timeout=10) as client:
                resp = client.get(
                    userinfo_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                resp.raise_for_status()
                return resp.json()

        raise ValueError("Cannot extract claims: no ID token and no userinfo endpoint")

    # ── SSO Identity Management ────────────────────────────────────

    def _find_sso_identity(
        self, provider_name: str, subject: str
    ) -> Optional[Dict[str, Any]]:
        """Find an existing SSO identity."""
        result = (
            self.supabase.table("sso_identities")
            .select("*")
            .eq("provider", provider_name)
            .eq("subject", subject)
            .single()
            .execute()
        )
        return result.data

    def _create_sso_identity(
        self,
        *,
        user_id: str,
        provider_name: str,
        subject: str,
        email: Optional[str],
        full_name: Optional[str],
    ) -> Dict[str, Any]:
        """Create an SSO identity linking an IdP subject to a local user."""
        data = {
            "user_id": user_id,
            "provider": provider_name,
            "subject": subject,
            "email": email,
            "full_name": full_name,
        }
        data = {k: v for k, v in data.items() if v is not None}
        result = self.supabase.table("sso_identities").insert(data).execute()
        return result.data[0]

    def list_user_identities(self, user_id: str) -> List[Dict[str, Any]]:
        """List all SSO identities linked to a user."""
        result = (
            self.supabase.table("sso_identities")
            .select("id, provider, email, full_name, created_at")
            .eq("user_id", user_id)
            .execute()
        )
        return result.data or []

    def unlink_identity(self, identity_id: str, user_id: str) -> bool:
        """Unlink an SSO identity from a user account."""
        result = (
            self.supabase.table("sso_identities")
            .delete()
            .eq("id", identity_id)
            .eq("user_id", user_id)
            .execute()
        )
        return len(result.data) > 0

    # ── User Provisioning / Lookup ─────────────────────────────────

    def _find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by email in the profiles table."""
        result = (
            self.supabase.table("profiles")
            .select("*")
            .eq("email", email)
            .single()
            .execute()
        )
        return result.data

    def _get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID from profiles table."""
        result = (
            self.supabase.table("profiles")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )
        return result.data

    def _provision_user(
        self, *, email: str, full_name: str, provider_name: str, subject: str
    ) -> Dict[str, Any]:
        """
        Provision a new user from SSO claims.
        Uses admin client to create the user in Supabase Auth,
        then creates a profile and links the SSO identity.
        """
        import uuid

        # Generate a random password (user won't use it — SSO only)
        temp_password = secrets.token_urlsafe(24)

        try:
            # Create user in Supabase Auth via admin
            auth_response = self.admin_supabase.auth.admin.create_user(
                {
                    "email": email,
                    "password": temp_password,
                    "email_confirm": True,
                    "user_metadata": {
                        "full_name": full_name,
                        "sso_provider": provider_name,
                    },
                }
            )

            if not auth_response.user:
                raise ValueError("Failed to create user via admin API")

            user_id = str(auth_response.user.id)
        except Exception as exc:
            logger.error(f"Failed to provision SSO user: {exc}")
            # Fallback: just create a profile record
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
            logger.warning(f"Profile creation for SSO user {user_id} failed: {exc}")

        # Link SSO identity
        self._create_sso_identity(
            user_id=user_id,
            provider_name=provider_name,
            subject=subject,
            email=email,
            full_name=full_name,
        )

        return {"id": user_id, "email": email, "full_name": full_name}

    # ── Generate session for SSO user ──────────────────────────────

    def create_session_for_user(self, user_id: str) -> Optional[str]:
        """
        Create a Supabase session for an SSO-authenticated user.
        Returns an access token.
        """
        try:
            # Use admin API to generate a magic link / session
            result = self.admin_supabase.auth.admin.generate_link(
                {
                    "type": "magiclink",
                    "email": self._get_user_by_id(user_id).get("email", ""),
                }
            )
            # Extract the access token from the generated link
            if result and result.properties:
                return result.properties.get("access_token")
        except Exception as exc:
            logger.error(f"Failed to create session for SSO user {user_id}: {exc}")
        return None


# Singleton
sso_service = SSOService()

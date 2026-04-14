"""
Integration services for third-party integrations.
Includes Zapier, generic webhooks, and WordPress integration.
"""
import hashlib
import hmac
import json
import logging
import time
import uuid

import requests

logger = logging.getLogger(__name__)
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.core.config import get_settings


class BaseIntegrationService(ABC):
    """Base class for all integration services."""
    
    def __init__(self, integration_id: Optional[str] = None, config: Optional[Dict] = None):
        self.integration_id = integration_id
        self.config = config or {}
        self._supabase = None
    
    @property
    def supabase(self):
        """Lazy load supabase client."""
        if self._supabase is None:
            from app.core.supabase import get_supabase_admin_client
            self._supabase = get_supabase_admin_client()
        return self._supabase
    
    @abstractmethod
    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate integration configuration. Returns (is_valid, error_message)."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> tuple[bool, Optional[str]]:
        """Test the integration connection. Returns (success, error_message)."""
        pass
    
    @abstractmethod
    async def send_event(self, event_type: str, payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Send an event to the integration. Returns (success, error_message)."""
        pass
    
    def log_delivery(self, event_type: str, payload: Dict[str, Any], 
                     status: str, attempts: int = 0, 
                     response_status: Optional[int] = None,
                     response_body: Optional[str] = None,
                     error_message: Optional[str] = None):
        """Log webhook delivery attempt."""
        try:
            delivery_data = {
                "id": str(uuid.uuid4()),
                "webhook_id": self.integration_id,
                "event_type": event_type,
                "payload": payload,
                "status": status,
                "attempts": attempts,
                "response_status": response_status,
                "response_body": response_body[:5000] if response_body else None,
                "error_message": error_message,
                "delivered_at": datetime.now(timezone.utc).isoformat() if status == "delivered" else None,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self.supabase.table("webhook_deliveries").insert(delivery_data).execute()
        except Exception as e:
            logger.error(f"[Integration] Failed to log delivery: {e}")


class ZapierService(BaseIntegrationService):
    """Service for Zapier webhook integration."""
    
    def __init__(self, integration_id: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(integration_id, config)
        self.webhook_url = self.config.get("webhook_url", "")
    
    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate Zapier webhook configuration."""
        webhook_url = config.get("webhook_url", "")
        if not webhook_url:
            return False, "Webhook URL is required"
        if not webhook_url.startswith("https://hooks.zapier.com/"):
            return False, "Invalid Zapier webhook URL format"
        return True, None
    
    async def test_connection(self) -> tuple[bool, Optional[str]]:
        """Test Zapier webhook connection with a ping event."""
        if not self.webhook_url:
            return False, "No webhook URL configured"
        
        test_payload = {
            "event": "test.ping",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {"message": "Connection test from ContentForge AI"}
        }
        
        return await self._send_payload(test_payload, event_type="test.ping", is_test=True)
    
    async def send_event(self, event_type: str, payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Send event to Zapier webhook."""
        zapier_payload = {
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload
        }
        return await self._send_payload(zapier_payload, event_type=event_type)
    
    async def _send_payload(self, payload: Dict[str, Any], event_type: str, 
                           is_test: bool = False, max_retries: int = 3) -> tuple[bool, Optional[str]]:
        """Send payload to Zapier webhook with retry logic."""
        attempts = 0
        last_error = None
        
        while attempts < max_retries:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "ContentForge-AI-Integration/1.0",
                    "X-Event-Type": event_type,
                    "X-Integration-Type": "zapier"
                }
                
                # Add custom headers from config
                custom_headers = self.config.get("custom_headers", {})
                if custom_headers:
                    headers.update(custom_headers)
                
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if not is_test:
                    self.log_delivery(
                        event_type=event_type,
                        payload=payload,
                        status="delivered" if response.status_code < 400 else "failed",
                        attempts=attempts + 1,
                        response_status=response.status_code,
                        response_body=response.text[:1000] if response.text else None,
                        error_message=None if response.status_code < 400 else f"HTTP {response.status_code}"
                    )
                
                if response.status_code < 400:
                    return True, None
                else:
                    return False, f"Webhook returned HTTP {response.status_code}: {response.text[:500]}"
                    
            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                attempts += 1
                if attempts < max_retries:
                    time.sleep(2 ** attempts)  # Exponential backoff
            except requests.exceptions.RequestException as e:
                last_error = f"Request failed: {str(e)}"
                attempts += 1
                if attempts < max_retries:
                    time.sleep(2 ** attempts)
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                attempts += 1
                if attempts < max_retries:
                    time.sleep(2 ** attempts)
        
        if not is_test:
            self.log_delivery(
                event_type=event_type,
                payload=payload,
                status="failed",
                attempts=attempts,
                error_message=last_error
            )
        
        return False, last_error


class WebhookService(BaseIntegrationService):
    """Service for generic webhook integration with signature verification."""
    
    def __init__(self, integration_id: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(integration_id, config)
        self.webhook_url = self.config.get("webhook_url", "")
        self.secret = self.config.get("secret", "")
        self.signature_header = self.config.get("signature_header", "X-Webhook-Signature")
        self.signature_format = self.config.get("signature_format", "hex")  # hex or base64
        self.hash_algorithm = self.config.get("hash_algorithm", "sha256")  # sha256, sha512
        self.event_filter = self.config.get("event_filter", [])  # Empty list = all events
        self.payload_transform = self.config.get("payload_transform", {})  # Template for transformation
    
    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate generic webhook configuration."""
        webhook_url = config.get("webhook_url", "")
        if not webhook_url:
            return False, "Webhook URL is required"
        if not webhook_url.startswith(("https://", "http://")):
            return False, "Webhook URL must start with http:// or https://"
        
        hash_algo = config.get("hash_algorithm", "sha256")
        if hash_algo not in ["sha256", "sha512"]:
            return False, "Hash algorithm must be sha256 or sha512"
        
        return True, None
    
    async def test_connection(self) -> tuple[bool, Optional[str]]:
        """Test webhook connection with a ping event."""
        if not self.webhook_url:
            return False, "No webhook URL configured"
        
        test_payload = {
            "event": "test.ping",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {"message": "Connection test from ContentForge AI"}
        }
        
        return await self._send_payload(test_payload, event_type="test.ping", is_test=True)
    
    async def send_event(self, event_type: str, payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Send event to webhook with filtering and transformation."""
        # Check event filter
        if self.event_filter and event_type not in self.event_filter:
            return True, "Event filtered out"  # Not an error, just filtered
        
        # Apply payload transformation if configured
        transformed_payload = self._transform_payload(event_type, payload)
        
        webhook_payload = {
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": transformed_payload
        }
        
        return await self._send_payload(webhook_payload, event_type=event_type)
    
    def _transform_payload(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply payload transformation based on configuration template."""
        if not self.payload_transform:
            return payload
        
        # Simple field mapping transformation
        result = {}
        for key, value_template in self.payload_transform.items():
            if isinstance(value_template, str) and value_template.startswith("${"):
                # Extract nested value
                path = value_template[2:-1].split(".")
                current = payload
                for p in path:
                    if isinstance(current, dict):
                        current = current.get(p)
                    else:
                        current = None
                        break
                if current is not None:
                    result[key] = current
            else:
                result[key] = value_template
        
        return result if result else payload
    
    def _generate_signature(self, payload: Dict[str, Any]) -> str:
        """Generate webhook signature."""
        if not self.secret:
            return ""
        
        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        
        if self.hash_algorithm == "sha512":
            sig = hmac.new(
                self.secret.encode('utf-8'),
                payload_str.encode('utf-8'),
                hashlib.sha512
            ).digest()
        else:
            sig = hmac.new(
                self.secret.encode('utf-8'),
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).digest()
        
        if self.signature_format == "base64":
            import base64
            return base64.b64encode(sig).decode('utf-8')
        else:
            return sig.hex()
    
    async def _send_payload(self, payload: Dict[str, Any], event_type: str,
                           is_test: bool = False, max_retries: int = 3) -> tuple[bool, Optional[str]]:
        """Send payload to webhook with retry logic."""
        attempts = 0
        last_error = None
        
        while attempts < max_retries:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "ContentForge-AI-Integration/1.0",
                    "X-Event-Type": event_type,
                    "X-Integration-Type": "webhook",
                    "X-Webhook-ID": str(self.integration_id) if self.integration_id else ""
                }
                
                # Add custom headers
                custom_headers = self.config.get("custom_headers", {})
                if custom_headers:
                    headers.update(custom_headers)
                
                # Generate signature if secret is configured
                signature = self._generate_signature(payload)
                if signature:
                    headers[self.signature_header] = signature
                
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if not is_test:
                    self.log_delivery(
                        event_type=event_type,
                        payload=payload,
                        status="delivered" if response.status_code < 400 else "failed",
                        attempts=attempts + 1,
                        response_status=response.status_code,
                        response_body=response.text[:1000] if response.text else None,
                        error_message=None if response.status_code < 400 else f"HTTP {response.status_code}"
                    )
                
                if response.status_code < 400:
                    return True, None
                else:
                    return False, f"Webhook returned HTTP {response.status_code}: {response.text[:500]}"
                    
            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                attempts += 1
                if attempts < max_retries:
                    time.sleep(2 ** attempts)
            except requests.exceptions.RequestException as e:
                last_error = f"Request failed: {str(e)}"
                attempts += 1
                if attempts < max_retries:
                    time.sleep(2 ** attempts)
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                attempts += 1
                if attempts < max_retries:
                    time.sleep(2 ** attempts)
        
        if not is_test:
            self.log_delivery(
                event_type=event_type,
                payload=payload,
                status="failed",
                attempts=attempts,
                error_message=last_error
            )
        
        return False, last_error


class WordPressService(BaseIntegrationService):
    """Service for WordPress integration via REST API."""
    
    def __init__(self, integration_id: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(integration_id, config)
        self.site_url = self.config.get("site_url", "").rstrip("/")
        self.username = self.config.get("username", "")
        self.application_password = self.config.get("application_password", "")
        self.default_status = self.config.get("default_status", "draft")  # draft, publish, pending
        self.default_category = self.config.get("default_category", None)
    
    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate WordPress configuration."""
        site_url = config.get("site_url", "").rstrip("/")
        username = config.get("username", "")
        app_password = config.get("application_password", "")
        
        if not site_url:
            return False, "WordPress site URL is required"
        if not site_url.startswith(("https://", "http://")):
            return False, "Site URL must start with http:// or https://"
        if not username:
            return False, "Username is required"
        if not app_password:
            return False, "Application password is required"
        
        default_status = config.get("default_status", "draft")
        if default_status not in ["draft", "publish", "pending", "private"]:
            return False, "Default status must be draft, publish, pending, or private"
        
        return True, None
    
    async def test_connection(self) -> tuple[bool, Optional[str]]:
        """Test WordPress connection by fetching user info."""
        if not self.site_url:
            return False, "No site URL configured"
        
        try:
            import base64
            credentials = f"{self.username}:{self.application_password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded}",
                "User-Agent": "ContentForge-AI-Integration/1.0"
            }
            
            response = requests.get(
                f"{self.site_url}/wp-json/wp/v2/users/me",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return True, f"Connected as {user_data.get('name', self.username)}"
            elif response.status_code == 401:
                return False, "Authentication failed. Check username and application password."
            elif response.status_code == 403:
                return False, "Access denied. REST API may be disabled."
            else:
                return False, f"WordPress returned HTTP {response.status_code}: {response.text[:500]}"
                
        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except requests.exceptions.RequestException as e:
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    async def send_event(self, event_type: str, payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Handle WordPress events - primarily creates posts."""
        if event_type in ["content.created", "content.updated", "distribution.completed"]:
            return await self.create_post(payload)
        else:
            return True, f"Event type '{event_type}' not supported for WordPress"
    
    async def create_post(self, content_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Create a WordPress post."""
        try:
            import base64
            
            title = content_data.get("title", "")
            content = content_data.get("content", "")
            excerpt = content_data.get("excerpt", "")
            featured_image_url = content_data.get("featured_image", "")
            tags = content_data.get("tags", [])
            
            # WordPress post data
            post_data = {
                "title": title,
                "content": content,
                "excerpt": excerpt,
                "status": content_data.get("status", self.default_status),
            }
            
            # Add category if configured
            if self.default_category:
                post_data["categories"] = [self.default_category]
            
            # Add tags if provided
            if tags:
                post_data["tags"] = tags
            
            credentials = f"{self.username}:{self.application_password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/json",
                "User-Agent": "ContentForge-AI-Integration/1.0"
            }
            
            response = requests.post(
                f"{self.site_url}/wp-json/wp/v2/posts",
                json=post_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                post_url = result.get("link", "")
                post_id = result.get("id", "")
                
                self.log_delivery(
                    event_type="content.created",
                    payload=content_data,
                    status="delivered",
                    attempts=1,
                    response_status=response.status_code,
                    response_body=json.dumps({"post_id": post_id, "url": post_url})
                )
                
                return True, f"Post created: {post_url}"
            else:
                error_msg = f"WordPress returned HTTP {response.status_code}: {response.text[:500]}"
                self.log_delivery(
                    event_type="content.created",
                    payload=content_data,
                    status="failed",
                    attempts=1,
                    response_status=response.status_code,
                    error_message=error_msg
                )
                return False, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Request timeout"
            self.log_delivery(
                event_type="content.created",
                payload=content_data,
                status="failed",
                error_message=error_msg
            )
            return False, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            self.log_delivery(
                event_type="content.created",
                payload=content_data,
                status="failed",
                error_message=error_msg
            )
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.log_delivery(
                event_type="content.created",
                payload=content_data,
                status="failed",
                error_message=error_msg
            )
            return False, error_msg


class IntegrationFactory:
    """Factory for creating integration services."""
    
    _services = {
        "zapier": ZapierService,
        "webhook": WebhookService,
        "wordpress": WordPressService,
    }
    
    @classmethod
    def create_service(cls, integration_type: str, integration_id: Optional[str] = None,
                      config: Optional[Dict] = None) -> BaseIntegrationService:
        """Create an integration service instance."""
        service_class = cls._services.get(integration_type.lower())
        if not service_class:
            raise ValueError(f"Unknown integration type: {integration_type}")
        return service_class(integration_id, config)
    
    @classmethod
    def get_available_types(cls) -> List[Dict[str, Any]]:
        """Get list of available integration types with metadata."""
        return [
            {
                "type": "zapier",
                "name": "Zapier",
                "description": "Send events to Zapier webhooks for workflow automation",
                "icon": "zapier",
                "config_schema": {
                    "webhook_url": {"type": "string", "required": True, "label": "Zapier Webhook URL"},
                    "custom_headers": {"type": "object", "required": False, "label": "Custom Headers"}
                }
            },
            {
                "type": "webhook",
                "name": "Generic Webhook",
                "description": "Send events to any HTTP endpoint with signature verification",
                "icon": "webhook",
                "config_schema": {
                    "webhook_url": {"type": "string", "required": True, "label": "Webhook URL"},
                    "secret": {"type": "string", "required": False, "label": "Signature Secret"},
                    "signature_header": {"type": "string", "required": False, "default": "X-Webhook-Signature", "label": "Signature Header Name"},
                    "signature_format": {"type": "string", "required": False, "default": "hex", "enum": ["hex", "base64"], "label": "Signature Format"},
                    "hash_algorithm": {"type": "string", "required": False, "default": "sha256", "enum": ["sha256", "sha512"], "label": "Hash Algorithm"},
                    "event_filter": {"type": "array", "required": False, "label": "Event Filter (leave empty for all)"},
                    "custom_headers": {"type": "object", "required": False, "label": "Custom Headers"}
                }
            },
            {
                "type": "wordpress",
                "name": "WordPress",
                "description": "Auto-publish content to WordPress sites via REST API",
                "icon": "wordpress",
                "config_schema": {
                    "site_url": {"type": "string", "required": True, "label": "WordPress Site URL"},
                    "username": {"type": "string", "required": True, "label": "Username"},
                    "application_password": {"type": "string", "required": True, "label": "Application Password", "help": "Generate in WordPress Admin > Users > Profile > Application Passwords"},
                    "default_status": {"type": "string", "required": False, "default": "draft", "enum": ["draft", "publish", "pending", "private"], "label": "Default Post Status"},
                    "default_category": {"type": "number", "required": False, "label": "Default Category ID"}
                }
            }
        ]


# Event types that can trigger webhooks
AVAILABLE_EVENT_TYPES = [
    {"type": "content.created", "description": "When new content is created"},
    {"type": "content.updated", "description": "When content is updated"},
    {"type": "content.published", "description": "When content is published"},
    {"type": "distribution.completed", "description": "When content distribution completes"},
    {"type": "distribution.failed", "description": "When content distribution fails"},
    {"type": "user.signup", "description": "When a new user signs up"},
    {"type": "subscription.created", "description": "When a subscription is created"},
    {"type": "subscription.updated", "description": "When a subscription is updated"},
]

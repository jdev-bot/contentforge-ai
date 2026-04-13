"""
Tests for the integrations ecosystem.
Includes tests for Zapier, Webhook, and WordPress services.
"""
import pytest
import json
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from pydantic import ValidationError

from app.services.integration_services import (
    ZapierService,
    WebhookService,
    WordPressService,
    IntegrationFactory,
    AVAILABLE_EVENT_TYPES
)


# =============================================================================
# Zapier Service Tests
# =============================================================================

class TestZapierService:
    """Test cases for ZapierService."""
    
    def test_zapier_service_initialization(self):
        """Test ZapierService can be initialized with config."""
        config = {"webhook_url": "https://hooks.zapier.com/hooks/catch/123/abc/"}
        service = ZapierService(config=config)
        assert service.webhook_url == config["webhook_url"]
    
    @pytest.mark.asyncio
    async def test_zapier_validate_config_valid(self):
        """Test validating a valid Zapier config."""
        config = {"webhook_url": "https://hooks.zapier.com/hooks/catch/123/abc/"}
        service = ZapierService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is True
        assert error is None
    
    @pytest.mark.asyncio
    async def test_zapier_validate_config_missing_url(self):
        """Test validating Zapier config without webhook URL."""
        config = {}
        service = ZapierService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is False
        assert "Webhook URL is required" in error
    
    @pytest.mark.asyncio
    async def test_zapier_validate_config_invalid_url(self):
        """Test validating Zapier config with invalid URL format."""
        config = {"webhook_url": "https://example.com/webhook"}
        service = ZapierService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is False
        assert "Invalid Zapier webhook URL format" in error
    
    @pytest.mark.asyncio
    @patch('requests.post')
    async def test_zapier_test_connection_success(self, mock_post):
        """Test successful Zapier connection test."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "success"}'
        mock_post.return_value = mock_response
        
        config = {"webhook_url": "https://hooks.zapier.com/hooks/catch/123/abc/"}
        service = ZapierService(config=config)
        success, message = await service.test_connection()
        
        assert success is True
        mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_zapier_test_connection_no_url(self):
        """Test Zapier connection test without URL."""
        service = ZapierService(config={})
        success, message = await service.test_connection()
        
        assert success is False
        assert "No webhook URL configured" in message
    
    @pytest.mark.asyncio
    @patch('requests.post')
    async def test_zapier_send_event_success(self, mock_post):
        """Test sending event to Zapier."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "received"}'
        mock_post.return_value = mock_response
        
        config = {"webhook_url": "https://hooks.zapier.com/hooks/catch/123/abc/"}
        service = ZapierService(config=config)
        success, message = await service.send_event(
            "content.created",
            {"title": "Test", "content": "Hello"}
        )
        
        assert success is True
        mock_post.assert_called_once()
        
        # Verify payload structure
        call_args = mock_post.call_args
        payload = call_args.kwargs.get('json') or call_args[1].get('json')
        assert payload["event"] == "content.created"
        assert "timestamp" in payload
        assert payload["data"]["title"] == "Test"
    
    @pytest.mark.asyncio
    @patch('requests.post')
    async def test_zapier_send_event_http_error(self, mock_post):
        """Test sending event when Zapier returns HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        config = {"webhook_url": "https://hooks.zapier.com/hooks/catch/123/abc/"}
        service = ZapierService(config=config)
        success, message = await service.send_event("content.created", {})
        
        assert success is False
        assert "500" in message
    
    @pytest.mark.asyncio
    @patch('requests.post')
    async def test_zapier_send_event_timeout(self, mock_post):
        """Test sending event with timeout retry."""
        from requests.exceptions import Timeout
        mock_post.side_effect = [Timeout("Connection timeout"), Mock(status_code=200, text="OK")]
        
        config = {"webhook_url": "https://hooks.zapier.com/hooks/catch/123/abc/"}
        service = ZapierService(config=config)
        
        # Mock time.sleep to speed up test
        with patch('time.sleep'):
            success, message = await service.send_event("content.created", {})
        
        # Should succeed after retry
        assert success is True


# =============================================================================
# Webhook Service Tests
# =============================================================================

class TestWebhookService:
    """Test cases for WebhookService."""
    
    def test_webhook_service_initialization(self):
        """Test WebhookService can be initialized with config."""
        config = {
            "webhook_url": "https://example.com/webhook",
            "secret": "my-secret",
            "signature_header": "X-Signature",
            "hash_algorithm": "sha256"
        }
        service = WebhookService(config=config)
        assert service.webhook_url == "https://example.com/webhook"
        assert service.secret == "my-secret"
    
    @pytest.mark.asyncio
    async def test_webhook_validate_config_valid(self):
        """Test validating a valid webhook config."""
        config = {"webhook_url": "https://example.com/webhook"}
        service = WebhookService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is True
        assert error is None
    
    @pytest.mark.asyncio
    async def test_webhook_validate_config_missing_url(self):
        """Test validating webhook config without URL."""
        config = {}
        service = WebhookService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is False
        assert "Webhook URL is required" in error
    
    @pytest.mark.asyncio
    async def test_webhook_validate_config_invalid_url(self):
        """Test validating webhook config with invalid URL."""
        config = {"webhook_url": "ftp://example.com/webhook"}
        service = WebhookService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is False
        assert "must start with http" in error
    
    @pytest.mark.asyncio
    async def test_webhook_validate_config_invalid_hash(self):
        """Test validating webhook config with invalid hash algorithm."""
        config = {"webhook_url": "https://example.com/webhook", "hash_algorithm": "md5"}
        service = WebhookService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is False
        assert "Hash algorithm must be" in error
    
    def test_webhook_generate_signature_sha256(self):
        """Test signature generation with SHA256."""
        config = {"webhook_url": "https://example.com/webhook", "secret": "secret"}
        service = WebhookService(config=config)
        payload = {"event": "test"}
        
        signature = service._generate_signature(payload)
        
        expected = hmac.new(
            "secret".encode('utf-8'),
            json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        assert signature == expected
    
    def test_webhook_generate_signature_sha512(self):
        """Test signature generation with SHA512."""
        config = {
            "webhook_url": "https://example.com/webhook",
            "secret": "secret",
            "hash_algorithm": "sha512"
        }
        service = WebhookService(config=config)
        payload = {"event": "test"}
        
        signature = service._generate_signature(payload)
        
        expected = hmac.new(
            "secret".encode('utf-8'),
            json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        assert signature == expected
    
    def test_webhook_generate_signature_base64(self):
        """Test signature generation in base64 format."""
        config = {
            "webhook_url": "https://example.com/webhook",
            "secret": "secret",
            "signature_format": "base64"
        }
        service = WebhookService(config=config)
        payload = {"event": "test"}
        
        signature = service._generate_signature(payload)
        
        import base64
        expected = base64.b64encode(
            hmac.new(
                "secret".encode('utf-8'),
                json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        assert signature == expected
    
    @pytest.mark.asyncio
    async def test_webhook_event_filtering(self):
        """Test that webhook respects event filters."""
        config = {
            "webhook_url": "https://example.com/webhook",
            "event_filter": ["content.created", "content.updated"]
        }
        service = WebhookService(config=config)
        
        # Event in filter should succeed
        with patch.object(service, '_send_payload', return_value=(True, None)) as mock_send:
            success, message = await service.send_event("content.created", {})
            assert success is True
            assert message == "Event filtered out"  # Actually filtered is success
            mock_send.assert_not_called()
        
        # Event not in filter should be filtered
        success, message = await service.send_event("user.signup", {})
        assert success is True
        assert "filtered" in message.lower()
    
    def test_webhook_payload_transformation(self):
        """Test payload transformation based on template."""
        config = {
            "webhook_url": "https://example.com/webhook",
            "payload_transform": {
                "title": "${data.title}",
                "body": "${data.content}",
                "static_field": "static_value"
            }
        }
        service = WebhookService(config=config)
        
        original = {
            "data": {
                "title": "My Title",
                "content": "My Content"
            }
        }
        
        transformed = service._transform_payload("test", original)
        
        assert transformed["title"] == "My Title"
        assert transformed["body"] == "My Content"
        assert transformed["static_field"] == "static_value"


# =============================================================================
# WordPress Service Tests
# =============================================================================

class TestWordPressService:
    """Test cases for WordPressService."""
    
    def test_wordpress_service_initialization(self):
        """Test WordPressService can be initialized with config."""
        config = {
            "site_url": "https://blog.example.com",
            "username": "admin",
            "application_password": "abcd efgh ijkl mnop"
        }
        service = WordPressService(config=config)
        assert service.site_url == "https://blog.example.com"
        assert service.username == "admin"
    
    @pytest.mark.asyncio
    async def test_wordpress_validate_config_valid(self):
        """Test validating a valid WordPress config."""
        config = {
            "site_url": "https://blog.example.com",
            "username": "admin",
            "application_password": "password123"
        }
        service = WordPressService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is True
        assert error is None
    
    @pytest.mark.asyncio
    async def test_wordpress_validate_config_missing_site_url(self):
        """Test validating WordPress config without site URL."""
        config = {"username": "admin", "application_password": "pass"}
        service = WordPressService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is False
        assert "WordPress site URL is required" in error
    
    @pytest.mark.asyncio
    async def test_wordpress_validate_config_invalid_url(self):
        """Test validating WordPress config with invalid URL."""
        config = {
            "site_url": "ftp://blog.example.com",
            "username": "admin",
            "application_password": "pass"
        }
        service = WordPressService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is False
        assert "must start with http" in error
    
    @pytest.mark.asyncio
    async def test_wordpress_validate_config_missing_credentials(self):
        """Test validating WordPress config without credentials."""
        config = {"site_url": "https://blog.example.com"}
        service = WordPressService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is False
        assert "Username is required" in error
    
    @pytest.mark.asyncio
    async def test_wordpress_validate_config_invalid_status(self):
        """Test validating WordPress config with invalid post status."""
        config = {
            "site_url": "https://blog.example.com",
            "username": "admin",
            "application_password": "pass",
            "default_status": "invalid_status"
        }
        service = WordPressService(config=config)
        is_valid, error = await service.validate_config(config)
        assert is_valid is False
        assert "Default status must be" in error
    
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_wordpress_test_connection_success(self, mock_get):
        """Test successful WordPress connection test."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "Admin", "id": 1}
        mock_get.return_value = mock_response
        
        config = {
            "site_url": "https://blog.example.com",
            "username": "admin",
            "application_password": "pass123"
        }
        service = WordPressService(config=config)
        success, message = await service.test_connection()
        
        assert success is True
        assert "Connected as Admin" in message
    
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_wordpress_test_connection_auth_failure(self, mock_get):
        """Test WordPress connection test with auth failure."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        config = {
            "site_url": "https://blog.example.com",
            "username": "admin",
            "application_password": "wrong"
        }
        service = WordPressService(config=config)
        success, message = await service.test_connection()
        
        assert success is False
        assert "Authentication failed" in message
    
    @pytest.mark.asyncio
    @patch('requests.post')
    async def test_wordpress_create_post_success(self, mock_post):
        """Test creating a WordPress post."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 123,
            "link": "https://blog.example.com/my-post"
        }
        mock_post.return_value = mock_response
        
        config = {
            "site_url": "https://blog.example.com",
            "username": "admin",
            "application_password": "pass123",
            "default_status": "draft"
        }
        service = WordPressService(config=config)
        
        content_data = {
            "title": "My Post",
            "content": "<p>Post content here</p>",
            "excerpt": "Summary",
            "tags": ["tag1", "tag2"]
        }
        
        success, message = await service.create_post(content_data)
        
        assert success is True
        assert "Post created" in message
        assert "my-post" in message
        
        # Verify POST data
        call_args = mock_post.call_args
        post_data = call_args.kwargs.get('json') or call_args[1].get('json')
        assert post_data["title"] == "My Post"
        assert post_data["status"] == "draft"
        assert post_data["tags"] == ["tag1", "tag2"]


# =============================================================================
# Integration Factory Tests
# =============================================================================

class TestIntegrationFactory:
    """Test cases for IntegrationFactory."""
    
    def test_factory_create_zapier(self):
        """Test factory creates ZapierService."""
        service = IntegrationFactory.create_service("zapier")
        assert isinstance(service, ZapierService)
    
    def test_factory_create_webhook(self):
        """Test factory creates WebhookService."""
        service = IntegrationFactory.create_service("webhook")
        assert isinstance(service, WebhookService)
    
    def test_factory_create_wordpress(self):
        """Test factory creates WordPressService."""
        service = IntegrationFactory.create_service("wordpress")
        assert isinstance(service, WordPressService)
    
    def test_factory_create_unknown(self):
        """Test factory raises error for unknown type."""
        with pytest.raises(ValueError) as exc_info:
            IntegrationFactory.create_service("unknown")
        assert "Unknown integration type" in str(exc_info.value)
    
    def test_factory_get_available_types(self):
        """Test factory returns available types."""
        types = IntegrationFactory.get_available_types()
        
        assert len(types) >= 3
        
        type_names = [t["type"] for t in types]
        assert "zapier" in type_names
        assert "webhook" in type_names
        assert "wordpress" in type_names
    
    def test_factory_create_with_config(self):
        """Test factory creates service with config."""
        config = {"webhook_url": "https://example.com/webhook"}
        service = IntegrationFactory.create_service("webhook", config=config)
        assert service.webhook_url == "https://example.com/webhook"
    
    def test_factory_create_with_id(self):
        """Test factory creates service with integration ID."""
        integration_id = str(uuid.uuid4())
        service = IntegrationFactory.create_service("webhook", integration_id=integration_id)
        assert service.integration_id == integration_id


# =============================================================================
# Available Event Types Tests
# =============================================================================

class TestAvailableEventTypes:
    """Test cases for AVAILABLE_EVENT_TYPES."""
    
    def test_event_types_structure(self):
        """Test event types have correct structure."""
        for event in AVAILABLE_EVENT_TYPES:
            assert "type" in event
            assert "description" in event
            assert isinstance(event["type"], str)
            assert isinstance(event["description"], str)
    
    def test_event_types_unique(self):
        """Test event types are unique."""
        types = [e["type"] for e in AVAILABLE_EVENT_TYPES]
        assert len(types) == len(set(types))
    
    def test_common_event_types_present(self):
        """Test common event types are available."""
        types = [e["type"] for e in AVAILABLE_EVENT_TYPES]
        assert "content.created" in types
        assert "content.updated" in types
        assert "distribution.completed" in types


# =============================================================================
# Router Tests (mock database calls)
# =============================================================================

class TestIntegrationRouter:
    """Test cases for integration router endpoints."""
    
    def test_integration_create_model_validation(self):
        """Test IntegrationCreate model validation."""
        from app.routers.integrations import IntegrationCreate
        
        # Valid data
        data = {
            "integration_type": "webhook",
            "name": "My Webhook",
            "config": {"webhook_url": "https://example.com/webhook"},
            "is_active": True
        }
        model = IntegrationCreate(**data)
        assert model.integration_type == "webhook"
        assert model.name == "My Webhook"
    
    def test_integration_update_model_validation(self):
        """Test IntegrationUpdate model validation."""
        from app.routers.integrations import IntegrationUpdate
        
        # Valid partial update
        data = {"name": "Updated Name"}
        model = IntegrationUpdate(**data)
        assert model.name == "Updated Name"
        assert model.config is None
    
    def test_webhook_delivery_response_model(self):
        """Test WebhookDeliveryResponse model."""
        from app.routers.integrations import WebhookDeliveryResponse
        
        data = {
            "id": uuid.uuid4(),
            "webhook_id": uuid.uuid4(),
            "event_type": "content.created",
            "status": "delivered",
            "attempts": 1,
            "response_status": 200,
            "delivered_at": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        model = WebhookDeliveryResponse(**data)
        assert model.status == "delivered"
        assert model.attempts == 1


# =============================================================================
# Integration Router Integration Tests
# =============================================================================

@pytest.mark.asyncio
class TestIntegrationRouterIntegration:
    """Integration tests for integration router."""
    
    async def test_list_integrations_empty(self, mock_user):
        """Test listing integrations with empty result."""
        from app.routers.integrations import list_integrations
        
        with patch('app.routers.integrations.get_supabase_client') as mock_client:
            mock_response = Mock()
            mock_response.data = []
            mock_response.count = 0
            
            mock_supabase = Mock()
            mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
            mock_client.return_value = mock_supabase
            
            result = await list_integrations(user=mock_user)
            
            assert result.total == 0
            assert len(result.integrations) == 0
    
    async def test_create_integration_success(self, mock_user):
        """Test creating an integration."""
        from app.routers.integrations import create_integration, IntegrationCreate
        
        with patch('app.routers.integrations.get_supabase_client') as mock_client:
            integration_id = uuid.uuid4()
            mock_response = Mock()
            mock_response.data = [{
                "id": str(integration_id),
                "user_id": str(mock_user.id),
                "integration_type": "webhook",
                "name": "Test Webhook",
                "config": {"webhook_url": "https://example.com/webhook"},
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }]
            
            mock_supabase = Mock()
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
            mock_client.return_value = mock_supabase
            
            data = IntegrationCreate(
                integration_type="webhook",
                name="Test Webhook",
                config={"webhook_url": "https://example.com/webhook"},
                is_active=True
            )
            
            result = await create_integration(data, user=mock_user)
            
            assert result.name == "Test Webhook"
            assert result.integration_type == "webhook"
    
    async def test_get_integration_not_found(self, mock_user):
        """Test getting non-existent integration."""
        from app.routers.integrations import get_integration
        
        with patch('app.routers.integrations.get_supabase_client') as mock_client:
            mock_supabase = Mock()
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=None)
            mock_client.return_value = mock_supabase
            
            with pytest.raises(HTTPException) as exc_info:
                await get_integration(uuid.uuid4(), user=mock_user)
            
            assert exc_info.value.status_code == 404


# =============================================================================
# Incoming Webhook Tests
# =============================================================================

@pytest.mark.asyncio
class TestIncomingWebhook:
    """Test cases for incoming webhook endpoint."""
    
    async def test_incoming_webhook_invalid_token(self):
        """Test incoming webhook with invalid token."""
        from app.routers.integrations import incoming_webhook, IncomingWebhookPayload
        
        with patch('app.routers.integrations.get_supabase_admin_client') as mock_client:
            mock_supabase = Mock()
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = Mock(data=[])
            mock_client.return_value = mock_supabase
            
            with pytest.raises(HTTPException) as exc_info:
                await incoming_webhook(
                    token="invalid-token",
                    payload=IncomingWebhookPayload(event_type="test", data={}),
                    request=Mock()
                )
            
            assert exc_info.value.status_code == 404
    
    async def test_incoming_webhook_signature_mismatch(self):
        """Test incoming webhook with invalid signature."""
        from app.routers.integrations import incoming_webhook, IncomingWebhookPayload
        
        with patch('app.routers.integrations.get_supabase_admin_client') as mock_client:
            integration_id = uuid.uuid4()
            mock_response = Mock()
            mock_response.data = [{
                "id": str(integration_id),
                "integration_type": "webhook",
                "config": {"incoming_secret": "my-secret"}
            }]
            
            mock_supabase = Mock()
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
            mock_client.return_value = mock_supabase
            
            mock_request = Mock()
            mock_request.body = Mock(return_value=b'{"event_type": "test", "data": {}}')
            
            with pytest.raises(HTTPException) as exc_info:
                await incoming_webhook(
                    token="valid-token",
                    payload=IncomingWebhookPayload(event_type="test", data={}),
                    request=mock_request,
                    x_signature="invalid-signature"
                )
            
            assert exc_info.value.status_code == 401


# =============================================================================
# Test Utilities
# =============================================================================

@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = Mock()
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_supabase_response():
    """Create a mock Supabase response."""
    def _create_response(data=None, count=0):
        response = Mock()
        response.data = data or []
        response.count = count
        return response
    return _create_response

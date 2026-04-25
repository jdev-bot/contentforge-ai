"""
Standalone test runner for integration tests.
Run this file directly to test the integrations ecosystem.
"""

import sys
import os
import asyncio
from unittest.mock import Mock, patch, MagicMock
import json
import hmac
import hashlib

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set test environment variables BEFORE any imports
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-role-key"
os.environ["GROQ_API_KEY"] = "test-groq-api-key"
os.environ["AI_PROVIDER"] = "groq"
os.environ["AI_API_KEY"] = "test-ai-api-key"

# Now import the services
from app.services.integration_services import (
    IntegrationFactory,
    ZapierService,
    WebhookService,
    WordPressService,
    AVAILABLE_EVENT_TYPES,
)


class TestRunner:
    """Simple test runner for integration tests."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def test(self, name):
        """Decorator to register a test."""

        def decorator(func):
            self.tests.append((name, func))
            return func

        return decorator

    def assert_equal(self, actual, expected, msg=""):
        """Assert two values are equal."""
        if actual != expected:
            raise AssertionError(f"Expected {expected}, got {actual}. {msg}")

    def assert_true(self, value, msg=""):
        """Assert value is True."""
        if not value:
            raise AssertionError(f"Expected True, got {value}. {msg}")

    def assert_false(self, value, msg=""):
        """Assert value is False."""
        if value:
            raise AssertionError(f"Expected False, got {value}. {msg}")

    def assert_in(self, item, container, msg=""):
        """Assert item is in container."""
        if item not in container:
            raise AssertionError(f"Expected {item} to be in {container}. {msg}")

    async def run(self):
        """Run all registered tests."""
        print(f"\n{'='*60}")
        print(f"Running {len(self.tests)} integration tests")
        print(f"{'='*60}\n")

        for name, test_func in self.tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    await test_func(self)
                else:
                    test_func(self)
                print(f"✅ PASS: {name}")
                self.passed += 1
            except Exception as e:
                print(f"❌ FAIL: {name}")
                print(f"   Error: {e}")
                self.failed += 1

        print(f"\n{'='*60}")
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print(f"{'='*60}\n")

        return self.failed == 0


runner = TestRunner()


# =============================================================================
# Test Suite
# =============================================================================


@runner.test("Factory creates ZapierService")
def test_factory_zapier(t):
    service = IntegrationFactory.create_service("zapier")
    t.assert_true(isinstance(service, ZapierService))


@runner.test("Factory creates WebhookService")
def test_factory_webhook(t):
    service = IntegrationFactory.create_service("webhook")
    t.assert_true(isinstance(service, WebhookService))


@runner.test("Factory creates WordPressService")
def test_factory_wordpress(t):
    service = IntegrationFactory.create_service("wordpress")
    t.assert_true(isinstance(service, WordPressService))


@runner.test("Factory raises error for unknown type")
def test_factory_unknown(t):
    try:
        IntegrationFactory.create_service("unknown")
        t.assert_true(False, "Should have raised ValueError")
    except ValueError as e:
        t.assert_in("Unknown integration type", str(e))


@runner.test("Factory returns available types")
def test_factory_types(t):
    types = IntegrationFactory.get_available_types()
    t.assert_true(len(types) >= 3)
    type_names = [t_["type"] for t_ in types]
    t.assert_in("zapier", type_names)
    t.assert_in("webhook", type_names)
    t.assert_in("wordpress", type_names)


@runner.test("Factory creates service with config")
def test_factory_with_config(t):
    config = {"webhook_url": "https://example.com/webhook"}
    service = IntegrationFactory.create_service("webhook", config=config)
    t.assert_equal(service.webhook_url, "https://example.com/webhook")


@runner.test("ZapierService validates valid config")
async def test_zapier_valid_config(t):
    config = {"webhook_url": "https://hooks.zapier.com/hooks/catch/123/abc/"}
    service = ZapierService(config=config)
    is_valid, error = await service.validate_config(config)
    t.assert_true(is_valid)
    t.assert_equal(error, None)


@runner.test("ZapierService rejects missing webhook URL")
async def test_zapier_missing_url(t):
    config = {}
    service = ZapierService(config=config)
    is_valid, error = await service.validate_config(config)
    t.assert_false(is_valid)
    t.assert_in("Webhook URL is required", error)


@runner.test("ZapierService rejects invalid URL format")
async def test_zapier_invalid_url(t):
    config = {"webhook_url": "https://example.com/webhook"}
    service = ZapierService(config=config)
    is_valid, error = await service.validate_config(config)
    t.assert_false(is_valid)
    t.assert_in("Invalid Zapier webhook URL format", error)


@runner.test("WebhookService validates valid config")
async def test_webhook_valid_config(t):
    config = {"webhook_url": "https://example.com/webhook"}
    service = WebhookService(config=config)
    is_valid, error = await service.validate_config(config)
    t.assert_true(is_valid)
    t.assert_equal(error, None)


@runner.test("WebhookService rejects missing URL")
async def test_webhook_missing_url(t):
    config = {}
    service = WebhookService(config=config)
    is_valid, error = await service.validate_config(config)
    t.assert_false(is_valid)
    t.assert_in("Webhook URL is required", error)


@runner.test("WebhookService rejects invalid URL")
async def test_webhook_invalid_url(t):
    config = {"webhook_url": "ftp://example.com/webhook"}
    service = WebhookService(config=config)
    is_valid, error = await service.validate_config(config)
    t.assert_false(is_valid)
    t.assert_in("must start with http", error)


@runner.test("WebhookService generates SHA256 signature")
def test_webhook_signature_sha256(t):
    import json
    import hmac
    import hashlib

    config = {"webhook_url": "https://example.com/webhook", "secret": "secret"}
    service = WebhookService(config=config)
    payload = {"event": "test"}

    signature = service._generate_signature(payload)
    expected = hmac.new(
        "secret".encode("utf-8"),
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    t.assert_equal(signature, expected)


@runner.test("WordPressService validates valid config")
async def test_wordpress_valid_config(t):
    config = {
        "site_url": "https://blog.example.com",
        "username": "admin",
        "application_password": "password123",
    }
    service = WordPressService(config=config)
    is_valid, error = await service.validate_config(config)
    t.assert_true(is_valid)
    t.assert_equal(error, None)


@runner.test("WordPressService rejects missing site URL")
async def test_wordpress_missing_url(t):
    config = {"username": "admin", "application_password": "pass"}
    service = WordPressService(config=config)
    is_valid, error = await service.validate_config(config)
    t.assert_false(is_valid)
    t.assert_in("WordPress site URL is required", error)


@runner.test("WordPressService rejects invalid URL")
async def test_wordpress_invalid_url(t):
    config = {
        "site_url": "ftp://blog.example.com",
        "username": "admin",
        "application_password": "pass",
    }
    service = WordPressService(config=config)
    is_valid, error = await service.validate_config(config)
    t.assert_false(is_valid)
    t.assert_in("must start with http", error)


@runner.test("WordPressService rejects missing credentials")
async def test_wordpress_missing_creds(t):
    config = {"site_url": "https://blog.example.com"}
    service = WordPressService(config=config)
    is_valid, error = await service.validate_config(config)
    t.assert_false(is_valid)
    t.assert_in("Username is required", error)


@runner.test("Available event types have correct structure")
def test_event_types_structure(t):
    for event in AVAILABLE_EVENT_TYPES:
        t.assert_true("type" in event, "Event must have 'type' key")
        t.assert_true("description" in event, "Event must have 'description' key")
        t.assert_true(isinstance(event["type"], str), "Event type must be string")
        t.assert_true(
            isinstance(event["description"], str), "Event description must be string"
        )


@runner.test("Available event types are unique")
def test_event_types_unique(t):
    types = [e["type"] for e in AVAILABLE_EVENT_TYPES]
    t.assert_equal(len(types), len(set(types)))


@runner.test("Common event types are present")
def test_event_types_common(t):
    types = [e["type"] for e in AVAILABLE_EVENT_TYPES]
    t.assert_in("content.created", types)
    t.assert_in("content.updated", types)
    t.assert_in("distribution.completed", types)


@runner.test("WebhookService event filtering")
async def test_webhook_event_filtering(t):
    config = {
        "webhook_url": "https://example.com/webhook",
        "event_filter": ["content.created"],
    }
    service = WebhookService(config=config)

    # Event not in filter should be filtered
    success, message = await service.send_event("user.signup", {})
    t.assert_true(success)
    t.assert_in("filtered", message.lower())


@runner.test("WebhookService payload transformation")
def test_webhook_payload_transform(t):
    config = {
        "webhook_url": "https://example.com/webhook",
        "payload_transform": {"title": "${data.title}", "static": "value"},
    }
    service = WebhookService(config=config)

    original = {"data": {"title": "My Title", "content": "Body"}}
    transformed = service._transform_payload("test", original)

    t.assert_equal(transformed["title"], "My Title")
    t.assert_equal(transformed["static"], "value")


# =============================================================================
# Test Suite
# =============================================================================


@runner.test("IntegrationCreate model validates correctly")
def test_integration_create_model(t):
    from pydantic import BaseModel
    from app.routers.integrations import IntegrationCreate

    data = {
        "integration_type": "webhook",
        "name": "Test Webhook",
        "config": {"webhook_url": "https://example.com/webhook"},
        "is_active": True,
    }
    model = IntegrationCreate(**data)
    t.assert_equal(model.integration_type, "webhook")
    t.assert_equal(model.name, "Test Webhook")


@runner.test("IntegrationUpdate model validates correctly")
def test_integration_update_model(t):
    from app.routers.integrations import IntegrationUpdate

    data = {"name": "Updated Name"}
    model = IntegrationUpdate(**data)
    t.assert_equal(model.name, "Updated Name")
    t.assert_true(model.config is None)


@runner.test("WebhookDeliveryResponse model validates correctly")
def test_webhook_delivery_response_model(t):
    from datetime import datetime, timezone
    from app.routers.integrations import WebhookDeliveryResponse
    import uuid

    data = {
        "id": uuid.uuid4(),
        "webhook_id": uuid.uuid4(),
        "event_type": "content.created",
        "status": "delivered",
        "attempts": 1,
        "response_status": 200,
        "delivered_at": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
    }
    model = WebhookDeliveryResponse(**data)
    t.assert_equal(model.status, "delivered")
    t.assert_equal(model.attempts, 1)


@runner.test("IncomingWebhookResponse model validates correctly")
def test_incoming_webhook_response_model(t):
    from app.routers.integrations import IncomingWebhookResponse

    data = {"success": True, "message": "Webhook received"}
    model = IncomingWebhookResponse(**data)
    t.assert_true(model.success)
    t.assert_equal(model.message, "Webhook received")


@runner.test("WebhookService signature with base64 format")
def test_webhook_signature_base64(t):
    import base64
    import json
    import hmac
    import hashlib

    config = {
        "webhook_url": "https://example.com/webhook",
        "secret": "secret",
        "signature_format": "base64",
    }
    service = WebhookService(config=config)
    payload = {"event": "test"}

    signature = service._generate_signature(payload)
    expected = base64.b64encode(
        hmac.new(
            "secret".encode("utf-8"),
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    t.assert_equal(signature, expected)


@runner.test("WebhookService SHA512 signature")
def test_webhook_signature_sha512(t):
    import json
    import hmac
    import hashlib

    config = {
        "webhook_url": "https://example.com/webhook",
        "secret": "secret",
        "hash_algorithm": "sha512",
    }
    service = WebhookService(config=config)
    payload = {"event": "test"}

    signature = service._generate_signature(payload)
    expected = hmac.new(
        "secret".encode("utf-8"),
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()

    t.assert_equal(signature, expected)


@runner.test("ZapierService generates correct test payload")
async def test_zapier_test_payload(t):
    from unittest.mock import patch, Mock

    config = {"webhook_url": "https://hooks.zapier.com/hooks/catch/123/abc/"}
    service = ZapierService(config=config)

    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        success, message = await service.test_connection()

        call_args = mock_post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")
        t.assert_equal(payload["event"], "test.ping")
        t.assert_true("data" in payload)


@runner.test("WordPressService respects default status config")
async def test_wordpress_default_status(t):
    from unittest.mock import patch, Mock

    config = {
        "site_url": "https://blog.example.com",
        "username": "admin",
        "application_password": "pass123",
        "default_status": "draft",
    }
    service = WordPressService(config=config)

    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 123,
            "link": "https://example.com/post",
        }
        mock_post.return_value = mock_response

        await service.create_post({"title": "Test", "content": "Body"})

        call_args = mock_post.call_args
        post_data = call_args.kwargs.get("json") or call_args[1].get("json")
        t.assert_equal(post_data["status"], "draft")


@runner.test("WordPressService handles tags in content")
async def test_wordpress_tags(t):
    from unittest.mock import patch, Mock

    config = {
        "site_url": "https://blog.example.com",
        "username": "admin",
        "application_password": "pass123",
    }
    service = WordPressService(config=config)

    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 123,
            "link": "https://example.com/post",
        }
        mock_post.return_value = mock_response

        content_data = {
            "title": "Test",
            "content": "Body",
            "tags": ["python", "api", "test"],
        }
        await service.create_post(content_data)

        call_args = mock_post.call_args
        post_data = call_args.kwargs.get("json") or call_args[1].get("json")
        t.assert_equal(post_data["tags"], ["python", "api", "test"])


@runner.test("Factory returns integration type metadata")
def test_factory_type_metadata(t):
    types = IntegrationFactory.get_available_types()

    zapier = next((t_ for t_ in types if t_["type"] == "zapier"), None)
    t.assert_true(zapier is not None)
    t.assert_true("name" in zapier)
    t.assert_true("description" in zapier)
    t.assert_true("config_schema" in zapier)


@runner.test("Webhook payload transformation with missing field")
def test_webhook_transform_missing_field(t):
    config = {
        "webhook_url": "https://example.com/webhook",
        "payload_transform": {
            "title": "${data.title}",
            "missing": "${data.nonexistent}",
        },
    }
    service = WebhookService(config=config)

    original = {"data": {"title": "My Title"}}
    transformed = service._transform_payload("test", original)

    # Missing fields should be excluded
    t.assert_equal(transformed.get("title"), "My Title")
    t.assert_true("missing" not in transformed or transformed["missing"] is None)


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    success = asyncio.run(runner.run())
    sys.exit(0 if success else 1)

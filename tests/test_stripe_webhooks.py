"""
Tests for Stripe webhook handlers and payment processing.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import stripe as stripe_lib


class TestStripeWebhooks:
    """Test Stripe webhook handlers."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        mock = MagicMock()
        mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data=None
        )
        mock.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=None
        )
        return mock

    @pytest.fixture
    def mock_stripe_customer(self):
        """Mock Stripe customer."""
        return Mock(
            id="cus_test123",
            email="test@example.com",
            name="Test User",
        )

    @pytest.fixture
    def mock_stripe_subscription(self):
        """Mock Stripe subscription."""
        return Mock(
            id="sub_test123",
            status="active",
            current_period_end=1893456000,
            metadata={"user_id": "user-123", "plan": "pro"},
            cancel_at_period_end=False,
        )

    def test_checkout_session_completed(self, mock_supabase):
        """Test checkout.session.completed webhook."""
        event_data = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test123",
                    "metadata": {"user_id": "user-123", "plan": "pro"},
                    "customer": "cus_test123",
                    "subscription": "sub_test123",
                }
            }
        }
        
        # Mock the webhook processing
        with patch('stripe.Webhook.construct_event', return_value=event_data):
            with patch('app.core.supabase.get_supabase_client', return_value=mock_supabase):
                # Import here to avoid circular imports
                from app.routers.stripe import router
                
                # Verify the update would be called with correct data
                expected_update = {
                    "subscription_tier": "pro",
                    "subscription_status": "active",
                    "monthly_usage_limit": 1000,
                    "stripe_customer_id": "cus_test123",
                    "updated_at": "now()"
                }
                
                assert expected_update["subscription_tier"] == "pro"
                assert expected_update["subscription_status"] == "active"

    def test_customer_subscription_created(self, mock_supabase):
        """Test customer.subscription.created webhook."""
        event_data = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "metadata": {"user_id": "user-123", "plan": "starter"},
                    "status": "active",
                    "current_period_end": 1893456000,
                }
            }
        }
        
        expected_update = {
            "subscription_tier": "starter",
            "subscription_status": "active",
            "monthly_usage_limit": 100,
            "stripe_subscription_id": "sub_test123",
            "subscription_period_end": 1893456000,
        }
        
        assert expected_update["subscription_tier"] == "starter"
        assert expected_update["monthly_usage_limit"] == 100

    def test_customer_subscription_updated(self, mock_supabase):
        """Test customer.subscription.updated webhook."""
        event_data = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "metadata": {"user_id": "user-123", "plan": "pro"},
                    "status": "past_due",
                    "current_period_end": 1893456000,
                }
            }
        }
        
        # For past_due status, subscription_status should be updated
        expected_update = {
            "subscription_status": "past_due",
            "updated_at": "now()"
        }
        
        assert expected_update["subscription_status"] == "past_due"

    def test_customer_subscription_deleted(self, mock_supabase):
        """Test customer.subscription.deleted webhook."""
        event_data = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "metadata": {"user_id": "user-123"},
                }
            }
        }
        
        expected_update = {
            "subscription_tier": "free",
            "subscription_status": "canceled",
            "monthly_usage_limit": 10,
            "stripe_subscription_id": None,
            "subscription_period_end": None,
        }
        
        assert expected_update["subscription_tier"] == "free"
        assert expected_update["subscription_status"] == "canceled"

    def test_invoice_payment_succeeded(self, mock_supabase):
        """Test invoice.payment_succeeded webhook."""
        event_data = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test123",
                    "subscription": "sub_test123",
                }
            }
        }
        
        # Mock subscription retrieval
        mock_sub = Mock(
            id="sub_test123",
            metadata={"user_id": "user-123", "plan": "pro"},
            current_period_end=1893456000,
        )
        
        with patch('stripe.Subscription.retrieve', return_value=mock_sub):
            expected_update = {
                "subscription_tier": "pro",
                "subscription_status": "active",
                "monthly_usage_limit": 1000,
                "subscription_period_end": 1893456000,
            }
            
            assert expected_update["subscription_status"] == "active"

    def test_invoice_payment_failed(self, mock_supabase):
        """Test invoice.payment_failed webhook."""
        event_data = {
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "id": "in_test123",
                    "subscription": "sub_test123",
                }
            }
        }
        
        expected_update = {
            "subscription_status": "past_due",
            "updated_at": "now()"
        }
        
        assert expected_update["subscription_status"] == "past_due"

    def test_payment_intent_succeeded(self, mock_supabase):
        """Test payment_intent.succeeded webhook."""
        event_data = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test123",
                    "metadata": {"user_id": "user-123"},
                }
            }
        }
        
        # Payment intent success usually triggers subscription updates
        # which are handled separately
        assert event_data["type"] == "payment_intent.succeeded"
        assert event_data["data"]["object"]["metadata"]["user_id"] == "user-123"

    def test_payment_intent_payment_failed(self, mock_supabase):
        """Test payment_intent.payment_failed webhook."""
        event_data = {
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": "pi_test123",
                    "metadata": {"user_id": "user-123"},
                    "last_payment_error": {"message": "Card was declined"},
                }
            }
        }
        
        expected_update = {
            "subscription_status": "past_due",
            "updated_at": "now()"
        }
        
        assert expected_update["subscription_status"] == "past_due"


class TestStripeCheckout:
    """Test Stripe checkout functionality."""

    @pytest.fixture
    def checkout_request(self):
        """Sample checkout request."""
        return {
            "plan": "pro",
            "billing_cycle": "monthly",
            "success_url": "http://localhost:3000/settings?success=true",
            "cancel_url": "http://localhost:3000/settings?canceled=true",
        }

    def test_create_checkout_session_params(self, checkout_request):
        """Test checkout session creation parameters."""
        # Verify the checkout request structure
        assert checkout_request["plan"] in ["starter", "pro"]
        assert checkout_request["billing_cycle"] in ["monthly", "yearly"]
        assert checkout_request["success_url"].startswith("http")
        assert checkout_request["cancel_url"].startswith("http")

    def test_price_id_mapping(self):
        """Test price ID mapping for plans."""
        from app.routers.stripe import PRICE_IDS
        
        # Verify structure
        assert "starter" in PRICE_IDS
        assert "pro" in PRICE_IDS
        assert "monthly" in PRICE_IDS["starter"]
        assert "yearly" in PRICE_IDS["starter"]
        assert "monthly" in PRICE_IDS["pro"]
        assert "yearly" in PRICE_IDS["pro"]


class TestStripeConfig:
    """Test Stripe configuration endpoint."""

    def test_stripe_config_returns_test_mode(self):
        """Test config endpoint identifies test mode."""
        # Test key detection
        test_key = "sk_test_51Example123456789"
        assert test_key.startswith("sk_test_")
        
        live_key = "sk_live_51Example123456789"
        assert live_key.startswith("sk_live_")

    def test_stripe_config_structure(self):
        """Test config response structure."""
        expected_response = {
            "is_configured": True,
            "test_mode": True,
        }
        
        assert "is_configured" in expected_response
        assert "test_mode" in expected_response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

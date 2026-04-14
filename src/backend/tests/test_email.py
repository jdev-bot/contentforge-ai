"""
Tests for email service functionality.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.email_service import (
    EmailService,
    EmailTemplateType,
    EmailPreferences,
    get_email_service,
    EMAIL_TEMPLATES,
)


@pytest.fixture
def email_service():
    """Create email service instance."""
    return EmailService()


@pytest.fixture
def mock_settings():
    """Mock settings for tests."""
    with patch("app.services.email_service.get_settings") as mock:
        settings = Mock()
        settings.RESEND_API_KEY = "test_resend_key"
        settings.SMTP_HOST = None
        settings.SMTP_USER = None
        mock.return_value = settings
        yield settings


class TestEmailTemplates:
    """Test email template rendering."""
    
    def test_welcome_template_renders(self, email_service):
        """Test welcome email template renders correctly."""
        html = email_service._render_template(
            EmailTemplateType.WELCOME,
            user_name="Test User",
        )
        
        assert "Welcome to ContentForge AI" in html
        assert "Test User" in html
        assert "Go to Dashboard" in html
        assert "<!DOCTYPE html>" in html
    
    def test_password_reset_template_renders(self, email_service):
        """Test password reset template renders correctly."""
        html = email_service._render_template(
            EmailTemplateType.PASSWORD_RESET,
            user_name="Test User",
            reset_url="https://example.com/reset?token=abc123",
            expiry_hours=24,
        )
        
        assert "Password Reset Request" in html
        assert "Test User" in html
        assert "abc123" in html
        assert "24 hours" in html
    
    def test_subscription_confirmation_template(self, email_service):
        """Test subscription confirmation template."""
        html = email_service._render_template(
            EmailTemplateType.SUBSCRIPTION_CONFIRMATION,
            user_name="Test User",
            plan_name="Pro",
            price="$49",
            billing_cycle="month",
            usage_limit=1000,
        )
        
        assert "Pro" in html
        assert "$49" in html
        assert "1000" in html
        assert "Subscription Confirmed" in html
    
    def test_invoice_receipt_template(self, email_service):
        """Test invoice receipt template."""
        html = email_service._render_template(
            EmailTemplateType.INVOICE_RECEIPT,
            user_name="Test User",
            invoice_number="INV-001",
            amount="$49.00",
            plan_name="Pro",
            billing_period="Monthly",
            invoice_url="https://example.com/invoice",
        )
        
        assert "Payment Received" in html
        assert "INV-001" in html
        assert "$49.00" in html
    
    def test_weekly_summary_template(self, email_service):
        """Test weekly summary template."""
        html = email_service._render_template(
            EmailTemplateType.WEEKLY_USAGE_SUMMARY,
            user_name="Test User",
            week_range="Jan 1 - Jan 7",
            content_created=15,
            word_count=7500,
            monthly_usage=45,
            monthly_limit=100,
            usage_percentage=45,
        )
        
        assert "Your Weekly Summary" in html
        assert "15" in html
        assert "7500" in html
        assert "45" in html
    
    def test_usage_alert_template(self, email_service):
        """Test usage alert template."""
        html = email_service._render_template(
            EmailTemplateType.USAGE_ALERT,
            user_name="Test User",
            monthly_usage=80,
            monthly_limit=100,
            usage_percentage=80,
            remaining=20,
            plan_name="Pro",
        )
        
        assert "Usage Alert" in html
        assert "80%" in html
        assert "20" in html
        assert "Upgrade Plan" in html
    
    def test_abandoned_cart_template(self, email_service):
        """Test abandoned cart template."""
        html = email_service._render_template(
            EmailTemplateType.ABANDONED_CART,
            user_name="Test User",
            signup_url="https://example.com/signup",
        )
        
        assert "Welcome Back" in html
        assert "WELCOME20" in html
        assert "20% off" in html
    
    def test_feature_announcement_template(self, email_service):
        """Test feature announcement template."""
        html = email_service._render_template(
            EmailTemplateType.FEATURE_ANNOUNCEMENT,
            user_name="Test User",
            feature_name="AI Video Summarization",
            feature_description="Automatically create video summaries",
            feature_icon="🎬",
            benefits=["Save time", "Increase engagement", "Reach more viewers"],
            feature_url="https://example.com/feature",
        )
        
        assert "New Feature Available" in html
        assert "AI Video Summarization" in html
        assert "🎬" in html


class TestEmailSubjects:
    """Test email subject generation."""
    
    def test_get_welcome_subject(self, email_service):
        """Test welcome subject."""
        subject = email_service._get_subject(EmailTemplateType.WELCOME)
        assert "Welcome" in subject
    
    def test_get_password_reset_subject(self, email_service):
        """Test password reset subject."""
        subject = email_service._get_subject(EmailTemplateType.PASSWORD_RESET)
        assert "Reset" in subject
    
    def test_get_invoice_subject(self, email_service):
        """Test invoice receipt subject."""
        subject = email_service._get_subject(EmailTemplateType.INVOICE_RECEIPT)
        assert "receipt" in subject.lower()


class TestEmailSending:
    """Test email sending functionality."""
    
    @pytest.mark.asyncio
    async def test_send_via_resend_success(self, email_service, mock_settings):
        """Test successful Resend API call."""
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "email_123"}
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client
            
            result = await email_service.send_via_resend(
                "test@example.com",
                "Test Subject",
                "<html>Test</html>"
            )
            
            assert result == "email_123"
    
    @pytest.mark.asyncio
    async def test_send_via_resend_no_api_key(self, email_service):
        """Test Resend fails without API key."""
        with patch("app.services.email_service.get_settings") as mock:
            settings = Mock()
            settings.RESEND_API_KEY = None
            mock.return_value = settings
            
            service = EmailService()
            result = await service.send_via_resend(
                "test@example.com",
                "Test Subject",
                "<html>Test</html>"
            )
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_send_via_resend_api_error(self, email_service, mock_settings):
        """Test Resend API error handling."""
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client
            
            result = await email_service.send_via_resend(
                "test@example.com",
                "Test Subject",
                "<html>Test</html>"
            )
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_send_via_smtp_success(self, email_service):
        """Test SMTP fallback sending."""
        with patch("app.services.email_service.get_settings") as mock:
            settings = Mock()
            settings.SMTP_HOST = "smtp.example.com"
            settings.SMTP_PORT = 587
            settings.SMTP_USER = "user@example.com"
            settings.SMTP_PASSWORD = "password"
            mock.return_value = settings
            
            with patch("smtplib.SMTP") as mock_smtp:
                mock_server = Mock()
                mock_smtp.return_value.__enter__ = Mock(return_value=mock_server)
                mock_smtp.return_value.__exit__ = Mock(return_value=False)
                
                service = EmailService()
                result = await service.send_via_smtp(
                    "test@example.com",
                    "Test Subject",
                    "<html>Test</html>"
                )
                
                assert result is True
                mock_server.login.assert_called_once()
                mock_server.sendmail.assert_called_once()


class TestUserPreferences:
    """Test user preference filtering."""
    
    @pytest.mark.asyncio
    async def test_marketing_email_respected(self, email_service):
        """Test marketing emails respect user preferences."""
        prefs = EmailPreferences()
        prefs.marketing_emails = False
        
        # Mock send_via_resend to return None
        with patch.object(email_service, "send_via_resend", return_value=None):
            with patch.object(email_service, "send_via_smtp", return_value=False):
                result = await email_service.send_email(
                    "test@example.com",
                    EmailTemplateType.FEATURE_ANNOUNCEMENT,
                    {"user_name": "Test"},
                    prefs
                )
                
                # Should be skipped due to preferences
                assert result is None
    
    @pytest.mark.asyncio
    async def test_weekly_digest_respected(self, email_service):
        """Test weekly digest respects user preferences."""
        prefs = EmailPreferences()
        prefs.weekly_digest = False
        
        with patch.object(email_service, "send_via_resend", return_value=None):
            with patch.object(email_service, "send_via_smtp", return_value=False):
                result = await email_service.send_email(
                    "test@example.com",
                    EmailTemplateType.WEEKLY_USAGE_SUMMARY,
                    {"user_name": "Test"},
                    prefs
                )
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_usage_alert_respected(self, email_service):
        """Test usage alerts respect user preferences."""
        prefs = EmailPreferences()
        prefs.usage_alerts = False
        
        with patch.object(email_service, "send_via_resend", return_value=None):
            with patch.object(email_service, "send_via_smtp", return_value=False):
                result = await email_service.send_email(
                    "test@example.com",
                    EmailTemplateType.USAGE_ALERT,
                    {"user_name": "Test"},
                    prefs
                )
                
                assert result is None


class TestEmailServiceSingleton:
    """Test email service singleton."""
    
    def test_get_email_service_returns_singleton(self):
        """Test get_email_service returns same instance."""
        service1 = get_email_service()
        service2 = get_email_service()
        
        assert service1 is service2


class TestConvenienceMethods:
    """Test email service convenience methods."""
    
    @pytest.mark.asyncio
    async def test_send_welcome_email(self, email_service):
        """Test send_welcome_email convenience method."""
        with patch.object(email_service, "send_email", return_value="email_123"):
            result = await email_service.send_welcome_email(
                "test@example.com",
                "Test User"
            )
            
            assert result == "email_123"
    
    @pytest.mark.asyncio
    async def test_send_password_reset(self, email_service):
        """Test send_password_reset convenience method."""
        with patch.object(email_service, "send_email", return_value="email_123"):
            result = await email_service.send_password_reset(
                "test@example.com",
                "Test User",
                "reset_token_123"
            )
            
            assert result == "email_123"
    
    @pytest.mark.asyncio
    async def test_send_usage_alert(self, email_service):
        """Test send_usage_alert convenience method."""
        with patch.object(email_service, "send_email", return_value="email_123"):
            result = await email_service.send_usage_alert(
                "test@example.com",
                "Test User",
                80,
                100,
                "Pro"
            )
            
            assert result == "email_123"

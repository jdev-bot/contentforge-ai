"""
Email service with Resend.com integration, SMTP fallback, and Celery task queue.
"""
import logging
import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, List, Union
from enum import Enum

import httpx
from jinja2 import Template

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class EmailTemplateType(str, Enum):
    """Email template types."""
    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"
    SUBSCRIPTION_CONFIRMATION = "subscription_confirmation"
    INVOICE_RECEIPT = "invoice_receipt"
    WEEKLY_USAGE_SUMMARY = "weekly_usage_summary"
    FEATURE_ANNOUNCEMENT = "feature_announcement"
    ABANDONED_CART = "abandoned_cart"
    USAGE_ALERT = "usage_alert"


class EmailPreferences:
    """User email preferences model."""
    marketing_emails: bool = True
    usage_alerts: bool = True
    weekly_digest: bool = True
    feature_announcements: bool = True
    invoice_receipts: bool = True
    digest_frequency: str = "weekly"  # daily, weekly, monthly


# HTML Email Templates
EMAIL_TEMPLATES = {
    EmailTemplateType.WELCOME: Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to ContentForge AI</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f4f4f5; }
        .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .header { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 40px 30px; text-align: center; }
        .header h1 { color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; }
        .content { padding: 40px 30px; }
        .content h2 { color: #1f2937; margin-top: 0; font-size: 22px; }
        .content p { color: #4b5563; line-height: 1.7; font-size: 16px; }
        .button { display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; margin: 20px 0; }
        .feature { background-color: #f9fafb; border-left: 4px solid #6366f1; padding: 16px 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }
        .feature h3 { margin: 0 0 8px 0; color: #1f2937; font-size: 16px; }
        .feature p { margin: 0; color: #6b7280; font-size: 14px; }
        .footer { background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb; }
        .footer p { color: #9ca3af; font-size: 14px; margin: 0; }
        .footer a { color: #6366f1; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Welcome to ContentForge AI</h1>
        </div>
        <div class="content">
            <h2>Hi {{ user_name }},</h2>
            <p>Welcome aboard! We're thrilled to have you join the ContentForge AI community. Your account has been successfully created and you're ready to start creating amazing content.</p>
            
            <div style="text-align: center;">
                <a href="{{ dashboard_url }}" class="button">Go to Dashboard</a>
            </div>
            
            <p>Here's what you can do with ContentForge AI:</p>
            
            <div class="feature">
                <h3>🤖 AI-Powered Content Generation</h3>
                <p>Create blog posts, social media content, and more in seconds.</p>
            </div>
            
            <div class="feature">
                <h3>📊 Content Analytics</h3>
                <p>Track engagement and optimize your content strategy.</p>
            </div>
            
            <div class="feature">
                <h3>🔗 Multi-Channel Distribution</h3>
                <p>Publish to WordPress, social media, and more with one click.</p>
            </div>
            
            <p style="margin-top: 30px;">Need help getting started? Reply to this email or check out our <a href="{{ help_url }}">help center</a>.</p>
            
            <p>Happy creating!<br>The ContentForge AI Team</p>
        </div>
        <div class="footer">
            <p>© {{ year }} ContentForge AI. All rights reserved.</p>
            <p style="margin-top: 10px;"><a href="{{ unsubscribe_url }}">Manage email preferences</a></p>
        </div>
    </div>
</body>
</html>
"""),

    EmailTemplateType.PASSWORD_RESET: Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f4f4f5; }
        .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .header { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 40px 30px; text-align: center; }
        .header h1 { color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; }
        .content { padding: 40px 30px; }
        .content h2 { color: #1f2937; margin-top: 0; font-size: 22px; }
        .content p { color: #4b5563; line-height: 1.7; font-size: 16px; }
        .button { display: inline-block; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; margin: 20px 0; }
        .warning { background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }
        .warning p { margin: 0; color: #92400e; font-size: 14px; }
        .footer { background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb; }
        .footer p { color: #9ca3af; font-size: 14px; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Password Reset Request</h1>
        </div>
        <div class="content">
            <h2>Hi {{ user_name }},</h2>
            <p>We received a request to reset the password for your ContentForge AI account. Click the button below to set a new password:</p>
            
            <div style="text-align: center;">
                <a href="{{ reset_url }}" class="button">Reset Password</a>
            </div>
            
            <div class="warning">
                <p><strong>Security Notice:</strong> This link will expire in {{ expiry_hours }} hours. If you didn't request this password reset, you can safely ignore this email.</p>
            </div>
            
            <p style="margin-top: 30px;">If the button doesn't work, copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background-color: #f3f4f6; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 14px;">{{ reset_url }}</p>
            
            <p>Need help? Contact us at <a href="mailto:support@contentforge.ai">support@contentforge.ai</a></p>
        </div>
        <div class="footer">
            <p>© {{ year }} ContentForge AI. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""),

    EmailTemplateType.SUBSCRIPTION_CONFIRMATION: Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subscription Confirmed</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f4f4f5; }
        .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .header { background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 40px 30px; text-align: center; }
        .header h1 { color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; }
        .content { padding: 40px 30px; }
        .content h2 { color: #1f2937; margin-top: 0; font-size: 22px; }
        .content p { color: #4b5563; line-height: 1.7; font-size: 16px; }
        .plan-card { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #ffffff; padding: 24px; border-radius: 12px; margin: 24px 0; }
        .plan-card h3 { margin: 0 0 8px 0; font-size: 20px; }
        .plan-card .price { font-size: 32px; font-weight: 700; }
        .plan-card .period { font-size: 16px; opacity: 0.9; }
        .feature-list { list-style: none; padding: 0; margin: 20px 0; }
        .feature-list li { padding: 8px 0; color: #4b5563; }
        .feature-list li::before { content: "✓"; color: #10b981; font-weight: bold; margin-right: 12px; }
        .button { display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; margin: 20px 0; }
        .footer { background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb; }
        .footer p { color: #9ca3af; font-size: 14px; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Subscription Confirmed!</h1>
        </div>
        <div class="content">
            <h2>Thank you, {{ user_name }}!</h2>
            <p>Your subscription to ContentForge AI has been successfully activated. You now have access to all {{ plan_name }} features.</p>
            
            <div class="plan-card">
                <h3>{{ plan_name }}</h3>
                <div class="price">{{ price }}<span class="period">/{{ billing_cycle }}</span></div>
            </div>
            
            <h3>What's included:</h3>
            <ul class="feature-list">
                <li>{{ usage_limit }} content generations per month</li>
                <li>Advanced AI models</li>
                <li>Priority support</li>
                <li>Analytics dashboard</li>
                <li>API access</li>
            </ul>
            
            <div style="text-align: center;">
                <a href="{{ dashboard_url }}" class="button">Start Creating</a>
            </div>
            
            <p style="margin-top: 30px;">You can manage your subscription anytime from your <a href="{{ settings_url }}">account settings</a>.</p>
        </div>
        <div class="footer">
            <p>© {{ year }} ContentForge AI. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""),

    EmailTemplateType.INVOICE_RECEIPT: Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Receipt</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f4f4f5; }
        .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .header { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 40px 30px; text-align: center; }
        .header h1 { color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; }
        .content { padding: 40px 30px; }
        .content h2 { color: #1f2937; margin-top: 0; font-size: 22px; }
        .content p { color: #4b5563; line-height: 1.7; font-size: 16px; }
        .receipt-box { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 24px; margin: 24px 0; }
        .receipt-row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e5e7eb; }
        .receipt-row:last-child { border-bottom: none; font-weight: 700; }
        .receipt-row.total { color: #10b981; font-size: 18px; }
        .success-badge { display: inline-block; background-color: #d1fae5; color: #065f46; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; }
        .button { display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; margin: 20px 0; }
        .footer { background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb; }
        .footer p { color: #9ca3af; font-size: 14px; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Payment Received</h1>
        </div>
        <div class="content">
            <h2>Hi {{ user_name }},</h2>
            <p>Thank you for your payment. We've successfully processed your subscription renewal.</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <span class="success-badge">Payment Successful</span>
            </div>
            
            <div class="receipt-box">
                <div class="receipt-row">
                    <span>Invoice Number</span>
                    <span>{{ invoice_number }}</span>
                </div>
                <div class="receipt-row">
                    <span>Date</span>
                    <span>{{ date }}</span>
                </div>
                <div class="receipt-row">
                    <span>Plan</span>
                    <span>{{ plan_name }}</span>
                </div>
                <div class="receipt-row">
                    <span>Billing Period</span>
                    <span>{{ billing_period }}</span>
                </div>
                <div class="receipt-row total">
                    <span>Total Paid</span>
                    <span>{{ amount }}</span>
                </div>
            </div>
            
            <div style="text-align: center;">
                <a href="{{ invoice_url }}" class="button">Download Invoice</a>
            </div>
            
            <p style="margin-top: 30px;">Questions about your billing? Contact us at <a href="mailto:billing@contentforge.ai">billing@contentforge.ai</a></p>
        </div>
        <div class="footer">
            <p>© {{ year }} ContentForge AI. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""),

    EmailTemplateType.WEEKLY_USAGE_SUMMARY: Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Weekly Summary</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f4f4f5; }
        .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .header { background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); padding: 40px 30px; text-align: center; }
        .header h1 { color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; }
        .content { padding: 40px 30px; }
        .content h2 { color: #1f2937; margin-top: 0; font-size: 22px; }
        .content p { color: #4b5563; line-height: 1.7; font-size: 16px; }
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 24px 0; }
        .stat-card { background-color: #f9fafb; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-card .number { font-size: 32px; font-weight: 700; color: #6366f1; }
        .stat-card .label { font-size: 14px; color: #6b7280; margin-top: 4px; }
        .usage-bar { background-color: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden; margin: 16px 0; }
        .usage-fill { background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%); height: 100%; border-radius: 4px; }
        .highlight { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid #f59e0b; padding: 16px 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }
        .highlight h3 { margin: 0 0 8px 0; color: #92400e; font-size: 16px; }
        .button { display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; margin: 20px 0; }
        .footer { background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb; }
        .footer p { color: #9ca3af; font-size: 14px; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Your Weekly Summary</h1>
        </div>
        <div class="content">
            <h2>Hi {{ user_name }},</h2>
            <p>Here's how you used ContentForge AI this week ({{ week_range }}):</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">{{ content_created }}</div>
                    <div class="label">Content Created</div>
                </div>
                <div class="stat-card">
                    <div class="number">{{ word_count }}</div>
                    <div class="label">Words Generated</div>
                </div>
            </div>
            
            <h3>Monthly Usage</h3>
            <p>{{ monthly_usage }} / {{ monthly_limit }} generations used</p>
            <div class="usage-bar">
                <div class="usage-fill" style="width: {{ usage_percentage }}%;"></div>
            </div>
            
            {% if top_performing %}
            <div class="highlight">
                <h3>🏆 Top Performing Content</h3>
                <p style="margin: 0;">{{ top_performing }}</p>
            </div>
            {% endif %}
            
            <div style="text-align: center;">
                <a href="{{ dashboard_url }}" class="button">Create More Content</a>
            </div>
        </div>
        <div class="footer">
            <p>© {{ year }} ContentForge AI. All rights reserved.</p>
            <p style="margin-top: 10px;"><a href="{{ unsubscribe_url }}">Unsubscribe from weekly digests</a></p>
        </div>
    </div>
</body>
</html>
"""),

    EmailTemplateType.FEATURE_ANNOUNCEMENT: Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Feature Announcement</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f4f4f5; }
        .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .header { background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); padding: 40px 30px; text-align: center; }
        .header h1 { color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; }
        .content { padding: 40px 30px; }
        .content h2 { color: #1f2937; margin-top: 0; font-size: 22px; }
        .content p { color: #4b5563; line-height: 1.7; font-size: 16px; }
        .feature-showcase { background: linear-gradient(135deg, #f3e8ff 0%, #e0e7ff 100%); padding: 30px; border-radius: 12px; margin: 24px 0; text-align: center; }
        .feature-showcase h3 { margin: 0 0 12px 0; color: #7c3aed; font-size: 24px; }
        .feature-showcase p { margin: 0; color: #6b7280; }
        .feature-icon { font-size: 48px; margin-bottom: 16px; }
        .benefit-list { list-style: none; padding: 0; margin: 20px 0; }
        .benefit-list li { padding: 12px 0; color: #4b5563; display: flex; align-items: flex-start; }
        .benefit-list li::before { content: "🚀"; margin-right: 12px; }
        .button { display: inline-block; background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; margin: 20px 0; }
        .footer { background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb; }
        .footer p { color: #9ca3af; font-size: 14px; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✨ New Feature Available</h1>
        </div>
        <div class="content">
            <h2>Hi {{ user_name }},</h2>
            <p>We're excited to announce a powerful new feature that will supercharge your content creation workflow!</p>
            
            <div class="feature-showcase">
                <div class="feature-icon">{{ feature_icon }}</div>
                <h3>{{ feature_name }}</h3>
                <p>{{ feature_description }}</p>
            </div>
            
            <h3>What you can do:</h3>
            <ul class="benefit-list">
                {% for benefit in benefits %}
                <li>{{ benefit }}</li>
                {% endfor %}
            </ul>
            
            <div style="text-align: center;">
                <a href="{{ feature_url }}" class="button">Try It Now</a>
            </div>
            
            <p style="margin-top: 30px;">Have feedback? We'd love to hear from you—just reply to this email.</p>
        </div>
        <div class="footer">
            <p>© {{ year }} ContentForge AI. All rights reserved.</p>
            <p style="margin-top: 10px;"><a href="{{ unsubscribe_url }}">Unsubscribe from feature announcements</a></p>
        </div>
    </div>
</body>
</html>
"""),

    EmailTemplateType.ABANDONED_CART: Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Your Registration</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f4f4f5; }
        .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .header { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 40px 30px; text-align: center; }
        .header h1 { color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; }
        .content { padding: 40px 30px; }
        .content h2 { color: #1f2937; margin-top: 0; font-size: 22px; }
        .content p { color: #4b5563; line-height: 1.7; font-size: 16px; }
        .offer-box { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 2px dashed #f59e0b; padding: 24px; border-radius: 12px; margin: 24px 0; text-align: center; }
        .offer-box h3 { margin: 0 0 8px 0; color: #92400e; font-size: 18px; }
        .offer-box .code { font-family: monospace; font-size: 24px; font-weight: 700; color: #92400e; background-color: #ffffff; padding: 8px 16px; border-radius: 6px; display: inline-block; margin: 12px 0; }
        .benefit-list { list-style: none; padding: 0; margin: 20px 0; }
        .benefit-list li { padding: 8px 0; color: #4b5563; }
        .benefit-list li::before { content: "✓"; color: #10b981; font-weight: bold; margin-right: 12px; }
        .button { display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; margin: 20px 0; }
        .button-secondary { display: inline-block; background-color: #e5e7eb; color: #374151; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; margin: 10px 0; }
        .footer { background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb; }
        .footer p { color: #9ca3af; font-size: 14px; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👋 Welcome Back!</h1>
        </div>
        <div class="content">
            <h2>Hi {{ user_name }},</h2>
            <p>We noticed you started signing up for ContentForge AI but didn't complete your registration. No worries—it only takes a moment to get started!</p>
            
            <div class="offer-box">
                <h3>🎁 Special Welcome Offer</h3>
                <p>Use code</p>
                <div class="code">WELCOME20</div>
                <p>for 20% off your first month!</p>
            </div>
            
            <h3>What you'll get:</h3>
            <ul class="benefit-list">
                <li>10 free content generations to start</li>
                <li>Access to advanced AI models</li>
                <li>Content analytics & insights</li>
                <li>Priority customer support</li>
            </ul>
            
            <div style="text-align: center;">
                <a href="{{ signup_url }}" class="button">Complete Signup</a>
            </div>
            
            <p style="margin-top: 30px; text-align: center;">
                <a href="{{ unsubscribe_url }}" class="button-secondary">I'm not interested</a>
            </p>
        </div>
        <div class="footer">
            <p>© {{ year }} ContentForge AI. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""),

    EmailTemplateType.USAGE_ALERT: Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Usage Alert</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f4f4f5; }
        .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .header { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 40px 30px; text-align: center; }
        .header h1 { color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; }
        .content { padding: 40px 30px; }
        .content h2 { color: #1f2937; margin-top: 0; font-size: 22px; }
        .content p { color: #4b5563; line-height: 1.7; font-size: 16px; }
        .alert-box { background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 20px; margin: 24px 0; border-radius: 0 8px 8px 0; }
        .alert-box h3 { margin: 0 0 8px 0; color: #92400e; }
        .alert-box p { margin: 0; color: #a16207; }
        .usage-stats { background-color: #f9fafb; padding: 24px; border-radius: 8px; margin: 20px 0; }
        .usage-row { display: flex; justify-content: space-between; padding: 8px 0; }
        .usage-bar { background-color: #e5e7eb; height: 12px; border-radius: 6px; overflow: hidden; margin: 16px 0; }
        .usage-fill { background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%); height: 100%; border-radius: 6px; }
        .button { display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; margin: 10px 5px; }
        .button-secondary { display: inline-block; background-color: #e5e7eb; color: #374151; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; margin: 10px 5px; }
        .footer { background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb; }
        .footer p { color: #9ca3af; font-size: 14px; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Usage Alert</h1>
        </div>
        <div class="content">
            <h2>Hi {{ user_name }},</h2>
            <p>You're making great progress with ContentForge AI! We wanted to give you a heads up about your usage:</p>
            
            <div class="alert-box">
                <h3>📊 You've used {{ usage_percentage }}% of your monthly limit</h3>
                <p>You have {{ remaining }} generations remaining this month.</p>
            </div>
            
            <div class="usage-stats">
                <div class="usage-row">
                    <span>Current Plan</span>
                    <strong>{{ plan_name }}</strong>
                </div>
                <div class="usage-row">
                    <span>Monthly Limit</span>
                    <strong>{{ monthly_limit }} generations</strong>
                </div>
                <div class="usage-row">
                    <span>Used This Month</span>
                    <strong>{{ monthly_usage }}</strong>
                </div>
                <div class="usage-bar">
                    <div class="usage-fill" style="width: {{ usage_percentage }}%;"></div>
                </div>
                <p style="text-align: center; margin: 8px 0 0 0; font-size: 14px; color: #6b7280;">{{ remaining }} remaining</p>
            </div>
            
            <p>To ensure uninterrupted access, consider upgrading your plan:</p>
            
            <div style="text-align: center;">
                <a href="{{ upgrade_url }}" class="button">Upgrade Plan</a>
                <a href="{{ dashboard_url }}" class="button-secondary">View Dashboard</a>
            </div>
        </div>
        <div class="footer">
            <p>© {{ year }} ContentForge AI. All rights reserved.</p>
            <p style="margin-top: 10px;"><a href="{{ unsubscribe_url }}">Unsubscribe from usage alerts</a></p>
        </div>
    </div>
</body>
</html>
"""),
}


class EmailService:
    """Email service with Resend.com integration and SMTP fallback."""
    
    def __init__(self):
        self.settings = get_settings()
        self.from_email = "noreply@contentforge.ai"
        self.from_name = "ContentForge AI"
        self.base_url = "https://app.contentforge.ai"
        
    def _get_from_address(self) -> str:
        """Get formatted from address."""
        return f"{self.from_name} <{self.from_email}>"
    
    def _render_template(self, template_type: EmailTemplateType, **kwargs) -> str:
        """Render email template with provided variables."""
        template = EMAIL_TEMPLATES.get(template_type)
        if not template:
            raise ValueError(f"Unknown template type: {template_type}")
        
        # Add default variables
        kwargs.setdefault('year', datetime.now().year)
        kwargs.setdefault('dashboard_url', f"{self.base_url}/dashboard")
        kwargs.setdefault('settings_url', f"{self.base_url}/settings")
        kwargs.setdefault('help_url', f"{self.base_url}/help")
        kwargs.setdefault('unsubscribe_url', f"{self.base_url}/settings/notifications")
        
        return template.render(**kwargs)
    
    def _get_subject(self, template_type: EmailTemplateType) -> str:
        """Get email subject for template type."""
        subjects = {
            EmailTemplateType.WELCOME: "🚀 Welcome to ContentForge AI!",
            EmailTemplateType.PASSWORD_RESET: "Reset your ContentForge AI password",
            EmailTemplateType.SUBSCRIPTION_CONFIRMATION: "🎉 Your subscription is confirmed!",
            EmailTemplateType.INVOICE_RECEIPT: "Payment receipt from ContentForge AI",
            EmailTemplateType.WEEKLY_USAGE_SUMMARY: "📊 Your ContentForge AI weekly summary",
            EmailTemplateType.FEATURE_ANNOUNCEMENT: "✨ New feature: Check it out!",
            EmailTemplateType.ABANDONED_CART: "👋 Complete your signup and get 20% off",
            EmailTemplateType.USAGE_ALERT: "⚠️ You're approaching your usage limit",
        }
        return subjects.get(template_type, "Message from ContentForge AI")
    
    async def send_via_resend(self, to_email: str, subject: str, html_content: str) -> Optional[str]:
        """Send email via Resend.com API."""
        if not self.settings.RESEND_API_KEY:
            logger.warning("RESEND_API_KEY not configured")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {self.settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": self._get_from_address(),
                        "to": to_email,
                        "subject": subject,
                        "html": html_content,
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Email sent via Resend: {result.get('id')}")
                    return result.get('id')
                else:
                    logger.error(f"Resend API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error sending via Resend: {e}")
            return None
    
    async def send_via_smtp(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via SMTP as fallback."""
        smtp_host = getattr(self.settings, 'SMTP_HOST', None)
        smtp_port = getattr(self.settings, 'SMTP_PORT', 587)
        smtp_user = getattr(self.settings, 'SMTP_USER', None)
        smtp_password = getattr(self.settings, 'SMTP_PASSWORD', None)
        
        if not smtp_host or not smtp_user:
            logger.warning("SMTP not configured")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self._get_from_address()
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls(context=context)
                server.login(smtp_user, smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            logger.info(f"Email sent via SMTP to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending via SMTP: {e}")
            return False
    
    async def send_email(
        self,
        to_email: str,
        template_type: EmailTemplateType,
        template_data: Dict,
        user_preferences: Optional[EmailPreferences] = None
    ) -> Optional[str]:
        """
        Send templated email.
        
        Args:
            to_email: Recipient email address
            template_type: Type of email template
            template_data: Data for template rendering
            user_preferences: User's email preferences (for opt-out checks)
            
        Returns:
            Email ID if sent successfully, None otherwise
        """
        # Check user preferences
        if user_preferences:
            if template_type == EmailTemplateType.FEATURE_ANNOUNCEMENT and not user_preferences.marketing_emails:
                logger.info(f"Skipping marketing email to {to_email} - user opted out")
                return None
            if template_type == EmailTemplateType.WEEKLY_USAGE_SUMMARY and not user_preferences.weekly_digest:
                logger.info(f"Skipping weekly digest to {to_email} - user opted out")
                return None
            if template_type == EmailTemplateType.USAGE_ALERT and not user_preferences.usage_alerts:
                logger.info(f"Skipping usage alert to {to_email} - user opted out")
                return None
            if template_type == EmailTemplateType.INVOICE_RECEIPT and not user_preferences.invoice_receipts:
                logger.info(f"Skipping invoice to {to_email} - user opted out")
                return None
        
        # Render template
        html_content = self._render_template(template_type, **template_data)
        subject = self._get_subject(template_type)
        
        # Try Resend first
        email_id = await self.send_via_resend(to_email, subject, html_content)
        if email_id:
            return email_id
        
        # Fallback to SMTP
        smtp_success = await self.send_via_smtp(to_email, subject, html_content)
        if smtp_success:
            return "smtp-sent"
        
        logger.error(f"Failed to send email to {to_email} via all methods")
        return None
    
    # Convenience methods for specific email types
    
    async def send_welcome_email(self, to_email: str, user_name: str, **kwargs) -> Optional[str]:
        """Send welcome email to new user."""
        template_data = {
            'user_name': user_name,
            'signup_url': f"{self.base_url}/signup",
            **kwargs
        }
        return await self.send_email(to_email, EmailTemplateType.WELCOME, template_data)
    
    async def send_password_reset(
        self,
        to_email: str,
        user_name: str,
        reset_token: str,
        expiry_hours: int = 24,
        **kwargs
    ) -> Optional[str]:
        """Send password reset email."""
        template_data = {
            'user_name': user_name,
            'reset_url': f"{self.base_url}/reset-password?token={reset_token}",
            'expiry_hours': expiry_hours,
            **kwargs
        }
        return await self.send_email(to_email, EmailTemplateType.PASSWORD_RESET, template_data)
    
    async def send_subscription_confirmation(
        self,
        to_email: str,
        user_name: str,
        plan_name: str,
        price: str,
        billing_cycle: str,
        usage_limit: int,
        **kwargs
    ) -> Optional[str]:
        """Send subscription confirmation email."""
        template_data = {
            'user_name': user_name,
            'plan_name': plan_name,
            'price': price,
            'billing_cycle': billing_cycle,
            'usage_limit': usage_limit,
            **kwargs
        }
        return await self.send_email(to_email, EmailTemplateType.SUBSCRIPTION_CONFIRMATION, template_data)
    
    async def send_invoice_receipt(
        self,
        to_email: str,
        user_name: str,
        invoice_number: str,
        amount: str,
        plan_name: str,
        billing_period: str,
        invoice_url: str,
        **kwargs
    ) -> Optional[str]:
        """Send invoice receipt email."""
        template_data = {
            'user_name': user_name,
            'invoice_number': invoice_number,
            'amount': amount,
            'plan_name': plan_name,
            'billing_period': billing_period,
            'invoice_url': invoice_url,
            'date': datetime.now().strftime('%B %d, %Y'),
            **kwargs
        }
        preferences = kwargs.get('user_preferences', EmailPreferences())
        preferences.invoice_receipts = kwargs.get('invoice_receipts', True)
        return await self.send_email(
            to_email,
            EmailTemplateType.INVOICE_RECEIPT,
            template_data,
            preferences
        )
    
    async def send_weekly_summary(
        self,
        to_email: str,
        user_name: str,
        week_range: str,
        content_created: int,
        word_count: int,
        monthly_usage: int,
        monthly_limit: int,
        top_performing: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """Send weekly usage summary email."""
        usage_percentage = min(100, int((monthly_usage / monthly_limit) * 100)) if monthly_limit > 0 else 0
        template_data = {
            'user_name': user_name,
            'week_range': week_range,
            'content_created': content_created,
            'word_count': word_count,
            'monthly_usage': monthly_usage,
            'monthly_limit': monthly_limit,
            'usage_percentage': usage_percentage,
            'top_performing': top_performing,
            **kwargs
        }
        preferences = kwargs.get('user_preferences', EmailPreferences())
        preferences.weekly_digest = kwargs.get('weekly_digest', True)
        return await self.send_email(
            to_email,
            EmailTemplateType.WEEKLY_USAGE_SUMMARY,
            template_data,
            preferences
        )
    
    async def send_feature_announcement(
        self,
        to_email: str,
        user_name: str,
        feature_name: str,
        feature_description: str,
        feature_icon: str,
        benefits: List[str],
        feature_url: str,
        **kwargs
    ) -> Optional[str]:
        """Send feature announcement email."""
        template_data = {
            'user_name': user_name,
            'feature_name': feature_name,
            'feature_description': feature_description,
            'feature_icon': feature_icon,
            'benefits': benefits,
            'feature_url': feature_url,
            **kwargs
        }
        preferences = kwargs.get('user_preferences', EmailPreferences())
        preferences.marketing_emails = kwargs.get('marketing_emails', True)
        return await self.send_email(
            to_email,
            EmailTemplateType.FEATURE_ANNOUNCEMENT,
            template_data,
            preferences
        )
    
    async def send_abandoned_cart(
        self,
        to_email: str,
        user_name: str,
        signup_url: str,
        **kwargs
    ) -> Optional[str]:
        """Send abandoned cart (incomplete signup) email."""
        template_data = {
            'user_name': user_name,
            'signup_url': signup_url,
            **kwargs
        }
        return await self.send_email(to_email, EmailTemplateType.ABANDONED_CART, template_data)
    
    async def send_usage_alert(
        self,
        to_email: str,
        user_name: str,
        monthly_usage: int,
        monthly_limit: int,
        plan_name: str,
        **kwargs
    ) -> Optional[str]:
        """Send usage alert email when approaching limit."""
        usage_percentage = min(100, int((monthly_usage / monthly_limit) * 100)) if monthly_limit > 0 else 0
        remaining = monthly_limit - monthly_usage
        
        template_data = {
            'user_name': user_name,
            'monthly_usage': monthly_usage,
            'monthly_limit': monthly_limit,
            'usage_percentage': usage_percentage,
            'remaining': remaining,
            'plan_name': plan_name,
            'upgrade_url': f"{self.base_url}/settings/subscription",
            **kwargs
        }
        preferences = kwargs.get('user_preferences', EmailPreferences())
        preferences.usage_alerts = kwargs.get('usage_alerts', True)
        return await self.send_email(
            to_email,
            EmailTemplateType.USAGE_ALERT,
            template_data,
            preferences
        )


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get singleton email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

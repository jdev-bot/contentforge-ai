"""
Celery tasks for email sending with retry logic and rate limiting.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.services.email_service import (
    EmailPreferences,
    EmailService,
    EmailTemplateType,
    get_email_service,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailTaskError(Exception):
    """Custom exception for email task errors."""

    pass


def get_user_email_preferences(user_id: str) -> EmailPreferences:
    """Fetch user email preferences from database."""
    try:
        supabase = get_supabase_admin_client()
        result = (
            supabase.table("profiles")
            .select("email_preferences")
            .eq("id", user_id)
            .single()
            .execute()
        )

        if result.data and result.data.get("email_preferences"):
            prefs = result.data["email_preferences"]
            return EmailPreferences(
                marketing_emails=prefs.get("marketing_emails", True),
                usage_alerts=prefs.get("usage_alerts", True),
                weekly_digest=prefs.get("weekly_digest", True),
                feature_announcements=prefs.get("feature_announcements", True),
                invoice_receipts=prefs.get("invoice_receipts", True),
                digest_frequency=prefs.get("digest_frequency", "weekly"),
            )
    except Exception as e:
        logger.warning(f"Failed to fetch email preferences for user {user_id}: {e}")

    # Return defaults
    return EmailPreferences()


def update_email_status(
    email_id: str, status: str, error_message: Optional[str] = None
):
    """Update email status in tracking table."""
    try:
        supabase = get_supabase_admin_client()
        update_data = {
            "status": status,
            "sent_at": "now()" if status == "sent" else None,
        }
        if error_message:
            update_data["error_message"] = error_message

        supabase.table("email_tracking").update(update_data).eq(
            "id", email_id
        ).execute()
    except Exception as e:
        logger.error(f"Failed to update email status: {e}")


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(httpx.HTTPError, Exception),
    retry_backoff=True,
    retry_backoff_max=300,  # Max 5 minutes between retries
    retry_jitter=True,
)
def send_email_task(
    self,
    to_email: str,
    template_type: str,
    template_data: Dict,
    user_id: Optional[str] = None,
    track_id: Optional[str] = None,
):
    """
    Send a single email asynchronously with retry logic.

    Args:
        to_email: Recipient email
        template_type: Email template type
        template_data: Template variables
        user_id: Optional user ID for preference lookup
        track_id: Optional tracking ID
    """
    email_service = get_email_service()
    template_enum = EmailTemplateType(template_type)

    # Get user preferences if user_id provided
    preferences = None
    if user_id:
        preferences = get_user_email_preferences(user_id)

    try:
        # Send email
        result = email_service.send_email(
            to_email=to_email,
            template_type=template_enum,
            template_data=template_data,
            user_preferences=preferences,
        )

        if result:
            if track_id:
                update_email_status(track_id, "sent")
            logger.info(f"Email sent successfully to {to_email}: {result}")
            return {"status": "success", "email_id": result}
        else:
            # Email skipped (user preference)
            if track_id:
                update_email_status(track_id, "skipped")
            logger.info(f"Email skipped for {to_email} (user preferences)")
            return {"status": "skipped", "reason": "user_preferences"}

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        if track_id:
            update_email_status(track_id, "failed", str(e))

        # Retry with exponential backoff
        try:
            self.retry(countdown=60 * (2**self.request.retries))
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for email to {to_email}")
            raise EmailTaskError(
                f"Failed to send email after {self.max_retries} retries"
            )


@celery_app.task
def send_bulk_emails_task(
    recipients: List[Dict],
    template_type: str,
    template_data: Dict,
    rate_limit_per_minute: int = 60,
):
    """
    Send bulk emails with rate limiting.

    Args:
        recipients: List of dicts with 'email', 'user_id', 'custom_data'
        template_type: Email template type
        template_data: Common template data
        rate_limit_per_minute: Max emails per minute
    """
    import time

    email_service = get_email_service()
    template_enum = EmailTemplateType(template_type)
    results = []

    # Calculate delay between emails
    delay = 60.0 / rate_limit_per_minute

    for i, recipient in enumerate(recipients):
        try:
            to_email = recipient["email"]
            user_id = recipient.get("user_id")
            custom_data = recipient.get("custom_data", {})

            # Merge template data
            merged_data = {**template_data, **custom_data}

            # Get user preferences
            preferences = None
            if user_id:
                preferences = get_user_email_preferences(user_id)

            # Send email
            result = email_service.send_email(
                to_email=to_email,
                template_type=template_enum,
                template_data=merged_data,
                user_preferences=preferences,
            )

            results.append(
                {
                    "email": to_email,
                    "status": "sent" if result else "skipped",
                    "email_id": result,
                }
            )

            # Rate limiting delay
            if i < len(recipients) - 1:
                time.sleep(delay)

        except Exception as e:
            logger.error(f"Failed to send bulk email to {recipient.get('email')}: {e}")
            results.append(
                {
                    "email": recipient.get("email"),
                    "status": "failed",
                    "error": str(e),
                }
            )

    return {"status": "completed", "sent": len(results), "results": results}


@celery_app.task
def send_welcome_email_task(user_id: str, email: str, user_name: str):
    """Send welcome email to new user."""
    try:
        email_service = get_email_service()
        result = email_service.send_welcome_email(
            to_email=email,
            user_name=user_name,
        )

        # Update user profile to track welcome email sent
        try:
            supabase = get_supabase_admin_client()
            supabase.table("profiles").update(
                {
                    "welcome_email_sent": True,
                    "welcome_email_sent_at": "now()",
                }
            ).eq("id", user_id).execute()
        except Exception as e:
            logger.warning(f"Failed to update welcome email status: {e}")

        return {"status": "success", "email_id": result}
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        raise


@celery_app.task
def send_usage_alert_task(user_id: str, email: str, user_name: str):
    """Send usage alert when user hits 80% of their limit."""
    try:
        # Get current usage
        supabase = get_supabase_admin_client()
        result = (
            supabase.table("profiles")
            .select("monthly_usage_count, monthly_usage_limit, subscription_tier")
            .eq("id", user_id)
            .single()
            .execute()
        )

        if not result.data:
            raise EmailTaskError(f"User {user_id} not found")

        monthly_usage = result.data.get("monthly_usage_count", 0)
        monthly_limit = result.data.get("monthly_usage_limit", 10)
        plan_name = result.data.get("subscription_tier", "free")

        # Calculate percentage
        usage_percentage = (
            (monthly_usage / monthly_limit) * 100 if monthly_limit > 0 else 0
        )

        # Only send if between 80-100%
        if usage_percentage < 80:
            return {"status": "skipped", "reason": "usage_below_threshold"}

        # Check if alert was already sent recently
        alert_result = (
            supabase.table("email_tracking")
            .select("*")
            .eq("user_id", user_id)
            .eq("template_type", EmailTemplateType.USAGE_ALERT.value)
            .order("sent_at", desc=True)
            .limit(1)
            .execute()
        )

        if alert_result.data:
            last_sent = alert_result.data[0].get("sent_at")
            if last_sent:
                last_sent_date = datetime.fromisoformat(
                    last_sent.replace("Z", "+00:00")
                )
                if datetime.now(last_sent_date.tzinfo) - last_sent_date < timedelta(
                    days=7
                ):
                    return {"status": "skipped", "reason": "alert_sent_recently"}

        # Get user preferences
        preferences = get_user_email_preferences(user_id)

        email_service = get_email_service()
        result = email_service.send_usage_alert(
            to_email=email,
            user_name=user_name,
            monthly_usage=monthly_usage,
            monthly_limit=monthly_limit,
            plan_name=plan_name,
            user_preferences=preferences,
        )

        # Track email
        try:
            supabase.table("email_tracking").insert(
                {
                    "user_id": user_id,
                    "template_type": EmailTemplateType.USAGE_ALERT.value,
                    "status": "sent" if result else "skipped",
                    "email_id": result,
                }
            ).execute()
        except Exception as e:
            logger.warning(f"Failed to track usage alert: {e}")

        return {"status": "success", "email_id": result}

    except Exception as e:
        logger.error(f"Failed to send usage alert: {e}")
        raise


@celery_app.task
def send_weekly_digests():
    """Send weekly usage summary to all subscribed users."""
    try:
        supabase = get_supabase_admin_client()

        # Get users who want weekly digest
        result = (
            supabase.table("profiles")
            .select(
                "id, email, full_name, monthly_usage_count, monthly_usage_limit, subscription_tier"
            )
            .eq("email_preferences->weekly_digest", True)
            .execute()
        )

        if not result.data:
            return {"status": "completed", "sent": 0}

        # Calculate week range
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        week_range = f"{week_ago.strftime('%b %d')} - {today.strftime('%b %d')}"

        email_service = get_email_service()
        sent_count = 0

        for user in result.data:
            try:
                # Get user preferences
                preferences = get_user_email_preferences(user["id"])

                # Calculate stats
                monthly_usage = user.get("monthly_usage_count", 0)
                monthly_limit = user.get("monthly_usage_limit", 10)

                # For demo purposes, generate weekly stats
                # In production, query actual content creation stats
                content_created = min(monthly_usage, 20)  # Estimate
                word_count = content_created * 500  # Estimate

                result = email_service.send_weekly_summary(
                    to_email=user["email"],
                    user_name=user.get("full_name", "there"),
                    week_range=week_range,
                    content_created=content_created,
                    word_count=word_count,
                    monthly_usage=monthly_usage,
                    monthly_limit=monthly_limit,
                    user_preferences=preferences,
                )

                if result:
                    sent_count += 1

            except Exception as e:
                logger.error(
                    f"Failed to send weekly digest to {user.get('email')}: {e}"
                )
                continue

        return {"status": "completed", "sent": sent_count}

    except Exception as e:
        logger.error(f"Failed to send weekly digests: {e}")
        raise


@celery_app.task
def send_abandoned_cart_reminder(
    user_id: str,
    email: str,
    user_name: str,
    signup_step: str,
    hours_since_signup: int,
):
    """Send abandoned cart reminder for incomplete signups."""
    try:
        # Check if user has completed signup
        supabase = get_supabase_admin_client()
        result = (
            supabase.table("profiles")
            .select("email_verified")
            .eq("id", user_id)
            .single()
            .execute()
        )

        if result.data and result.data.get("email_verified"):
            return {"status": "skipped", "reason": "signup_completed"}

        # Determine which reminder to send
        if hours_since_signup < 24:
            return {"status": "skipped", "reason": "too_soon"}

        email_service = get_email_service()
        result = email_service.send_abandoned_cart(
            to_email=email,
            user_name=user_name,
            signup_url=f"{email_service.base_url}/signup?resume={user_id}",
        )

        return {"status": "success", "email_id": result}

    except Exception as e:
        logger.error(f"Failed to send abandoned cart reminder: {e}")
        raise


@celery_app.task
def send_invoice_receipt_task(
    user_id: str,
    email: str,
    user_name: str,
    invoice_number: str,
    amount: str,
    plan_name: str,
    billing_period: str,
    stripe_invoice_id: str,
):
    """Send invoice receipt after successful payment."""
    try:
        invoice_url = f"https://invoice.stripe.com/{stripe_invoice_id}"

        preferences = get_user_email_preferences(user_id)

        email_service = get_email_service()
        result = email_service.send_invoice_receipt(
            to_email=email,
            user_name=user_name,
            invoice_number=invoice_number,
            amount=amount,
            plan_name=plan_name,
            billing_period=billing_period,
            invoice_url=invoice_url,
            user_preferences=preferences,
        )

        return {"status": "success", "email_id": result}

    except Exception as e:
        logger.error(f"Failed to send invoice receipt: {e}")
        raise


# Retry failed emails task
@celery_app.task
def retry_failed_emails(limit: int = 100):
    """Retry failed emails from the tracking table."""
    try:
        supabase = get_supabase_admin_client()
        result = (
            supabase.table("email_tracking")
            .select("*")
            .eq("status", "failed")
            .lt("retry_count", 3)
            .limit(limit)
            .execute()
        )

        if not result.data:
            return {"status": "completed", "retried": 0}

        retried = 0
        for email_record in result.data:
            try:
                # Re-queue the email
                send_email_task.delay(
                    to_email=email_record["to_email"],
                    template_type=email_record["template_type"],
                    template_data=email_record["template_data"],
                    user_id=email_record.get("user_id"),
                    track_id=email_record["id"],
                )

                # Update retry count
                supabase.table("email_tracking").update(
                    {
                        "retry_count": email_record.get("retry_count", 0) + 1,
                        "status": "pending",
                    }
                ).eq("id", email_record["id"]).execute()

                retried += 1

            except Exception as e:
                logger.error(f"Failed to retry email {email_record['id']}: {e}")

        return {"status": "completed", "retried": retried}

    except Exception as e:
        logger.error(f"Failed to retry failed emails: {e}")
        raise

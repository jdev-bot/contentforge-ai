# Tasks module initialization
from app.tasks.email import (
    send_email_task,
    send_bulk_emails_task,
    send_welcome_email_task,
    send_usage_alert_task,
    send_weekly_digests,
    send_abandoned_cart_reminder,
    send_invoice_receipt_task,
    retry_failed_emails,
)
from app.tasks.rss import (
    fetch_rss_feeds_task,
    fetch_single_feed_task,
    process_rss_entry_task,
    cleanup_old_rss_entries_task,
    retry_failed_feeds_task,
)

__all__ = [
    # Email tasks
    "send_email_task",
    "send_bulk_emails_task",
    "send_welcome_email_task",
    "send_usage_alert_task",
    "send_weekly_digests",
    "send_abandoned_cart_reminder",
    "send_invoice_receipt_task",
    "retry_failed_emails",
    # RSS tasks
    "fetch_rss_feeds_task",
    "fetch_single_feed_task",
    "process_rss_entry_task",
    "cleanup_old_rss_entries_task",
    "retry_failed_feeds_task",
]

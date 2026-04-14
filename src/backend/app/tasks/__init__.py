# Tasks module initialization
from app.tasks.competitors import (
    analyze_content_gaps_task,
    cleanup_old_competitor_content_task,
    competitor_health_check_task,
    fetch_competitor_data_task,
    generate_competitor_insights_task,
    notify_high_opportunity_gaps_task,
)
from app.tasks.email import (
    retry_failed_emails,
    send_abandoned_cart_reminder,
    send_bulk_emails_task,
    send_email_task,
    send_invoice_receipt_task,
    send_usage_alert_task,
    send_weekly_digests,
    send_welcome_email_task,
)
from app.tasks.rss import (
    cleanup_old_rss_entries_task,
    fetch_rss_feeds_task,
    fetch_single_feed_task,
    process_rss_entry_task,
    retry_failed_feeds_task,
)
from app.tasks.trends import (
    cleanup_expired_trends_task,
    generate_trend_content_suggestions_task,
    get_trending_insights_task,
    notify_users_of_relevant_trends_task,
    update_trending_topics_task,
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
    # Trends tasks
    "update_trending_topics_task",
    "cleanup_expired_trends_task",
    "generate_trend_content_suggestions_task",
    "notify_users_of_relevant_trends_task",
    "get_trending_insights_task",
    # Competitor tasks
    "fetch_competitor_data_task",
    "analyze_content_gaps_task",
    "generate_competitor_insights_task",
    "notify_high_opportunity_gaps_task",
    "cleanup_old_competitor_content_task",
    "competitor_health_check_task",
]

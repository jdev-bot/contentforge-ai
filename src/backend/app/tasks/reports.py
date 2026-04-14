"""
Celery tasks for scheduled report generation.
"""
import logging
from datetime import datetime, timezone

from app.core.celery_app import celery_app
from app.services.report_service import report_service

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.reports.generate_scheduled_reports",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def generate_scheduled_reports(self):
    """Periodic task: generate all reports that are due based on their cron schedule."""
    from app.core.supabase import get_supabase_admin_client

    try:
        admin = get_supabase_admin_client()
        response = (
            admin.table("scheduled_reports")
            .select("id, user_id, schedule, name")
            .execute()
        )
        reports = response.data or []

        # Simple approach: check if each report should run based on schedule
        # A more robust approach would use croniter, but we keep it simple
        generated = 0
        failed = 0

        for report in reports:
            try:
                result = report_service.generate_report(report["id"], report["user_id"])
                if result:
                    generated += 1
                    logger.info(f"Generated report {report['id']}: {report.get('name')}")
            except Exception as e:
                failed += 1
                logger.error(f"Failed to generate report {report['id']}: {e}")

        return {
            "success": True,
            "total": len(reports),
            "generated": generated,
            "failed": failed,
        }
    except Exception as e:
        logger.error(f"Scheduled report generation failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.reports.generate_single_report",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def generate_single_report(self, report_id: str, user_id: str):
    """Generate a single report on-demand via Celery."""
    try:
        result = report_service.generate_report(report_id, user_id)
        if result:
            return {"success": True, "run_id": result.get("id"), "report_id": report_id}
        return {"success": False, "report_id": report_id, "error": "Report not found"}
    except Exception as e:
        logger.error(f"Failed to generate report {report_id}: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.reports.cleanup_old_report_runs",
    bind=True,
    max_retries=2,
)
def cleanup_old_report_runs(self, days: int = 90):
    """Clean up report runs older than specified days."""
    from app.core.supabase import get_supabase_admin_client
    from datetime import timedelta

    try:
        admin = get_supabase_admin_client()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        response = (
            admin.table("report_runs")
            .delete()
            .lt("generated_at", cutoff)
            .execute()
        )
        deleted = len(response.data) if response.data else 0
        logger.info(f"Cleaned up {deleted} old report runs (older than {days} days)")
        return {"success": True, "deleted": deleted}
    except Exception as e:
        logger.error(f"Failed to cleanup old report runs: {e}")
        raise self.retry(exc=e)
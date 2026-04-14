"""
Report Scheduling Service

Handles scheduled report generation, email delivery, and storage.
"""

import csv
import io
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from jinja2 import Template

from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.services.email_service import get_email_service

logger = logging.getLogger(__name__)

VALID_REPORT_TYPES = [
    "content_summary",
    "performance_overview",
    "quality_report",
    "sentiment_report",
    "team_activity",
]

VALID_FORMATS = ["pdf", "html", "csv"]

# Jinja2 report templates
REPORT_TEMPLATES = {
    "content_summary": Template("""
<!DOCTYPE html>
<html>
<head><style>
body { font-family: Arial, sans-serif; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
h1 { color: #1a1a2e; border-bottom: 2px solid #0f3460; padding-bottom: 10px; }
.metric { display: inline-block; background: #f0f0f0; border-radius: 8px; padding: 15px 20px; margin: 5px; min-width: 120px; }
.metric .value { font-size: 24px; font-weight: bold; color: #0f3460; }
.metric .label { font-size: 12px; color: #666; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }
th { background: #0f3460; color: white; }
.footer { margin-top: 30px; font-size: 12px; color: #999; }
</style></head>
<body>
<h1>Content Summary Report</h1>
<p>Generated: {{ generated_at }}</p>
<h2>Overview</h2>
<div class="metric"><div class="value">{{ data.total_content }}</div><div class="label">Total Content</div></div>
<div class="metric"><div class="value">{{ data.completed_count }}</div><div class="label">Completed</div></div>
<div class="metric"><div class="value">{{ data.pending_count }}</div><div class="label">Pending</div></div>
{% if data.by_status %}
<h2>Content by Status</h2>
<table><tr><th>Status</th><th>Count</th></tr>
{% for status, count in data.by_status.items() %}
<tr><td>{{ status }}</td><td>{{ count }}</td></tr>
{% endfor %}
</table>
{% endif %}
<div class="footer">ContentForge AI — Automated Report</div>
</body></html>
"""),
    "performance_overview": Template("""
<!DOCTYPE html>
<html>
<head><style>
body { font-family: Arial, sans-serif; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
h1 { color: #1a1a2e; border-bottom: 2px solid #0f3460; padding-bottom: 10px; }
.metric { display: inline-block; background: #f0f0f0; border-radius: 8px; padding: 15px 20px; margin: 5px; min-width: 120px; }
.metric .value { font-size: 24px; font-weight: bold; color: #0f3460; }
.metric .label { font-size: 12px; color: #666; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }
th { background: #0f3460; color: white; }
.footer { margin-top: 30px; font-size: 12px; color: #999; }
</style></head>
<body>
<h1>Performance Overview Report</h1>
<p>Generated: {{ generated_at }}</p>
<h2>Key Metrics</h2>
<div class="metric"><div class="value">{{ data.total_distributions }}</div><div class="label">Total Distributions</div></div>
<div class="metric"><div class="value">{{ data.success_rate }}%</div><div class="label">Success Rate</div></div>
<div class="metric"><div class="value">{{ data.total_assets }}</div><div class="label">Total Assets</div></div>
{% if data.by_platform %}
<h2>By Platform</h2>
<table><tr><th>Platform</th><th>Count</th><th>Success Rate</th></tr>
{% for platform, info in data.by_platform.items() %}
<tr><td>{{ platform }}</td><td>{{ info.count }}</td><td>{{ info.success_rate }}%</td></tr>
{% endfor %}
</table>
{% endif %}
<div class="footer">ContentForge AI — Automated Report</div>
</body></html>
"""),
    "quality_report": Template("""
<!DOCTYPE html>
<html>
<head><style>
body { font-family: Arial, sans-serif; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
h1 { color: #1a1a2e; border-bottom: 2px solid #0f3460; padding-bottom: 10px; }
.metric { display: inline-block; background: #f0f0f0; border-radius: 8px; padding: 15px 20px; margin: 5px; min-width: 120px; }
.metric .value { font-size: 24px; font-weight: bold; color: #0f3460; }
.metric .label { font-size: 12px; color: #666; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }
th { background: #0f3460; color: white; }
.footer { margin-top: 30px; font-size: 12px; color: #999; }
</style></head>
<body>
<h1>Quality Report</h1>
<p>Generated: {{ generated_at }}</p>
<h2>Scores</h2>
<div class="metric"><div class="value">{{ data.average_score }}</div><div class="label">Average Score</div></div>
<div class="metric"><div class="value">{{ data.total_scored }}</div><div class="label">Items Scored</div></div>
{% if data.by_category %}
<h2>By Category</h2>
<table><tr><th>Category</th><th>Average</th></tr>
{% for cat, info in data.by_category.items() %}
<tr><td>{{ cat }}</td><td>{{ info.average }}</td></tr>
{% endfor %}
</table>
{% endif %}
<div class="footer">ContentForge AI — Automated Report</div>
</body></html>
"""),
    "sentiment_report": Template("""
<!DOCTYPE html>
<html>
<head><style>
body { font-family: Arial, sans-serif; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
h1 { color: #1a1a2e; border-bottom: 2px solid #0f3460; padding-bottom: 10px; }
.metric { display: inline-block; background: #f0f0f0; border-radius: 8px; padding: 15px 20px; margin: 5px; min-width: 120px; }
.metric .value { font-size: 24px; font-weight: bold; color: #0f3460; }
.metric .label { font-size: 12px; color: #666; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }
th { background: #0f3460; color: white; }
.footer { margin-top: 30px; font-size: 12px; color: #999; }
</style></head>
<body>
<h1>Sentiment Report</h1>
<p>Generated: {{ generated_at }}</p>
<h2>Overview</h2>
<div class="metric"><div class="value">{{ data.total_analyzed }}</div><div class="label">Items Analyzed</div></div>
<div class="metric"><div class="value">{{ data.average_score }}</div><div class="label">Avg Score</div></div>
{% if data.by_sentiment %}
<h2>By Sentiment</h2>
<table><tr><th>Sentiment</th><th>Count</th></tr>
{% for sentiment, count in data.by_sentiment.items() %}
<tr><td>{{ sentiment }}</td><td>{{ count }}</td></tr>
{% endfor %}
</table>
{% endif %}
<div class="footer">ContentForge AI — Automated Report</div>
</body></html>
"""),
    "team_activity": Template("""
<!DOCTYPE html>
<html>
<head><style>
body { font-family: Arial, sans-serif; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
h1 { color: #1a1a2e; border-bottom: 2px solid #0f3460; padding-bottom: 10px; }
.metric { display: inline-block; background: #f0f0f0; border-radius: 8px; padding: 15px 20px; margin: 5px; min-width: 120px; }
.metric .value { font-size: 24px; font-weight: bold; color: #0f3460; }
.metric .label { font-size: 12px; color: #666; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }
th { background: #0f3460; color: white; }
.footer { margin-top: 30px; font-size: 12px; color: #999; }
</style></head>
<body>
<h1>Team Activity Report</h1>
<p>Generated: {{ generated_at }}</p>
<h2>Activity (Last 7 Days)</h2>
<div class="metric"><div class="value">{{ data.recent_items_count }}</div><div class="label">New Items</div></div>
{% if data.recent_items %}
<table><tr><th>Date</th><th>Items</th></tr>
{% for item in data.recent_items[:10] %}
<tr><td>{{ item.created_at }}</td><td>{{ item.id }}</td></tr>
{% endfor %}
</table>
{% endif %}
<div class="footer">ContentForge AI — Automated Report</div>
</body></html>
"""),
}


class ReportService:
    """Service for scheduled reports."""

    def __init__(self):
        self._supabase = None
        self._admin_supabase = None

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    @supabase.setter
    def supabase(self, value):
        self._supabase = value

    @property
    def admin_supabase(self):
        if self._admin_supabase is None:
            self._admin_supabase = get_supabase_admin_client()
        return self._admin_supabase

    # ── Report CRUD ────────────────────────────────────────────────

    def list_reports(self, user_id: str) -> List[Dict[str, Any]]:
        """List all scheduled reports for a user."""
        response = (
            self.supabase.table("scheduled_reports")
            .select(
                "id, user_id, name, description, report_type, schedule, format, recipients, filters, created_at, updated_at"
            )
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []

    def create_report(
        self,
        user_id: str,
        name: str,
        report_type: str,
        schedule: str,
        format: str = "html",
        description: Optional[str] = None,
        recipients: Optional[List[str]] = None,
        filters: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create a new scheduled report."""
        if report_type not in VALID_REPORT_TYPES:
            raise ValueError(f"Invalid report type: {report_type}")
        if format not in VALID_FORMATS:
            raise ValueError(f"Invalid format: {format}")

        payload = {
            "id": str(uuid4()),
            "user_id": user_id,
            "name": name,
            "description": description,
            "report_type": report_type,
            "schedule": schedule,
            "format": format,
            "recipients": recipients or [],
            "filters": filters or {},
        }
        response = self.supabase.table("scheduled_reports").insert(payload).execute()
        return response.data[0] if response.data else payload

    def get_report(self, report_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a scheduled report configuration."""
        response = (
            self.supabase.table("scheduled_reports")
            .select(
                "id, user_id, name, description, report_type, schedule, format, recipients, filters, created_at, updated_at"
            )
            .eq("id", report_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        return response.data

    def update_report(
        self,
        report_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        report_type: Optional[str] = None,
        schedule: Optional[str] = None,
        format: Optional[str] = None,
        recipients: Optional[List[str]] = None,
        filters: Optional[Dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a scheduled report."""
        existing = self.get_report(report_id, user_id)
        if not existing:
            return None

        updates: Dict[str, Any] = {}
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if report_type is not None:
            if report_type not in VALID_REPORT_TYPES:
                raise ValueError(f"Invalid report type: {report_type}")
            updates["report_type"] = report_type
        if schedule is not None:
            updates["schedule"] = schedule
        if format is not None:
            if format not in VALID_FORMATS:
                raise ValueError(f"Invalid format: {format}")
            updates["format"] = format
        if recipients is not None:
            updates["recipients"] = recipients
        if filters is not None:
            updates["filters"] = filters

        if not updates:
            return existing

        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        response = (
            self.supabase.table("scheduled_reports")
            .update(updates)
            .eq("id", report_id)
            .eq("user_id", user_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def delete_report(self, report_id: str, user_id: str) -> bool:
        """Delete a scheduled report."""
        existing = self.get_report(report_id, user_id)
        if not existing:
            return False

        # Delete report runs first
        self.supabase.table("report_runs").delete().eq("report_id", report_id).execute()
        self.supabase.table("scheduled_reports").delete().eq("id", report_id).eq(
            "user_id", user_id
        ).execute()
        return True

    # ── Report Generation ──────────────────────────────────────────

    def generate_report(self, report_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Generate a report now and return run info."""
        report = self.get_report(report_id, user_id)
        if not report:
            return None

        # Gather data
        data = self._gather_report_data(
            report["report_type"], user_id, report.get("filters", {})
        )

        # Render report
        generated_at = datetime.now(timezone.utc).isoformat()
        report_format = report.get("format", "html")
        content, content_type, storage_path = self._render_report(
            report["report_type"],
            data,
            report_format,
            generated_at,
        )

        # Store in Supabase storage
        file_name = f"{report['report_type']}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.{report_format}"
        storage_path = self._store_report(file_name, content, content_type)

        # Record run
        run_id = str(uuid4())
        run_payload = {
            "id": run_id,
            "report_id": report_id,
            "user_id": user_id,
            "status": "completed",
            "format": report_format,
            "storage_path": storage_path,
            "file_name": file_name,
            "generated_at": generated_at,
        }
        run_resp = self.supabase.table("report_runs").insert(run_payload).execute()
        run_data = run_resp.data[0] if run_resp.data else run_payload

        # Send via email if recipients
        recipients = report.get("recipients", [])
        if recipients:
            try:
                self._send_report_email(
                    report["name"],
                    recipients,
                    content,
                    content_type,
                    file_name,
                )
            except Exception as e:
                logger.error(f"Failed to send report email: {e}")
                # Update run status
                self.supabase.table("report_runs").update(
                    {
                        "status": "completed_delivery_failed",
                        "error_message": str(e),
                    }
                ).eq("id", run_id).execute()

        return run_data

    def get_report_history(self, report_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get generation history for a report."""
        # Verify ownership
        report = self.get_report(report_id, user_id)
        if not report:
            return []

        response = (
            self.supabase.table("report_runs")
            .select(
                "id, report_id, status, format, storage_path, file_name, generated_at, error_message"
            )
            .eq("report_id", report_id)
            .order("generated_at", desc=True)
            .limit(50)
            .execute()
        )
        return response.data or []

    def download_report(
        self, report_id: str, run_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get download info for a generated report."""
        # Verify ownership
        report = self.get_report(report_id, user_id)
        if not report:
            return None

        run_resp = (
            self.supabase.table("report_runs")
            .select(
                "id, report_id, status, format, storage_path, file_name, generated_at"
            )
            .eq("id", run_id)
            .eq("report_id", report_id)
            .maybe_single()
            .execute()
        )
        if not run_resp.data:
            return None

        run = run_resp.data
        # Generate a signed URL from Supabase storage
        if run.get("storage_path"):
            try:
                signed_url = self.admin_supabase.storage.from_(
                    "reports"
                ).create_signed_url(run["storage_path"], 3600)
                run["download_url"] = signed_url.get("signedURL", "")
            except Exception as e:
                logger.error(f"Failed to create signed URL: {e}")
                run["download_url"] = ""

        return run

    # ── Data Gathering ─────────────────────────────────────────────

    def _gather_report_data(
        self, report_type: str, user_id: str, filters: Dict
    ) -> Dict[str, Any]:
        """Gather data for a given report type."""
        gatherer = getattr(self, f"_gather_{report_type}", None)
        if gatherer:
            return gatherer(user_id, filters)
        return {}

    def _gather_content_summary(self, user_id: str, filters: Dict) -> Dict[str, Any]:
        """Gather content summary data."""
        resp = (
            self.supabase.table("content")
            .select("status, created_at")
            .eq("user_id", user_id)
            .execute()
        )
        items = resp.data or []
        by_status: Dict[str, int] = {}
        for item in items:
            s = item.get("status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1

        return {
            "total_content": len(items),
            "completed_count": by_status.get("completed", 0),
            "pending_count": by_status.get("pending", 0),
            "by_status": by_status,
        }

    def _gather_performance_overview(
        self, user_id: str, filters: Dict
    ) -> Dict[str, Any]:
        """Gather performance overview data."""
        dist_resp = (
            self.supabase.table("distributions")
            .select("platform, status")
            .eq("user_id", user_id)
            .execute()
        )
        dist_items = dist_resp.data or []

        asset_resp = (
            self.supabase.table("generated_assets")
            .select("type")
            .eq("user_id", user_id)
            .execute()
        )
        asset_items = asset_resp.data or []

        by_platform: Dict[str, Dict] = {}
        by_status: Dict[str, int] = {}
        for item in dist_items:
            p = item.get("platform", "unknown")
            s = item.get("status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1
            if p not in by_platform:
                by_platform[p] = {"count": 0, "published": 0}
            by_platform[p]["count"] += 1
            if s == "published":
                by_platform[p]["published"] += 1

        for p in by_platform:
            total = by_platform[p]["count"]
            published = by_platform[p]["published"]
            by_platform[p]["success_rate"] = (
                round(published / total * 100, 1) if total else 0
            )

        total = len(dist_items)
        published = by_status.get("published", 0)

        return {
            "total_distributions": total,
            "success_rate": round(published / total * 100, 1) if total else 0,
            "total_assets": len(asset_items),
            "by_platform": by_platform,
        }

    def _gather_quality_report(self, user_id: str, filters: Dict) -> Dict[str, Any]:
        """Gather quality report data."""
        try:
            resp = (
                self.supabase.table("quality_scores")
                .select("score, category")
                .eq("user_id", user_id)
                .limit(200)
                .execute()
            )
            items = resp.data or []
            by_category: Dict[str, Dict] = {}
            total = 0
            for i in items:
                s = i.get("score", 0)
                total += s
                cat = i.get("category", "uncategorized")
                if cat not in by_category:
                    by_category[cat] = {"scores": [], "average": 0}
                by_category[cat]["scores"].append(s)

            for cat_data in by_category.values():
                scores = cat_data["scores"]
                cat_data["average"] = (
                    round(sum(scores) / len(scores), 1) if scores else 0
                )
                del cat_data["scores"]

            return {
                "average_score": round(total / len(items), 1) if items else 0,
                "total_scored": len(items),
                "by_category": by_category,
            }
        except Exception:
            return {"average_score": 0, "total_scored": 0, "by_category": {}}

    def _gather_sentiment_report(self, user_id: str, filters: Dict) -> Dict[str, Any]:
        """Gather sentiment report data."""
        try:
            resp = (
                self.supabase.table("sentiment_results")
                .select("sentiment, score")
                .eq("user_id", user_id)
                .limit(200)
                .execute()
            )
            items = resp.data or []
            by_sentiment: Dict[str, int] = {}
            scores = []
            for i in items:
                s = i.get("sentiment", "neutral")
                by_sentiment[s] = by_sentiment.get(s, 0) + 1
                if i.get("score") is not None:
                    scores.append(i["score"])

            return {
                "total_analyzed": len(items),
                "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
                "by_sentiment": by_sentiment,
            }
        except Exception:
            return {"total_analyzed": 0, "average_score": 0, "by_sentiment": {}}

    def _gather_team_activity(self, user_id: str, filters: Dict) -> Dict[str, Any]:
        """Gather team activity data."""
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        try:
            resp = (
                self.supabase.table("content")
                .select("id, created_at")
                .eq("user_id", user_id)
                .gte("created_at", seven_days_ago)
                .order("created_at", desc=True)
                .limit(50)
                .execute()
            )
            items = resp.data or []
            return {
                "recent_items_count": len(items),
                "recent_items": items[:10],
            }
        except Exception:
            return {"recent_items_count": 0, "recent_items": []}

    # ── Rendering ───────────────────────────────────────────────────

    def _render_report(
        self, report_type: str, data: Dict, fmt: str, generated_at: str
    ) -> tuple:
        """Render a report to the specified format. Returns (content, content_type, storage_path)."""
        if fmt == "html":
            template = REPORT_TEMPLATES.get(report_type)
            if template:
                html = template.render(data=data, generated_at=generated_at)
                return html, "text/html", f"reports/{report_type}"
            return (
                "<html><body><p>Report template not found</p></body></html>",
                "text/html",
                f"reports/{report_type}",
            )

        elif fmt == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Metric", "Value"])
            for key, value in data.items():
                if not isinstance(value, (dict, list)):
                    writer.writerow([key, value])
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        writer.writerow([f"{key}.{sub_key}", sub_value])
            return output.getvalue(), "text/csv", f"reports/{report_type}"

        elif fmt == "pdf":
            # PDF generation would require weasyprint or similar
            # Fall back to HTML for now with a note
            template = REPORT_TEMPLATES.get(report_type)
            if template:
                html = template.render(data=data, generated_at=generated_at)
            else:
                html = "<html><body><p>Report data not available</p></body></html>"
            return html, "text/html", f"reports/{report_type}"

        return json.dumps(data, indent=2), "application/json", f"reports/{report_type}"

    # ── Storage ────────────────────────────────────────────────────

    def _store_report(self, file_name: str, content: str, content_type: str) -> str:
        """Store a generated report in Supabase storage."""
        try:
            storage_path = f"reports/{file_name}"
            self.admin_supabase.storage.from_("reports").upload(
                storage_path,
                content.encode("utf-8"),
                {"content-type": content_type, "upsert": "true"},
            )
            return storage_path
        except Exception as e:
            logger.error(f"Failed to store report: {e}")
            return f"reports/{file_name}"

    # ── Email Delivery ─────────────────────────────────────────────

    def _send_report_email(
        self,
        report_name: str,
        recipients: List[str],
        content: str,
        content_type: str,
        file_name: str,
    ):
        """Send a report via email using the existing email service."""
        for recipient in recipients:
            try:
                get_email_service().send_email(
                    to_email=recipient,
                    subject=f"ContentForge Report: {report_name}",
                    html_content=content if content_type == "text/html" else None,
                    text_content=(
                        content
                        if content_type != "text/html"
                        else "Please view in HTML-compatible email client."
                    ),
                )
            except Exception as e:
                logger.error(f"Failed to send report email to {recipient}: {e}")
                raise


# Singleton instance
report_service = ReportService()

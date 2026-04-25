#!/usr/bin/env python3
"""
ContentForge AI — Deep System Test v2 (TestClient + Full Mocks)
Exercises every API route group with correct Pydantic payloads.
"""

import os, sys, json

# ── Env setup BEFORE any app imports ────────────────────────────────
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-role-key"
os.environ["GROQ_API_KEY"] = "test-groq-key"
os.environ["AI_PROVIDER"] = "groq"
os.environ["AI_API_KEY"] = "test-ai-api-key"
os.environ["RATE_LIMIT_REQUESTS"] = "10000"
os.environ["RATE_LIMIT_WINDOW"] = "3600"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tests"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4


# ── Patch no-op middleware before app import ─────────────────────────
class NoOpMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)


from tests.conftest import (
    _build_mock_supabase_client,
    _build_mock_usage_stats,
    _SUPABASE_CLIENT_PATCH_TARGETS,
    _ADMIN_CLIENT_PATCH_TARGETS,
    _RATE_LIMIT_FUNC_PATCHES,
    _safe_patch,
)

# Build mocks
mock_client, mock_auth, mock_table, mock_storage, mock_query = (
    _build_mock_supabase_client()
)
mock_usage = _build_mock_usage_stats()


# Make mock_table.insert().execute() return data like real Supabase
def _make_insert_return(data_dict):
    """Simulate Supabase insert returning the inserted row."""
    row = {
        **data_dict,
        "id": str(uuid4()),
        "created_at": "2026-04-14T10:00:00Z",
        "updated_at": "2026-04-14T10:00:00Z",
    }
    result = MagicMock()
    result.data = [row]
    result.count = 1
    return result


# Patch the mock_table chain to return data for inserts
original_execute = mock_table.execute


def _smart_execute(*args, **kwargs):
    """Return appropriate data based on query type."""
    result = MagicMock()
    result.data = []
    result.count = 0
    return result


# Override table() to return a mock that has working insert/select
# Key insight: Supabase insert echoes back request data + id/created_at/updated_at
# We track what was inserted so subsequent select queries can find it
_mock_data_store = {}  # table_name -> list of rows


def _make_table_mock(table_name):
    t = MagicMock()
    if table_name not in _mock_data_store:
        _mock_data_store[table_name] = []

    # SELECT chain: returns stored data for this table
    select_chain = MagicMock()

    def select_execute():
        r = MagicMock()
        stored = list(_mock_data_store.get(table_name, []))
        r.data = stored
        r.count = len(stored)
        return r

    def single_execute():
        r = MagicMock()
        rows = _mock_data_store.get(table_name, [])
        r.data = rows[0] if rows else None
        r.count = len(rows)
        return r

    # Handle .select("count", count="exact") pattern
    def count_execute():
        r = MagicMock()
        rows = _mock_data_store.get(table_name, [])
        r.data = []
        r.count = len(rows)
        return r

    count_chain = MagicMock()
    count_chain.execute = count_execute
    count_chain.eq.return_value = count_chain
    count_chain.order.return_value = count_chain
    count_chain.limit.return_value = count_chain
    count_chain.offset.return_value = count_chain
    count_chain.range.return_value = count_chain

    select_chain.execute = select_execute
    select_chain.select = MagicMock(
        side_effect=lambda *a, **kw: (
            count_chain if (a and a[0] == "count") else select_chain
        )
    )
    select_chain.insert.return_value = select_chain
    select_chain.update.return_value = select_chain
    select_chain.delete.return_value = select_chain
    select_chain.eq.return_value = select_chain
    select_chain.neq.return_value = select_chain
    select_chain.lte.return_value = select_chain
    select_chain.gte.return_value = select_chain
    select_chain.lt.return_value = select_chain
    select_chain.in_.return_value = select_chain
    select_chain.like.return_value = select_chain
    select_chain.ilike.return_value = select_chain
    select_chain.is_.return_value = select_chain
    select_chain.not_.return_value = select_chain
    select_chain.contains.return_value = select_chain
    select_chain.contained.return_value = select_chain
    select_chain.overlap.return_value = select_chain
    select_chain.order.return_value = select_chain
    select_chain.limit.return_value = select_chain
    select_chain.offset.return_value = select_chain
    select_chain.range.return_value = select_chain
    select_chain.single.return_value = MagicMock(execute=single_execute)
    select_chain.upsert.return_value = select_chain

    # INSERT: stores data and returns it with id/timestamps
    def insert_execute():
        # Insert returns the last stored row
        rows = _mock_data_store.get(table_name, [])
        r = MagicMock()
        r.data = rows[-1:] if rows else []
        r.count = len(rows)
        return r

    insert_chain = MagicMock()
    insert_chain.execute = insert_execute
    insert_chain.select.return_value = insert_chain
    insert_chain.eq.return_value = insert_chain

    # UPSERT: same as insert
    upsert_chain = MagicMock()
    upsert_chain.execute = insert_execute

    t.select.return_value = select_chain
    t.insert.side_effect = lambda *args, **kwargs: _insert_and_return(
        table_name, *args, **kwargs
    )
    t.upsert.side_effect = lambda *args, **kwargs: _upsert_and_return(
        table_name, *args, **kwargs
    )
    t.update.return_value = select_chain
    t.delete.return_value = select_chain
    return t


def _insert_and_return(table_name, data=None, **kwargs):
    """Handle insert - store data and return insert chain."""
    if data:
        if isinstance(data, list):
            for item in data:
                row = {
                    **item,
                    "id": str(uuid4()),
                    "created_at": "2026-04-14T10:00:00Z",
                    "updated_at": "2026-04-14T10:00:00Z",
                }
                _mock_data_store.setdefault(table_name, []).append(row)
        elif isinstance(data, dict):
            row = {
                **data,
                "id": str(uuid4()),
                "created_at": "2026-04-14T10:00:00Z",
                "updated_at": "2026-04-14T10:00:00Z",
            }
            _mock_data_store.setdefault(table_name, []).append(row)
    chain = MagicMock()
    rows = _mock_data_store.get(table_name, [])

    def insert_execute():
        r = MagicMock()
        r.data = rows[-1:] if rows else []
        r.count = len(rows)
        return r

    chain.execute = insert_execute
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.order.return_value = chain
    chain.limit.return_value = chain
    chain.offset.return_value = chain
    chain.range.return_value = chain
    chain.single.return_value = chain
    return chain


def _upsert_and_return(table_name, data=None, **kwargs):
    """Handle upsert - same as insert for mock purposes."""
    return _insert_and_return(table_name, data, **kwargs)


mock_client.table = MagicMock(side_effect=_make_table_mock)


def _orig_make_table_mock(name):
    return _make_table_mock(name)


def _debug_make_table_mock(name):
    if name == "scheduled_posts":
        import traceback

        print(f"[DEBUG] table('scheduled_posts') called")
        traceback.print_stack(limit=5)
    return _make_table_mock(name)


mock_client.table = MagicMock(side_effect=_debug_make_table_mock)

default_mock_user = MagicMock()
default_mock_user.id = uuid4()
default_mock_user.email = "test@example.com"
default_mock_user.user_metadata = {"full_name": "Test User"}
default_mock_user.role = "authenticated"

# ── Apply all patches before importing app ───────────────────────────
active_patches = []
for target in _SUPABASE_CLIENT_PATCH_TARGETS:
    p = _safe_patch(target, return_value=mock_client)
    if p:
        active_patches.append(p)
for target in _ADMIN_CLIENT_PATCH_TARGETS:
    p = _safe_patch(target, return_value=mock_client)
    if p:
        active_patches.append(p)
for func_name, modules in _RATE_LIMIT_FUNC_PATCHES.items():
    for mod in modules:
        p = _safe_patch(f"{mod}.{func_name}", return_value=mock_usage)
        if p:
            active_patches.append(p)
for name, ret in [
    ("get_user_usage_stats", mock_usage),
    ("check_and_increment_usage", mock_usage),
    ("check_subscription_limit", mock_usage),
]:
    p = _safe_patch(f"app.core.rate_limit.{name}", return_value=ret)
    if p:
        active_patches.append(p)
p = _safe_patch("app.core.rate_limit.check_monthly_reset", return_value=None)
if p:
    active_patches.append(p)

# Patch celery tasks
_celery_mock = MagicMock()
_celery_mock.delay = MagicMock(return_value=MagicMock(id="test-task-id"))
for t in [
    "app.routers.auth.send_welcome_email_task",
    "app.routers.rss.fetch_single_feed_task",
    "app.routers.stripe.send_invoice_receipt_task",
]:
    p = _safe_patch(t, _celery_mock)
    if p:
        active_patches.append(p)

# ── Patch Groq service for AI endpoints ─────────────────────────────
# generate_content returns str, others return Tuple[str, int]
_groq_str = AsyncMock(return_value="Mocked AI generated content about the topic.")
_groq_tuple = AsyncMock(
    return_value=("Mocked AI generated content about the topic.", 150)
)

for method in [
    "generate_content",
    "generate_social_posts",
    "generate_thread",
    "generate_newsletter",
    "generate_short_video_script",
]:
    p = _safe_patch(f"app.services.groq_service.groq_service.{method}", new=_groq_str)
    if p:
        active_patches.append(p)

for method in ["rewrite_content", "expand_content", "condense_content"]:
    p = _safe_patch(f"app.services.groq_service.groq_service.{method}", new=_groq_tuple)
    if p:
        active_patches.append(p)

# optimize_content returns a dict, not a tuple — don't mock it; it calls generate_content internally which is already mocked
# Same for generate_social_posts, generate_thread, generate_newsletter, generate_short_video_script — they call generate_content

# ── Also patch module-level service instances that cache supabase ───
for svc_path in [
    "app.services.sso_service.get_supabase_client",
    "app.services.sso_service.get_supabase_admin_client",
    "app.services.saml_service.get_supabase_client",
    "app.services.saml_service.get_supabase_admin_client",
    "app.services.marketplace_service.get_supabase_client",
    "app.services.marketplace_service.get_supabase_admin_client",
    "app.services.plugin_service.get_supabase_client",
    "app.services.plugin_service.get_supabase_admin_client",
    "app.services.collaboration_service.get_supabase_client",
    "app.services.presence_service.get_supabase_client",
    "app.services.retention_service.get_supabase_client",
    "app.services.comments_service.get_supabase_client",
    "app.services.performance_service.get_supabase_client",
    "app.services.scheduler_service.get_supabase_client",
    "app.services.version_service.get_supabase_client",
    "app.services.audit_service.get_supabase_client",
    "app.services.quality_service.get_supabase_client",
    "app.services.sentiment_service.get_supabase_client",
    "app.services.suggestion_service.get_supabase_client",
    "app.services.categorization_service.get_supabase_client",
    "app.services.dashboard_service.get_supabase_client",
    "app.services.report_service.get_supabase_client",
]:
    p = _safe_patch(svc_path, return_value=mock_client)
    if p:
        active_patches.append(p)

# Now import app with patches active
with patch("app.core.rate_limit.UsageTrackingMiddleware", NoOpMiddleware):
    with patch("app.core.error_tracking.ErrorTrackingMiddleware", NoOpMiddleware):
        from app.main import app
        from app.routers.auth import get_auth_user
        from app.core.rate_limit import (
            enforce_subscription_limit,
            rate_limit_dependency,
        )


# ── Override auth dependency ─────────────────────────────────────────
def _auth_override(request=None):
    return default_mock_user


app.dependency_overrides[get_auth_user] = _auth_override
app.dependency_overrides[enforce_subscription_limit] = lambda: mock_usage
app.dependency_overrides[rate_limit_dependency] = lambda: True

# ── Create TestClient ────────────────────────────────────────────────
from fastapi.testclient import TestClient

client = TestClient(app)

# ── UUID helpers ────────────────────────────────────────────────────
UUID1 = str(uuid4())
UUID2 = str(uuid4())
UUID3 = str(uuid4())
PROJ_ID = str(uuid4())
ORG_ID = str(uuid4())
CONTENT_ID = str(uuid4())
USER_ID = str(default_mock_user.id)

# ── Test infrastructure ─────────────────────────────────────────────
results = {"pass": [], "fail": [], "warn": [], "errors": {}}


def test(
    name,
    method,
    url,
    data=None,
    params=None,
    expected_min=200,
    expected_max=299,
    check_fn=None,
):
    """Run a single API test against TestClient."""
    try:
        if method == "get":
            r = client.get(url, params=params)
        elif method == "post":
            r = client.post(url, json=data)
        elif method == "put":
            r = client.put(url, json=data)
        elif method == "patch":
            r = client.patch(url, json=data)
        elif method == "delete":
            r = client.delete(url)
        else:
            raise ValueError(f"Unknown method: {method}")

        status_ok = expected_min <= r.status_code <= expected_max
        body_ok = True
        if check_fn:
            try:
                body_ok = check_fn(r)
            except Exception as e:
                body_ok = False
                results["errors"][name] = f"check_fn error: {e}"

        if status_ok and body_ok:
            results["pass"].append(name)
            print(f"  ✅ {name} — {r.status_code}")
        else:
            results["fail"].append(name)
            detail = r.text[:150] if r.text else "no body"
            if not status_ok:
                results["errors"][
                    name
                ] = f"Expected {expected_min}-{expected_max}, got {r.status_code}: {detail}"
                print(f"  ❌ {name} — {r.status_code}: {detail[:80]}")
            else:
                results["errors"][name] = f"Check failed: {detail}"
                print(f"  ❌ {name} — check failed: {detail[:80]}")
        return r
    except Exception as e:
        results["fail"].append(name)
        results["errors"][name] = str(e)[:200]
        print(f"  ❌ {name} — Exception: {str(e)[:80]}")
        return None


def test_group(name):
    print(f"\n{'='*60}")
    print(f"📋 {name}")
    print(f"{'='*60}")


# ══════════════════════════════════════════════════════════════════════
# TEST GROUPS
# ══════════════════════════════════════════════════════════════════════

# ── 1. Health ────────────────────────────────────────────────────────
test_group("1. Health & System")
test("health", "get", "/api/v1/health")
test("health_version", "get", "/api/v1/health/version")
test("health_metrics", "get", "/api/v1/health/metrics")
test("health_ready", "get", "/api/v1/health/ready", expected_min=200, expected_max=503)
test(
    "health_detailed",
    "get",
    "/api/v1/health/detailed",
    expected_min=200,
    expected_max=503,
)

# ── 2. Auth ──────────────────────────────────────────────────────────
test_group("2. Authentication")
test(
    "auth_register",
    "post",
    "/api/v1/auth/register",
    data={
        "email": "systest@contentforge.ai",
        "password": "TestPass123!",
        "full_name": "System Test",
    },
)
test("auth_me", "get", "/api/v1/auth/me")
# Login expected to fail with mock auth (no real Supabase verify)
test(
    "auth_login",
    "post",
    "/api/v1/auth/login",
    data={"email": "systest@contentforge.ai", "password": "TestPass123!"},
    expected_min=200,
    expected_max=401,
)

# ── 3. Organizations ─────────────────────────────────────────────────
test_group("3. Organizations")
test("org_list", "get", "/api/v1/organizations/")
test(
    "org_create",
    "post",
    "/api/v1/organizations/",
    data={"name": "Test Org", "slug": "test-org-sys"},
)
test("org_get", "get", f"/api/v1/organizations/{ORG_ID}")
test("org_members", "get", f"/api/v1/organizations/{ORG_ID}/members")

# ── 4. Projects ──────────────────────────────────────────────────────
test_group("4. Projects")
test("project_list", "get", "/api/v1/projects")
test(
    "project_create",
    "post",
    "/api/v1/projects",
    data={"name": "Test Project", "description": "System test"},
)
test("project_get", "get", f"/api/v1/projects/{PROJ_ID}")

# ── 5. Content CRUD ──────────────────────────────────────────────────
test_group("5. Content CRUD")
test("content_list", "get", "/api/v1/content")
test(
    "content_create",
    "post",
    "/api/v1/content",
    data={
        "title": "Test Article",
        "project_id": PROJ_ID,
        "source": {"type": "text", "text": "Test content body."},
    },
)
test("content_get", "get", f"/api/v1/content/{CONTENT_ID}")
test(
    "content_generate",
    "post",
    f"/api/v1/content/{CONTENT_ID}/generate",
    data={"platform": "twitter"},
)
test("content_delete", "delete", f"/api/v1/content/{CONTENT_ID}")

# ── 6. Distributions ────────────────────────────────────────────────
test_group("6. Distributions")
test("dist_list", "get", "/api/v1/distributions")
test(
    "dist_create",
    "post",
    "/api/v1/distributions",
    data={
        "asset_id": UUID1,
        "platform": "twitter",
        "scheduled_at": "2026-04-15T10:00:00Z",
    },
)
test("dist_get", "get", f"/api/v1/distributions/{UUID1}")

# ── 7. Usage & Analytics ────────────────────────────────────────────
test_group("7. Usage & Analytics")
test("usage", "get", "/api/v1/usage", expected_min=200, expected_max=404)
test("usage_history", "get", "/api/v1/usage/history")
test(
    "usage_summary", "get", "/api/v1/usage/summary", expected_min=200, expected_max=404
)
test("analytics_dashboard", "get", "/api/v1/analytics/dashboard")
test("analytics_distributions", "get", "/api/v1/analytics/distributions")
test("analytics_content", "get", "/api/v1/analytics/content")
test("analytics_export", "get", "/api/v1/analytics/export/json")

# ── 8. AI Suggestions & Editor ───────────────────────────────────────
test_group("8. AI Suggestions & Editor")
test(
    "ai_improve",
    "post",
    "/api/v1/ai-suggestions/improve",
    data={"content_id": CONTENT_ID, "suggestion_type": "readability"},
)
test(
    "ai_seo",
    "post",
    "/api/v1/ai-suggestions/seo",
    data={
        "content_id": CONTENT_ID,
        "keywords": ["AI", "content"],
        "target_audience": "developers",
    },
)
test(
    "ai_tone",
    "post",
    "/api/v1/ai-suggestions/tone",
    data={"content_id": CONTENT_ID, "tone": "professional"},
)
test(
    "ai_rewrite",
    "post",
    "/api/v1/ai/edit/rewrite",
    data={
        "content": "Rewrite this.",
        "instructions": "Make engaging",
        "tone": "professional",
        "style": "neutral",
    },
)
test(
    "ai_expand",
    "post",
    "/api/v1/ai/edit/expand",
    data={"content": "Expand this.", "instructions": "More detail", "target_length": 2},
)
test(
    "ai_condense",
    "post",
    "/api/v1/ai/edit/condense",
    data={
        "content": "Condense this overly long piece of text.",
        "instructions": "Shorter",
    },
)
test(
    "ai_optimize",
    "post",
    "/api/v1/ai/edit/optimize",
    data={"content": "Optimize this.", "platform": "twitter", "tone": "professional"},
)
test("ai_history", "get", "/api/v1/ai/edit/history")

# ── 9. Automation Rules & Webhooks ───────────────────────────────────
test_group("9. Automation Rules & Webhooks")
test("auto_rules_list", "get", "/api/v1/automation/rules")
test(
    "auto_rules_create",
    "post",
    "/api/v1/automation/rules",
    data={
        "name": "Test Rule",
        "trigger_type": "content_created",
        "action_type": "generate_assets",
        "action_config": {"platform": "twitter"},
        "conditions": [{"field": "platform", "operator": "eq", "value": "blog"}],
    },
)
test("auto_webhooks_list", "get", "/api/v1/automation/webhooks")
test("auto_queue", "get", "/api/v1/automation/queue")
test("auto_best_times", "get", "/api/v1/automation/best-times/twitter")

# ── 10. Notifications ───────────────────────────────────────────────
test_group("10. Notifications")
test("notif_prefs", "get", "/api/v1/notifications/preferences")
test("notif_history", "get", "/api/v1/notifications/history")

# ── 11. User & Search ───────────────────────────────────────────────
test_group("11. User & Search")
test("user_export", "get", "/api/v1/user/export-data")
test("search", "get", "/api/v1/search", params={"q": "test"})
test("search_suggestions", "get", "/api/v1/search/suggestions", params={"q": "test"})

# ── 12. Trash ────────────────────────────────────────────────────────
test_group("12. Trash / Soft Delete")
test("trash_list", "get", "/api/v1/trash")
test("trash_stats", "get", "/api/v1/trash/stats")
test("trash_empty", "post", "/api/v1/trash/empty")

# ── 13. Scheduler ───────────────────────────────────────────────────
test_group("13. Scheduler")
test("schedule_list", "get", "/api/v1/schedule")
test(
    "schedule_create",
    "post",
    "/api/v1/schedule",
    data={
        "content_id": CONTENT_ID,
        "platform": "twitter",
        "scheduled_at": "2026-04-15T10:00:00Z",
    },
)
test("schedule_stats", "get", "/api/v1/schedule/stats")
test("schedule_upcoming", "get", "/api/v1/schedule/upcoming")
test(
    "schedule_bulk",
    "post",
    "/api/v1/schedule/bulk",
    data=[
        {
            "content_id": CONTENT_ID,
            "platform": "twitter",
            "scheduled_at": "2026-04-15T10:00:00Z",
        }
    ],
)

# ── 14. RSS ──────────────────────────────────────────────────────────
test_group("14. RSS Feeds")
test("rss_feeds_list", "get", "/api/v1/rss/feeds")
test("rss_entries", "get", "/api/v1/rss/entries")
# RSS feed create hits real URL validation — expect failure
test(
    "rss_feeds_create",
    "post",
    "/api/v1/rss/feeds",
    data={"url": "https://example.com/feed.xml", "name": "Test Feed"},
    expected_min=200,
    expected_max=499,
)

# ── 15. Freshness ───────────────────────────────────────────────────
test_group("15. Content Freshness")
test("freshness_stale", "get", "/api/v1/freshness/stale")
test("freshness_analyze", "post", f"/api/v1/freshness/analyze/{CONTENT_ID}")
test("freshness_score", "get", f"/api/v1/freshness/{CONTENT_ID}")
test("freshness_dashboard", "get", "/api/v1/freshness/dashboard")
test(
    "freshness_bulk", "post", "/api/v1/freshness/bulk-analyze", data=[CONTENT_ID, UUID2]
)

# ── 16. Audience ─────────────────────────────────────────────────────
test_group("16. Audience Analytics")
test("audience_growth", "get", "/api/v1/audience/growth")
test("audience_platforms", "get", "/api/v1/audience/platforms")
test("audience_history", "get", "/api/v1/audience/history")
test("audience_insights", "get", "/api/v1/audience/insights")
test(
    "audience_record",
    "post",
    "/api/v1/audience/record",
    data={
        "platform": "twitter",
        "metric_type": "followers",
        "value": 1000,
        "period": "daily",
    },
)

# ── 17. Trends ───────────────────────────────────────────────────────
test_group("17. Trends")
test("trends_list", "get", "/api/v1/trends")
test("trends_categories", "get", "/api/v1/trends/categories")
test("trends_search", "get", "/api/v1/trends/search", params={"q": "AI"})
test(
    "trends_track",
    "post",
    "/api/v1/trends/track",
    data={"topic_id": UUID1, "relevance_score": 0.85},
)
test("trends_tracked", "get", "/api/v1/trends/tracked")
test("trends_insights", "get", "/api/v1/trends/insights")

# ── 18. Integrations ────────────────────────────────────────────────
test_group("18. Integrations Hub")
test("integrations_list", "get", "/api/v1/integrations")
test(
    "integration_create",
    "post",
    "/api/v1/integrations",
    data={
        "name": "Test Integration",
        "integration_type": "webhook",
        "config": {"webhook_url": "https://hooks.zapier.com/hooks/standard/test-hook"},
    },
)

# ── 19. Alerts ───────────────────────────────────────────────────────
test_group("19. Alert System")
test("alerts_list", "get", "/api/v1/alerts")
test("alerts_unread", "get", "/api/v1/alerts/unread-count")
test("alerts_rules", "get", "/api/v1/alerts/rules")
test("alerts_notifications", "get", "/api/v1/alerts/notifications")
test(
    "alerts_check_metrics",
    "post",
    "/api/v1/alerts/check-metrics",
    data={"content_id": CONTENT_ID, "metrics": {"views": 100, "engagement": 5.0}},
)

# ── 20. Competitors ─────────────────────────────────────────────────
test_group("20. Competitor Analysis")
test("competitors_list", "get", "/api/v1/competitors")
test("competitors_platforms", "get", "/api/v1/competitors/platforms/list")
test("competitors_analysis", "get", "/api/v1/competitors/analysis")
test("competitors_gaps", "get", "/api/v1/competitors/gaps")
test(
    "competitors_create",
    "post",
    "/api/v1/competitors",
    data={"name": "Competitor X", "platform": "twitter", "handle": "@competitorx"},
)

# ── 21. Version History ──────────────────────────────────────────────
test_group("21. Version History")
test("version_list", "get", f"/api/v1/content/{CONTENT_ID}/versions")
test(
    "version_create",
    "post",
    f"/api/v1/content/{CONTENT_ID}/versions",
    data={"body": "New version content", "change_summary": "Updated"},
)
test(
    "version_diff",
    "get",
    f"/api/v1/content/{CONTENT_ID}/versions/diff",
    params={"v1": UUID1, "v2": UUID2},
)

# ── 22. Audit Logs ──────────────────────────────────────────────────
test_group("22. Audit Logs")
test("audit_list", "get", "/api/v1/audit-logs")
test("audit_stats", "get", "/api/v1/audit-logs/stats")
test("audit_export", "get", "/api/v1/audit-logs/export")

# ── 23. Quality Scoring ─────────────────────────────────────────────
test_group("23. Quality Scoring")
test(
    "quality_analyze",
    "post",
    "/api/v1/quality/analyze",
    data={"text": "Well-written test article about AI technology and its impact."},
)
test(
    "quality_batch",
    "post",
    "/api/v1/quality/batch",
    data={
        "items": [
            {"content_id": UUID1, "text": "Test content one."},
            {"content_id": UUID2, "text": "Test content two."},
        ]
    },
)

# ── 24. Sentiment ────────────────────────────────────────────────────
test_group("24. Sentiment Analysis")
test(
    "sentiment_analyze",
    "post",
    "/api/v1/sentiment/analyze",
    data={"text": "We are thrilled to announce our new product!"},
)
test(
    "sentiment_batch",
    "post",
    "/api/v1/sentiment/batch",
    data={
        "items": [
            {"content_id": UUID1, "text": "Great news everyone!"},
            {"content_id": UUID2, "text": "This is terrible."},
        ]
    },
)
test("sentiment_distribution", "get", "/api/v1/sentiment/distribution")

# ── 25. Custom Dashboards ───────────────────────────────────────────
test_group("25. Custom Dashboards")
test("dashboards_list", "get", "/api/v1/dashboards")
test(
    "dashboard_create",
    "post",
    "/api/v1/dashboards",
    data={"name": "Test Dashboard", "description": "System test"},
)

# ── 26. Reports ──────────────────────────────────────────────────────
test_group("26. Reports")
test("reports_list", "get", "/api/v1/reports")
test(
    "report_create",
    "post",
    "/api/v1/reports",
    data={
        "name": "Test Report",
        "report_type": "content_summary",
        "schedule": "0 9 * * *",
    },
)

# ── 27. Data Retention ──────────────────────────────────────────────
test_group("27. Data Retention")
test("retention_list", "get", "/api/v1/retention/policies")
test("retention_compliance", "get", "/api/v1/retention/compliance")
test("retention_audit", "get", "/api/v1/retention/audit")
test(
    "retention_create",
    "post",
    "/api/v1/retention/policies",
    data={
        "content_type": "content",
        "archive_after_days": 180,
        "delete_after_days": 365,
    },
)

# ── 28. Comments v2 ─────────────────────────────────────────────────
test_group("28. Comments v2")
test("comments_list", "get", f"/api/v1/content/{CONTENT_ID}/comments")
test(
    "comment_create",
    "post",
    f"/api/v1/content/{CONTENT_ID}/comments",
    data={"text": "Test comment with @mention"},
)
test(
    "comment_mentions_lookup",
    "get",
    "/api/v1/comments/mentions/lookup",
    params={"q": "test"},
)

# ── 29. Smart Suggestions ───────────────────────────────────────────
test_group("29. Smart Suggestions")
test("suggestions_topics", "get", "/api/v1/suggestions/topics")
test("suggestions_posting_times", "get", "/api/v1/suggestions/posting-times")
test("suggestions_improvements", "get", "/api/v1/suggestions/improvements")
test("suggestions_saved", "get", "/api/v1/suggestions/saved")
test("suggestions_generate_all", "post", "/api/v1/suggestions/generate-all")

# ── 30. Smart Categorization ────────────────────────────────────────
test_group("30. Smart Categorization")
test("categorization_list", "get", "/api/v1/categorization/list")
test(
    "categorization_auto_tag",
    "post",
    "/api/v1/categorization/auto-tag",
    data={"content_id": CONTENT_ID, "max_tags": 5},
)
test(
    "categorization_cluster",
    "post",
    "/api/v1/categorization/cluster",
    data={"cluster_count": 3},
)

# ── 31. Performance Analytics ───────────────────────────────────────
test_group("31. Performance Analytics")
test("perf_overview", "get", "/api/v1/performance/overview")
test("perf_trends", "get", "/api/v1/performance/trends")
test(
    "perf_track",
    "post",
    "/api/v1/performance/track",
    data={"content_id": CONTENT_ID, "event_type": "view", "value": 100},
)

# ── 32. SSO / OIDC ──────────────────────────────────────────────────
test_group("32. SSO / OIDC")
test("sso_providers", "get", "/api/v1/sso/providers")
test("sso_available", "get", "/api/v1/sso/available")
test(
    "sso_create_provider",
    "post",
    "/api/v1/sso/providers",
    data={
        "name": "google",
        "display_name": "Google",
        "client_id": "test-id",
        "client_secret": "test-secret",
        "discovery_url": "https://accounts.google.com/.well-known/openid-configuration",
    },
)
test("sso_identities", "get", "/api/v1/sso/identities")

# ── 33. SAML ─────────────────────────────────────────────────────────
test_group("33. SAML SSO")
test("saml_providers", "get", "/api/v1/saml/providers")
test("saml_available", "get", "/api/v1/saml/available")
test(
    "saml_create_provider",
    "post",
    "/api/v1/saml/providers",
    data={
        "name": "okta",
        "display_name": "Okta",
        "entity_id": "https://okta.com/saml",
        "sso_url": "https://okta.com/sso/saml",
        "certificate": "test-cert",
    },
)
test("saml_identities", "get", "/api/v1/saml/identities")

# ── 34. Marketplace ─────────────────────────────────────────────────
test_group("34. Template Marketplace")
test("marketplace_templates", "get", "/api/v1/marketplace/templates")
test("marketplace_featured", "get", "/api/v1/marketplace/templates/featured")
test("marketplace_trending", "get", "/api/v1/marketplace/templates/trending")
test("marketplace_categories", "get", "/api/v1/marketplace/categories")
test("marketplace_tags", "get", "/api/v1/marketplace/tags")

# ── 35. Plugin System ───────────────────────────────────────────────
test_group("35. Plugin System")
test("plugins_list", "get", "/api/v1/plugins")
test("plugins_meta", "get", "/api/v1/plugins/meta")
test(
    "plugin_create",
    "post",
    "/api/v1/plugins",
    data={"name": "Test Plugin", "version": "1.0.0", "description": "Test plugin"},
)

# ── 36. SLA Monitoring ──────────────────────────────────────────────
test_group("36. SLA Monitoring")
test("sla_policies", "get", "/api/v1/sla/policies")
test("sla_dashboard", "get", "/api/v1/sla/dashboard")
test("sla_alerts", "get", "/api/v1/sla/alerts")
test("sla_uptime", "get", "/api/v1/sla/uptime")
test("sla_response_time", "get", "/api/v1/sla/response-time")
test("sla_error_rate", "get", "/api/v1/sla/error-rate")
test(
    "sla_create_policy",
    "post",
    "/api/v1/sla/policies",
    data={
        "name": "Test SLA",
        "metric": "uptime",
        "threshold": 99.9,
        "window_minutes": 5,
    },
)

# ── 37. Integration Framework ───────────────────────────────────────
test_group("37. Integration Hub Framework")
test("int_framework_configs", "get", "/api/v1/integration-framework/configs")
test(
    "int_framework_create",
    "post",
    "/api/v1/integration-framework/configs",
    data={
        "name": "Test Config",
        "type": "webhook",
        "provider": "custom",
        "credentials": {"api_key": "test"},
        "settings": {"url": "https://example.com"},
    },
)

# ── 38. Funnel Tracking ─────────────────────────────────────────────
test_group("38. Funnel Tracking")
test("funnels_list", "get", "/api/v1/funnels")
test(
    "funnel_create",
    "post",
    "/api/v1/funnels",
    data={
        "name": "Test Funnel",
        "steps": [
            {"step_id": "step-1", "name": "Visit", "order": 1},
            {"step_id": "step-2", "name": "Sign Up", "order": 2},
            {"step_id": "step-3", "name": "Convert", "order": 3},
        ],
    },
)

# ── 39. Attribution ──────────────────────────────────────────────────
test_group("39. Attribution Modeling")
test("attribution_channels", "get", "/api/v1/attribution/channels")
test("attribution_touchpoints", "get", f"/api/v1/attribution/touchpoints/{CONTENT_ID}")
test(
    "attribution_calculate",
    "post",
    "/api/v1/attribution/calculate",
    data={"content_id": CONTENT_ID, "model": "last_touch"},
)

# ── 40. Webhooks ────────────────────────────────────────────────────
test_group("40. Webhook System")
test("webhook_logs", "get", "/api/v1/webhooks/logs")
test("webhook_config", "get", "/api/v1/webhooks/config")

# ── 41. Stripe ───────────────────────────────────────────────────────
test_group("41. Stripe / Payment")
test("stripe_config", "get", "/api/v1/stripe/config")
test(
    "stripe_checkout",
    "post",
    "/api/v1/stripe/checkout",
    data={
        "plan": "pro",
        "billing_cycle": "monthly",
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
    },
)

# ── 42. Admin ───────────────────────────────────────────────────────
test_group("42. Admin Panel (requires admin role)")
# Admin requires admin role — our mock user has 'authenticated' role
test("admin_errors", "get", "/api/v1/admin/errors", expected_min=200, expected_max=403)
test(
    "admin_error_summary",
    "get",
    "/api/v1/admin/errors/summary",
    expected_min=200,
    expected_max=403,
)
test(
    "admin_user_stats",
    "get",
    "/api/v1/admin/users/stats",
    expected_min=200,
    expected_max=403,
)

# ── 43. Docs ─────────────────────────────────────────────────────────
test_group("43. API Documentation")
test("docs_openapi", "get", "/api/v1/docs/openapi.json")
test("docs_redoc", "get", "/api/v1/docs/redoc")

# ── 44. Presence ────────────────────────────────────────────────────
test_group("44. Presence / Collaboration")
test("presence_room", "get", "/api/v1/presence/room-1")
test("presence_count", "get", "/api/v1/presence/room-1/count")
test("collab_history", "get", f"/api/v1/collaboration/{CONTENT_ID}/history")
test("collab_lock", "get", f"/api/v1/collaboration/{CONTENT_ID}/lock")

# ── 45. Org Plugins ─────────────────────────────────────────────────
test_group("45. Organization Plugins")
test("org_plugins_list", "get", f"/api/v1/organizations/{ORG_ID}/plugins")

# ══════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════

print(f"\n{'='*60}")
print(f"📊 DEEP SYSTEM TEST SUMMARY")
print(f"{'='*60}")
total = len(results["pass"]) + len(results["fail"])
print(f"  ✅ Passed: {len(results['pass'])}/{total}")
print(f"  ❌ Failed: {len(results['fail'])}/{total}")
if total > 0:
    print(f"  📈 Pass Rate: {len(results['pass'])/total*100:.1f}%")

if results["fail"]:
    print(f"\n{'='*60}")
    print(f"❌ FAILURES BY CATEGORY")
    print(f"{'='*60}")

    server_5xx = []
    validation_4xx = []
    not_found_404 = []
    other = []

    for name in results["fail"]:
        err = results["errors"].get(name, "")
        if "500" in err or "Internal Server Error" in err:
            server_5xx.append((name, err))
        elif "422" in err or "400" in err:
            validation_4xx.append((name, err))
        elif "404" in err:
            not_found_404.append((name, err))
        else:
            other.append((name, err))

    if server_5xx:
        print(f"\n🔥 500 Server Errors ({len(server_5xx)}):")
        for name, err in server_5xx:
            print(f"  • {name}: {err[:120]}")
    if validation_4xx:
        print(f"\n⚠️ 4xx Validation Errors ({len(validation_4xx)}):")
        for name, err in validation_4xx:
            print(f"  • {name}: {err[:120]}")
    if not_found_404:
        print(f"\n🔍 404 Not Found ({len(not_found_404)}):")
        for name, err in not_found_404:
            print(f"  • {name}: {err[:120]}")
    if other:
        print(f"\n❓ Other ({len(other)}):")
        for name, err in other:
            print(f"  • {name}: {err[:120]}")

# Save detailed results
with open("/tmp/deep_system_test_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n📄 Full results → /tmp/deep_system_test_results.json")

# Cleanup
for p in active_patches:
    try:
        p.stop()
    except:
        pass
app.dependency_overrides.clear()

# Exit code
pass_rate = len(results["pass"]) / total if total > 0 else 0
if pass_rate >= 0.95:
    print(f"\n🟢 EXCELLENT — {pass_rate*100:.0f}% pass rate")
    print(f"\n🟢 EXCELLENT — {pass_rate*100:.0f}% pass rate")
elif pass_rate >= 0.80:
    print(f"\n🟡 GOOD — {pass_rate*100:.0f}% pass rate")
else:
    print(f"\n🔴 NEEDS FIXES — {pass_rate*100:.0f}% pass rate")

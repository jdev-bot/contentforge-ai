"""
FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import get_settings
from app.routers import (
    ab_testing,
    admin,
    ai_editor,
    api_keys,
    ai_suggestions,
    alerts,
    analytics,
    attribution,
    audience,
    audit_logs,
    auth,
    automation,
    categorization,
    collaboration,
    comments,
    competitors,
    content,
    dashboards,
    distributions,
    docs,
    freshness,
    funnel,
    health,
    init,
    integration_framework,
    integrations,
    marketplace,
    notifications,
    organizations,
    performance,
    plugins,
    presence,
    projects,
    quality_scoring,
    reports,
    retention,
    rss,
    saml,
    scheduler,
    search,
    sentiment,
    sla,
    sso,
)
from app.routers import stripe as stripe_router
from app.routers import (
    engagement_prediction,
    suggestions,
    team_calendar,
    trash,
    trends,
    usage,
    user,
    version_history,
    webhooks,
    ws,
)

logger = logging.getLogger(__name__)

settings = get_settings()


from app.services.websocket_manager import websocket_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    await websocket_manager.start()
    yield
    # Shutdown
    await websocket_manager.stop()
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title="ContentForge AI API",
    description="AI-powered content repurposing and distribution platform",
    version="0.1.0",
    lifespan=lifespan,
    redirect_slashes=False,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


from app.services.groq_service import NoAPIKeyConfigured
@app.exception_handler(NoAPIKeyConfigured)
async def no_api_key_handler(request, exc):
    """Return 403 with clear message when user has no API key configured."""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=403,
        content={
            "detail": str(exc),
            "code": "NO_API_KEY",
            "action": "Add your API key in Settings → API Keys",
        },
    )

from app.core.error_tracking import ErrorTrackingMiddleware

# Import middleware
from app.core.rate_limit import UsageTrackingMiddleware
from app.core.byok_middleware import BYOKMiddleware
from app.middleware.rate_limit_headers import RateLimitHeadersMiddleware
from app.middleware.performance import PerformanceMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.etag import ETagMiddleware

# ETag middleware (adds 304 Not Modified for cacheable endpoints)
app.add_middleware(ETagMiddleware)

# Request ID middleware (adds X-Request-ID for tracing)
app.add_middleware(RequestIDMiddleware)

# Performance monitoring (adds X-Response-Time header, logs slow requests)
app.add_middleware(PerformanceMiddleware)

# Error tracking middleware (must be early to catch all errors)
app.add_middleware(ErrorTrackingMiddleware)

# Rate limit headers middleware (adds X-RateLimit headers)
app.add_middleware(RateLimitHeadersMiddleware)

# BYOK middleware — resolve per-user API keys before route handlers
app.add_middleware(BYOKMiddleware)

# Usage tracking middleware
app.add_middleware(UsageTrackingMiddleware)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Request-ID",
        "X-API-Key",
        "Upgrade",
        "Connection",
        "Sec-WebSocket-Key",
        "Sec-WebSocket-Version",
    ],
)

# Routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(init.router, prefix="/api/v1", tags=["init"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(organizations.router, prefix="/api/v1", tags=["organizations"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(content.router, prefix="/api/v1", tags=["content"])
app.include_router(distributions.router, prefix="/api/v1", tags=["distributions"])
app.include_router(usage.router, prefix="/api/v1", tags=["usage"])
app.include_router(docs.router, prefix="/api/v1", tags=["documentation"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(webhooks.router, prefix="/api/v1", tags=["webhooks"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(stripe_router.router, prefix="/api/v1", tags=["stripe"])
app.include_router(ai_suggestions.router, prefix="/api/v1", tags=["ai-suggestions"])
app.include_router(ai_editor.router, prefix="/api/v1", tags=["ai-editor"])
app.include_router(automation.router, prefix="/api/v1", tags=["automation"])
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])
app.include_router(user.router, prefix="/api/v1", tags=["user"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(trash.router, prefix="/api/v1", tags=["trash"])
app.include_router(scheduler.router, prefix="/api/v1", tags=["scheduler"])
app.include_router(rss.router, prefix="/api/v1", tags=["rss"])
app.include_router(freshness.router, prefix="/api/v1", tags=["freshness"])
app.include_router(audience.router, prefix="/api/v1", tags=["audience"])
app.include_router(trends.router, prefix="/api/v1", tags=["trends"])
app.include_router(integrations.router, prefix="/api/v1", tags=["integrations"])
app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
app.include_router(competitors.router, prefix="/api/v1", tags=["competitors"])
app.include_router(version_history.router, prefix="/api/v1", tags=["version-history"])
app.include_router(audit_logs.router, prefix="/api/v1", tags=["audit-logs"])
app.include_router(quality_scoring.router, prefix="/api/v1", tags=["quality-scoring"])
app.include_router(sentiment.router, prefix="/api/v1", tags=["sentiment"])
app.include_router(dashboards.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
app.include_router(retention.router, prefix="/api/v1", tags=["retention"])
app.include_router(comments.router, prefix="/api/v1", tags=["comments"])
app.include_router(suggestions.router, prefix="/api/v1", tags=["suggestions"])
app.include_router(categorization.router, prefix="/api/v1", tags=["categorization"])
app.include_router(performance.router, prefix="/api/v1", tags=["performance"])
app.include_router(sso.router, prefix="/api/v1", tags=["sso"])
app.include_router(saml.router, prefix="/api/v1", tags=["saml"])
app.include_router(marketplace.router, prefix="/api/v1", tags=["marketplace"])
app.include_router(presence.router, prefix="/api/v1", tags=["presence"])
app.include_router(collaboration.router, prefix="/api/v1", tags=["collaboration"])
app.include_router(ws.router, tags=["websocket"])
app.include_router(plugins.router, prefix="/api/v1", tags=["plugins"])
app.include_router(sla.router, prefix="/api/v1", tags=["sla"])
app.include_router(
    integration_framework.router, prefix="/api/v1", tags=["integration-framework"]
)
app.include_router(funnel.router, prefix="/api/v1", tags=["funnels"])
app.include_router(attribution.router, prefix="/api/v1", tags=["attribution"])
app.include_router(team_calendar.router, prefix="/api/v1", tags=["team-calendar"])
app.include_router(engagement_prediction.router, prefix="/api/v1", tags=["engagement-prediction"])
app.include_router(ab_testing.router, prefix="/api/v1", tags=["ab-testing"])
app.include_router(api_keys.router, prefix="/api/v1/api-keys", tags=["api-keys"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running",
        "environment": settings.APP_ENV,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

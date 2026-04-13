"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.routers import auth, content, projects, distributions, health, usage, docs, admin, webhooks, analytics, stripe as stripe_router, organizations, ai_suggestions, automation, notifications, user, search, trash, scheduler, ai_editor, translation, rss

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    yield
    # Shutdown
    print(f"🛑 Shutting down {settings.APP_NAME}")


app = FastAPI(
    title="ContentForge AI API",
    description="AI-powered content repurposing and distribution platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Import middleware
from app.core.rate_limit import UsageTrackingMiddleware
from app.core.error_tracking import ErrorTrackingMiddleware
from app.middleware.rate_limit_headers import RateLimitHeadersMiddleware

# Error tracking middleware (must be first to catch all errors)
app.add_middleware(ErrorTrackingMiddleware)

# Rate limit headers middleware (adds X-RateLimit headers)
app.add_middleware(RateLimitHeadersMiddleware)

# Usage tracking middleware
app.add_middleware(UsageTrackingMiddleware)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
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
app.include_router(translation.router, prefix="/api/v1", tags=["translation"])
app.include_router(rss.router, prefix="/api/v1", tags=["rss"])


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

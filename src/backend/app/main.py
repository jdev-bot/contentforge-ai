"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.routers import auth, content, projects, distributions, health, usage

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

# Import rate limit middleware
from app.core.rate_limit import UsageTrackingMiddleware

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
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(content.router, prefix="/api/v1", tags=["content"])
app.include_router(distributions.router, prefix="/api/v1", tags=["distributions"])
app.include_router(usage.router, prefix="/api/v1", tags=["usage"])


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

"""
Health check endpoints with detailed component status.
Includes database, Redis, Groq, Stripe, and n8n connectivity checks.
"""
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.supabase import get_supabase_client

router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    """Basic health check response."""
    status: str
    timestamp: str
    version: str


class ComponentStatus(BaseModel):
    """Status of an individual component."""
    status: str = Field(..., description="healthy, degraded, or unhealthy")
    response_time_ms: Optional[float] = Field(None, description="Response time in milliseconds")
    message: Optional[str] = Field(None, description="Status message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    last_checked: Optional[str] = Field(None, description="ISO timestamp of last check")


class DetailedHealthResponse(BaseModel):
    """Detailed health check response."""
    status: str
    timestamp: str
    version: str
    environment: str
    uptime_seconds: Optional[int] = None
    components: Dict[str, ComponentStatus]
    alerts: Optional[List[str]] = None


class SystemMetrics(BaseModel):
    """System metrics response."""
    timestamp: str
    database: Dict[str, Any]
    redis: Optional[Dict[str, Any]] = None
    external_apis: Dict[str, Any]


# Store startup time for uptime calculation
_startup_time = time.time()


def check_disk_space() -> Dict[str, Any]:
    """Check disk space usage."""
    try:
        import shutil
        stat = shutil.disk_usage("/")
        total_gb = stat.total / (1024**3)
        used_gb = stat.used / (1024**3)
        free_gb = stat.free / (1024**3)
        percent_used = (stat.used / stat.total) * 100
        
        status = "healthy"
        if percent_used > 90:
            status = "unhealthy"
        elif percent_used > 75:
            status = "degraded"
        
        return {
            "status": status,
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "free_gb": round(free_gb, 2),
            "percent_used": round(percent_used, 2)
        }
    except Exception as e:
        return {
            "status": "unknown",
            "error": str(e)
        }


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns simple status indicating the API is running.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="0.1.0",
    )


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check():
    """
    Readiness check for Kubernetes/Docker orchestration.
    
    Checks if the service is ready to accept traffic.
    Includes database connectivity check.
    """
    try:
        supabase = get_supabase_client()
        # Quick query to verify DB connectivity
        result = supabase.table("profiles").select("count", count="exact").limit(0).execute()
        
        return HealthResponse(
            status="ready",
            timestamp=datetime.now(timezone.utc).isoformat(),
            version="0.1.0",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
        )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check endpoint including database, Redis, and external API connectivity.
    
    Returns status of all system components including:
    - Database (Supabase PostgreSQL)
    - Cache (Redis)
    - AI API (Groq)
    - Payment API (Stripe)
    - Workflow Engine (n8n)
    - System resources (disk space)
    
    **Response codes:**
    - 200: All critical components healthy
    - 503: One or more critical components unhealthy
    """
    components: Dict[str, ComponentStatus] = {}
    overall_status = "healthy"
    alerts: List[str] = []
    
    # Check Database (Supabase)
    try:
        start_time = time.time()
        supabase = get_supabase_client()
        # Simple query to check connection
        result = supabase.table("profiles").select("count", count="exact").limit(0).execute()
        db_response_time = (time.time() - start_time) * 1000
        
        components["database"] = ComponentStatus(
            status="healthy",
            response_time_ms=round(db_response_time, 2),
            message="Supabase connection established",
            details={"type": "supabase-postgresql"},
            last_checked=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        overall_status = "degraded"
        components["database"] = ComponentStatus(
            status="unhealthy",
            message=f"Database connection failed: {str(e)}",
            details={"type": "supabase-postgresql"},
            last_checked=datetime.now(timezone.utc).isoformat()
        )
        alerts.append("Database connection failed")
    
    # Check Redis (if configured)
    try:
        start_time = time.time()
        redis_url = getattr(settings, 'REDIS_URL', None) or "redis://localhost:6379"
        
        try:
            import redis.asyncio as redis_lib
            redis_client = redis_lib.from_url(redis_url, socket_connect_timeout=5)
            await redis_client.ping()
            await redis_client.close()
            
            redis_response_time = (time.time() - start_time) * 1000
            components["redis"] = ComponentStatus(
                status="healthy",
                response_time_ms=round(redis_response_time, 2),
                message="Redis connection established",
                details={"url": redis_url.replace("//", "//***@") if "@" in redis_url else redis_url},
                last_checked=datetime.now(timezone.utc).isoformat()
            )
        except ImportError:
            components["redis"] = ComponentStatus(
                status="unknown",
                message="Redis library not installed",
                details={"url": redis_url.replace("//", "//***@") if "@" in redis_url else redis_url},
                last_checked=datetime.now(timezone.utc).isoformat()
            )
    except Exception as e:
        overall_status = "degraded"
        components["redis"] = ComponentStatus(
            status="unhealthy",
            message=f"Redis connection failed: {str(e)}",
            details={"url": redis_url.replace("//", "//***@") if "@" in redis_url else redis_url},
            last_checked=datetime.now(timezone.utc).isoformat()
        )
        alerts.append("Redis connection failed")
    
    # Check Groq API
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
            )
            
            if response.status_code == 200:
                groq_response_time = (time.time() - start_time) * 1000
                components["groq"] = ComponentStatus(
                    status="healthy",
                    response_time_ms=round(groq_response_time, 2),
                    message="Groq API accessible",
                    details={"model": settings.GROQ_MODEL},
                    last_checked=datetime.now(timezone.utc).isoformat()
                )
            else:
                overall_status = "degraded"
                components["groq"] = ComponentStatus(
                    status="unhealthy",
                    message=f"Groq API returned status {response.status_code}",
                    details={"model": settings.GROQ_MODEL},
                    last_checked=datetime.now(timezone.utc).isoformat()
                )
                alerts.append(f"Groq API returned status {response.status_code}")
    except Exception as e:
        overall_status = "degraded"
        components["groq"] = ComponentStatus(
            status="unhealthy",
            message=f"Groq API check failed: {str(e)}",
            details={"model": settings.GROQ_MODEL},
            last_checked=datetime.now(timezone.utc).isoformat()
        )
        alerts.append("Groq API unavailable")
    
    # Check Stripe API
    stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    if stripe_key:
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.stripe.com/v1/account",
                    headers={"Authorization": f"Bearer {stripe_key}"}
                )
                
                if response.status_code == 200:
                    stripe_response_time = (time.time() - start_time) * 1000
                    account_data = response.json()
                    components["stripe"] = ComponentStatus(
                        status="healthy",
                        response_time_ms=round(stripe_response_time, 2),
                        message="Stripe API accessible",
                        details={
                            "account_id": account_data.get("id"),
                            "charges_enabled": account_data.get("charges_enabled"),
                            "payouts_enabled": account_data.get("payouts_enabled")
                        },
                        last_checked=datetime.now(timezone.utc).isoformat()
                    )
                else:
                    overall_status = "degraded"
                    components["stripe"] = ComponentStatus(
                        status="unhealthy",
                        message=f"Stripe API returned status {response.status_code}",
                        details={"status_code": response.status_code},
                        last_checked=datetime.now(timezone.utc).isoformat()
                    )
                    alerts.append(f"Stripe API returned status {response.status_code}")
        except Exception as e:
            overall_status = "degraded"
            components["stripe"] = ComponentStatus(
                status="unhealthy",
                message=f"Stripe API check failed: {str(e)}",
                last_checked=datetime.now(timezone.utc).isoformat()
            )
            alerts.append("Stripe API unavailable")
    else:
        components["stripe"] = ComponentStatus(
            status="unknown",
            message="Stripe not configured",
            last_checked=datetime.now(timezone.utc).isoformat()
        )
    
    # Check n8n (if configured)
    n8n_url = getattr(settings, 'N8N_WEBHOOK_URL', None)
    if n8n_url:
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                # n8n typically returns the UI on root path
                response = await client.get(n8n_url.replace('/webhook/', '/healthz').rsplit('/', 1)[0] + '/healthz')
                
                n8n_response_time = (time.time() - start_time) * 1000
                if response.status_code in [200, 401, 403]:  # Auth errors mean it's running
                    components["n8n"] = ComponentStatus(
                        status="healthy",
                        response_time_ms=round(n8n_response_time, 2),
                        message="n8n workflow engine accessible",
                        last_checked=datetime.now(timezone.utc).isoformat()
                    )
                else:
                    overall_status = "degraded"
                    components["n8n"] = ComponentStatus(
                        status="degraded",
                        message=f"n8n returned status {response.status_code}",
                        last_checked=datetime.now(timezone.utc).isoformat()
                    )
                    alerts.append(f"n8n returned status {response.status_code}")
        except Exception as e:
            overall_status = "degraded"
            components["n8n"] = ComponentStatus(
                status="unhealthy",
                message=f"n8n check failed: {str(e)}",
                last_checked=datetime.now(timezone.utc).isoformat()
            )
            alerts.append("n8n workflow engine unavailable")
    else:
        components["n8n"] = ComponentStatus(
            status="unknown",
            message="n8n not configured",
            last_checked=datetime.now(timezone.utc).isoformat()
        )
    
    # Check Disk Space
    disk_info = check_disk_space()
    components["disk"] = ComponentStatus(
        status=disk_info.get("status", "unknown"),
        message=f"Disk usage: {disk_info.get('percent_used', 0):.1f}%",
        details=disk_info,
        last_checked=datetime.now(timezone.utc).isoformat()
    )
    
    if disk_info.get("status") == "unhealthy":
        overall_status = "degraded"
        alerts.append(f"Disk space critically low: {disk_info.get('free_gb', 0):.1f}GB free")
    elif disk_info.get("status") == "degraded":
        if overall_status == "healthy":
            overall_status = "degraded"
        alerts.append(f"Disk space low: {disk_info.get('free_gb', 0):.1f}GB free")
    
    # Calculate uptime
    uptime_seconds = int(time.time() - _startup_time)
    
    # Check if any critical component is unhealthy
    critical_components = ["database", "stripe"]
    critical_unhealthy = False
    for component_name in critical_components:
        if components.get(component_name, ComponentStatus(status="unknown")).status == "unhealthy":
            critical_unhealthy = True
            break
    
    if critical_unhealthy or overall_status == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DetailedHealthResponse(
                status="unhealthy",
                timestamp=datetime.now(timezone.utc).isoformat(),
                version="0.1.0",
                environment=settings.APP_ENV,
                uptime_seconds=uptime_seconds,
                components=components,
                alerts=alerts or None
            ).model_dump()
        )
    
    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="0.1.0",
        environment=settings.APP_ENV,
        uptime_seconds=uptime_seconds,
        components=components,
        alerts=alerts if alerts else None
    )


@router.get("/health/metrics", response_model=SystemMetrics)
async def system_metrics():
    """
    System metrics endpoint.
    
    Returns detailed metrics for monitoring and alerting systems.
    """
    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {},
        "external_apis": {}
    }
    
    # Database metrics
    try:
        supabase = get_supabase_client()
        # Get connection pool stats (if available)
        metrics["database"] = {
            "status": "connected",
            "pool_size": getattr(settings, 'DB_POOL_SIZE', 10),
            "max_overflow": getattr(settings, 'DB_MAX_OVERFLOW', 20)
        }
    except Exception as e:
        metrics["database"] = {
            "status": "error",
            "error": str(e)
        }
    
    # External API metrics
    # Groq
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
            )
            metrics["external_apis"]["groq"] = {
                "status": "healthy" if response.status_code == 200 else "degraded",
                "response_time_ms": round((time.time() - start_time) * 1000, 2),
                "status_code": response.status_code
            }
    except Exception as e:
        metrics["external_apis"]["groq"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Stripe
    stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    if stripe_key:
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.stripe.com/v1/account",
                    headers={"Authorization": f"Bearer {stripe_key}"}
                )
                metrics["external_apis"]["stripe"] = {
                    "status": "healthy" if response.status_code == 200 else "degraded",
                    "response_time_ms": round((time.time() - start_time) * 1000, 2),
                    "status_code": response.status_code
                }
        except Exception as e:
            metrics["external_apis"]["stripe"] = {
                "status": "unhealthy",
                "error": str(e)
            }
    else:
        metrics["external_apis"]["stripe"] = {"status": "not_configured"}
    
    return SystemMetrics(**metrics)


@router.get("/health/version")
async def version_info():
    """
    Version and build information.
    """
    return {
        "version": "0.1.0",
        "build_date": "2026-04-12",
        "git_commit": getattr(settings, 'GIT_COMMIT', 'unknown'),
        "python_version": "3.11",
        "environment": settings.APP_ENV,
        "features": {
            "stripe": bool(getattr(settings, 'STRIPE_SECRET_KEY', None)),
            "redis": bool(getattr(settings, 'REDIS_URL', None)),
            "n8n": bool(getattr(settings, 'N8N_WEBHOOK_URL', None)),
            "resend": bool(getattr(settings, 'RESEND_API_KEY', None))
        }
    }
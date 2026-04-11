"""
Health check endpoints.
"""
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
import httpx

from app.core.config import get_settings
from app.core.supabase import get_supabase_client

router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class ComponentStatus(BaseModel):
    status: str
    response_time_ms: Optional[float] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class DetailedHealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    environment: str
    components: Dict[str, ComponentStatus]


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0",
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check endpoint including database, Redis, and Groq connectivity.
    
    Returns status of all system components.
    """
    import time
    
    components: Dict[str, ComponentStatus] = {}
    overall_status = "healthy"
    
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
            details={"type": "supabase-postgresql"}
        )
    except Exception as e:
        overall_status = "degraded"
        components["database"] = ComponentStatus(
            status="unhealthy",
            message=f"Database connection failed: {str(e)}",
            details={"type": "supabase-postgresql"}
        )
    
    # Check Redis (if configured)
    try:
        start_time = time.time()
        # Check if Redis URL is configured
        redis_url = getattr(settings, 'REDIS_URL', None) or "redis://localhost:6379"
        
        # Try to connect to Redis
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
                details={"url": redis_url.replace("//", "//***@") if "@" in redis_url else redis_url}
            )
        except ImportError:
            components["redis"] = ComponentStatus(
                status="unknown",
                message="Redis library not installed",
                details={"url": redis_url.replace("//", "//***@") if "@" in redis_url else redis_url}
            )
        except Exception as e:
            overall_status = "degraded"
            components["redis"] = ComponentStatus(
                status="unhealthy",
                message=f"Redis connection failed: {str(e)}",
                details={"url": redis_url.replace("//", "//***@") if "@" in redis_url else redis_url}
            )
    except Exception as e:
        overall_status = "degraded"
        components["redis"] = ComponentStatus(
            status="unhealthy",
            message=f"Redis check failed: {str(e)}"
        )
    
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
                    details={"model": settings.GROQ_MODEL}
                )
            else:
                overall_status = "degraded"
                components["groq"] = ComponentStatus(
                    status="unhealthy",
                    message=f"Groq API returned status {response.status_code}",
                    details={"model": settings.GROQ_MODEL}
                )
    except Exception as e:
        overall_status = "degraded"
        components["groq"] = ComponentStatus(
            status="unhealthy",
            message=f"Groq API check failed: {str(e)}",
            details={"model": settings.GROQ_MODEL}
        )
    
    # Check if any critical component is unhealthy
    critical_components = ["database"]
    for component_name in critical_components:
        if components.get(component_name, ComponentStatus(status="unknown")).status == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=DetailedHealthResponse(
                    status="unhealthy",
                    timestamp=datetime.utcnow().isoformat(),
                    version="0.1.0",
                    environment=settings.APP_ENV,
                    components=components
                ).model_dump()
            )
    
    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0",
        environment=settings.APP_ENV,
        components=components
    )

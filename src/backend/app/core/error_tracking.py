"""
Error tracking middleware and utilities for logging 4xx/5xx errors.
"""
import time
import traceback
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request, HTTPException
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.supabase import get_supabase_client


class ErrorLogEntry(BaseModel):
    """Error log entry model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status_code: int
    error_type: str
    message: str
    detail: Optional[str] = None
    path: str
    method: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_body: Optional[str] = None
    traceback: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def log_error_to_database(
    status_code: int,
    error_type: str,
    message: str,
    path: str,
    method: str,
    detail: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_body: Optional[str] = None,
    traceback_str: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Log an error to the database.
    
    Returns the error log ID if successful, None otherwise.
    """
    try:
        supabase = get_supabase_client()
        
        error_data = {
            "id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": status_code,
            "error_type": error_type,
            "message": message,
            "detail": detail,
            "path": path,
            "method": method,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "request_body": request_body,
            "traceback": traceback_str,
            "metadata": metadata or {},
        }
        
        result = supabase.table("error_logs").insert(error_data).execute()
        
        if result.data:
            return result.data[0].get("id")
        return None
        
    except Exception as e:
        # If database logging fails, print to console
        print(f"Failed to log error to database: {e}")
        print(f"Original error: {message}")
        return None


class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track and log all 4xx/5xx errors to the database.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request and log errors."""
        start_time = time.time()
        
        # Get request details before processing
        path = request.url.path
        method = request.method
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Try to get user ID from auth header
        user_id = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.core.supabase import get_supabase_client
                token = auth_header.replace("Bearer ", "")
                supabase = get_supabase_client()
                user = supabase.auth.get_user(token)
                if user and user.user:
                    user_id = str(user.user.id)
            except Exception:
                pass  # Don't fail if auth fails
        
        # Read request body for errors
        request_body = None
        try:
            if method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
                if body:
                    request_body = body.decode('utf-8')[:2000]  # Limit size
        except Exception:
            pass
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Log 4xx/5xx errors
            if response.status_code >= 400:
                error_type = "client_error" if response.status_code < 500 else "server_error"
                message = f"HTTP {response.status_code} error"
                
                log_error_to_database(
                    status_code=response.status_code,
                    error_type=error_type,
                    message=message,
                    path=path,
                    method=method,
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_body=request_body,
                    metadata={
                        "response_time_ms": round((time.time() - start_time) * 1000, 2)
                    }
                )
            
            return response
            
        except HTTPException as exc:
            # Log HTTP exceptions
            error_type = "client_error" if exc.status_code < 500 else "server_error"
            
            log_error_to_database(
                status_code=exc.status_code,
                error_type=error_type,
                message=str(exc.detail),
                path=path,
                method=method,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_body=request_body,
                metadata={
                    "response_time_ms": round((time.time() - start_time) * 1000, 2),
                    "headers": dict(request.headers)
                }
            )
            raise
            
        except Exception as exc:
            # Log unhandled exceptions
            log_error_to_database(
                status_code=500,
                error_type="unhandled_exception",
                message=str(exc),
                path=path,
                method=method,
                detail=type(exc).__name__,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_body=request_body,
                traceback_str=traceback.format_exc(),
                metadata={
                    "response_time_ms": round((time.time() - start_time) * 1000, 2)
                }
            )
            raise


def get_recent_errors(limit: int = 100) -> list:
    """Get recent errors from the database."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("error_logs").select(
            "*"
        ).order("timestamp", desc=True).limit(limit).execute()
        
        return result.data
    except Exception as e:
        print(f"Failed to retrieve error logs: {e}")
        return []


def get_error_summary(hours: int = 24) -> Dict[str, Any]:
    """Get error summary statistics."""
    try:
        supabase = get_supabase_client()
        
        # Get time threshold
        from datetime import timedelta
        threshold = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        
        result = supabase.table("error_logs").select(
            "*"
        ).gte("timestamp", threshold).execute()
        
        errors = result.data
        
        # Calculate summary
        total = len(errors)
        by_status = {}
        by_type = {}
        
        for error in errors:
            status = error.get("status_code", 0)
            error_type = error.get("error_type", "unknown")
            
            by_status[status] = by_status.get(status, 0) + 1
            by_type[error_type] = by_type.get(error_type, 0) + 1
        
        return {
            "total": total,
            "period_hours": hours,
            "by_status_code": by_status,
            "by_type": by_type,
            "recent": errors[:10] if errors else []
        }
        
    except Exception as e:
        print(f"Failed to retrieve error summary: {e}")
        return {"total": 0, "error": str(e)}

"""
Authentication router with Supabase integration.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status as http_status
from pydantic import BaseModel, EmailStr

from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.tasks.email import send_welcome_email_task

router = APIRouter()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    subscription_tier: str = "free"
    monthly_usage_count: int = 0
    monthly_usage_limit: int = 10


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


def get_auth_user(request: Request):
    """Dependency to get current authenticated user from Supabase session.

    Caches the user_id in request state so downstream middleware
    (error tracking, rate limit headers) can use it without
    making another supabase.auth.get_user() network call.
    """
    # Check if user was already validated and cached in this request
    from app.core.request_context import get_request_user, set_request_user_id, set_request_user
    cached = get_request_user(request)
    if cached:
        return cached

    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.replace("Bearer ", "")
    supabase = get_supabase_client()

    try:
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Cache for downstream middleware
        set_request_user_id(request, str(user.user.id))
        set_request_user(request, user.user)
        return user.user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/auth/register", response_model=TokenResponse, status_code=http_status.HTTP_201_CREATED
)
async def register(user_data: UserRegister):
    """Register a new user and trigger welcome email."""
    supabase = get_supabase_client()

    try:
        auth_response = supabase.auth.sign_up(
            {
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name,
                    }
                },
            }
        )

        if not auth_response.user:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Registration failed",
            )

        user_id = str(auth_response.user.id)

        # Queue welcome email
        try:
            send_welcome_email_task.delay(
                user_id=user_id,
                email=user_data.email,
                user_name=user_data.full_name,
            )
        except Exception as email_err:
            # Log error but don't fail registration
            import logging

            logging.getLogger(__name__).warning(
                f"Failed to queue welcome email: {email_err}"
            )

        # Get session for token
        session = auth_response.session

        if not session:
            # Email confirmation might be required
            return TokenResponse(
                access_token="",
                token_type="bearer",
                user=UserResponse(
                    id=user_id,
                    email=auth_response.user.email,
                    full_name=user_data.full_name,
                ),
            )

        return TokenResponse(
            access_token=session.access_token,
            token_type="bearer",
            user=UserResponse(
                id=user_id,
                email=auth_response.user.email,
                full_name=user_data.full_name,
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Login a user."""
    supabase = get_supabase_client()

    try:
        auth_response = supabase.auth.sign_in_with_password(
            {
                "email": user_data.email,
                "password": user_data.password,
            }
        )

        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Get profile data
        profile_data = auth_response.user.user_metadata or {}

        return TokenResponse(
            access_token=auth_response.session.access_token,
            token_type="bearer",
            user=UserResponse(
                id=str(auth_response.user.id),
                email=auth_response.user.email,
                full_name=profile_data.get("full_name"),
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )


@router.post("/auth/logout")
async def logout(request: Request):
    """Logout a user."""
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        supabase = get_supabase_client()
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

    return {"message": "Logged out successfully"}


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user(user=Depends(get_auth_user)):
    """Get current authenticated user with subscription details."""
    supabase = get_supabase_admin_client()
    profile_data = user.user_metadata or {}

    # Fetch subscription info from profiles table
    try:
        result = (
            supabase.table("profiles")
            .select("subscription_tier, monthly_usage_count, monthly_usage_limit")
            .eq("id", str(user.id))
            .single()
            .execute()
        )

        if result.data:
            subscription_tier = result.data.get("subscription_tier", "free")
            monthly_usage_count = result.data.get("monthly_usage_count", 0)
            monthly_usage_limit = result.data.get("monthly_usage_limit", 10)
        else:
            subscription_tier = "free"
            monthly_usage_count = 0
            monthly_usage_limit = 10
    except Exception:
        subscription_tier = "free"
        monthly_usage_count = 0
        monthly_usage_limit = 10

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=profile_data.get("full_name"),
        is_active=True,
        subscription_tier=subscription_tier,
        monthly_usage_count=monthly_usage_count,
        monthly_usage_limit=monthly_usage_limit,
    )


class UpdateProfileRequest(BaseModel):
    full_name: str


@router.patch("/auth/me", response_model=UserResponse)
async def update_current_user(
    update_data: UpdateProfileRequest, user=Depends(get_auth_user)
):
    """Update current user's profile."""
    supabase = get_supabase_client()

    try:
        # Update user metadata in Supabase Auth
        auth_response = supabase.auth.update_user(
            {
                "data": {
                    "full_name": update_data.full_name,
                }
            }
        )

        if not auth_response.user:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile",
            )

        # Also update in profiles table
        supabase_admin = get_supabase_admin_client()
        supabase_admin.table("profiles").update(
            {"full_name": update_data.full_name, "updated_at": "now()"}
        ).eq("id", str(user.id)).execute()

        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=update_data.full_name,
            is_active=True,
        )

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

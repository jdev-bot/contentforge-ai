"""
Authentication router with Supabase integration.
"""
from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.supabase import get_supabase_client

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


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


def get_auth_user(request: Request):
    """Dependency to get current authenticated user from Supabase session."""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.replace("Bearer ", "")
    supabase = get_supabase_client()
    
    try:
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user."""
    supabase = get_supabase_client()
    
    try:
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name,
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed",
            )
        
        # Get session for token
        session = auth_response.session
        
        if not session:
            # Email confirmation might be required
            return TokenResponse(
                access_token="",
                token_type="bearer",
                user=UserResponse(
                    id=str(auth_response.user.id),
                    email=auth_response.user.email,
                    full_name=user_data.full_name,
                )
            )
        
        return TokenResponse(
            access_token=session.access_token,
            token_type="bearer",
            user=UserResponse(
                id=str(auth_response.user.id),
                email=auth_response.user.email,
                full_name=user_data.full_name,
            )
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Login a user."""
    supabase = get_supabase_client()
    
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password,
        })
        
        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
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
            )
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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
        except:
            pass
    
    return {"message": "Logged out successfully"}


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user(user=Depends(get_auth_user)):
    """Get current authenticated user."""
    profile_data = user.user_metadata or {}
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=profile_data.get("full_name"),
        is_active=True,
    )

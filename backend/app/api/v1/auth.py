from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.domain.auth import User
from app.application.services.auth_service import AuthService
from app.infrastructure.db.repositories.auth_repo import (
    SQLUserRepository,
    SQLSessionRepository,
    SQLAuditLogRepository,
    SQLLoginHistoryRepository
)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Pydantic Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Helper to resolve service instance
def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        user_repo=SQLUserRepository(db),
        session_repo=SQLSessionRepository(db),
        audit_repo=SQLAuditLogRepository(db),
        history_repo=SQLLoginHistoryRepository(db)
    )

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegister, 
    request: Request,
    service: AuthService = Depends(get_auth_service)
):
    try:
        user = await service.register_user(
            email=payload.email, 
            password=payload.password,
            ip=request.client.host if request.client else None
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=LoginResponse)
async def login(
    payload: UserLogin,
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    try:
        ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent")
        
        result = await service.authenticate_user(
            email=payload.email,
            password=payload.password,
            ip_address=ip,
            user_agent=ua
        )
        
        # Set HTTPOnly cookie for secure refresh token handling
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=True,  # Set True in production over SSL/HTTPS
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days expiration
        )
        
        return {
            "access_token": result["access_token"],
            "user": result["user"]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    # Retrieve refresh token from cookies
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            # Decode to retrieve session JTI
            import jwt
            from app.core.config import settings
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
            jti = payload.get("jti")
            if jti:
                await service.revoke_user_session(
                    user_id=current_user.id,
                    session_id=jti,
                    requester_ip=request.client.host if request.client else None
                )
        except Exception:
            # Silence failures in background revocation during logout
            pass
            
    response.delete_cookie("refresh_token")

@router.post("/refresh", response_model=Dict[str, Any])
async def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session refresh token cookie is missing."
        )
        
    try:
        ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent")
        
        result = await service.refresh_session_tokens(
            refresh_token=refresh_token,
            ip_address=ip,
            user_agent=ua
        )
        
        # Reset HTTPOnly cookie with rotated refresh token
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60
        )
        
        return {
            "access_token": result["access_token"]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

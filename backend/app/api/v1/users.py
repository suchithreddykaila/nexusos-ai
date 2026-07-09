from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.domain.auth import User, UserPreferences
from app.application.services.auth_service import AuthService
from app.infrastructure.db.repositories.auth_repo import (
    SQLUserRepository,
    SQLSessionRepository,
    SQLAuditLogRepository,
    SQLLoginHistoryRepository
)

router = APIRouter(prefix="/users", tags=["users"])

# Pydantic Schemas
class ProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class PreferencesUpdate(BaseModel):
    theme: str
    default_provider: str
    default_model: str
    custom_settings: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

class LoginHistoryResponse(BaseModel):
    id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    failure_reason: Optional[str] = None
    created_at: datetime

class PreferencesResponse(BaseModel):
    theme: str
    default_provider: str
    default_model: str
    custom_settings: Dict[str, Any]

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        user_repo=SQLUserRepository(db),
        session_repo=SQLSessionRepository(db),
        audit_repo=SQLAuditLogRepository(db),
        history_repo=SQLLoginHistoryRepository(db)
    )

@router.put("/profile")
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    try:
        updated = await service.user_repo.update_profile(
            user_id=current_user.id,
            email=payload.email,
            avatar_url=payload.avatar_url
        )
        return updated
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
    payload: PasswordUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    try:
        ip = request.client.host if request.client else None
        await service.change_password(
            user_id=current_user.id,
            old_password=payload.old_password,
            new_password=payload.new_password,
            ip_address=ip
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    sessions = await service.session_repo.list_user_sessions(current_user.id)
    return sessions

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    session_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    ip = request.client.host if request.client else None
    await service.revoke_user_session(
        user_id=current_user.id,
        session_id=session_id,
        requester_ip=ip
    )

@router.get("/login-history", response_model=List[LoginHistoryResponse])
async def get_login_history(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    history = await service.history_repo.list_login_history(current_user.id)
    return history

@router.get("/preferences", response_model=PreferencesResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    prefs = await service.user_repo.get_preferences(current_user.id)
    if not prefs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found.")
    return prefs

@router.put("/preferences", response_model=PreferencesResponse)
async def update_preferences(
    payload: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    prefs = UserPreferences(
        user_id=current_user.id,
        theme=payload.theme,
        default_provider=payload.default_provider,
        default_model=payload.default_model,
        custom_settings=payload.custom_settings or {}
    )
    updated = await service.user_repo.update_preferences(prefs)
    return updated

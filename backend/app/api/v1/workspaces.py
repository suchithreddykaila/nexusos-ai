from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.domain.auth import User
from app.domain.workspaces import Workspace, WorkspaceMember, WorkspaceInvitation, WorkspaceAISettings, WorkspaceStorage, WorkspaceActivity
from app.application.services.workspace_service import WorkspaceService
from app.infrastructure.db.repositories.workspace_repo import (
    SQLWorkspaceRepository,
    SQLWorkspaceInvitationRepository,
    SQLWorkspaceActivityRepository
)
from app.infrastructure.db.repositories.auth_repo import SQLUserRepository

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

# Pydantic Request Schemas
class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    color_theme: Optional[str] = None

class MemberInviteRequest(BaseModel):
    email: EmailStr
    role_name: str = "viewer"

class WorkspaceAIUpdate(BaseModel):
    default_provider: str
    default_model: str
    temperature: float = 0.7
    max_tokens: int = 2048

# Response wrappers
class WorkspaceResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    color_theme: str
    icon: str
    is_archived: bool

class MemberResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    email: Optional[str] = None
    role_name: str
    created_at: datetime

class InviteResponse(BaseModel):
    id: str
    workspace_id: str
    email: EmailStr
    role_name: str
    status: str
    expires_at: datetime

class AISettingsResponse(BaseModel):
    workspace_id: str
    default_provider: str
    default_model: str
    temperature: float
    max_tokens: int
    streaming: bool
    offline_mode: bool
    privacy_mode: bool

class StorageResponse(BaseModel):
    workspace_id: str
    bytes_used: int
    bytes_quota: int

class ActivityResponse(BaseModel):
    id: str
    user_id: str
    email: Optional[str] = None
    action: str
    details: Dict[str, Any]
    created_at: datetime

def get_workspace_service(db: AsyncSession = Depends(get_db)) -> WorkspaceService:
    return WorkspaceService(
        db_session=db,
        workspace_repo=SQLWorkspaceRepository(db),
        invite_repo=SQLWorkspaceInvitationRepository(db),
        activity_repo=SQLWorkspaceActivityRepository(db),
        user_repo=SQLUserRepository(db)
    )

@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    try:
        ws = await service.create_user_workspace(
            user_id=current_user.id,
            user_email=current_user.email,
            name=payload.name,
            description=payload.description
        )
        return ws
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=List[WorkspaceResponse])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    workspaces = await service.workspace_repo.list_workspaces_for_user(current_user.id)
    return workspaces

@router.get("/{ws_id}", response_model=WorkspaceResponse)
async def get_workspace(
    ws_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    # Verify access seat
    member = await service.workspace_repo.get_member(ws_id, current_user.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access permissions to this workspace.")
        
    ws = await service.workspace_repo.get_workspace(ws_id)
    if not ws:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found or archived.")
    return ws

@router.put("/{ws_id}", response_model=WorkspaceResponse)
async def update_workspace(
    ws_id: str,
    payload: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    # Verify owner or admin permissions
    member = await service.workspace_repo.get_member(ws_id, current_user.id)
    if not member or member.role_name not in ["owner", "administrator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient workspace editor permissions.")
        
    ws = await service.workspace_repo.update_workspace(
        ws_id=ws_id,
        name=payload.name,
        description=payload.description,
        logo_url=payload.logo_url,
        color_theme=payload.color_theme
    )
    return ws

@router.delete("/{ws_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    ws_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    # Verify owner seat
    member = await service.workspace_repo.get_member(ws_id, current_user.id)
    if not member or member.role_name != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the Workspace owner can delete this instance.")
        
    await service.workspace_repo.update_workspace(ws_id, is_archived=True)

@router.post("/{ws_id}/switch", response_model=WorkspaceResponse)
async def switch_workspace(
    ws_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    try:
        ws = await service.switch_active_workspace(
            user_id=current_user.id,
            previous_ws_id=None,
            new_ws_id=ws_id
        )
        return ws
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.post("/{ws_id}/invite", response_model=InviteResponse)
async def invite_member(
    ws_id: str,
    payload: MemberInviteRequest,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    try:
        inv = await service.invite_team_member(
            ws_id=ws_id,
            requester_id=current_user.id,
            email=payload.email,
            role_name=payload.role_name
        )
        return inv
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/invitations/{invite_id}/accept", response_model=MemberResponse)
async def accept_invitation(
    invite_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    try:
        member = await service.accept_member_invitation(
            invite_id=invite_id,
            user_id=current_user.id,
            email=current_user.email
        )
        return member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/invitations/{invite_id}/decline", status_code=status.HTTP_204_NO_CONTENT)
async def decline_invitation(
    invite_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    inv = await service.invite_repo.get_invitation(invite_id)
    if not inv or inv.status != "pending":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active invitation not found.")
        
    await service.invite_repo.update_invitation_status(invite_id, "declined")

@router.get("/{ws_id}/members", response_model=List[MemberResponse])
async def list_members(
    ws_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    # Verify access seat
    member = await service.workspace_repo.get_member(ws_id, current_user.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access permissions to this workspace.")
        
    members = await service.workspace_repo.list_members(ws_id)
    return members

@router.delete("/{ws_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    ws_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    # Verify permissions: only owner/admin can remove seats, or self-remove
    member = await service.workspace_repo.get_member(ws_id, current_user.id)
    if not member:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access permissions.")
         
    if member.role_name not in ["owner", "administrator"] and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient admin seat permissions.")

    await service.workspace_repo.remove_member(ws_id, user_id)

@router.get("/{ws_id}/activity", response_model=List[ActivityResponse])
async def get_activity(
    ws_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    # Verify access seat
    member = await service.workspace_repo.get_member(ws_id, current_user.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access permissions.")
        
    activities = await service.activity_repo.list_activities(ws_id)
    return activities

@router.get("/{ws_id}/storage", response_model=StorageResponse)
async def get_storage(
    ws_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    member = await service.workspace_repo.get_member(ws_id, current_user.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access permissions.")
        
    storage = await service.workspace_repo.get_storage(ws_id)
    if not storage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage config not found.")
    return storage

@router.get("/{ws_id}/ai", response_model=AISettingsResponse)
async def get_ai_settings(
    ws_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    member = await service.workspace_repo.get_member(ws_id, current_user.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access permissions.")
        
    ai = await service.workspace_repo.get_ai_settings(ws_id)
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI config overrides not found.")
    return ai

@router.put("/{ws_id}/ai", response_model=AISettingsResponse)
async def update_ai_settings(
    ws_id: str,
    payload: WorkspaceAIUpdate,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    try:
        updated = await service.update_workspace_ai_settings(
            ws_id=ws_id,
            user_id=current_user.id,
            provider=payload.default_provider,
            model=payload.default_model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens
        )
        return updated
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

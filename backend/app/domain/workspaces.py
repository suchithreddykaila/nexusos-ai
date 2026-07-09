from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field

class Organization(BaseModel):
    id: str
    name: str
    billing_status: str = "active"
    created_at: datetime
    updated_at: datetime

class Workspace(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    color_theme: str = "slate"
    icon: str = "briefcase"
    timezone: str = "UTC"
    language: str = "en"
    is_archived: bool = False
    created_at: datetime
    updated_at: datetime

class WorkspaceMember(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    email: Optional[str] = None
    role_name: str  # owner, administrator, manager, editor, contributor, viewer, guest
    created_at: datetime
    updated_at: datetime

class WorkspaceInvitation(BaseModel):
    id: str
    workspace_id: str
    email: EmailStr
    role_name: str
    status: str = "pending"  # pending, accepted, declined, expired, revoked
    expires_at: datetime
    created_at: datetime

class WorkspaceAISettings(BaseModel):
    workspace_id: str
    default_provider: str = "ollama"
    default_model: str = "llama3.2:3b"
    temperature: float = 0.7
    max_tokens: int = 2048
    streaming: bool = True
    offline_mode: bool = True
    privacy_mode: bool = True
    updated_at: datetime

class WorkspaceStorage(BaseModel):
    workspace_id: str
    bytes_used: int = 0
    bytes_quota: int = 10 * 1024 * 1024 * 1024  # 10 GB default
    updated_at: datetime

class WorkspaceActivity(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    email: Optional[str] = None
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

class WorkspacePreferences(BaseModel):
    workspace_id: str
    enable_notifications: bool = True
    custom_settings: Dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime

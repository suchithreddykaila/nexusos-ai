from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field

class Permission(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class Role(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[Permission] = Field(default_factory=list)

class UserPreferences(BaseModel):
    user_id: str
    theme: str = "light"
    default_provider: str = "ollama"
    default_model: str = "llama3.2:3b"
    custom_settings: Dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    id: str
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    avatar_url: Optional[str] = None
    roles: List[Role] = Field(default_factory=list)
    preferences: Optional[UserPreferences] = None
    created_at: datetime
    updated_at: datetime

class UserSession(BaseModel):
    id: str
    user_id: str
    session_token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    expires_at: datetime
    created_at: datetime

class LoginHistory(BaseModel):
    id: str
    user_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str  # "success", "failed"
    failure_reason: Optional[str] = None
    created_at: datetime

class AuditLog(BaseModel):
    id: str
    user_id: Optional[str] = None
    action: str
    component: str
    ip_address: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

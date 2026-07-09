from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class DomainEvent(BaseModel):
    """
    Abstract Base Schema for all Domain Events.
    """
    event_id: str = Field(description="Unique UUID or tracking identifier for the event trace")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DocumentUploadedEvent(DomainEvent):
    document_id: str
    filename: str
    mime_type: str
    storage_path: str
    workspace_id: str
    uploaded_by: str

class DocumentParsedEvent(DomainEvent):
    document_id: str
    text_length: int
    metadata: Dict[str, Any]

class VectorIndexedEvent(DomainEvent):
    document_id: str
    collection_name: str
    vector_dimensions: int

class GraphLinkedEvent(DomainEvent):
    document_id: str
    source_entity: str
    target_entity: str
    relationship_type: str

class SystemAlertEvent(DomainEvent):
    component: str
    severity: str  # "INFO", "WARNING", "ERROR", "CRITICAL"
    message: str
    details: Optional[Dict[str, Any]] = None

# Identity and Authentication Domain Events
class UserRegisteredEvent(DomainEvent):
    user_id: str
    email: str

class UserLoggedInEvent(DomainEvent):
    user_id: str
    email: str
    session_id: str
    ip_address: Optional[str] = None

class UserLoggedOutEvent(DomainEvent):
    user_id: str
    session_id: str

class PasswordChangedEvent(DomainEvent):
    user_id: str

class ProfileUpdatedEvent(DomainEvent):
    user_id: str
    updates: Dict[str, Any]

class AvatarUploadedEvent(DomainEvent):
    user_id: str
    avatar_url: str

class SessionRevokedEvent(DomainEvent):
    user_id: str
    session_id: str
    revoked_by: str

class AuditLogCreatedEvent(DomainEvent):
    log_id: str
    user_id: Optional[str] = None
    action: str
    component: str

# Workspace and Organization Platform Events
class WorkspaceCreatedEvent(DomainEvent):
    workspace_id: str
    organization_id: str
    name: str

class WorkspaceUpdatedEvent(DomainEvent):
    workspace_id: str
    updates: Dict[str, Any]

class WorkspaceDeletedEvent(DomainEvent):
    workspace_id: str

class WorkspaceArchivedEvent(DomainEvent):
    workspace_id: str

class WorkspaceRestoredEvent(DomainEvent):
    workspace_id: str

class WorkspaceSwitchedEvent(DomainEvent):
    user_id: str
    previous_workspace_id: Optional[str]
    new_workspace_id: str

class MemberInvitedEvent(DomainEvent):
    invitation_id: str
    workspace_id: str
    email: str
    role_name: str

class InvitationAcceptedEvent(DomainEvent):
    invitation_id: str
    workspace_id: str
    user_id: str
    email: str

class InvitationDeclinedEvent(DomainEvent):
    invitation_id: str
    workspace_id: str
    email: str

class MemberRemovedEvent(DomainEvent):
    workspace_id: str
    user_id: str

class RoleChangedEvent(DomainEvent):
    workspace_id: str
    user_id: str
    new_role: str

class WorkspaceSettingsUpdatedEvent(DomainEvent):
    workspace_id: str
    updates: Dict[str, Any]

class WorkspaceAIUpdatedEvent(DomainEvent):
    workspace_id: str
    default_provider: str
    default_model: str

class WorkspacePreferenceUpdatedEvent(DomainEvent):
    workspace_id: str

class WorkspaceStorageUpdatedEvent(DomainEvent):
    workspace_id: str
    bytes_used: int


# ==========================================
# KNOWLEDGE ORGANIZATION AND PROCESSING EVENTS
# ==========================================

class ProjectCreatedEvent(DomainEvent):
    project_id: str
    workspace_id: str
    name: str

class CollectionCreatedEvent(DomainEvent):
    collection_id: str
    project_id: str
    workspace_id: str
    name: str

class FolderCreatedEvent(DomainEvent):
    folder_id: str
    collection_id: str
    workspace_id: str
    name: str

class FolderMovedEvent(DomainEvent):
    folder_id: str
    previous_parent_id: Optional[str]
    new_parent_id: Optional[str]

class AssetCreatedEvent(DomainEvent):
    asset_id: str
    workspace_id: str
    name: str
    asset_type: str

class AssetDeletedEvent(DomainEvent):
    asset_id: str
    workspace_id: str

class AssetStatusChangedEvent(DomainEvent):
    asset_id: str
    workspace_id: str
    old_status: str
    new_status: str
    processing_stage: str

class AssetMetadataUpdatedEvent(DomainEvent):
    asset_id: str
    workspace_id: str

class AssetVersionCreatedEvent(DomainEvent):
    asset_id: str
    version_number: int
    storage_path: str

class AssetVectorLinkedEvent(DomainEvent):
    asset_id: str
    vector_index_id: str

class AssetGraphLinkedEvent(DomainEvent):
    asset_id: str
    graph_node_id: str

class FavoriteAddedEvent(DomainEvent):
    user_id: str
    workspace_id: str
    target_id: str
    target_type: str

class RecycleItemCreatedEvent(DomainEvent):
    item_id: str
    workspace_id: str
    item_type: str

class RecycleItemRestoredEvent(DomainEvent):
    item_id: str
    workspace_id: str
    item_type: str



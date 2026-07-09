from abc import ABC, abstractmethod
from typing import Any, List, Optional
from app.domain.auth import User, UserPreferences, UserSession, AuditLog, LoginHistory
from app.domain.workspaces import (
    Workspace, 
    WorkspaceMember, 
    WorkspaceInvitation, 
    WorkspaceAISettings, 
    WorkspaceStorage, 
    WorkspaceActivity
)
from app.domain.knowledge import (
    Project,
    Collection,
    Folder,
    KnowledgeAsset,
    Tag,
    Favorite,
    Bookmark,
    AssetVersion,
    RecycleItem,
    TimelineEvent
)

class DocumentRepository(ABC):
    """
    Domain interface contract for Document entity persistence.
    """
    @abstractmethod
    async def add(self, document_data: Any) -> Any:
        pass

    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def list_all(self, workspace_id: Optional[str] = None) -> List[Any]:
        pass

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        pass


class IUserRepository(ABC):
    """
    Core Domain Repository contract for user accounts and preferences mapping.
    """
    @abstractmethod
    async def create_user(self, email: str, hashed_password: str) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_password_hash(self, user_id: str) -> Optional[str]:
        pass

    @abstractmethod
    async def update_password(self, user_id: str, new_hashed_password: str) -> bool:
        pass

    @abstractmethod
    async def update_profile(
        self, 
        user_id: str, 
        email: Optional[str] = None, 
        avatar_url: Optional[str] = None
    ) -> User:
        pass

    @abstractmethod
    async def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        pass

    @abstractmethod
    async def update_preferences(self, preferences: UserPreferences) -> UserPreferences:
        pass


class ISessionRepository(ABC):
    """
    Core Domain Repository contract for managing active device login sessions.
    """
    @abstractmethod
    async def create_session(
        self, 
        user_id: str, 
        session_token: str, 
        expires_at: Any, 
        ip_address: Optional[str] = None, 
        user_agent: Optional[str] = None
    ) -> UserSession:
        pass

    @abstractmethod
    async def get_session(self, session_token: str) -> Optional[UserSession]:
        pass

    @abstractmethod
    async def list_user_sessions(self, user_id: str) -> List[UserSession]:
        pass

    @abstractmethod
    async def revoke_session(self, session_id: str) -> bool:
        pass

    @abstractmethod
    async def revoke_all_sessions(self, user_id: str) -> bool:
        pass


class IAuditLogRepository(ABC):
    """
    Core Domain Repository contract for recording security audits logs.
    """
    @abstractmethod
    async def create_audit_log(
        self, 
        user_id: Optional[str], 
        action: str, 
        component: str, 
        ip_address: Optional[str], 
        details: dict
    ) -> AuditLog:
        pass

    @abstractmethod
    async def list_audit_logs(self, user_id: Optional[str] = None) -> List[AuditLog]:
        pass


class ILoginHistoryRepository(ABC):
    """
    Core Domain Repository contract for keeping history logs of credentials logins.
    """
    @abstractmethod
    async def record_login_attempt(
        self, 
        user_id: str, 
        status: str, 
        failure_reason: Optional[str], 
        ip_address: Optional[str], 
        user_agent: Optional[str]
    ) -> LoginHistory:
        pass

    @abstractmethod
    async def list_login_history(self, user_id: str) -> List[LoginHistory]:
        pass


class IWorkspaceRepository(ABC):
    """
    Core Domain Repository contract for Workspace and multi-tenant billing structures.
    """
    @abstractmethod
    async def create_workspace(
        self, 
        org_id: str, 
        name: str, 
        description: Optional[str] = None
    ) -> Workspace:
        pass

    @abstractmethod
    async def get_workspace(self, ws_id: str) -> Optional[Workspace]:
        pass

    @abstractmethod
    async def update_workspace(
        self, 
        ws_id: str, 
        name: Optional[str] = None, 
        description: Optional[str] = None,
        logo_url: Optional[str] = None,
        color_theme: Optional[str] = None,
        is_archived: Optional[bool] = None
    ) -> Workspace:
        pass

    @abstractmethod
    async def list_workspaces_for_user(self, user_id: str) -> List[Workspace]:
        pass

    @abstractmethod
    async def add_member(self, ws_id: str, user_id: str, role_name: str) -> WorkspaceMember:
        pass

    @abstractmethod
    async def get_member(self, ws_id: str, user_id: str) -> Optional[WorkspaceMember]:
        pass

    @abstractmethod
    async def list_members(self, ws_id: str) -> List[WorkspaceMember]:
        pass

    @abstractmethod
    async def update_member_role(self, ws_id: str, member_user_id: str, role_name: str) -> bool:
        pass

    @abstractmethod
    async def remove_member(self, ws_id: str, member_user_id: str) -> bool:
        pass

    @abstractmethod
    async def get_ai_settings(self, ws_id: str) -> Optional[WorkspaceAISettings]:
        pass

    @abstractmethod
    async def update_ai_settings(self, settings: WorkspaceAISettings) -> WorkspaceAISettings:
        pass

    @abstractmethod
    async def get_storage(self, ws_id: str) -> Optional[WorkspaceStorage]:
        pass

    @abstractmethod
    async def update_storage(self, ws_id: str, bytes_used: int) -> WorkspaceStorage:
        pass


class IWorkspaceInvitationRepository(ABC):
    """
    Core Domain Repository contract for managing member seating invitations.
    """
    @abstractmethod
    async def create_invitation(
        self, 
        ws_id: str, 
        email: str, 
        role_name: str, 
        expires_at: Any
    ) -> WorkspaceInvitation:
        pass

    @abstractmethod
    async def get_invitation(self, invite_id: str) -> Optional[WorkspaceInvitation]:
        pass

    @abstractmethod
    async def update_invitation_status(self, invite_id: str, status: str) -> bool:
        pass

    @abstractmethod
    async def list_invitations(self, ws_id: str) -> List[WorkspaceInvitation]:
        pass


class IWorkspaceActivityRepository(ABC):
    """
    Core Domain Repository contract for recording user events logs inside active workspaces.
    """
    @abstractmethod
    async def record_activity(
        self, 
        ws_id: str, 
        user_id: str, 
        action: str, 
        details: dict
    ) -> WorkspaceActivity:
        pass

    @abstractmethod
    async def list_activities(self, ws_id: str, limit: int = 50) -> List[WorkspaceActivity]:
        pass


class IKnowledgeRepository(ABC):
    """
    Core Domain Repository contract for projects, collections, and recursive folders.
    """
    @abstractmethod
    async def create_project(
        self, 
        ws_id: str, 
        name: str, 
        description: Optional[str] = None,
        color: str = "slate",
        icon: str = "folder"
    ) -> Project:
        pass

    @abstractmethod
    async def get_project(self, project_id: str) -> Optional[Project]:
        pass

    @abstractmethod
    async def list_projects(self, ws_id: str) -> List[Project]:
        pass

    @abstractmethod
    async def update_project(
        self, 
        project_id: str, 
        name: Optional[str] = None, 
        description: Optional[str] = None,
        color: Optional[str] = None,
        is_archived: Optional[bool] = None
    ) -> Project:
        pass

    @abstractmethod
    async def create_collection(
        self, 
        project_id: str, 
        ws_id: str, 
        name: str, 
        description: Optional[str] = None,
        color: str = "slate",
        icon: str = "layers"
    ) -> Collection:
        pass

    @abstractmethod
    async def get_collection(self, col_id: str) -> Optional[Collection]:
        pass

    @abstractmethod
    async def list_collections(self, project_id: str) -> List[Collection]:
        pass

    @abstractmethod
    async def update_collection(
        self, 
        col_id: str, 
        name: Optional[str] = None, 
        description: Optional[str] = None,
        is_archived: Optional[bool] = None
    ) -> Collection:
        pass

    @abstractmethod
    async def create_folder(
        self, 
        col_id: str, 
        parent_id: Optional[str], 
        ws_id: str, 
        name: str,
        color: str = "slate",
        icon: str = "folder"
    ) -> Folder:
        pass

    @abstractmethod
    async def get_folder(self, folder_id: str) -> Optional[Folder]:
        pass

    @abstractmethod
    async def list_folders(self, col_id: str, parent_id: Optional[str] = None) -> List[Folder]:
        pass

    @abstractmethod
    async def update_folder(
        self, 
        folder_id: str, 
        name: Optional[str] = None, 
        parent_id: Optional[str] = None,
        is_archived: Optional[bool] = None
    ) -> Folder:
        pass


class IAssetRepository(ABC):
    """
    Core Domain Repository contract for physical file assets and indexing tags.
    """
    @abstractmethod
    async def create_asset(
        self, 
        ws_id: str, 
        folder_id: Optional[str], 
        col_id: Optional[str], 
        proj_id: Optional[str], 
        name: str, 
        asset_type: str, 
        details: dict,
        status: str = "pending",
        processing_stage: str = "pending",
        checksum: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> KnowledgeAsset:
        pass

    @abstractmethod
    async def get_asset(self, asset_id: str) -> Optional[KnowledgeAsset]:
        pass

    @abstractmethod
    async def list_assets(
        self, 
        ws_id: str, 
        folder_id: Optional[str] = None, 
        asset_type: Optional[str] = None
    ) -> List[KnowledgeAsset]:
        pass

    @abstractmethod
    async def update_asset(
        self, 
        asset_id: str, 
        name: Optional[str] = None, 
        folder_id: Optional[str] = None, 
        details: Optional[dict] = None,
        status: Optional[str] = None,
        processing_stage: Optional[str] = None,
        checksum: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> KnowledgeAsset:
        pass

    @abstractmethod
    async def delete_asset(self, asset_id: str) -> bool:
        pass

    @abstractmethod
    async def add_tag(self, ws_id: str, name: str, color: str) -> Tag:
        pass

    @abstractmethod
    async def list_tags(self, ws_id: str) -> List[Tag]:
        pass

    @abstractmethod
    async def apply_tag_to_asset(self, asset_id: str, tag_id: str) -> bool:
        pass

    @abstractmethod
    async def list_asset_tags(self, asset_id: str) -> List[Tag]:
        pass


class IFavoriteRepository(ABC):
    """
    Core Domain Repository contract for user workspace bookmarks and favorites.
    """
    @abstractmethod
    async def add_favorite(
        self, 
        user_id: str, 
        ws_id: str, 
        target_id: str, 
        target_type: str
    ) -> Favorite:
        pass

    @abstractmethod
    async def list_favorites(self, user_id: str, ws_id: str) -> List[Favorite]:
        pass

    @abstractmethod
    async def remove_favorite(self, user_id: str, ws_id: str, target_id: str) -> bool:
        pass


class IRecycleBinRepository(ABC):
    """
    Core Domain Repository contract for trashing elements soft deletes.
    """
    @abstractmethod
    async def send_to_recycle_bin(
        self, 
        ws_id: str, 
        item_id: str, 
        item_type: str, 
        original_parent_id: Optional[str], 
        deleted_by: str
    ) -> RecycleItem:
        pass

    @abstractmethod
    async def list_recycle_bin(self, ws_id: str) -> List[RecycleItem]:
        pass

    @abstractmethod
    async def get_recycle_item(self, item_id: str) -> Optional[RecycleItem]:
        pass

    @abstractmethod
    async def remove_from_recycle_bin(self, item_id: str) -> bool:
        pass


class ITimelineRepository(ABC):
    """
    Core Domain Repository contract for cataloguing events sequences.
    """
    @abstractmethod
    async def record_event(
        self, 
        ws_id: str, 
        target_id: str, 
        target_type: str, 
        user_id: str, 
        action: str
    ) -> TimelineEvent:
        pass

    @abstractmethod
    async def list_events(self, ws_id: str, limit: int = 50) -> List[TimelineEvent]:
        pass

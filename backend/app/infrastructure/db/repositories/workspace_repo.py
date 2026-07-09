import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.workspaces import (
    Workspace, 
    WorkspaceMember, 
    WorkspaceInvitation, 
    WorkspaceAISettings, 
    WorkspaceStorage, 
    WorkspaceActivity
)
from app.domain.repositories import (
    IWorkspaceRepository, 
    IWorkspaceInvitationRepository, 
    IWorkspaceActivityRepository
)
from app.infrastructure.db.models import (
    WorkspaceDB, 
    WorkspaceMemberDB, 
    WorkspaceInvitationDB, 
    WorkspaceAISettingsDB, 
    WorkspaceStorageDB, 
    WorkspaceActivityDB, 
    WorkspacePreferencesDB
)

def map_workspace_db_to_domain(db_ws: WorkspaceDB) -> Workspace:
    return Workspace(
        id=db_ws.id,
        organization_id=db_ws.organization_id,
        name=db_ws.name,
        description=db_ws.description,
        logo_url=db_ws.logo_url,
        color_theme=db_ws.color_theme,
        icon=db_ws.icon,
        timezone=db_ws.timezone,
        language=db_ws.language,
        is_archived=db_ws.is_archived,
        created_at=db_ws.created_at,
        updated_at=db_ws.updated_at
    )

def map_member_db_to_domain(db_m: WorkspaceMemberDB) -> WorkspaceMember:
    return WorkspaceMember(
        id=db_m.id,
        workspace_id=db_m.workspace_id,
        user_id=db_m.user_id,
        email=db_m.user.email if db_m.user else None,
        role_name=db_m.role_name,
        created_at=db_m.created_at,
        updated_at=db_m.updated_at
    )

class SQLWorkspaceRepository(IWorkspaceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_workspace(
        self, 
        org_id: str, 
        name: str, 
        description: Optional[str] = None
    ) -> Workspace:
        db_ws = WorkspaceDB(
            id=str(uuid.uuid4()),
            organization_id=org_id,
            name=name,
            description=description,
            color_theme="slate",
            icon="briefcase",
            timezone="UTC",
            language="en"
        )
        self.session.add(db_ws)
        await self.session.flush()

        # Seed AI default settings
        ai_settings = WorkspaceAISettingsDB(
            workspace_id=db_ws.id,
            default_provider="ollama",
            default_model="llama3.2:3b",
            temperature=0.7,
            max_tokens=2048,
            streaming=True,
            offline_mode=True,
            privacy_mode=True
        )
        self.session.add(ai_settings)

        # Seed storage quotas trackers
        storage = WorkspaceStorageDB(
            workspace_id=db_ws.id,
            bytes_used=0,
            bytes_quota=10 * 1024 * 1024 * 1024  # 10 GB
        )
        self.session.add(storage)

        # Seed default workspace preferences
        prefs = WorkspacePreferencesDB(
            workspace_id=db_ws.id,
            enable_notifications=True,
            custom_settings={}
        )
        self.session.add(prefs)
        await self.session.flush()

        return map_workspace_db_to_domain(db_ws)

    async def get_workspace(self, ws_id: str) -> Optional[Workspace]:
        result = await self.session.execute(
            select(WorkspaceDB).where(WorkspaceDB.id == ws_id, WorkspaceDB.is_archived == False)
        )
        db_ws = result.scalar_one_or_none()
        if db_ws:
            return map_workspace_db_to_domain(db_ws)
        return None

    async def update_workspace(
        self, 
        ws_id: str, 
        name: Optional[str] = None, 
        description: Optional[str] = None,
        logo_url: Optional[str] = None,
        color_theme: Optional[str] = None,
        is_archived: Optional[bool] = None
    ) -> Workspace:
        values = {"updated_at": datetime.now(timezone.utc)}
        if name:
            values["name"] = name
        if description:
            values["description"] = description
        if logo_url:
            values["logo_url"] = logo_url
        if color_theme:
            values["color_theme"] = color_theme
        if is_archived is not None:
            values["is_archived"] = is_archived

        await self.session.execute(
            update(WorkspaceDB)
            .where(WorkspaceDB.id == ws_id)
            .values(**values)
        )
        result = await self.session.execute(select(WorkspaceDB).where(WorkspaceDB.id == ws_id))
        db_ws = result.scalar_one()
        return map_workspace_db_to_domain(db_ws)

    async def list_workspaces_for_user(self, user_id: str) -> List[Workspace]:
        # Retrieve all workspaces where user is active in workspace_members
        result = await self.session.execute(
            select(WorkspaceDB)
            .join(WorkspaceMemberDB, WorkspaceDB.id == WorkspaceMemberDB.workspace_id)
            .where(WorkspaceMemberDB.user_id == user_id, WorkspaceDB.is_archived == False)
            .order_by(WorkspaceDB.created_at.desc())
        )
        db_workspaces = result.scalars().all()
        return [map_workspace_db_to_domain(ws) for ws in db_workspaces]

    async def add_member(self, ws_id: str, user_id: str, role_name: str) -> WorkspaceMember:
        db_m = WorkspaceMemberDB(
            id=str(uuid.uuid4()),
            workspace_id=ws_id,
            user_id=user_id,
            role_name=role_name
        )
        self.session.add(db_m)
        await self.session.flush()

        # Fetch with user relation loaded
        result = await self.session.execute(
            select(WorkspaceMemberDB).where(WorkspaceMemberDB.id == db_m.id)
        )
        db_m = result.scalar_one()
        return map_member_db_to_domain(db_m)

    async def get_member(self, ws_id: str, user_id: str) -> Optional[WorkspaceMember]:
        result = await self.session.execute(
            select(WorkspaceMemberDB)
            .where(WorkspaceMemberDB.workspace_id == ws_id, WorkspaceMemberDB.user_id == user_id)
        )
        db_m = result.scalar_one_or_none()
        if db_m:
            return map_member_db_to_domain(db_m)
        return None

    async def list_members(self, ws_id: str) -> List[WorkspaceMember]:
        result = await self.session.execute(
            select(WorkspaceMemberDB)
            .where(WorkspaceMemberDB.workspace_id == ws_id)
            .order_by(WorkspaceMemberDB.created_at.asc())
        )
        db_members = result.scalars().all()
        return [map_member_db_to_domain(m) for m in db_members]

    async def update_member_role(self, ws_id: str, member_user_id: str, role_name: str) -> bool:
        await self.session.execute(
            update(WorkspaceMemberDB)
            .where(WorkspaceMemberDB.workspace_id == ws_id, WorkspaceMemberDB.user_id == member_user_id)
            .values(role_name=role_name, updated_at=datetime.now(timezone.utc))
        )
        return True

    async def remove_member(self, ws_id: str, member_user_id: str) -> bool:
        await self.session.execute(
            delete(WorkspaceMemberDB)
            .where(WorkspaceMemberDB.workspace_id == ws_id, WorkspaceMemberDB.user_id == member_user_id)
        )
        return True

    async def get_ai_settings(self, ws_id: str) -> Optional[WorkspaceAISettings]:
        result = await self.session.execute(
            select(WorkspaceAISettingsDB).where(WorkspaceAISettingsDB.workspace_id == ws_id)
        )
        db_ai = result.scalar_one_or_none()
        if db_ai:
            return WorkspaceAISettings(
                workspace_id=db_ai.workspace_id,
                default_provider=db_ai.default_provider,
                default_model=db_ai.default_model,
                temperature=db_ai.temperature,
                max_tokens=db_ai.max_tokens,
                streaming=db_ai.streaming,
                offline_mode=db_ai.offline_mode,
                privacy_mode=db_ai.privacy_mode,
                updated_at=db_ai.updated_at
            )
        return None

    async def update_ai_settings(self, settings: WorkspaceAISettings) -> WorkspaceAISettings:
        await self.session.execute(
            update(WorkspaceAISettingsDB)
            .where(WorkspaceAISettingsDB.workspace_id == settings.workspace_id)
            .values(
                default_provider=settings.default_provider,
                default_model=settings.default_model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                streaming=settings.streaming,
                offline_mode=settings.offline_mode,
                privacy_mode=settings.privacy_mode,
                updated_at=datetime.now(timezone.utc)
            )
        )
        return settings

    async def get_storage(self, ws_id: str) -> Optional[WorkspaceStorage]:
        result = await self.session.execute(
            select(WorkspaceStorageDB).where(WorkspaceStorageDB.workspace_id == ws_id)
        )
        db_st = result.scalar_one_or_none()
        if db_st:
            return WorkspaceStorage(
                workspace_id=db_st.workspace_id,
                bytes_used=db_st.bytes_used,
                bytes_quota=db_st.bytes_quota,
                updated_at=db_st.updated_at
            )
        return None

    async def update_storage(self, ws_id: str, bytes_used: int) -> WorkspaceStorage:
        await self.session.execute(
            update(WorkspaceStorageDB)
            .where(WorkspaceStorageDB.workspace_id == ws_id)
            .values(bytes_used=bytes_used, updated_at=datetime.now(timezone.utc))
        )
        result = await self.session.execute(
            select(WorkspaceStorageDB).where(WorkspaceStorageDB.workspace_id == ws_id)
        )
        db_st = result.scalar_one()
        return WorkspaceStorage(
            workspace_id=db_st.workspace_id,
            bytes_used=db_st.bytes_used,
            bytes_quota=db_st.bytes_quota,
            updated_at=db_st.updated_at
        )


class SQLWorkspaceInvitationRepository(IWorkspaceInvitationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_invitation(
        self, 
        ws_id: str, 
        email: str, 
        role_name: str, 
        expires_at: datetime
    ) -> WorkspaceInvitation:
        db_inv = WorkspaceInvitationDB(
            id=str(uuid.uuid4()),
            workspace_id=ws_id,
            email=email,
            role_name=role_name,
            status="pending",
            expires_at=expires_at
        )
        self.session.add(db_inv)
        await self.session.flush()
        return WorkspaceInvitation(
            id=db_inv.id,
            workspace_id=db_inv.workspace_id,
            email=db_inv.email,
            role_name=db_inv.role_name,
            status=db_inv.status,
            expires_at=db_inv.expires_at,
            created_at=db_inv.created_at
        )

    async def get_invitation(self, invite_id: str) -> Optional[WorkspaceInvitation]:
        result = await self.session.execute(
            select(WorkspaceInvitationDB).where(WorkspaceInvitationDB.id == invite_id)
        )
        db_inv = result.scalar_one_or_none()
        if db_inv:
            return WorkspaceInvitation(
                id=db_inv.id,
                workspace_id=db_inv.workspace_id,
                email=db_inv.email,
                role_name=db_inv.role_name,
                status=db_inv.status,
                expires_at=db_inv.expires_at,
                created_at=db_inv.created_at
            )
        return None

    async def update_invitation_status(self, invite_id: str, status: str) -> bool:
        await self.session.execute(
            update(WorkspaceInvitationDB)
            .where(WorkspaceInvitationDB.id == invite_id)
            .values(status=status)
        )
        return True

    async def list_invitations(self, ws_id: str) -> List[WorkspaceInvitation]:
        result = await self.session.execute(
            select(WorkspaceInvitationDB)
            .where(WorkspaceInvitationDB.workspace_id == ws_id, WorkspaceInvitationDB.status == "pending")
            .order_by(WorkspaceInvitationDB.created_at.desc())
        )
        db_invs = result.scalars().all()
        return [
            WorkspaceInvitation(
                id=i.id,
                workspace_id=i.workspace_id,
                email=i.email,
                role_name=i.role_name,
                status=i.status,
                expires_at=i.expires_at,
                created_at=i.created_at
            ) for i in db_invs
        ]


class SQLWorkspaceActivityRepository(IWorkspaceActivityRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_activity(
        self, 
        ws_id: str, 
        user_id: str, 
        action: str, 
        details: dict
    ) -> WorkspaceActivity:
        db_act = WorkspaceActivityDB(
            id=str(uuid.uuid4()),
            workspace_id=ws_id,
            user_id=user_id,
            action=action,
            details=details
        )
        self.session.add(db_act)
        await self.session.flush()
        
        # Load user relation
        result = await self.session.execute(
            select(WorkspaceActivityDB).where(WorkspaceActivityDB.id == db_act.id)
        )
        db_act = result.scalar_one()
        return WorkspaceActivity(
            id=db_act.id,
            workspace_id=db_act.workspace_id,
            user_id=db_act.user_id,
            email=db_act.user.email if db_act.user else None,
            action=db_act.action,
            details=db_act.details,
            created_at=db_act.created_at
        )

    async def list_activities(self, ws_id: str, limit: int = 50) -> List[WorkspaceActivity]:
        result = await self.session.execute(
            select(WorkspaceActivityDB)
            .where(WorkspaceActivityDB.workspace_id == ws_id)
            .order_by(WorkspaceActivityDB.created_at.desc())
            .limit(limit)
        )
        db_acts = result.scalars().all()
        return [
            WorkspaceActivity(
                id=a.id,
                workspace_id=a.workspace_id,
                user_id=a.user_id,
                email=a.user.email if a.user else None,
                action=a.action,
                details=a.details,
                created_at=a.created_at
            ) for a in db_acts
        ]

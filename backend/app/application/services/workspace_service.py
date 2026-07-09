import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from app.domain.workspaces import Workspace, WorkspaceMember, WorkspaceInvitation, WorkspaceAISettings, WorkspaceStorage, WorkspaceActivity
from app.domain.repositories import IWorkspaceRepository, IWorkspaceInvitationRepository, IWorkspaceActivityRepository, IUserRepository
from app.domain.events import (
    WorkspaceCreatedEvent,
    WorkspaceUpdatedEvent,
    WorkspaceDeletedEvent,
    WorkspaceArchivedEvent,
    WorkspaceRestoredEvent,
    WorkspaceSwitchedEvent,
    MemberInvitedEvent,
    InvitationAcceptedEvent,
    InvitationDeclinedEvent,
    MemberRemovedEvent,
    RoleChangedEvent,
    WorkspaceAIUpdatedEvent,
    WorkspaceStorageUpdatedEvent
)
from app.infrastructure.events.dispatcher import event_bus
from app.infrastructure.db.models import OrganizationDB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

class WorkspaceService:
    def __init__(
        self,
        db_session: AsyncSession,
        workspace_repo: IWorkspaceRepository,
        invite_repo: IWorkspaceInvitationRepository,
        activity_repo: IWorkspaceActivityRepository,
        user_repo: IUserRepository
    ):
        self.db = db_session
        self.workspace_repo = workspace_repo
        self.invite_repo = invite_repo
        self.activity_repo = activity_repo
        self.user_repo = user_repo

    async def get_or_create_default_org(self, user_email: str) -> str:
        # Check if an organization exists in the DB
        result = await self.db.execute(select(OrganizationDB).limit(1))
        db_org = result.scalar_one_or_none()
        if db_org:
            return db_org.id

        # Seed initial Personal Organization
        new_org = OrganizationDB(
            id=str(uuid.uuid4()),
            name=f"Personal Org ({user_email})",
            billing_status="active"
        )
        self.db.add(new_org)
        await self.db.flush()
        return new_org.id

    async def create_user_workspace(self, user_id: str, user_email: str, name: str, description: Optional[str] = None) -> Workspace:
        org_id = await self.get_or_create_default_org(user_email)
        
        # Create workspace in repository
        workspace = await self.workspace_repo.create_workspace(
            org_id=org_id,
            name=name,
            description=description
        )

        # Add the creator as Owner
        await self.workspace_repo.add_member(
            ws_id=workspace.id,
            user_id=user_id,
            role_name="owner"
        )

        # Record activity
        await self.activity_repo.record_activity(
            ws_id=workspace.id,
            user_id=user_id,
            action="WORKSPACE_CREATION",
            details={"name": name}
        )

        # Dispatch event
        await event_bus.publish(
            WorkspaceCreatedEvent(
                event_id=str(uuid.uuid4()),
                workspace_id=workspace.id,
                organization_id=org_id,
                name=name
            )
        )

        return workspace

    async def switch_active_workspace(self, user_id: str, previous_ws_id: Optional[str], new_ws_id: str) -> Workspace:
        # Validate member access
        member = await self.workspace_repo.get_member(new_ws_id, user_id)
        if not member:
            raise ValueError("Insufficient access permissions. You are not a member of this workspace.")

        workspace = await self.workspace_repo.get_workspace(new_ws_id)
        if not workspace:
            raise ValueError("Target workspace is archived or not found.")

        # Record activity
        await self.activity_repo.record_activity(
            ws_id=new_ws_id,
            user_id=user_id,
            action="WORKSPACE_SWITCH",
            details={"previous_workspace_id": previous_ws_id}
        )

        # Dispatch switch event
        await event_bus.publish(
            WorkspaceSwitchedEvent(
                event_id=str(uuid.uuid4()),
                user_id=user_id,
                previous_workspace_id=previous_ws_id,
                new_workspace_id=new_ws_id
            )
        )

        return workspace

    async def invite_team_member(self, ws_id: str, requester_id: str, email: str, role_name: str) -> WorkspaceInvitation:
        # Verify requester is owner or administrator
        requester_seat = await self.workspace_repo.get_member(ws_id, requester_id)
        if not requester_seat or requester_seat.role_name not in ["owner", "administrator"]:
            raise PermissionError("Insufficient workspace permissions to invite members.")

        # Create invitation
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        invitation = await self.invite_repo.create_invitation(
            ws_id=ws_id,
            email=email,
            role_name=role_name,
            expires_at=expires_at
        )

        # Record activity
        await self.activity_repo.record_activity(
            ws_id=ws_id,
            user_id=requester_id,
            action="MEMBER_INVITED",
            details={"email": email, "role": role_name}
        )

        # Dispatch event
        await event_bus.publish(
            MemberInvitedEvent(
                event_id=str(uuid.uuid4()),
                invitation_id=invitation.id,
                workspace_id=ws_id,
                email=email,
                role_name=role_name
            )
        )

        return invitation

    async def accept_member_invitation(self, invite_id: str, user_id: str, email: str) -> WorkspaceMember:
        invitation = await self.invite_repo.get_invitation(invite_id)
        if not invitation or invitation.status != "pending":
            raise ValueError("Invitation link is invalid or already processed.")

        if invitation.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            await self.invite_repo.update_invitation_status(invite_id, "expired")
            raise ValueError("Invitation link has expired.")

        # Accept seat, add user as member
        member = await self.workspace_repo.add_member(
            ws_id=invitation.workspace_id,
            user_id=user_id,
            role_name=invitation.role_name
        )

        # Update invitation
        await self.invite_repo.update_invitation_status(invite_id, "accepted")

        # Record activity
        await self.activity_repo.record_activity(
            ws_id=invitation.workspace_id,
            user_id=user_id,
            action="INVITATION_ACCEPTED",
            details={"invite_id": invite_id}
        )

        # Dispatch event
        await event_bus.publish(
            InvitationAcceptedEvent(
                event_id=str(uuid.uuid4()),
                invitation_id=invite_id,
                workspace_id=invitation.workspace_id,
                user_id=user_id,
                email=email
            )
        )

        return member

    async def update_workspace_ai_settings(
        self, 
        ws_id: str, 
        user_id: str, 
        provider: str, 
        model: str, 
        temperature: float, 
        max_tokens: int
    ) -> WorkspaceAISettings:
        # Verify access
        seat = await self.workspace_repo.get_member(ws_id, user_id)
        if not seat or seat.role_name not in ["owner", "administrator", "manager"]:
            raise PermissionError("Insufficient permissions to update workspace AI configurations.")

        settings = WorkspaceAISettings(
            workspace_id=ws_id,
            default_provider=provider,
            default_model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True,
            offline_mode=True,
            privacy_mode=True,
            updated_at=datetime.now(timezone.utc)
        )

        updated = await self.workspace_repo.update_ai_settings(settings)

        # Record activity
        await self.activity_repo.record_activity(
            ws_id=ws_id,
            user_id=user_id,
            action="AI_SETTINGS_UPDATE",
            details={"provider": provider, "model": model}
        )

        # Dispatch event
        await event_bus.publish(
            WorkspaceAIUpdatedEvent(
                event_id=str(uuid.uuid4()),
                workspace_id=ws_id,
                default_provider=provider,
                default_model=model
            )
        )

        return updated

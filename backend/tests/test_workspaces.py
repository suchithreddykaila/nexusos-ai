import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta

# Add backend root directory to path for app imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.domain.workspaces import Workspace, WorkspaceMember, WorkspaceInvitation, WorkspaceAISettings
from app.application.services.workspace_service import WorkspaceService

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def mock_ws_repo():
    repo = MagicMock()
    repo.create_workspace = AsyncMock()
    repo.get_workspace = AsyncMock()
    repo.update_workspace = AsyncMock()
    repo.list_workspaces_for_user = AsyncMock()
    repo.add_member = AsyncMock()
    repo.get_member = AsyncMock()
    repo.list_members = AsyncMock()
    repo.update_member_role = AsyncMock()
    repo.remove_member = AsyncMock()
    repo.get_ai_settings = AsyncMock()
    repo.update_ai_settings = AsyncMock()
    repo.get_storage = AsyncMock()
    repo.update_storage = AsyncMock()
    return repo

@pytest.fixture
def mock_invite_repo():
    repo = MagicMock()
    repo.create_invitation = AsyncMock()
    repo.get_invitation = AsyncMock()
    repo.update_invitation_status = AsyncMock()
    repo.list_invitations = AsyncMock()
    return repo

@pytest.fixture
def mock_act_repo():
    repo = MagicMock()
    repo.record_activity = AsyncMock()
    repo.list_activities = AsyncMock()
    return repo

@pytest.fixture
def mock_user_repo():
    return MagicMock()

@pytest.fixture
def ws_service(mock_db_session, mock_ws_repo, mock_invite_repo, mock_act_repo, mock_user_repo):
    svc = WorkspaceService(
        db_session=mock_db_session,
        workspace_repo=mock_ws_repo,
        invite_repo=mock_invite_repo,
        activity_repo=mock_act_repo,
        user_repo=mock_user_repo
    )
    svc.get_or_create_default_org = AsyncMock(return_value="org_123")
    return svc

@pytest.mark.asyncio
async def test_create_user_workspace_success(ws_service, mock_ws_repo, mock_act_repo):
    user_id = "user_abc"
    user_email = "test@example.com"
    ws_name = "Department A"
    
    mock_ws_repo.create_workspace.return_value = Workspace(
        id="ws_789",
        organization_id="org_123",
        name=ws_name,
        color_theme="slate",
        icon="briefcase",
        timezone="UTC",
        language="en",
        is_archived=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    ws = await ws_service.create_user_workspace(user_id, user_email, ws_name)
    
    assert ws.id == "ws_789"
    assert ws.name == ws_name
    mock_ws_repo.create_workspace.assert_called_once_with(org_id="org_123", name=ws_name, description=None)
    mock_ws_repo.add_member.assert_called_once_with(ws_id="ws_789", user_id=user_id, role_name="owner")
    mock_act_repo.record_activity.assert_called_once()

@pytest.mark.asyncio
async def test_invite_team_member_success(ws_service, mock_ws_repo, mock_invite_repo):
    ws_id = "ws_789"
    requester_id = "owner_123"
    invitee_email = "colleague@example.com"
    
    mock_ws_repo.get_member.return_value = WorkspaceMember(
        id="m_1",
        workspace_id=ws_id,
        user_id=requester_id,
        role_name="owner",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    mock_invite_repo.create_invitation.return_value = WorkspaceInvitation(
        id="invite_999",
        workspace_id=ws_id,
        email=invitee_email,
        role_name="editor",
        status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        created_at=datetime.now(timezone.utc)
    )
    
    inv = await ws_service.invite_team_member(ws_id, requester_id, invitee_email, "editor")
    
    assert inv.id == "invite_999"
    assert inv.email == invitee_email
    mock_invite_repo.create_invitation.assert_called_once()

@pytest.mark.asyncio
async def test_invite_team_member_insufficient_permissions(ws_service, mock_ws_repo):
    ws_id = "ws_789"
    requester_id = "viewer_123"
    
    mock_ws_repo.get_member.return_value = WorkspaceMember(
        id="m_1",
        workspace_id=ws_id,
        user_id=requester_id,
        role_name="viewer",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    with pytest.raises(PermissionError, match="Insufficient workspace permissions"):
        await ws_service.invite_team_member(ws_id, requester_id, "colleague@example.com", "editor")

@pytest.mark.asyncio
async def test_accept_invitation_success(ws_service, mock_invite_repo, mock_ws_repo):
    invite_id = "invite_999"
    user_id = "new_user_123"
    email = "colleague@example.com"
    
    mock_invite_repo.get_invitation.return_value = WorkspaceInvitation(
        id=invite_id,
        workspace_id="ws_789",
        email=email,
        role_name="editor",
        status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        created_at=datetime.now(timezone.utc)
    )
    
    mock_ws_repo.add_member.return_value = WorkspaceMember(
        id="m_2",
        workspace_id="ws_789",
        user_id=user_id,
        role_name="editor",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    member = await ws_service.accept_member_invitation(invite_id, user_id, email)
    
    assert member.role_name == "editor"
    mock_invite_repo.update_invitation_status.assert_called_once_with(invite_id, "accepted")
    mock_ws_repo.add_member.assert_called_once()

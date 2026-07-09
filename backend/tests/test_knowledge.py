import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

# Add path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.domain.knowledge import Project, Collection, Folder, KnowledgeAsset, RecycleItem
from app.application.services.knowledge_service import KnowledgeService

@pytest.fixture
def mock_knowledge_repo():
    repo = MagicMock()
    repo.create_project = AsyncMock()
    repo.get_project = AsyncMock()
    repo.list_projects = AsyncMock()
    repo.update_project = AsyncMock()
    repo.create_collection = AsyncMock()
    repo.get_collection = AsyncMock()
    repo.list_collections = AsyncMock()
    repo.update_collection = AsyncMock()
    repo.create_folder = AsyncMock()
    repo.get_folder = AsyncMock()
    repo.list_folders = AsyncMock()
    repo.update_folder = AsyncMock()
    return repo

@pytest.fixture
def mock_asset_repo():
    repo = MagicMock()
    repo.create_asset = AsyncMock()
    repo.get_asset = AsyncMock()
    repo.list_assets = AsyncMock()
    repo.update_asset = AsyncMock()
    repo.delete_asset = AsyncMock()
    return repo

@pytest.fixture
def mock_fav_repo():
    return MagicMock()

@pytest.fixture
def mock_recycle_repo():
    repo = MagicMock()
    repo.send_to_recycle_bin = AsyncMock()
    repo.list_recycle_bin = AsyncMock()
    repo.get_recycle_item = AsyncMock()
    repo.remove_from_recycle_bin = AsyncMock()
    return repo

@pytest.fixture
def mock_timeline_repo():
    repo = MagicMock()
    repo.record_event = AsyncMock()
    return repo

@pytest.fixture
def knowledge_service(
    mock_knowledge_repo, mock_asset_repo, mock_fav_repo, mock_recycle_repo, mock_timeline_repo
):
    return KnowledgeService(
        knowledge_repo=mock_knowledge_repo,
        asset_repo=mock_asset_repo,
        favorite_repo=mock_fav_repo,
        recycle_repo=mock_recycle_repo,
        timeline_repo=mock_timeline_repo
    )

@pytest.mark.asyncio
async def test_create_project_success(knowledge_service, mock_knowledge_repo, mock_timeline_repo):
    ws_id = "ws_123"
    user_id = "user_abc"
    name = "Q4 Planning"
    
    mock_knowledge_repo.create_project.return_value = Project(
        id="proj_789",
        workspace_id=ws_id,
        name=name,
        color="slate",
        icon="folder",
        is_archived=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    p = await knowledge_service.create_user_project(ws_id, user_id, name)
    
    assert p.id == "proj_789"
    assert p.name == name
    mock_knowledge_repo.create_project.assert_called_once_with(ws_id=ws_id, name=name, description=None)
    mock_timeline_repo.record_event.assert_called_once()

@pytest.mark.asyncio
async def test_create_folder_success(knowledge_service, mock_knowledge_repo, mock_timeline_repo):
    col_id = "col_555"
    ws_id = "ws_123"
    user_id = "user_abc"
    name = "Internal Drafts"
    
    mock_knowledge_repo.create_folder.return_value = Folder(
        id="folder_999",
        collection_id=col_id,
        parent_id=None,
        workspace_id=ws_id,
        name=name,
        color="slate",
        icon="folder",
        is_archived=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    f = await knowledge_service.create_user_folder(col_id, None, ws_id, user_id, name)
    
    assert f.id == "folder_999"
    assert f.name == name
    mock_knowledge_repo.create_folder.assert_called_once_with(col_id=col_id, parent_id=None, ws_id=ws_id, name=name)

@pytest.mark.asyncio
async def test_move_folder_success(knowledge_service, mock_knowledge_repo):
    folder_id = "folder_999"
    new_parent_id = "folder_new_parent"
    user_id = "user_abc"
    
    mock_knowledge_repo.get_folder.return_value = Folder(
        id=folder_id,
        collection_id="col_555",
        parent_id="folder_old_parent",
        workspace_id="ws_123",
        name="Internal Drafts",
        color="slate",
        icon="folder",
        is_archived=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    mock_knowledge_repo.update_folder.return_value = Folder(
        id=folder_id,
        collection_id="col_555",
        parent_id=new_parent_id,
        workspace_id="ws_123",
        name="Internal Drafts",
        color="slate",
        icon="folder",
        is_archived=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    f = await knowledge_service.move_user_folder(folder_id, new_parent_id, user_id)
    
    assert f.parent_id == new_parent_id
    mock_knowledge_repo.update_folder.assert_called_once_with(folder_id, parent_id=new_parent_id)

@pytest.mark.asyncio
async def test_soft_delete_and_restore_asset_success(
    knowledge_service, mock_asset_repo, mock_recycle_repo, mock_timeline_repo
):
    asset_id = "asset_888"
    ws_id = "ws_123"
    user_id = "user_abc"
    
    mock_asset_repo.get_asset.return_value = KnowledgeAsset(
        id=asset_id,
        folder_id="folder_999",
        workspace_id=ws_id,
        name="draft.txt",
        asset_type="document",
        details={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    mock_recycle_repo.send_to_recycle_bin.return_value = RecycleItem(
        id="rec_item_111",
        workspace_id=ws_id,
        item_id=asset_id,
        item_type="asset",
        original_parent_id="folder_999",
        deleted_by=user_id,
        deleted_at=datetime.now(timezone.utc)
    )
    
    # 1. Test soft delete
    rec = await knowledge_service.soft_delete_knowledge_asset(asset_id, user_id, ws_id)
    assert rec.item_id == asset_id
    mock_asset_repo.update_asset.assert_called_once_with(asset_id, folder_id=None)
    
    # 2. Test restore
    mock_recycle_repo.get_recycle_item.return_value = RecycleItem(
        id="rec_item_111",
        workspace_id=ws_id,
        item_id=asset_id,
        item_type="asset",
        original_parent_id="folder_999",
        deleted_by=user_id,
        deleted_at=datetime.now(timezone.utc)
    )
    
    restored = await knowledge_service.restore_knowledge_item(asset_id, user_id, ws_id)
    assert restored is True
    # Verify that the folder_id link was restored to folder_999
    mock_asset_repo.update_asset.assert_any_call(asset_id, folder_id="folder_999")

@pytest.mark.asyncio
async def test_update_asset_status_success(
    knowledge_service, mock_asset_repo, mock_timeline_repo
):
    asset_id = "asset_888"
    ws_id = "ws_123"
    user_id = "user_abc"
    
    mock_asset_repo.get_asset.return_value = KnowledgeAsset(
        id=asset_id,
        folder_id="folder_999",
        workspace_id=ws_id,
        name="draft.txt",
        asset_type="document",
        status="pending",
        processing_stage="pending",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    mock_asset_repo.update_asset.return_value = KnowledgeAsset(
        id=asset_id,
        folder_id="folder_999",
        workspace_id=ws_id,
        name="draft.txt",
        asset_type="document",
        status="processing",
        processing_stage="chunking",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    updated = await knowledge_service.update_user_asset_status(
        asset_id=asset_id,
        ws_id=ws_id,
        user_id=user_id,
        status="processing",
        stage="chunking"
    )
    
    assert updated.status == "processing"
    assert updated.processing_stage == "chunking"
    mock_asset_repo.update_asset.assert_called_once_with(
        asset_id=asset_id,
        status="processing",
        processing_stage="chunking",
        updated_by=user_id
    )


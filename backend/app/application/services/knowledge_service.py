import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from app.domain.knowledge import (
    Project, Collection, Folder, KnowledgeAsset, Tag, Favorite, RecycleItem, TimelineEvent
)
from app.domain.repositories import (
    IKnowledgeRepository, IAssetRepository, IFavoriteRepository, IRecycleBinRepository, ITimelineRepository
)
from app.domain.events import DomainEvent
from app.infrastructure.events.dispatcher import event_bus

from app.domain.events import (
    ProjectCreatedEvent,
    CollectionCreatedEvent,
    FolderCreatedEvent,
    FolderMovedEvent,
    AssetCreatedEvent,
    AssetDeletedEvent,
    FavoriteAddedEvent,
    RecycleItemCreatedEvent,
    RecycleItemRestoredEvent,
    AssetStatusChangedEvent
)


class KnowledgeService:
    def __init__(
        self,
        knowledge_repo: IKnowledgeRepository,
        asset_repo: IAssetRepository,
        favorite_repo: IFavoriteRepository,
        recycle_repo: IRecycleBinRepository,
        timeline_repo: ITimelineRepository
    ):
        self.knowledge_repo = knowledge_repo
        self.asset_repo = asset_repo
        self.favorite_repo = favorite_repo
        self.recycle_repo = recycle_repo
        self.timeline_repo = timeline_repo

    async def create_user_project(self, ws_id: str, user_id: str, name: str, description: Optional[str] = None) -> Project:
        proj = await self.knowledge_repo.create_project(ws_id=ws_id, name=name, description=description)
        
        # Log Timeline
        await self.timeline_repo.record_event(
            ws_id=ws_id,
            target_id=proj.id,
            target_type="project",
            user_id=user_id,
            action="PROJECT_CREATION"
        )
        
        # Publish event
        await event_bus.publish(
            ProjectCreatedEvent(
                event_id=str(uuid.uuid4()),
                project_id=proj.id,
                workspace_id=ws_id,
                name=name
            )
        )
        return proj

    async def archive_project(self, project_id: str, user_id: str) -> Project:
        proj = await self.knowledge_repo.get_project(project_id)
        if not proj:
            raise ValueError("Project not found.")
            
        updated = await self.knowledge_repo.update_project(project_id, is_archived=True)
        
        # Log Timeline
        await self.timeline_repo.record_event(
            ws_id=proj.workspace_id,
            target_id=project_id,
            target_type="project",
            user_id=user_id,
            action="PROJECT_ARCHIVE"
        )
        return updated

    async def create_user_collection(self, project_id: str, ws_id: str, user_id: str, name: str, description: Optional[str] = None) -> Collection:
        col = await self.knowledge_repo.create_collection(
            project_id=project_id,
            ws_id=ws_id,
            name=name,
            description=description
        )
        
        # Log Timeline
        await self.timeline_repo.record_event(
            ws_id=ws_id,
            target_id=col.id,
            target_type="collection",
            user_id=user_id,
            action="COLLECTION_CREATION"
        )

        # Publish Event
        await event_bus.publish(
            CollectionCreatedEvent(
                event_id=str(uuid.uuid4()),
                collection_id=col.id,
                project_id=project_id,
                workspace_id=ws_id,
                name=name
            )
        )
        return col

    async def create_user_folder(self, col_id: str, parent_id: Optional[str], ws_id: str, user_id: str, name: str) -> Folder:
        folder = await self.knowledge_repo.create_folder(
            col_id=col_id,
            parent_id=parent_id,
            ws_id=ws_id,
            name=name
        )

        # Log Timeline
        await self.timeline_repo.record_event(
            ws_id=ws_id,
            target_id=folder.id,
            target_type="folder",
            user_id=user_id,
            action="FOLDER_CREATION"
        )

        # Publish Event
        await event_bus.publish(
            FolderCreatedEvent(
                event_id=str(uuid.uuid4()),
                folder_id=folder.id,
                collection_id=col_id,
                workspace_id=ws_id,
                name=name
            )
        )
        return folder

    async def move_user_folder(self, folder_id: str, new_parent_id: Optional[str], user_id: str) -> Folder:
        folder = await self.knowledge_repo.get_folder(folder_id)
        if not folder:
            raise ValueError("Folder not found.")

        prev_parent = folder.parent_id
        updated = await self.knowledge_repo.update_folder(folder_id, parent_id=new_parent_id)

        # Log Timeline
        await self.timeline_repo.record_event(
            ws_id=folder.workspace_id,
            target_id=folder_id,
            target_type="folder",
            user_id=user_id,
            action="FOLDER_MOVE"
        )

        # Publish Event
        await event_bus.publish(
            FolderMovedEvent(
                event_id=str(uuid.uuid4()),
                folder_id=folder_id,
                previous_parent_id=prev_parent,
                new_parent_id=new_parent_id
            )
        )
        return updated

    async def create_user_asset(
        self, 
        ws_id: str, 
        folder_id: Optional[str], 
        col_id: Optional[str], 
        proj_id: Optional[str], 
        name: str, 
        asset_type: str, 
        details: dict,
        user_id: str,
        status: str = "pending",
        processing_stage: str = "pending",
        checksum: Optional[str] = None
    ) -> KnowledgeAsset:
        asset = await self.asset_repo.create_asset(
            ws_id=ws_id,
            folder_id=folder_id,
            col_id=col_id,
            proj_id=proj_id,
            name=name,
            asset_type=asset_type,
            details=details,
            status=status,
            processing_stage=processing_stage,
            checksum=checksum,
            created_by=user_id
        )

        # Log Timeline
        await self.timeline_repo.record_event(
            ws_id=ws_id,
            target_id=asset.id,
            target_type="asset",
            user_id=user_id,
            action="ASSET_CREATION"
        )

        # Publish Event
        await event_bus.publish(
            AssetCreatedEvent(
                event_id=str(uuid.uuid4()),
                asset_id=asset.id,
                workspace_id=ws_id,
                name=name,
                asset_type=asset_type
            )
        )
        return asset

    async def soft_delete_knowledge_asset(self, asset_id: str, user_id: str, ws_id: str) -> RecycleItem:
        asset = await self.asset_repo.get_asset(asset_id)
        if not asset:
            raise ValueError("Asset not found.")

        # Record trashing seat
        recycle = await self.recycle_repo.send_to_recycle_bin(
            ws_id=ws_id,
            item_id=asset_id,
            item_type="asset",
            original_parent_id=asset.folder_id,
            deleted_by=user_id
        )

        # Dissociate from folder so it disappears from visual tree view
        await self.asset_repo.update_asset(asset_id, folder_id=None)

        # Log Timeline
        await self.timeline_repo.record_event(
            ws_id=ws_id,
            target_id=asset_id,
            target_type="asset",
            user_id=user_id,
            action="ASSET_TRASH"
        )

        # Publish Event
        await event_bus.publish(
            RecycleItemCreatedEvent(
                event_id=str(uuid.uuid4()),
                item_id=asset_id,
                workspace_id=ws_id,
                item_type="asset"
            )
        )
        return recycle

    async def restore_knowledge_item(self, item_id: str, user_id: str, ws_id: str) -> bool:
        item = await self.recycle_repo.get_recycle_item(item_id)
        if not item:
            raise ValueError("Item not found inside Recycle Bin.")

        if item.item_type == "asset":
            # Restore folder_id linkage
            await self.asset_repo.update_asset(item.item_id, folder_id=item.original_parent_id)

        # Remove from trashing list
        await self.recycle_repo.remove_from_recycle_bin(item_id)

        # Log Timeline
        await self.timeline_repo.record_event(
            ws_id=ws_id,
            target_id=item.item_id,
            target_type=item.item_type,
            user_id=user_id,
            action="ASSET_RESTORE"
        )

        # Publish Event
        await event_bus.publish(
            RecycleItemRestoredEvent(
                event_id=str(uuid.uuid4()),
                item_id=item.item_id,
                workspace_id=ws_id,
                item_type=item.item_type
            )
        )
        return True

    async def permanent_delete_knowledge_item(self, item_id: str, user_id: str, ws_id: str) -> bool:
        item = await self.recycle_repo.get_recycle_item(item_id)
        if not item:
            raise ValueError("Item not found in Recycle Bin.")

        if item.item_type == "asset":
            await self.asset_repo.delete_asset(item.item_id)

        await self.recycle_repo.remove_from_recycle_bin(item_id)

        # Log Timeline
        await self.timeline_repo.record_event(
            ws_id=ws_id,
            target_id=item.item_id,
            target_type=item.item_type,
            user_id=user_id,
            action="ASSET_PERMANENT_DELETE"
        )
        return True

    async def update_user_asset_status(
        self, 
        asset_id: str, 
        ws_id: str, 
        user_id: str, 
        status: str, 
        stage: str
    ) -> KnowledgeAsset:
        asset = await self.asset_repo.get_asset(asset_id)
        if not asset:
            raise ValueError("Asset not found.")

        old_status = asset.status
        updated = await self.asset_repo.update_asset(
            asset_id=asset_id,
            status=status,
            processing_stage=stage,
            updated_by=user_id
        )

        # Log Timeline
        await self.timeline_repo.record_event(
            ws_id=ws_id,
            target_id=asset_id,
            target_type="asset",
            user_id=user_id,
            action=f"STATUS_CHANGE_{status.upper()}"
        )

        # Publish Event
        await event_bus.publish(
            AssetStatusChangedEvent(
                event_id=str(uuid.uuid4()),
                asset_id=asset_id,
                workspace_id=ws_id,
                old_status=old_status,
                new_status=status,
                processing_stage=stage
            )
        )
        return updated

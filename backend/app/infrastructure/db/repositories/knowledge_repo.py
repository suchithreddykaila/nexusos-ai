import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
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
from app.domain.repositories import (
    IKnowledgeRepository,
    IAssetRepository,
    IFavoriteRepository,
    IRecycleBinRepository,
    ITimelineRepository
)
from app.infrastructure.db.models import (
    ProjectDB,
    CollectionDB,
    FolderDB,
    KnowledgeAssetDB,
    TagDB,
    FavoriteDB,
    BookmarkDB,
    AssetVersionDB,
    RecycleBinDB,
    TimelineEventDB,
    asset_tags
)

# Mapper helpers
def map_project(db: ProjectDB) -> Project:
    return Project(
        id=db.id,
        workspace_id=db.workspace_id,
        name=db.name,
        description=db.description,
        color=db.color,
        icon=db.icon,
        is_archived=db.is_archived,
        created_at=db.created_at,
        updated_at=db.updated_at
    )

def map_collection(db: CollectionDB) -> Collection:
    return Collection(
        id=db.id,
        project_id=db.project_id,
        workspace_id=db.workspace_id,
        name=db.name,
        description=db.description,
        color=db.color,
        icon=db.icon,
        is_archived=db.is_archived,
        created_at=db.created_at,
        updated_at=db.updated_at
    )

def map_folder(db: FolderDB) -> Folder:
    return Folder(
        id=db.id,
        collection_id=db.collection_id,
        parent_id=db.parent_id,
        workspace_id=db.workspace_id,
        name=db.name,
        color=db.color,
        icon=db.icon,
        is_archived=db.is_archived,
        created_at=db.created_at,
        updated_at=db.updated_at
    )

def map_asset(db: KnowledgeAssetDB) -> KnowledgeAsset:
    return KnowledgeAsset(
        id=db.id,
        folder_id=db.folder_id,
        collection_id=db.collection_id,
        project_id=db.project_id,
        workspace_id=db.workspace_id,
        name=db.name,
        asset_type=db.asset_type,
        status=db.status,
        processing_stage=db.processing_stage,
        checksum=db.checksum,
        created_by=db.created_by,
        updated_by=db.updated_by,
        deleted_by=db.deleted_by,
        details=db.details,
        created_at=db.created_at,
        updated_at=db.updated_at
    )

def map_tag(db: TagDB) -> Tag:
    return Tag(
        id=db.id,
        workspace_id=db.workspace_id,
        name=db.name,
        color=db.color
    )


class SQLKnowledgeRepository(IKnowledgeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_project(
        self, 
        ws_id: str, 
        name: str, 
        description: Optional[str] = None,
        color: str = "slate",
        icon: str = "folder"
    ) -> Project:
        db_proj = ProjectDB(
            id=str(uuid.uuid4()),
            workspace_id=ws_id,
            name=name,
            description=description,
            color=color,
            icon=icon
        )
        self.session.add(db_proj)
        await self.session.flush()
        return map_project(db_proj)

    async def get_project(self, project_id: str) -> Optional[Project]:
        res = await self.session.execute(select(ProjectDB).where(ProjectDB.id == project_id))
        db_proj = res.scalar_one_or_none()
        return map_project(db_proj) if db_proj else None

    async def list_projects(self, ws_id: str) -> List[Project]:
        res = await self.session.execute(
            select(ProjectDB).where(ProjectDB.workspace_id == ws_id, ProjectDB.is_archived == False).order_by(ProjectDB.created_at.desc())
        )
        return [map_project(p) for p in res.scalars().all()]

    async def update_project(
        self, 
        project_id: str, 
        name: Optional[str] = None, 
        description: Optional[str] = None,
        color: Optional[str] = None,
        is_archived: Optional[bool] = None
    ) -> Project:
        vals = {"updated_at": datetime.now(timezone.utc)}
        if name is not None: vals["name"] = name
        if description is not None: vals["description"] = description
        if color is not None: vals["color"] = color
        if is_archived is not None: vals["is_archived"] = is_archived

        await self.session.execute(update(ProjectDB).where(ProjectDB.id == project_id).values(**vals))
        res = await self.session.execute(select(ProjectDB).where(ProjectDB.id == project_id))
        return map_project(res.scalar_one())

    async def create_collection(
        self, 
        project_id: str, 
        ws_id: str, 
        name: str, 
        description: Optional[str] = None,
        color: str = "slate",
        icon: str = "layers"
    ) -> Collection:
        db_col = CollectionDB(
            id=str(uuid.uuid4()),
            project_id=project_id,
            workspace_id=ws_id,
            name=name,
            description=description,
            color=color,
            icon=icon
        )
        self.session.add(db_col)
        await self.session.flush()
        return map_collection(db_col)

    async def get_collection(self, col_id: str) -> Optional[Collection]:
        res = await self.session.execute(select(CollectionDB).where(CollectionDB.id == col_id))
        db_col = res.scalar_one_or_none()
        return map_collection(db_col) if db_col else None

    async def list_collections(self, project_id: str) -> List[Collection]:
        res = await self.session.execute(
            select(CollectionDB).where(CollectionDB.project_id == project_id, CollectionDB.is_archived == False).order_by(CollectionDB.created_at.desc())
        )
        return [map_collection(c) for c in res.scalars().all()]

    async def update_collection(
        self, 
        col_id: str, 
        name: Optional[str] = None, 
        description: Optional[str] = None,
        is_archived: Optional[bool] = None
    ) -> Collection:
        vals = {"updated_at": datetime.now(timezone.utc)}
        if name is not None: vals["name"] = name
        if description is not None: vals["description"] = description
        if is_archived is not None: vals["is_archived"] = is_archived

        await self.session.execute(update(CollectionDB).where(CollectionDB.id == col_id).values(**vals))
        res = await self.session.execute(select(CollectionDB).where(CollectionDB.id == col_id))
        return map_collection(res.scalar_one())

    async def create_folder(
        self, 
        col_id: str, 
        parent_id: Optional[str], 
        ws_id: str, 
        name: str,
        color: str = "slate",
        icon: str = "folder"
    ) -> Folder:
        db_f = FolderDB(
            id=str(uuid.uuid4()),
            collection_id=col_id,
            parent_id=parent_id,
            workspace_id=ws_id,
            name=name,
            color=color,
            icon=icon
        )
        self.session.add(db_f)
        await self.session.flush()
        return map_folder(db_f)

    async def get_folder(self, folder_id: str) -> Optional[Folder]:
        res = await self.session.execute(select(FolderDB).where(FolderDB.id == folder_id))
        db_f = res.scalar_one_or_none()
        return map_folder(db_f) if db_f else None

    async def list_folders(self, col_id: str, parent_id: Optional[str] = None) -> List[Folder]:
        stmt = select(FolderDB).where(FolderDB.collection_id == col_id, FolderDB.is_archived == False)
        if parent_id:
            stmt = stmt.where(FolderDB.parent_id == parent_id)
        else:
            stmt = stmt.where(FolderDB.parent_id == None)
        res = await self.session.execute(stmt.order_by(FolderDB.name.asc()))
        return [map_folder(f) for f in res.scalars().all()]

    async def update_folder(
        self, 
        folder_id: str, 
        name: Optional[str] = None, 
        parent_id: Optional[str] = None,
        is_archived: Optional[bool] = None
    ) -> Folder:
        vals = {"updated_at": datetime.now(timezone.utc)}
        if name is not None: vals["name"] = name
        if parent_id is not None: vals["parent_id"] = parent_id
        if is_archived is not None: vals["is_archived"] = is_archived

        await self.session.execute(update(FolderDB).where(FolderDB.id == folder_id).values(**vals))
        res = await self.session.execute(select(FolderDB).where(FolderDB.id == folder_id))
        return map_folder(res.scalar_one())


class SQLAssetRepository(IAssetRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

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
        db_ast = KnowledgeAssetDB(
            id=str(uuid.uuid4()),
            workspace_id=ws_id,
            folder_id=folder_id,
            collection_id=col_id,
            project_id=proj_id,
            name=name,
            asset_type=asset_type,
            status=status,
            processing_stage=processing_stage,
            checksum=checksum,
            created_by=created_by,
            details=details
        )
        self.session.add(db_ast)
        await self.session.flush()
        return map_asset(db_ast)

    async def get_asset(self, asset_id: str) -> Optional[KnowledgeAsset]:
        res = await self.session.execute(select(KnowledgeAssetDB).where(KnowledgeAssetDB.id == asset_id))
        db_ast = res.scalar_one_or_none()
        return map_asset(db_ast) if db_ast else None

    async def list_assets(
        self, 
        ws_id: str, 
        folder_id: Optional[str] = None, 
        asset_type: Optional[str] = None
    ) -> List[KnowledgeAsset]:
        stmt = select(KnowledgeAssetDB).where(KnowledgeAssetDB.workspace_id == ws_id)
        if folder_id:
            stmt = stmt.where(KnowledgeAssetDB.folder_id == folder_id)
        if asset_type:
            stmt = stmt.where(KnowledgeAssetDB.asset_type == asset_type)
        res = await self.session.execute(stmt.order_by(KnowledgeAssetDB.created_at.desc()))
        return [map_asset(a) for a in res.scalars().all()]

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
        vals = {"updated_at": datetime.now(timezone.utc)}
        if name is not None: vals["name"] = name
        if folder_id is not None: vals["folder_id"] = folder_id
        if details is not None: vals["details"] = details
        if status is not None: vals["status"] = status
        if processing_stage is not None: vals["processing_stage"] = processing_stage
        if checksum is not None: vals["checksum"] = checksum
        if updated_by is not None: vals["updated_by"] = updated_by

        await self.session.execute(update(KnowledgeAssetDB).where(KnowledgeAssetDB.id == asset_id).values(**vals))
        res = await self.session.execute(select(KnowledgeAssetDB).where(KnowledgeAssetDB.id == asset_id))
        return map_asset(res.scalar_one())

    async def delete_asset(self, asset_id: str) -> bool:
        await self.session.execute(delete(KnowledgeAssetDB).where(KnowledgeAssetDB.id == asset_id))
        return True

    async def add_tag(self, ws_id: str, name: str, color: str) -> Tag:
        db_tag = TagDB(id=str(uuid.uuid4()), workspace_id=ws_id, name=name, color=color)
        self.session.add(db_tag)
        await self.session.flush()
        return map_tag(db_tag)

    async def list_tags(self, ws_id: str) -> List[Tag]:
        res = await self.session.execute(select(TagDB).where(TagDB.workspace_id == ws_id))
        return [map_tag(t) for t in res.scalars().all()]

    async def apply_tag_to_asset(self, asset_id: str, tag_id: str) -> bool:
        # Simple association insert
        await self.session.execute(
            asset_tags.insert().values(asset_id=asset_id, tag_id=tag_id)
        )
        return True

    async def list_asset_tags(self, asset_id: str) -> List[Tag]:
        res = await self.session.execute(
            select(TagDB).join(asset_tags).where(asset_tags.c.asset_id == asset_id)
        )
        return [map_tag(t) for t in res.scalars().all()]


class SQLFavoriteRepository(IFavoriteRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_favorite(self, user_id: str, ws_id: str, target_id: str, target_type: str) -> Favorite:
        db_fav = FavoriteDB(
            id=str(uuid.uuid4()),
            user_id=user_id,
            workspace_id=ws_id,
            target_id=target_id,
            target_type=target_type
        )
        self.session.add(db_fav)
        await self.session.flush()
        return Favorite(
            id=db_fav.id,
            user_id=db_fav.user_id,
            workspace_id=db_fav.workspace_id,
            target_id=db_fav.target_id,
            target_type=db_fav.target_type,
            created_at=db_fav.created_at
        )

    async def list_favorites(self, user_id: str, ws_id: str) -> List[Favorite]:
        res = await self.session.execute(
            select(FavoriteDB).where(FavoriteDB.user_id == user_id, FavoriteDB.workspace_id == ws_id)
        )
        return [
            Favorite(
                id=f.id,
                user_id=f.user_id,
                workspace_id=f.workspace_id,
                target_id=f.target_id,
                target_type=f.target_type,
                created_at=f.created_at
            ) for f in res.scalars().all()
        ]

    async def remove_favorite(self, user_id: str, ws_id: str, target_id: str) -> bool:
        await self.session.execute(
            delete(FavoriteDB).where(
                FavoriteDB.user_id == user_id, 
                FavoriteDB.workspace_id == ws_id, 
                FavoriteDB.target_id == target_id
            )
        )
        return True


class SQLRecycleBinRepository(IRecycleBinRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def send_to_recycle_bin(
        self, 
        ws_id: str, 
        item_id: str, 
        item_type: str, 
        original_parent_id: Optional[str], 
        deleted_by: str
    ) -> RecycleItem:
        db_rec = RecycleBinDB(
            id=str(uuid.uuid4()),
            workspace_id=ws_id,
            item_id=item_id,
            item_type=item_type,
            original_parent_id=original_parent_id,
            deleted_by=deleted_by
        )
        self.session.add(db_rec)
        await self.session.flush()
        return RecycleItem(
            id=db_rec.id,
            workspace_id=db_rec.workspace_id,
            item_id=db_rec.item_id,
            item_type=db_rec.item_type,
            original_parent_id=db_rec.original_parent_id,
            deleted_by=db_rec.deleted_by,
            deleted_at=db_rec.deleted_at
        )

    async def list_recycle_bin(self, ws_id: str) -> List[RecycleItem]:
        res = await self.session.execute(
            select(RecycleBinDB).where(RecycleBinDB.workspace_id == ws_id).order_by(RecycleBinDB.deleted_at.desc())
        )
        return [
            RecycleItem(
                id=r.id,
                workspace_id=r.workspace_id,
                item_id=r.item_id,
                item_type=r.item_type,
                original_parent_id=r.original_parent_id,
                deleted_by=r.deleted_by,
                deleted_at=r.deleted_at
            ) for r in res.scalars().all()
        ]

    async def get_recycle_item(self, item_id: str) -> Optional[RecycleItem]:
        res = await self.session.execute(select(RecycleBinDB).where(RecycleBinDB.item_id == item_id))
        db_rec = res.scalar_one_or_none()
        if db_rec:
            return RecycleItem(
                id=db_rec.id,
                workspace_id=db_rec.workspace_id,
                item_id=db_rec.item_id,
                item_type=db_rec.item_type,
                original_parent_id=db_rec.original_parent_id,
                deleted_by=db_rec.deleted_by,
                deleted_at=db_rec.deleted_at
            )
        return None

    async def remove_from_recycle_bin(self, item_id: str) -> bool:
        await self.session.execute(delete(RecycleBinDB).where(RecycleBinDB.item_id == item_id))
        return True


class SQLTimelineRepository(ITimelineRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_event(self, ws_id: str, target_id: str, target_type: str, user_id: str, action: str) -> TimelineEvent:
        db_evt = TimelineEventDB(
            id=str(uuid.uuid4()),
            workspace_id=ws_id,
            target_id=target_id,
            target_type=target_type,
            user_id=user_id,
            action=action
        )
        self.session.add(db_evt)
        await self.session.flush()
        return TimelineEvent(
            id=db_evt.id,
            workspace_id=db_evt.workspace_id,
            target_id=db_evt.target_id,
            target_type=db_evt.target_type,
            user_id=db_evt.user_id,
            action=db_evt.action,
            created_at=db_evt.created_at
        )

    async def list_events(self, ws_id: str, limit: int = 50) -> List[TimelineEvent]:
        res = await self.session.execute(
            select(TimelineEventDB).where(TimelineEventDB.workspace_id == ws_id).order_by(TimelineEventDB.created_at.desc()).limit(limit)
        )
        return [
            TimelineEvent(
                id=e.id,
                workspace_id=e.workspace_id,
                target_id=e.target_id,
                target_type=e.target_type,
                user_id=e.user_id,
                action=e.action,
                created_at=e.created_at
            ) for e in res.scalars().all()
        ]

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from enum import Enum

class AssetStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"
    DELETED = "deleted"

class AssetProcessingStage(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    VIRUS_SCAN = "virus_scan"
    FORMAT_DETECTION = "format_detection"
    PARSER_SELECTION = "parser_selection"
    TEXT_EXTRACTION = "text_extraction"
    OCR = "ocr"
    LANGUAGE_DETECTION = "language_detection"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    VECTOR_STORAGE = "vector_storage"
    GRAPH_UPDATE = "graph_update"
    SUMMARY_GENERATION = "summary_generation"
    COMPLETED = "completed"

class Project(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    color: str = "slate"
    icon: str = "folder"
    is_archived: bool = False
    created_at: datetime
    updated_at: datetime

class Collection(BaseModel):
    id: str
    project_id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    color: str = "slate"
    icon: str = "layers"
    is_archived: bool = False
    created_at: datetime
    updated_at: datetime

class Folder(BaseModel):
    id: str
    collection_id: str
    parent_id: Optional[str] = None
    workspace_id: str
    name: str
    color: str = "slate"
    icon: str = "folder"
    is_archived: bool = False
    created_at: datetime
    updated_at: datetime

class KnowledgeAsset(BaseModel):
    id: str
    folder_id: Optional[str] = None
    collection_id: Optional[str] = None
    project_id: Optional[str] = None
    workspace_id: str
    name: str
    asset_type: str  # document, link, code, dataset, image, video, audio
    
    # Ingestion & Processing lifecycle states
    status: str = "pending"
    processing_stage: str = "pending"
    checksum: Optional[str] = None
    
    # Audit references
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None

    # details is the single source of truth for all ingestion & processing lifecycle states:
    # - storage_path: str
    # - size_bytes: int
    # - mime_type: str
    # - error_message: str
    # - chunk_count: int
    # - vector_index: str (e.g. Qdrant or Milvus index tag)
    # - graph_node_id: str (Neo4j corresponding relationship entity identifier)
    # - ai_summary: str
    details: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime
    updated_at: datetime

class Tag(BaseModel):
    id: str
    workspace_id: str
    name: str
    color: str = "slate"

class Favorite(BaseModel):
    id: str
    user_id: str
    workspace_id: str
    target_id: str
    target_type: str  # project, collection, folder, asset
    created_at: datetime

class Bookmark(BaseModel):
    id: str
    user_id: str
    workspace_id: str
    asset_id: str
    created_at: datetime

class AssetVersion(BaseModel):
    id: str
    asset_id: str
    version_number: int
    storage_path: str
    created_at: datetime

class RecycleItem(BaseModel):
    id: str
    workspace_id: str
    item_id: str
    item_type: str  # project, collection, folder, asset
    original_parent_id: Optional[str] = None
    deleted_by: str
    deleted_at: datetime

class TimelineEvent(BaseModel):
    id: str
    workspace_id: str
    target_id: str
    target_type: str
    user_id: str
    action: str
    created_at: datetime

from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.domain.auth import User
from app.application.services.knowledge_service import KnowledgeService
from app.infrastructure.db.repositories.knowledge_repo import (
    SQLKnowledgeRepository,
    SQLAssetRepository,
    SQLFavoriteRepository,
    SQLRecycleBinRepository,
    SQLTimelineRepository
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# Request Schemas
class ProjectCreate(BaseModel):
    workspace_id: str
    name: str
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class CollectionCreate(BaseModel):
    workspace_id: str
    name: str
    description: Optional[str] = None

class FolderCreate(BaseModel):
    workspace_id: str
    name: str
    parent_id: Optional[str] = None

class FolderMove(BaseModel):
    parent_id: Optional[str] = None

class AssetCreate(BaseModel):
    workspace_id: str
    folder_id: Optional[str] = None
    collection_id: Optional[str] = None
    project_id: Optional[str] = None
    name: str
    asset_type: str
    details: Dict[str, Any] = {}

class FavoriteRequest(BaseModel):
    workspace_id: str
    target_id: str
    target_type: str

class TagCreate(BaseModel):
    workspace_id: str
    name: str
    color: str = "slate"

# Response Schemas
class ProjectResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    color: str
    icon: str
    is_archived: bool
    created_at: datetime

class CollectionResponse(BaseModel):
    id: str
    project_id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    color: str
    icon: str
    is_archived: bool
    created_at: datetime

class FolderResponse(BaseModel):
    id: str
    collection_id: str
    parent_id: Optional[str] = None
    workspace_id: str
    name: str
    color: str
    icon: str
    is_archived: bool
    created_at: datetime

class AssetResponse(BaseModel):
    id: str
    folder_id: Optional[str] = None
    collection_id: Optional[str] = None
    project_id: Optional[str] = None
    workspace_id: str
    name: str
    asset_type: str
    details: Dict[str, Any]
    created_at: datetime

class FavoriteResponse(BaseModel):
    id: str
    user_id: str
    workspace_id: str
    target_id: str
    target_type: str
    created_at: datetime

class RecycleItemResponse(BaseModel):
    id: str
    workspace_id: str
    item_id: str
    item_type: str
    original_parent_id: Optional[str] = None
    deleted_by: str
    deleted_at: datetime

class TimelineEventResponse(BaseModel):
    id: str
    workspace_id: str
    target_id: str
    target_type: str
    user_id: str
    action: str
    created_at: datetime

class TagResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    color: str

def get_knowledge_service(db: AsyncSession = Depends(get_db)) -> KnowledgeService:
    return KnowledgeService(
        knowledge_repo=SQLKnowledgeRepository(db),
        asset_repo=SQLAssetRepository(db),
        favorite_repo=SQLFavoriteRepository(db),
        recycle_repo=SQLRecycleBinRepository(db),
        timeline_repo=SQLTimelineRepository(db)
    )

# --- Projects ---
@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.create_user_project(
        ws_id=payload.workspace_id,
        user_id=current_user.id,
        name=payload.name,
        description=payload.description
    )

@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.knowledge_repo.list_projects(workspace_id)

@router.get("/projects/{proj_id}", response_model=ProjectResponse)
async def get_project(
    proj_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    p = await service.knowledge_repo.get_project(proj_id)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return p

@router.put("/projects/{proj_id}", response_model=ProjectResponse)
async def update_project(
    proj_id: str,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.knowledge_repo.update_project(
        project_id=proj_id,
        name=payload.name,
        description=payload.description,
        color=payload.color
    )

@router.delete("/projects/{proj_id}", response_model=ProjectResponse)
async def delete_project(
    proj_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.archive_project(project_id=proj_id, user_id=current_user.id)

# --- Collections ---
@router.post("/projects/{proj_id}/collections", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    proj_id: str,
    payload: CollectionCreate,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.create_user_collection(
        project_id=proj_id,
        ws_id=payload.workspace_id,
        user_id=current_user.id,
        name=payload.name,
        description=payload.description
    )

@router.get("/projects/{proj_id}/collections", response_model=List[CollectionResponse])
async def list_collections(
    proj_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.knowledge_repo.list_collections(proj_id)

# --- Folders ---
@router.post("/collections/{col_id}/folders", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    col_id: str,
    payload: FolderCreate,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.create_user_folder(
        col_id=col_id,
        parent_id=payload.parent_id,
        ws_id=payload.workspace_id,
        user_id=current_user.id,
        name=payload.name
    )

@router.get("/collections/{col_id}/folders", response_model=List[FolderResponse])
async def list_folders(
    col_id: str,
    parent_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.knowledge_repo.list_folders(col_id=col_id, parent_id=parent_id)

@router.put("/folders/{folder_id}/move", response_model=FolderResponse)
async def move_folder(
    folder_id: str,
    payload: FolderMove,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        return await service.move_user_folder(
            folder_id=folder_id,
            new_parent_id=payload.parent_id,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- Assets ---
@router.post("/assets", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreate,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.create_user_asset(
        ws_id=payload.workspace_id,
        folder_id=payload.folder_id,
        col_id=payload.collection_id,
        proj_id=payload.project_id,
        name=payload.name,
        asset_type=payload.asset_type,
        details=payload.details,
        user_id=current_user.id
    )

@router.get("/assets", response_model=List[AssetResponse])
async def list_assets(
    workspace_id: str,
    folder_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.asset_repo.list_assets(ws_id=workspace_id, folder_id=folder_id)

@router.delete("/assets/{asset_id}", response_model=RecycleItemResponse)
async def delete_asset(
    asset_id: str,
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        return await service.soft_delete_knowledge_asset(
            asset_id=asset_id,
            user_id=current_user.id,
            ws_id=workspace_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- Recycle Bin ---
@router.get("/recycle-bin", response_model=List[RecycleItemResponse])
async def list_recycle_bin(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.recycle_repo.list_recycle_bin(workspace_id)

@router.post("/recycle-bin/{item_id}/restore")
async def restore_item(
    item_id: str,
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        await service.restore_knowledge_item(item_id=item_id, user_id=current_user.id, ws_id=workspace_id)
        return {"status": "success", "message": "Item successfully restored."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/recycle-bin/{item_id}")
async def permanent_delete_item(
    item_id: str,
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        await service.permanent_delete_knowledge_item(item_id=item_id, user_id=current_user.id, ws_id=workspace_id)
        return {"status": "success", "message": "Item permanently deleted."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- Favorites ---
@router.post("/favorites", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    payload: FavoriteRequest,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.favorite_repo.add_favorite(
        user_id=current_user.id,
        ws_id=payload.workspace_id,
        target_id=payload.target_id,
        target_type=payload.target_type
    )

@router.get("/favorites", response_model=List[FavoriteResponse])
async def list_favorites(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.favorite_repo.list_favorites(user_id=current_user.id, ws_id=workspace_id)

@router.delete("/favorites/{target_id}")
async def remove_favorite(
    target_id: str,
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    await service.favorite_repo.remove_favorite(
        user_id=current_user.id,
        ws_id=workspace_id,
        target_id=target_id
    )
    return {"status": "success"}

# --- Tags ---
@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    payload: TagCreate,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.asset_repo.add_tag(
        ws_id=payload.workspace_id,
        name=payload.name,
        color=payload.color
    )

@router.get("/tags", response_model=List[TagResponse])
async def list_tags(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.asset_repo.list_tags(workspace_id)

@router.post("/assets/{asset_id}/tags/{tag_id}")
async def apply_tag(
    asset_id: str,
    tag_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    await service.asset_repo.apply_tag_to_asset(asset_id, tag_id)
    return {"status": "success"}

# --- Timeline ---
@router.get("/timeline", response_model=List[TimelineEventResponse])
async def list_timeline(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.timeline_repo.list_events(workspace_id)


# ==========================================
# AI KNOWLEDGE ENGINE ENDPOINTS
# ==========================================

from fastapi.responses import StreamingResponse
from app.application.engine.knowledge_engine import AIKnowledgeEngine
from app.domain.engine import EngineResponse, Citation
from app.domain.search import SearchResultItem
from app.infrastructure.ai.failover import FailoverAIProviderProxy

def get_knowledge_engine(service: KnowledgeService = Depends(get_knowledge_service)) -> AIKnowledgeEngine:
    return AIKnowledgeEngine(asset_repo=service.asset_repo)

class QueryRequest(BaseModel):
    query: str
    workspace_id: str
    project_id: Optional[str] = None
    collection_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None
    preferred_provider: Optional[str] = "ollama"

class CompareRequest(BaseModel):
    query: str
    workspace_id: str
    asset_ids: List[str]
    preferred_provider: Optional[str] = "ollama"

class ExplainRequest(BaseModel):
    query: str
    workspace_id: str
    preferred_provider: Optional[str] = "ollama"

@router.post("/query", response_model=EngineResponse)
async def query_knowledge(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user),
    engine: AIKnowledgeEngine = Depends(get_knowledge_engine)
):
    return await engine.query_knowledge(
        query=payload.query,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        collection_id=payload.collection_id,
        history=payload.history,
        preferred_provider=payload.preferred_provider
    )

@router.post("/chat")
async def chat_stream(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user),
    engine: AIKnowledgeEngine = Depends(get_knowledge_engine)
):
    return StreamingResponse(
        engine.query_stream(
            query=payload.query,
            workspace_id=payload.workspace_id,
            project_id=payload.project_id,
            collection_id=payload.collection_id,
            history=payload.history,
            preferred_provider=payload.preferred_provider
        ),
        media_type="text/event-stream"
    )

@router.post("/compare", response_model=EngineResponse)
async def compare_documents(
    payload: CompareRequest,
    current_user: User = Depends(get_current_user),
    engine: AIKnowledgeEngine = Depends(get_knowledge_engine)
):
    retrieved_items = []
    for asset_id in payload.asset_ids:
        asset = await engine.retrieval_service.asset_repo.get_asset(asset_id)
        if asset:
            snippet = f"Document: [{asset.name}]\n"
            if "system_metadata" in asset.details:
                snippet += f"Mime-Type: {asset.details['system_metadata'].get('mime_type')}\n"
            if "document_metadata" in asset.details:
                snippet += f"Metadata: {asset.details['document_metadata']}\n"
            retrieved_items.append(SearchResultItem(
                title=asset.name,
                item_type="document",
                score=1.0,
                description=snippet,
                metadata={"asset_id": asset.id, "workspace_id": asset.workspace_id, "details": asset.details}
            ))
            
    context_str, citations = await engine.context_service.assemble_context(retrieved_items)
    messages = engine.prompt_constructor.build_prompt(
        query=f"Compare the following documents: {payload.query}",
        context_str=context_str
    )
    system_instr = messages[0]["content"]
    user_prompt = messages[-1]["content"]
    
    provider_proxy = FailoverAIProviderProxy(preferred_order=[payload.preferred_provider, "ollama", "gemini"])
    raw_response = await provider_proxy.generate_text(prompt=user_prompt, system_instruction=system_instr)
    
    response = EngineResponse(
        response_text=raw_response,
        citations=citations,
        provider_used=payload.preferred_provider,
        model_used="default"
    )
    return await engine.validation_service.validate_response(response)

@router.post("/explain", response_model=EngineResponse)
async def explain_topic(
    payload: ExplainRequest,
    current_user: User = Depends(get_current_user),
    engine: AIKnowledgeEngine = Depends(get_knowledge_engine)
):
    return await engine.query_knowledge(
        query=f"Explain in detail: {payload.query}",
        workspace_id=payload.workspace_id,
        preferred_provider=payload.preferred_provider
    )

@router.post("/search", response_model=List[SearchResultItem])
async def search_raw_assets(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user),
    engine: AIKnowledgeEngine = Depends(get_knowledge_engine)
):
    plan = await engine.query_service.analyze_query(
        query=payload.query,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        collection_id=payload.collection_id
    )
    retrieved = await engine.retrieval_service.retrieve_knowledge(plan)
    return await engine.ranking_engine.rerank_results(retrieved)

@router.post("/summarize", response_model=EngineResponse)
async def summarize_scope(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user),
    engine: AIKnowledgeEngine = Depends(get_knowledge_engine)
):
    return await engine.query_knowledge(
        query=f"Provide a summary of: {payload.query}",
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        collection_id=payload.collection_id,
        preferred_provider=payload.preferred_provider
    )

@router.get("/citations", response_model=List[Citation])
async def list_citations_info(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    engine: AIKnowledgeEngine = Depends(get_knowledge_engine)
):
    # Returns placeholder mock citations list for workspace UI filters
    return [
        Citation(id="cit_1", asset_id="mock_id_1", asset_name="Policy.pdf", snippet="Sample match citation", confidence_score=0.95),
        Citation(id="cit_2", asset_id="mock_id_2", asset_name="Guide.txt", snippet="Another matches fact", confidence_score=0.88)
    ]

@router.get("/history")
async def list_query_history(
    workspace_id: str,
    current_user: User = Depends(get_current_user)
):
    # Return placeholder session search activity logs list
    return [
        {"query": "summarize project objectives", "timestamp": "2026-07-08T12:00:00Z"},
        {"query": "compare contract draft 1 and 2", "timestamp": "2026-07-08T11:45:00Z"}
    ]

@router.get("/providers")
async def list_engine_providers(
    current_user: User = Depends(get_current_user)
):
    # Returns active registered provider tags
    return ["ollama", "gemini"]


from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.domain.auth import User
from app.domain.engine import EngineResponse, Citation
from app.domain.research import ResearchSession, ResearchNote
from app.application.engine.knowledge_engine import AIKnowledgeEngine
from app.application.services.knowledge_service import KnowledgeService
from app.api.v1.knowledge import get_knowledge_service, get_knowledge_engine
from app.application.services.research_service import ResearchService

router = APIRouter(prefix="/research", tags=["research"])

def get_research_service(
    db: AsyncSession = Depends(get_db),
    engine: AIKnowledgeEngine = Depends(get_knowledge_engine)
) -> ResearchService:
    return ResearchService(session=db, engine=engine)

# Request Schemas
class SessionCreate(BaseModel):
    workspace_id: str
    name: str
    description: Optional[str] = None
    asset_ids: List[str] = []

class NoteCreate(BaseModel):
    session_id: str
    title: str
    content: str
    linked_asset_ids: List[str] = []

class ResearchQueryRequest(BaseModel):
    query: str
    workspace_id: str
    asset_ids: List[str]
    preferred_provider: Optional[str] = "ollama"

class BibliographyRequest(BaseModel):
    asset_ids: List[str]
    style: Optional[str] = "apa"

class ExportRequest(BaseModel):
    session_id: str
    format: Optional[str] = "markdown"

# --- Session Management ---
@router.post("/session", response_model=ResearchSession, status_code=status.HTTP_201_CREATED)
async def create_research_session(
    payload: SessionCreate,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    return await service.create_session(
        ws_id=payload.workspace_id,
        name=payload.name,
        description=payload.description,
        asset_ids=payload.asset_ids
    )

@router.get("/session/{session_id}", response_model=ResearchSession)
async def get_research_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Research Session not found.")
    return session

# --- Notes notepad ---
@router.post("/notes", response_model=ResearchNote, status_code=status.HTTP_201_CREATED)
async def create_research_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    return await service.create_note(
        session_id=payload.session_id,
        title=payload.title,
        content=payload.content,
        linked_asset_ids=payload.linked_asset_ids
    )

@router.get("/session/{session_id}/notes", response_model=List[ResearchNote])
async def list_session_notes(
    session_id: str,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    return await service.list_notes(session_id)

@router.put("/notes/{note_id}", response_model=ResearchNote)
async def update_research_note(
    note_id: str,
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    return await service.update_note(
        note_id=note_id,
        title=payload.title,
        content=payload.content,
        linked_asset_ids=payload.linked_asset_ids
    )

@router.delete("/notes/{note_id}")
async def delete_research_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    await service.delete_note(note_id)
    return {"status": "success"}

# --- AI Research Assistant Operations ---
@router.post("/query", response_model=EngineResponse)
async def query_sources(
    payload: ResearchQueryRequest,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    return await service.query_selected_sources(
        query=payload.query,
        workspace_id=payload.workspace_id,
        asset_ids=payload.asset_ids,
        preferred_provider=payload.preferred_provider
    )

@router.post("/compare", response_model=EngineResponse)
async def compare_sources(
    payload: ResearchQueryRequest,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    return await service.query_selected_sources(
        query=f"Compare structural contradictions and key arguments in details of: {payload.query}",
        workspace_id=payload.workspace_id,
        asset_ids=payload.asset_ids,
        preferred_provider=payload.preferred_provider
    )

@router.post("/literature-review", response_model=EngineResponse)
async def generate_literature_review(
    payload: ResearchQueryRequest,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    return await service.query_selected_sources(
        query=f"Draft a formal academic literature review summarizing methodologies and results for: {payload.query}",
        workspace_id=payload.workspace_id,
        asset_ids=payload.asset_ids,
        preferred_provider=payload.preferred_provider
    )

@router.post("/summary", response_model=EngineResponse)
async def generate_aggregate_summary(
    payload: ResearchQueryRequest,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    return await service.query_selected_sources(
        query=f"Compile a detailed executive summary: {payload.query}",
        workspace_id=payload.workspace_id,
        asset_ids=payload.asset_ids,
        preferred_provider=payload.preferred_provider
    )

# --- Citation exporter ---
@router.post("/citations", response_model=List[str])
async def generate_citations_bibliography(
    payload: BibliographyRequest,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    return await service.generate_bibliography(
        asset_ids=payload.asset_ids,
        style=payload.style
    )

@router.post("/export")
async def export_research_package(
    payload: ExportRequest,
    current_user: User = Depends(get_current_user),
    service: ResearchService = Depends(get_research_service)
):
    # Returns export metadata links
    return {
        "status": "success",
        "download_url": f"http://localhost:8000/api/v1/research/session/{payload.session_id}/download?format={payload.format}",
        "format": payload.format,
        "exported_at": datetime.now().isoformat()
    }

@router.post("/insights")
async def generate_research_insights(
    payload: BibliographyRequest,
    current_user: User = Depends(get_current_user)
):
    # Entity graph relationship metadata placeholder insights
    return {
        "entities": ["Neural Networks", "Transformer Architectures", "RAG Pipeline"],
        "relationships": [
            {"source": "Transformer Architectures", "target": "RAG Pipeline", "type": "improves_retrieval"}
        ],
        "open_questions": ["How do local offline providers scale under long context token limits?"]
    }

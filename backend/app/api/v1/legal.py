from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_db, get_current_user
from app.domain.legal import LegalMatter, ContractAnalysis, ComplianceReport
from app.application.services.legal_service import LegalService
from app.application.engine.knowledge_engine import AIKnowledgeEngine
from app.infrastructure.db.repositories.knowledge_repo import AssetRepository
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/legal", tags=["Legal Intelligence"])

def get_legal_service(db: AsyncSession = Depends(get_db)):
    asset_repo = AssetRepository(db)
    engine = AIKnowledgeEngine(asset_repo)
    return LegalService(db, engine)

# --- Schemas ---
class CreateMatterReq(BaseModel):
    name: str
    client_name: Optional[str] = None
    description: Optional[str] = None
    workspace_id: str

class AnalyzeReq(BaseModel):
    matter_id: str
    asset_id: str
    workspace_id: str

class ExplainReq(BaseModel):
    asset_id: str
    clause_text: str
    audience: str = "Plain English"

class ComplianceReq(BaseModel):
    matter_id: str
    asset_ids: List[str]
    workspace_id: str
    framework: str

class CompareReq(BaseModel):
    asset_ids: List[str]
    workspace_id: str

# --- Endpoints ---

@router.post("/matters", response_model=LegalMatter)
async def create_matter(req: CreateMatterReq, service: LegalService = Depends(get_legal_service)):
    matter = LegalMatter(
        id=str(uuid.uuid4()),
        workspace_id=req.workspace_id,
        name=req.name,
        client_name=req.client_name,
        description=req.description,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    return await service.create_matter(matter)

@router.get("/matters", response_model=List[LegalMatter])
async def list_matters(workspace_id: str, service: LegalService = Depends(get_legal_service)):
    return await service.list_matters(workspace_id)

@router.post("/analyze", response_model=ContractAnalysis)
async def analyze_contract(req: AnalyzeReq, service: LegalService = Depends(get_legal_service)):
    return await service.analyze_contract(req.matter_id, req.asset_id, req.workspace_id)

@router.get("/analyze/{asset_id}", response_model=ContractAnalysis)
async def get_analysis(asset_id: str, workspace_id: str, service: LegalService = Depends(get_legal_service)):
    analysis = await service.get_analysis(asset_id, workspace_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.post("/explain")
async def explain_clause(req: ExplainReq, service: LegalService = Depends(get_legal_service)):
    explanation = await service.explain_clause(req.asset_id, req.clause_text, req.audience)
    return {"explanation": explanation}

@router.post("/compliance", response_model=ComplianceReport)
async def generate_compliance(req: ComplianceReq, service: LegalService = Depends(get_legal_service)):
    return await service.generate_compliance_report(req.matter_id, req.asset_ids, req.workspace_id, req.framework)

@router.post("/compare")
async def compare_contracts(req: CompareReq, service: LegalService = Depends(get_legal_service)):
    comparison = await service.compare_contracts(req.asset_ids, req.workspace_id)
    return {"comparison": comparison}

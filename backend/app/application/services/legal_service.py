import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.legal import (
    LegalMatter, ContractAnalysis, ExtractedClause, ClauseCategory, 
    RiskProfile, RiskLevel, TimelineEvent, ComplianceReport
)
from app.infrastructure.db.repositories.legal_repo import LegalRepository
from app.infrastructure.db.models import KnowledgeAssetDB
from app.application.engine.knowledge_engine import AIKnowledgeEngine
from app.infrastructure.ai.failover import FailoverAIProviderProxy
from app.domain.search import SearchResultItem

logger = logging.getLogger(__name__)

class LegalService:
    def __init__(self, session: AsyncSession, engine: AIKnowledgeEngine):
        self.session = session
        self.engine = engine
        self.repo = LegalRepository(session)

    # --- Matter Management ---
    async def create_matter(self, matter: LegalMatter) -> LegalMatter:
        return await self.repo.create_matter(matter)

    async def get_matter(self, matter_id: str, ws_id: str) -> Optional[LegalMatter]:
        return await self.repo.get_matter_by_id(matter_id, ws_id)

    async def list_matters(self, ws_id: str) -> List[LegalMatter]:
        return await self.repo.list_matters(ws_id)

    # --- Core AI Operations ---
    async def _execute_legal_prompt(self, asset_ids: List[str], system_prompt: str, user_prompt: str, preferred_provider: str = "ollama") -> str:
        # Load asset content manually to bypass global search limits, simulating explicit document loading
        retrieved_items = []
        for aid in asset_ids:
            res = await self.session.execute(select(KnowledgeAssetDB).where(KnowledgeAssetDB.id == aid))
            asset = res.scalar_one_or_none()
            if asset:
                snippet = f"Document: {asset.name}\n"
                if "ai_summary" in asset.details:
                    snippet += f"Content: {asset.details['ai_summary']}\n"
                if "extracted_text" in asset.details:
                    # In a real system, we might chunk this, but for now we pass the extracted text
                    text = asset.details["extracted_text"]
                    snippet += f"Text: {text[:20000]}\n" # Trim to avoid context limits
                retrieved_items.append(SearchResultItem(
                    title=asset.name,
                    item_type="document",
                    score=1.0,
                    description=snippet,
                    metadata={"asset_id": asset.id, "workspace_id": asset.workspace_id}
                ))

        context_str, _ = await self.engine.context_service.assemble_context(retrieved_items)
        
        provider_proxy = FailoverAIProviderProxy(preferred_order=[preferred_provider, "ollama", "gemini"])
        
        final_user_prompt = f"Context:\n{context_str}\n\nTask:\n{user_prompt}"
        
        raw_response = await provider_proxy.generate_text(prompt=final_user_prompt, system_instruction=system_prompt)
        return raw_response

    async def analyze_contract(self, matter_id: str, asset_id: str, ws_id: str) -> ContractAnalysis:
        # 1. Ask AI to extract clauses as JSON
        sys_prompt = "You are an expert Legal AI. Extract key clauses from the provided contract. Return ONLY a valid JSON array of objects with keys: category, text, explanation, negotiation, is_ambiguous (bool), is_one_sided (bool)."
        user_prompt = "Extract the clauses. Categories must be one of: Definitions, Parties, Effective Date, Expiration, Renewal, Payment, Confidentiality, Termination, Liability, Indemnification, Force Majeure, Jurisdiction, Governing Law, Dispute Resolution, Data Privacy, GDPR, Intellectual Property, Assignment, Warranty, Obligations, Deadlines, Penalties, Other."
        
        raw_json = await self._execute_legal_prompt([asset_id], sys_prompt, user_prompt)
        
        # Fallback parsing
        try:
            # Strip markdown blocks if present
            if raw_json.startswith("```json"):
                raw_json = raw_json.split("```json")[1].split("```")[0].strip()
            elif raw_json.startswith("```"):
                raw_json = raw_json.split("```")[1].split("```")[0].strip()
            parsed_clauses = json.loads(raw_json)
        except Exception as e:
            logger.error(f"Failed to parse clause json: {e}")
            parsed_clauses = []

        extracted_clauses = []
        import uuid
        for i, c in enumerate(parsed_clauses):
            try:
                cat_str = c.get("category", "Other")
                try:
                    cat = ClauseCategory(cat_str)
                except ValueError:
                    cat = ClauseCategory.OTHER
                
                extracted_clauses.append(ExtractedClause(
                    id=str(uuid.uuid4()),
                    category=cat,
                    text=c.get("text", "Unknown"),
                    explanation_plain_english=c.get("explanation"),
                    negotiation_suggestions=c.get("negotiation"),
                    is_ambiguous=c.get("is_ambiguous", False),
                    is_one_sided=c.get("is_one_sided", False)
                ))
            except Exception:
                pass

        # 2. Risk Assessment
        risk_sys = "You are a Legal Risk Assessor. Output JSON only with keys: risk_score (int 0-100), level (Critical, High, Medium, Low, Info), summary (string)."
        risk_user = "Assess the overall legal risk of this contract based on standard corporate standards."
        raw_risk = await self._execute_legal_prompt([asset_id], risk_sys, risk_user)
        try:
            if raw_risk.startswith("```json"):
                raw_risk = raw_risk.split("```json")[1].split("```")[0].strip()
            risk_data = json.loads(raw_risk)
            level_str = risk_data.get("level", "Info")
            try:
                level = RiskLevel(level_str)
            except ValueError:
                level = RiskLevel.INFO
                
            risk_profile = RiskProfile(
                risk_score=risk_data.get("risk_score", 0),
                level=level,
                summary=risk_data.get("summary", "No summary provided.")
            )
        except:
            risk_profile = RiskProfile(risk_score=0, level=RiskLevel.INFO, summary="Failed to parse risk.")

        # 3. Timeline Extraction
        time_sys = "You are a Legal Timeline Extractor. Output JSON array of objects: date, event_type, description."
        time_user = "Extract all dates, deadlines, renewals, and expiration events."
        raw_time = await self._execute_legal_prompt([asset_id], time_sys, time_user)
        timeline = []
        try:
            if raw_time.startswith("```json"):
                raw_time = raw_time.split("```json")[1].split("```")[0].strip()
            time_data = json.loads(raw_time)
            for t in time_data:
                timeline.append(TimelineEvent(
                    date=t.get("date", "Unknown"),
                    event_type=t.get("event_type", "Event"),
                    description=t.get("description", "Event description")
                ))
        except:
            pass
            
        # 4. Summary
        exec_sys = "You are an Executive Legal Summarizer. Write a 2-paragraph professional executive summary."
        exec_summary = await self._execute_legal_prompt([asset_id], exec_sys, "Summarize this contract for the C-suite.")

        analysis = ContractAnalysis(
            id=str(uuid.uuid4()),
            matter_id=matter_id,
            asset_id=asset_id,
            workspace_id=ws_id,
            executive_summary=exec_summary,
            clauses=extracted_clauses,
            risk_profile=risk_profile,
            timeline=timeline,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        return await self.repo.save_contract_analysis(analysis)

    async def get_analysis(self, asset_id: str, ws_id: str) -> Optional[ContractAnalysis]:
        return await self.repo.get_contract_analysis(asset_id, ws_id)

    async def generate_compliance_report(self, matter_id: str, asset_ids: List[str], ws_id: str, framework: str) -> ComplianceReport:
        sys_prompt = "You are a Compliance Auditor. Output JSON with: score (0.0-100.0), violations (array of objects), missing_requirements (array of strings), recommendations (array of strings)."
        user_prompt = f"Audit these documents against the {framework} framework."
        raw_resp = await self._execute_legal_prompt(asset_ids, sys_prompt, user_prompt)
        
        score = 0.0
        violations = []
        missing = []
        recs = []
        try:
            if raw_resp.startswith("```json"):
                raw_resp = raw_resp.split("```json")[1].split("```")[0].strip()
            data = json.loads(raw_resp)
            score = float(data.get("score", 0.0))
            violations = data.get("violations", [])
            missing = data.get("missing_requirements", [])
            recs = data.get("recommendations", [])
        except:
            logger.error("Failed to parse compliance json")
            
        import uuid
        report = ComplianceReport(
            id=str(uuid.uuid4()),
            matter_id=matter_id,
            asset_ids=asset_ids,
            workspace_id=ws_id,
            framework=framework,
            score=score,
            violations=violations,
            missing_requirements=missing,
            recommendations=recs,
            created_at=datetime.now(timezone.utc)
        )
        return await self.repo.save_compliance_report(report)

    async def compare_contracts(self, asset_ids: List[str], ws_id: str) -> str:
        sys_prompt = "You are a Legal Contract Comparison AI. Compare these agreements side-by-side. Output Markdown formatting highlighting differences, added clauses, removed clauses, and risk changes."
        user_prompt = "Perform a detailed side-by-side comparison of the provided contracts."
        return await self._execute_legal_prompt(asset_ids, sys_prompt, user_prompt)

    async def explain_clause(self, asset_id: str, clause_text: str, audience: str = "Plain English") -> str:
        sys_prompt = f"You are a Legal Explainer. Explain this clause to the user. Audience/Style: {audience}."
        user_prompt = f"Clause Text:\n{clause_text}\n\nProvide the explanation."
        return await self._execute_legal_prompt([asset_id], sys_prompt, user_prompt)

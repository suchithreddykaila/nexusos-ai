from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.infrastructure.db.models import LegalMatterDB, ContractAnalysisDB, ComplianceReportDB
from app.domain.legal import LegalMatter, ContractAnalysis, ComplianceReport

class LegalRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create_matter(self, matter: LegalMatter) -> LegalMatter:
        db_matter = LegalMatterDB(
            id=matter.id,
            workspace_id=matter.workspace_id,
            name=matter.name,
            client_name=matter.client_name,
            description=matter.description,
            status=matter.status,
            is_pinned=matter.is_pinned,
            created_at=matter.created_at,
            updated_at=matter.updated_at
        )
        self.session.add(db_matter)
        await self.session.flush()
        return matter

    async def get_matter_by_id(self, matter_id: str, workspace_id: str) -> Optional[LegalMatter]:
        stmt = select(LegalMatterDB).where(
            LegalMatterDB.id == matter_id,
            LegalMatterDB.workspace_id == workspace_id
        )
        result = await self.session.execute(stmt)
        db_matter = result.scalar_one_or_none()
        if not db_matter:
            return None
        return LegalMatter(
            id=db_matter.id,
            workspace_id=db_matter.workspace_id,
            name=db_matter.name,
            client_name=db_matter.client_name,
            description=db_matter.description,
            status=db_matter.status,
            is_pinned=db_matter.is_pinned,
            created_at=db_matter.created_at,
            updated_at=db_matter.updated_at
        )

    async def list_matters(self, workspace_id: str) -> List[LegalMatter]:
        stmt = select(LegalMatterDB).where(LegalMatterDB.workspace_id == workspace_id).order_by(LegalMatterDB.updated_at.desc())
        result = await self.session.execute(stmt)
        return [
            LegalMatter(
                id=db_matter.id,
                workspace_id=db_matter.workspace_id,
                name=db_matter.name,
                client_name=db_matter.client_name,
                description=db_matter.description,
                status=db_matter.status,
                is_pinned=db_matter.is_pinned,
                created_at=db_matter.created_at,
                updated_at=db_matter.updated_at
            ) for db_matter in result.scalars().all()
        ]

    async def save_contract_analysis(self, analysis: ContractAnalysis) -> ContractAnalysis:
        db_analysis = ContractAnalysisDB(
            id=analysis.id,
            matter_id=analysis.matter_id,
            asset_id=analysis.asset_id,
            workspace_id=analysis.workspace_id,
            executive_summary=analysis.executive_summary,
            clauses=[c.model_dump() for c in analysis.clauses],
            risk_profile=analysis.risk_profile.model_dump() if analysis.risk_profile else None,
            timeline=[t.model_dump() for t in analysis.timeline],
            created_at=analysis.created_at,
            updated_at=analysis.updated_at
        )
        self.session.add(db_analysis)
        await self.session.flush()
        return analysis

    async def get_contract_analysis(self, asset_id: str, workspace_id: str) -> Optional[ContractAnalysis]:
        stmt = select(ContractAnalysisDB).where(
            ContractAnalysisDB.asset_id == asset_id,
            ContractAnalysisDB.workspace_id == workspace_id
        )
        result = await self.session.execute(stmt)
        db_analysis = result.scalar_one_or_none()
        if not db_analysis:
            return None
        return ContractAnalysis(
            id=db_analysis.id,
            matter_id=db_analysis.matter_id,
            asset_id=db_analysis.asset_id,
            workspace_id=db_analysis.workspace_id,
            executive_summary=db_analysis.executive_summary,
            clauses=db_analysis.clauses,
            risk_profile=db_analysis.risk_profile,
            timeline=db_analysis.timeline,
            created_at=db_analysis.created_at,
            updated_at=db_analysis.updated_at
        )

    async def save_compliance_report(self, report: ComplianceReport) -> ComplianceReport:
        db_report = ComplianceReportDB(
            id=report.id,
            matter_id=report.matter_id,
            asset_ids=report.asset_ids,
            workspace_id=report.workspace_id,
            framework=report.framework,
            score=report.score,
            violations=report.violations,
            missing_requirements=report.missing_requirements,
            recommendations=report.recommendations,
            created_at=report.created_at
        )
        self.session.add(db_report)
        await self.session.flush()
        return report

    async def get_compliance_reports(self, matter_id: str, workspace_id: str) -> List[ComplianceReport]:
        stmt = select(ComplianceReportDB).where(
            ComplianceReportDB.matter_id == matter_id,
            ComplianceReportDB.workspace_id == workspace_id
        ).order_by(ComplianceReportDB.created_at.desc())
        result = await self.session.execute(stmt)
        return [
            ComplianceReport(
                id=db_report.id,
                matter_id=db_report.matter_id,
                asset_ids=db_report.asset_ids,
                workspace_id=db_report.workspace_id,
                framework=db_report.framework,
                score=db_report.score,
                violations=db_report.violations,
                missing_requirements=db_report.missing_requirements,
                recommendations=db_report.recommendations,
                created_at=db_report.created_at
            ) for db_report in result.scalars().all()
        ]

import pytest
import uuid
from datetime import datetime, timezone
from app.domain.legal import LegalMatter, ContractAnalysis, ExtractedClause, ClauseCategory, RiskProfile, RiskLevel, TimelineEvent, ComplianceReport

def test_legal_matter_creation():
    matter = LegalMatter(
        id=str(uuid.uuid4()),
        workspace_id="ws_1",
        name="Test Matter",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    assert matter.name == "Test Matter"
    assert matter.status == "Active"

def test_contract_analysis_model():
    clause = ExtractedClause(
        id=str(uuid.uuid4()),
        category=ClauseCategory.LIABILITY,
        text="Liability is capped at 1 million.",
        confidence_score=0.95
    )
    risk = RiskProfile(
        risk_score=50,
        level=RiskLevel.MEDIUM,
        high_risk_clauses=[],
        missing_clauses=["Governing Law"],
        compliance_concerns=[],
        summary="Medium risk due to missing governing law."
    )
    timeline = TimelineEvent(
        date="2026-10-01",
        event_type="Expiration",
        description="Contract expires on this date."
    )
    
    analysis = ContractAnalysis(
        id=str(uuid.uuid4()),
        matter_id="matter_1",
        asset_id="asset_1",
        workspace_id="ws_1",
        executive_summary="Summary of contract.",
        clauses=[clause],
        risk_profile=risk,
        timeline=[timeline],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    assert analysis.matter_id == "matter_1"
    assert len(analysis.clauses) == 1
    assert analysis.clauses[0].category == ClauseCategory.LIABILITY
    assert analysis.risk_profile.level == RiskLevel.MEDIUM
    assert len(analysis.timeline) == 1

def test_compliance_report_model():
    report = ComplianceReport(
        id=str(uuid.uuid4()),
        matter_id="matter_1",
        asset_ids=["asset_1"],
        workspace_id="ws_1",
        framework="GDPR",
        score=85.0,
        violations=[{"type": "Missing Data Processing Agreement"}],
        missing_requirements=["Article 28 DPA"],
        recommendations=["Draft and sign a DPA."],
        created_at=datetime.now(timezone.utc)
    )
    
    assert report.framework == "GDPR"
    assert report.score == 85.0
    assert len(report.missing_requirements) == 1

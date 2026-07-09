from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ClauseCategory(str, Enum):
    DEFINITIONS = "Definitions"
    PARTIES = "Parties"
    EFFECTIVE_DATE = "Effective Date"
    EXPIRATION = "Expiration"
    RENEWAL = "Renewal"
    PAYMENT = "Payment"
    CONFIDENTIALITY = "Confidentiality"
    TERMINATION = "Termination"
    LIABILITY = "Liability"
    INDEMNIFICATION = "Indemnification"
    FORCE_MAJEURE = "Force Majeure"
    JURISDICTION = "Jurisdiction"
    GOVERNING_LAW = "Governing Law"
    DISPUTE_RESOLUTION = "Dispute Resolution"
    DATA_PRIVACY = "Data Privacy"
    GDPR = "GDPR"
    INTELLECTUAL_PROPERTY = "Intellectual Property"
    ASSIGNMENT = "Assignment"
    WARRANTY = "Warranty"
    OBLIGATIONS = "Obligations"
    DEADLINES = "Deadlines"
    PENALTIES = "Penalties"
    OTHER = "Other"

class RiskLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"

class LegalMatter(BaseModel):
    id: str
    workspace_id: str
    name: str
    client_name: Optional[str] = None
    description: Optional[str] = None
    status: str = "Active" # Active, Closed, On Hold
    is_pinned: bool = False
    created_at: datetime
    updated_at: datetime

class ExtractedClause(BaseModel):
    id: str
    category: ClauseCategory
    text: str
    page_number: Optional[int] = None
    confidence_score: float = 1.0
    explanation_plain_english: Optional[str] = None
    negotiation_suggestions: Optional[str] = None
    is_ambiguous: bool = False
    is_one_sided: bool = False

class RiskProfile(BaseModel):
    risk_score: int = Field(ge=0, le=100) # 0 to 100
    level: RiskLevel
    high_risk_clauses: List[str] = Field(default_factory=list) # IDs of clauses
    missing_clauses: List[str] = Field(default_factory=list)
    compliance_concerns: List[str] = Field(default_factory=list)
    summary: str

class TimelineEvent(BaseModel):
    date: str # ISO Date or approximate e.g. "Upon execution"
    event_type: str # Renewal, Termination, Deadline
    description: str
    related_clause_id: Optional[str] = None

class ContractAnalysis(BaseModel):
    id: str
    matter_id: str
    asset_id: str
    workspace_id: str
    executive_summary: str
    clauses: List[ExtractedClause] = Field(default_factory=list)
    risk_profile: Optional[RiskProfile] = None
    timeline: List[TimelineEvent] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

class ComplianceReport(BaseModel):
    id: str
    matter_id: str
    asset_ids: List[str]
    workspace_id: str
    framework: str # GDPR, HIPAA, SOC2, etc.
    score: float
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    created_at: datetime

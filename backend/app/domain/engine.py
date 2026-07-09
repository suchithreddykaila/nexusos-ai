from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class QueryPlan(BaseModel):
    """
    Structured query plan formulated by the Query Understanding Service.
    """
    original_query: str
    intent: str  # compare, summarize, explain, search, list, translate, analyze
    workspace_id: str
    project_id: Optional[str] = None
    collection_id: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    strategy: str = "hybrid"  # semantic, keyword, hybrid
    complexity: str = "simple"  # simple, compound, complex

class Citation(BaseModel):
    """
    Reference back to a KnowledgeAsset supporting an AI answer.
    """
    id: str = Field(description="Unique citation ID matching inline marks")
    asset_id: str
    asset_name: str
    snippet: str
    page_number: Optional[int] = None
    chunk_index: Optional[int] = None
    confidence_score: float = 1.0

class EngineResponse(BaseModel):
    """
    Unified intelligence response containing citations and metrics tags.
    """
    response_text: str
    citations: List[Citation] = Field(default_factory=list)
    provider_used: str
    model_used: str
    latency_ms: float = 0.0
    tokens_used: int = 0
    validated: bool = True

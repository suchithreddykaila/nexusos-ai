from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    """
    Search request wrapper mapping semantic queries and filters.
    """
    query: str = Field(description="Search string keywords or semantic queries")
    limit: int = Field(default=10, description="Max results count to fetch")
    offset: int = Field(default=0, description="Pagination offset index")
    filters: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Filter flags (e.g. classification=['pdf'], workspace_id='work123')"
    )

class SearchResultItem(BaseModel):
    """
    Unified representation of a search hit, regardless of storage origin.
    """
    title: str = Field(description="Title of matched record (e.g. document name, command name)")
    item_type: str = Field(
        description="Type category (e.g. 'document', 'workflow', 'chat', 'setting', 'command')"
    )
    score: float = Field(default=1.0, description="Relevance ranking score (0.0 to 1.0)")
    description: Optional[str] = Field(default=None, description="Matched context snippet or subtitle")
    redirect_url: Optional[str] = Field(default=None, description="UI route mapped to this search result")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchResult(BaseModel):
    """
    Aggregated search response payload containing metrics logs.
    """
    query: str
    total_results: int
    items: List[SearchResultItem] = Field(default_factory=list)
    search_latency_ms: float = 0.0

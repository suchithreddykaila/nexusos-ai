from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ResearchSession(BaseModel):
    """
    Research workspace session context tracking selected sources.
    """
    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    asset_ids: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

class ResearchNote(BaseModel):
    """
    Markdown study note linked to research sources and citation facts.
    """
    id: str
    session_id: str
    title: str
    content: str  # Markdown editor rich content text
    linked_asset_ids: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

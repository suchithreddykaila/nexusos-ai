from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class StepExecution(BaseModel):
    """
    Tracing details of an individual plan step execution.
    """
    step_id: str
    description: str
    assigned_agent: Optional[str] = None
    applied_tool: Optional[str] = None
    input_args: Dict[str, Any] = Field(default_factory=dict)
    output_result: Optional[Any] = None
    status: str = "pending"  # pending, running, completed, failed

class WorkingMemory(BaseModel):
    """
    Short-lived scratchpad storage tracking active execution plans and subtasks context.
    """
    active_plan_id: Optional[str] = None
    steps: List[StepExecution] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)

class ShortTermMemory(BaseModel):
    """
    Standard chat session window context.
    """
    session_id: str
    messages: List[Dict[str, str]] = Field(default_factory=list)
    token_count: int = Field(default=0)

class WorkspaceContext(BaseModel):
    """
    Workspace specific operational parameters.
    """
    workspace_id: str
    workspace_role: str = "member"
    active_project_id: Optional[str] = None
    recent_documents: List[str] = Field(default_factory=list)
    recent_search_queries: List[str] = Field(default_factory=list)

class UserPreferences(BaseModel):
    theme: str = "light"
    default_ai_provider: str = "ollama"
    custom_ui_layout: Dict[str, Any] = Field(default_factory=dict)

class LayeredMemory(BaseModel):
    """
    Unified OS session context aggregating all active memory layers.
    """
    session_id: str
    user_id: str
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    working: WorkingMemory = Field(default_factory=WorkingMemory)
    chat: Optional[ShortTermMemory] = None
    workspace: Optional[WorkspaceContext] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class WorkflowNode(BaseModel):
    """
    Schema representing a single functional unit or step in a processing pipeline.
    """
    node_id: str = Field(description="Unique node identifier")
    name: str = Field(description="Display label of the step (e.g. OCR, Embed)")
    node_type: str = Field(description="Class of task executor (e.g., 'document_parse', 'vector_index')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Configuration parameters")
    max_retries: int = Field(default=2)
    retry_delay_seconds: int = Field(default=5)
    status: str = "pending"  # pending, running, completed, failed
    error_message: Optional[str] = None

class WorkflowEdge(BaseModel):
    """
    Defines transition edges between execution nodes.
    """
    edge_id: str
    source_node_id: str
    target_node_id: str
    condition: Optional[str] = Field(default=None, description="Conditional routing expression")

class WorkflowGraph(BaseModel):
    """
    Comprehensive pipeline definition containing nodes, edges, and dependencies.
    """
    graph_id: str
    name: str
    description: str
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)

class WorkflowExecutionContext(BaseModel):
    """
    Tracks state and data values flowing through nodes during a workflow execution session.
    """
    execution_id: str
    graph_id: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed

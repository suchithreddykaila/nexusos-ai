from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ToolDefinition(BaseModel):
    """
    Standard schema describing a tool's parameters and settings to LLMs.
    """
    name: str = Field(description="System identifier for the tool")
    description: str = Field(description="Documentation explaining what the tool does")
    parameters_schema: Dict[str, Any] = Field(description="JSON schema describing function parameters")
    timeout_seconds: int = Field(default=30, description="Max execution time before cancellation")
    max_retries: int = Field(default=2, description="Max retry attempts on network failures")
    requires_permission: Optional[str] = Field(default=None, description="RBAC scope required to execute this tool")

class ToolResult(BaseModel):
    """
    Unified container enclosing tool execution telemetry.
    """
    success: bool
    output: Any
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0

class BaseTool(ABC):
    """
    Abstract base class mapping execution contracts for all operational tools.
    """
    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """
        Execute core tool logic using structured arguments.
        """
        pass

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class SessionMemory(BaseModel):
    current_page: str = Field(default="/")
    selected_workspace: Optional[str] = None
    recent_documents: List[str] = Field(default_factory=list)
    recent_searches: List[str] = Field(default_factory=list)
    selected_provider: str = Field(default="ollama")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)

class AgentResponse(BaseModel):
    text: str = Field(description="Natural language response text compiled by the agent")
    navigate_to: Optional[str] = Field(default=None, description="Suggested UI page URL mapping if user requests redirects")
    execute_command: Optional[str] = Field(default=None, description="System transaction command if user executes actions")
    confidence_score: float = Field(default=1.0, description="Confidence estimation of target task parsing (0.0 to 1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SpecializedAgent(ABC):
    """
    Abstract Base Class for all modular agents in the OS agent registry.
    """
    @property
    @abstractmethod
    def unique_id(self) -> str:
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """
        Agent domain category (e.g. 'system', 'search', 'legal', 'finance')
        """
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def supported_tools(self) -> List[str]:
        """
        List of registered tool names that this agent is permitted to execute
        """
        pass

    @property
    @abstractmethod
    def required_permissions(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def execution_priority(self) -> int:
        """
        Higher priority agents are evaluated first by the task planner (range: 1 - 100)
        """
        pass

    @abstractmethod
    async def execute(
        self, 
        query: str, 
        session_memory: SessionMemory,
        api_provider: Any
    ) -> AgentResponse:
        """
        Execute core agent reasoning.
        """
        pass

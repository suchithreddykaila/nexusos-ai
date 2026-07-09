from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ModelMetadata(BaseModel):
    name: str = Field(description="Display name of the model")
    id: str = Field(description="Unique system identifier for the model (e.g., llama3.2:3b)")
    context_length: int = Field(description="Context window token limit")
    supports_streaming: bool = Field(default=True)
    supports_tools: bool = Field(default=False)
    supports_structured_output: bool = Field(default=False)
    cost_per_million_input: float = Field(default=0.0)
    cost_per_million_output: float = Field(default=0.0)

class AIProviderMetadata(BaseModel):
    name: str = Field(description="Provider identifier (e.g., ollama, gemini)")
    display_name: str = Field(description="Human-readable provider title")
    is_offline: bool = Field(description="Indicates if model runs locally without networking")
    is_configured: bool = Field(default=False, description="Flag indicating environment keys are valid")
    models: List[ModelMetadata] = Field(default_factory=list)

class ToolSpecification(BaseModel):
    name: str = Field(description="Function name to expose to the model")
    description: str = Field(description="Detailed documentation explaining tool execution logic")
    parameters_schema: Dict[str, Any] = Field(description="JSON schema describing expected function arguments")

class ToolCall(BaseModel):
    call_id: str
    name: str
    arguments: Dict[str, Any]

class AIResponse(BaseModel):
    text: str
    tool_calls: List[ToolCall] = Field(default_factory=list)
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

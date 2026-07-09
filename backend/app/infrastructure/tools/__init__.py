# Dynamic tool registries and system executables
from app.domain.tools import BaseTool, ToolDefinition, ToolResult
from app.infrastructure.tools.registry import tool_registry, register_tool
import app.infrastructure.tools.workspace_tools
import app.infrastructure.tools.knowledge_tools
import app.infrastructure.tools.legal_tools


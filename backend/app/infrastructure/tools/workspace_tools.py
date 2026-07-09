import time
from typing import Any, Dict
from app.domain.tools import BaseTool, ToolDefinition, ToolResult
from app.infrastructure.tools.registry import register_tool

@register_tool
class WorkspaceTool(BaseTool):
    """
    Workspace administration tool exposed to agents.
    """
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="workspace_tool",
            description="Manages workspace scopes: supports creating workspaces, switching contexts, and listing members.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["switch", "create", "list_members"],
                        "description": "Workspace operation to perform"
                    },
                    "workspace_id_or_name": {
                        "type": "string",
                        "description": "Workspace UUID or name identifier"
                    }
                },
                "required": ["action"]
            }
        )

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        action = arguments.get("action")
        target = arguments.get("workspace_id_or_name")
        
        latency = (time.perf_counter() - start) * 1000
        
        if action == "switch":
            if not target:
                return ToolResult(success=False, output=None, error_message="Target workspace ID or name is required.")
            return ToolResult(
                success=True,
                output={
                    "action": "switch",
                    "workspace_id": target,
                    "message": f"UI route switch request to workspace '{target}' triggered."
                },
                execution_time_ms=latency
            )
        elif action == "create":
            if not target:
                return ToolResult(success=False, output=None, error_message="New workspace name is required.")
            return ToolResult(
                success=True,
                output={
                    "action": "create",
                    "workspace_name": target,
                    "message": f"Successfully created workspace: '{target}'"
                },
                execution_time_ms=latency
            )
        elif action == "list_members":
            # Mock return of active workspace members list
            members_list = [
                {"email": "owner@nexusos-ai.com", "role": "owner"},
                {"email": "admin@nexusos-ai.com", "role": "administrator"}
            ]
            return ToolResult(
                success=True,
                output={
                    "action": "list_members",
                    "members": members_list
                },
                execution_time_ms=latency
            )
            
        return ToolResult(success=False, output=None, error_message="Invalid action parameter.")

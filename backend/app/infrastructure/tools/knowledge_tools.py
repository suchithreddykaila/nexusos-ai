import time
from typing import Any, Dict
from app.domain.tools import BaseTool, ToolDefinition, ToolResult
from app.infrastructure.tools.registry import register_tool

@register_tool
class KnowledgeTool(BaseTool):
    """
    Knowledge Organization tool exposed to agents.
    """
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="knowledge_tool",
            description="Manages projects, collections, folders, and assets: supports creating folders, moving assets, and searching indexing tags.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create_project", "create_folder", "move_folder", "search_assets"],
                        "description": "The knowledge operation to execute"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the project, collection, or folder to create"
                    },
                    "target_id": {
                        "type": "string",
                        "description": "Target ID of the asset or folder to move"
                    },
                    "parent_id": {
                        "type": "string",
                        "description": "Destination parent folder ID"
                    }
                },
                "required": ["action"]
            }
        )

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        action = arguments.get("action")
        name = arguments.get("name")
        target_id = arguments.get("target_id")
        parent_id = arguments.get("parent_id")
        
        latency = (time.perf_counter() - start) * 1000
        
        if action == "create_project":
            if not name:
                return ToolResult(success=False, output=None, error_message="Project name is required.")
            return ToolResult(
                success=True,
                output={
                    "action": "create_project",
                    "project_id": "proj-mock-created-uuid",
                    "name": name,
                    "message": f"Successfully created project '{name}'"
                },
                execution_time_ms=latency
            )
        elif action == "create_folder":
            if not name:
                return ToolResult(success=False, output=None, error_message="Folder name is required.")
            return ToolResult(
                success=True,
                output={
                    "action": "create_folder",
                    "folder_id": "folder-mock-created-uuid",
                    "name": name,
                    "message": f"Successfully created folder '{name}'"
                },
                execution_time_ms=latency
            )
        elif action == "move_folder":
            if not target_id:
                return ToolResult(success=False, output=None, error_message="Target folder ID is required.")
            return ToolResult(
                success=True,
                output={
                    "action": "move_folder",
                    "folder_id": target_id,
                    "parent_id": parent_id,
                    "message": f"Moved folder '{target_id}' under parent '{parent_id}'"
                },
                execution_time_ms=latency
            )
        elif action == "search_assets":
            # Mock return of searched assets list
            found = [
                {"id": "asset-1", "name": "q4_financials.pdf", "type": "document"},
                {"id": "asset-2", "name": "system_specs.png", "type": "image"}
            ]
            return ToolResult(
                success=True,
                output={
                    "action": "search_assets",
                    "results": found
                },
                execution_time_ms=latency
            )

        return ToolResult(success=False, output=None, error_message="Invalid action parameter.")

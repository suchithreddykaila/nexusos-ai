import time
from typing import Any, Dict
from app.domain.tools import BaseTool, ToolDefinition, ToolResult
from app.infrastructure.tools.registry import register_tool

@register_tool
class NavigationTool(BaseTool):
    """
    Tool exposed to agents to redirect the frontend viewport to a specific page.
    """
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="navigation_tool",
            description="Redirects the user interface viewport to a target system workspace page.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Target page route path (e.g. '/settings', '/documents', '/analytics')"
                    }
                },
                "required": ["destination"]
            }
        )

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        destination = arguments.get("destination")
        if not destination:
            return ToolResult(
                success=False, 
                output=None, 
                error_message="Parameter 'destination' is required."
            )
        
        latency = (time.perf_counter() - start) * 1000
        return ToolResult(
            success=True,
            output={
                "action": "navigate",
                "destination": destination,
                "status": "success"
            },
            execution_time_ms=latency
        )

@register_tool
class SystemDiagnosticsTool(BaseTool):
    """
    Tool exposed to agents to query and retrieve connection telemetry of active services.
    """
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="system_diagnostics_tool",
            description="Queries database status values and connection telemetry to build a system health map.",
            parameters_schema={"type": "object", "properties": {}}
        )

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        
        # Retrieve mocked systems telemetry checks for scaffolding tests
        telemetry_map = {
            "relational_db": "postgresql-connected",
            "vector_store": "chromadb-active",
            "graph_database": "neo4j-connected",
            "object_storage": "minio-healthy",
            "broker_cache": "redis-online",
            "worker_status": "celery-listening"
        }
        
        latency = (time.perf_counter() - start) * 1000
        return ToolResult(
            success=True,
            output=telemetry_map,
            execution_time_ms=latency
        )

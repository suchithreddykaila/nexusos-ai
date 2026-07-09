import logging
from typing import Dict, List, Type
from app.domain.tools import BaseTool, ToolDefinition

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Central operational database holding all system-execution tools.
    """
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool_instance: BaseTool):
        name = tool_instance.definition.name.lower()
        self._tools[name] = tool_instance
        logger.info(f"System execution tool registered: '{tool_instance.definition.name}'")

    def get_tool(self, name: str) -> BaseTool:
        tool = self._tools.get(name.lower())
        if not tool:
            raise ValueError(f"Tool '{name}' is not registered in the system.")
        return tool

    def list_tools(self) -> List[ToolDefinition]:
        return [tool.definition for tool in self._tools.values()]

# Global tool registry singleton instance
tool_registry = ToolRegistry()

def register_tool(cls: Type[BaseTool]):
    """
    Decorator to auto-register BaseTool classes dynamically during import sweeps.
    """
    try:
        instance = cls()
        tool_registry.register(instance)
    except Exception as e:
        logger.error(f"Failed to auto-register tool class {cls.__name__}: {e}")
    return cls

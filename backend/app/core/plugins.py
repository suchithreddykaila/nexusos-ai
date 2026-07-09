import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from app.domain.assistant import SpecializedAgent
from app.domain.tools import BaseTool

logger = logging.getLogger(__name__)

class BasePlugin(ABC):
    """
    Abstract contract defining modular boundaries for NexusOS AI plugins.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialization hook called when the plugin is loaded into the system.
        """
        pass

    def get_agents(self) -> List[SpecializedAgent]:
        return []

    def get_tools(self) -> List[BaseTool]:
        return []


class PluginManager:
    """
    System-level controller discovering and activating modular plugins.
    """
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}

    async def register_plugin(self, plugin: BasePlugin):
        name = plugin.name.lower()
        if name in self._plugins:
            logger.warning(f"Plugin '{plugin.name}' is already registered. Overwriting.")
        
        # Initialize plugin
        await plugin.initialize()
        self._plugins[name] = plugin
        logger.info(f"Plugin '{plugin.name}' (v{plugin.version}) loaded successfully.")

    def get_plugin(self, name: str) -> BasePlugin:
        plugin = self._plugins.get(name.lower())
        if not plugin:
            raise ValueError(f"Plugin '{name}' is not registered.")
        return plugin

    def list_plugins(self) -> List[BasePlugin]:
        return list(self._plugins.values())

# Global plugin manager singleton
plugin_manager = PluginManager()

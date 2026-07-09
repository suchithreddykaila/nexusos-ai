import logging
from typing import Dict, List, Type
from app.domain.assistant import SpecializedAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Central repository of all operational agents in the AI Operating System.
    """
    def __init__(self):
        self._agents: Dict[str, SpecializedAgent] = {}

    def register(self, agent_instance: SpecializedAgent):
        uid = agent_instance.unique_id.lower()
        self._agents[uid] = agent_instance
        logger.info(f"Registered Agent: '{agent_instance.display_name}' [{uid}]")

    def get_agent(self, unique_id: str) -> SpecializedAgent:
        agent = self._agents.get(unique_id.lower())
        if not agent:
            raise ValueError(f"Agent '{unique_id}' is not registered in the system.")
        return agent

    def list_agents(self) -> List[SpecializedAgent]:
        return list(self._agents.values())

    def get_agents_by_category(self, category: str) -> List[SpecializedAgent]:
        return [a for a in self._agents.values() if a.category.lower() == category.lower()]

# Global agent registry singleton instance
agent_registry = AgentRegistry()

def register_agent(cls: Type[SpecializedAgent]):
    """
    Decorator to dynamically register SpecializedAgent classes during imports.
    """
    try:
        instance = cls()
        agent_registry.register(instance)
    except Exception as e:
        logger.error(f"Failed to dynamically register agent class {cls.__name__}: {e}")
    return cls

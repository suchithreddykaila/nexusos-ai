from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.domain.knowledge import KnowledgeAsset

class ICognitiveProcessor(ABC):
    """
    Abstract Base Class representing a plugin-driven cognitive processing stage.
    """
    @property
    @abstractmethod
    def processor_id(self) -> str:
        """Returns the unique string ID for this processor."""
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """Returns the execution priority weight (higher runs earlier if no dependency exists)."""
        pass

    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """Returns the list of processor IDs that must execute successfully before this step."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Executed during registry setup or worker startup."""
        pass

    @abstractmethod
    async def validate(self, asset: KnowledgeAsset) -> bool:
        """Checks if the asset matches requirements for processing."""
        pass

    @abstractmethod
    async def can_process(self, asset: KnowledgeAsset) -> bool:
        """Dynamic check returning whether the asset can run through this stage."""
        pass

    @abstractmethod
    async def before_execute(self, asset: KnowledgeAsset) -> KnowledgeAsset:
        """Pre-execution hook (e.g. stage setups)."""
        pass

    @abstractmethod
    async def execute(self, asset: KnowledgeAsset, context: Dict[str, Any]) -> KnowledgeAsset:
        """Primary execution block containing core processing logic."""
        pass

    @abstractmethod
    async def after_execute(self, asset: KnowledgeAsset) -> KnowledgeAsset:
        """Post-execution hook (e.g. database checkpoint preps)."""
        pass

    @abstractmethod
    async def rollback(self, asset: KnowledgeAsset) -> KnowledgeAsset:
        """Rollback state updates if execution crashes subsequently in the pipeline."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Closes file descriptors or frees memory blocks."""
        pass

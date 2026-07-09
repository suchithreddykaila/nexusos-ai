import logging
from typing import Dict, List, Type, Optional
from app.domain.cognitive import ICognitiveProcessor

logger = logging.getLogger(__name__)

class ProcessorRegistry:
    _registry: Dict[str, Type[ICognitiveProcessor]] = {}

    @classmethod
    def register(cls, processor_cls: Type[ICognitiveProcessor]) -> Type[ICognitiveProcessor]:
        p_id = processor_cls.processor_id
        if not p_id:
            raise ValueError(f"Processor ID cannot be empty on class: {processor_cls.__name__}")
        cls._registry[p_id] = processor_cls
        logger.info(f"Processor registered dynamically: '{p_id}' ({processor_cls.__name__})")
        return processor_cls

    @classmethod
    def get_all(cls) -> List[Type[ICognitiveProcessor]]:
        return list(cls._registry.values())

    @classmethod
    def get(cls, processor_id: str) -> Optional[Type[ICognitiveProcessor]]:
        return cls._registry.get(processor_id)

def register_processor(processor_cls: Type[ICognitiveProcessor]) -> Type[ICognitiveProcessor]:
    """
    Decorator for registering cognitive processors.
    """
    ProcessorRegistry.register(processor_cls)
    return processor_cls

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List, Optional

class AIProvider(ABC):
    """
    Abstract Base Class defining the contract for all AI Model Providers (offline & cloud).
    """

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generates a non-streaming text response.
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generates a streaming text response chunk-by-chunk.
        """
        yield ""

    @abstractmethod
    async def get_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generates dense vector embeddings for a list of texts.
        """
        pass

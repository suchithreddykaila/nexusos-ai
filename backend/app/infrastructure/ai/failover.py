import logging
from typing import AsyncGenerator, Dict, List, Optional
from app.infrastructure.ai.provider import AIProvider
from app.infrastructure.ai.registry import provider_registry

logger = logging.getLogger(__name__)

class FailoverAIProviderProxy(AIProvider):
    """
    Proxy implementation of AIProvider that wraps a sequence of preferred models
    and automatically falls back to secondary options if primary providers fail.
    """
    def __init__(self, preferred_order: List[str]):
        self.preferred_order = [name.lower() for name in preferred_order]
        if not self.preferred_order:
            raise ValueError("Preferred provider chain order cannot be empty.")

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        errors = []
        for name in self.preferred_order:
            try:
                provider = provider_registry.get_provider(name)
                # Verify configurations before attempting call
                is_healthy = await provider_registry.check_health(name)
                if not is_healthy and name != self.preferred_order[-1]:
                    raise RuntimeError(f"Provider '{name}' health check failed.")
                
                logger.info(f"Routing text generation request to provider: '{name}'")
                return await provider.generate_text(prompt, system_instruction, history)
            except Exception as e:
                logger.warning(f"AI Provider '{name}' failed execution: {e}. Attempting fallback...")
                errors.append(f"{name}: {e}")
        
        raise RuntimeError(f"All providers in failover chain failed. Diagnostics: {', '.join(errors)}")

    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        errors = []
        for name in self.preferred_order:
            try:
                provider = provider_registry.get_provider(name)
                is_healthy = await provider_registry.check_health(name)
                if not is_healthy and name != self.preferred_order[-1]:
                    raise RuntimeError(f"Provider '{name}' health check failed.")
                
                logger.info(f"Routing stream generation request to provider: '{name}'")
                async for chunk in provider.generate_stream(prompt, system_instruction, history):
                    yield chunk
                return
            except Exception as e:
                logger.warning(f"AI Provider '{name}' stream execution failed: {e}. Attempting fallback...")
                errors.append(f"{name}: {e}")
        
        raise RuntimeError(f"All streaming providers in failover chain failed. Diagnostics: {', '.join(errors)}")

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        errors = []
        for name in self.preferred_order:
            try:
                provider = provider_registry.get_provider(name)
                is_healthy = await provider_registry.check_health(name)
                if not is_healthy and name != self.preferred_order[-1]:
                    raise RuntimeError(f"Provider '{name}' health check failed.")
                
                logger.info(f"Routing embedding generation request to provider: '{name}'")
                return await provider.get_embeddings(texts)
            except Exception as e:
                logger.warning(f"AI Provider '{name}' embedding execution failed: {e}. Attempting fallback...")
                errors.append(f"{name}: {e}")
        
        raise RuntimeError(f"All embedding providers in failover chain failed. Diagnostics: {', '.join(errors)}")

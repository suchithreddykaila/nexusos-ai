import logging
from typing import Dict, List, Optional
import httpx
from app.core.config import settings
from app.domain.ai import AIProviderMetadata, ModelMetadata
from app.infrastructure.ai.provider import AIProvider
from app.infrastructure.ai.ollama import OllamaProvider
from app.infrastructure.ai.gemini import GeminiProvider

logger = logging.getLogger(__name__)

class AIProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, AIProvider] = {}
        # Pre-seed providers
        self._providers["ollama"] = OllamaProvider()
        self._providers["gemini"] = GeminiProvider()

    def register_provider(self, name: str, provider: AIProvider):
        """
        Allows dynamically registering new providers at runtime.
        """
        self._providers[name.lower()] = provider
        logger.info(f"AI Provider '{name}' registered successfully.")

    def get_provider(self, name: str) -> AIProvider:
        prov = self._providers.get(name.lower())
        if not prov:
            raise ValueError(f"AI Provider '{name}' is not registered in the system.")
        return prov

    async def get_provider_metadata(self, name: str) -> AIProviderMetadata:
        name = name.lower()
        if name == "ollama":
            is_configured = False
            models = []
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                    if response.status_code == 200:
                        is_configured = True
                        data = response.json()
                        for model_info in data.get("models", []):
                            model_id = model_info.get("name")
                            models.append(ModelMetadata(
                                name=model_id.split(":")[0].title(),
                                id=model_id,
                                context_length=4096,
                                supports_tools=True,
                                supports_structured_output=True
                            ))
            except Exception:
                logger.warning("Ollama local daemon is not reachable during metadata check.")
                
            if not models:
                models = [
                    ModelMetadata(
                        name="Llama 3.2 (Offline Default)", 
                        id=settings.DEFAULT_OFFLINE_MODEL, 
                        context_length=4096
                    )
                ]

            return AIProviderMetadata(
                name="ollama",
                display_name="Ollama (Local Offline)",
                is_offline=True,
                is_configured=is_configured,
                models=models
            )

        elif name == "gemini":
            is_configured = settings.GEMINI_API_KEY is not None
            models = [
                ModelMetadata(
                    name="Gemini 2.5 Flash",
                    id="gemini-2.5-flash",
                    context_length=1048576,
                    supports_tools=True,
                    supports_structured_output=True
                ),
                ModelMetadata(
                    name="Gemini 1.5 Flash",
                    id="gemini-1.5-flash",
                    context_length=1048576,
                    supports_tools=True,
                    supports_structured_output=True
                )
            ]
            return AIProviderMetadata(
                name="gemini",
                display_name="Google Gemini (Cloud)",
                is_offline=False,
                is_configured=is_configured,
                models=models
            )
        else:
            raise ValueError(f"Unknown AI Provider: '{name}'")

    async def check_health(self, name: str) -> bool:
        """
        Check if the provider connection is active and responsive.
        """
        try:
            metadata = await self.get_provider_metadata(name)
            if name.lower() == "ollama":
                return metadata.is_configured
            elif name.lower() == "gemini":
                return metadata.is_configured  # Configuration checks for API key loading status
        except Exception:
            return False
        return False

# Global provider registry singleton
provider_registry = AIProviderRegistry()

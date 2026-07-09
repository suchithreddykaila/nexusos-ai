from typing import Optional
from app.core.config import settings
from app.infrastructure.ai.provider import AIProvider
from app.infrastructure.ai.ollama import OllamaProvider
from app.infrastructure.ai.gemini import GeminiProvider

class AIProviderFactory:
    @staticmethod
    def get_provider(provider_name: Optional[str] = None) -> AIProvider:
        """
        Dynamically return the appropriate AI provider (e.g. 'ollama' or 'gemini').
        Defaults to the system's default provider configuration.
        """
        name = (provider_name or settings.DEFAULT_PROVIDER).lower()
        if name == "ollama":
            return OllamaProvider()
        elif name == "gemini":
            return GeminiProvider()
        else:
            raise ValueError(f"Unknown AI Provider: {provider_name}. Supported providers are 'ollama' and 'gemini'.")

# Singleton instance for standard use cases
ai_factory = AIProviderFactory()

import json
import logging
from typing import AsyncGenerator, Dict, List, Optional
import httpx
from app.core.config import settings
from app.infrastructure.ai.provider import AIProvider

logger = logging.getLogger(__name__)

class OllamaProvider(AIProvider):
    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, model: str = settings.DEFAULT_OFFLINE_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise RuntimeError(f"Ollama provider failed: {e}")

    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            chunk = data.get("message", {}).get("content", "")
                            if chunk:
                                yield chunk
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise RuntimeError(f"Ollama stream failed: {e}")

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for text in texts:
                payload = {
                    "model": self.model,
                    "prompt": text
                }
                try:
                    response = await client.post(f"{self.base_url}/api/embeddings", json=payload)
                    response.raise_for_status()
                    data = response.json()
                    embeddings.append(data.get("embedding", []))
                except Exception as e:
                    logger.error(f"Ollama embedding error: {e}")
                    raise RuntimeError(f"Ollama embedding failed: {e}")
        return embeddings

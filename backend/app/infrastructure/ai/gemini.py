import asyncio
import logging
from typing import AsyncGenerator, Dict, List, Optional
import google.generativeai as genai
from app.core.config import settings
from app.infrastructure.ai.provider import AIProvider

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = settings.GEMINI_API_KEY, model_name: str = settings.DEFAULT_CLOUD_MODEL):
        self.model_name = model_name
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            logger.warning("Gemini API Key is not set. GeminiProvider will require configuration to run.")

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        if not self.api_key:
            raise ValueError("Gemini API Key is missing. Configure GEMINI_API_KEY in backend settings.")
        
        contents = []
        if history:
            for item in history:
                role = "user" if item.get("role") == "user" else "model"
                contents.append({"role": role, "parts": [item.get("content", "")]})
        contents.append({"role": "user", "parts": [prompt]})
        
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction

        try:
            model = genai.GenerativeModel(self.model_name)
            response = await model.generate_content_async(
                contents=contents,
                generation_config=config
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise RuntimeError(f"Gemini provider failed: {e}")

    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            raise ValueError("Gemini API Key is missing. Configure GEMINI_API_KEY in backend settings.")
        
        contents = []
        if history:
            for item in history:
                role = "user" if item.get("role") == "user" else "model"
                contents.append({"role": role, "parts": [item.get("content", "")]})
        contents.append({"role": "user", "parts": [prompt]})

        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction

        try:
            model = genai.GenerativeModel(self.model_name)
            response = await model.generate_content_async(
                contents=contents,
                generation_config=config,
                stream=True
            )
            async for chunk in response:
                yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise RuntimeError(f"Gemini stream failed: {e}")

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            raise ValueError("Gemini API Key is missing. Configure GEMINI_API_KEY in backend settings.")
        
        try:
            model = "models/text-embedding-004"
            # Wrap the blocking SDK call in asyncio.to_thread to keep it async friendly
            response = await asyncio.to_thread(
                genai.embed_content,
                model=model,
                content=texts,
                task_type="retrieval_document"
            )
            embeddings = response.get("embedding", [])
            # Ensure return format is list of lists
            if len(texts) == 1 and embeddings and not isinstance(embeddings[0], list):
                return [embeddings]
            return embeddings
        except Exception as e:
            logger.error(f"Gemini embedding error: {e}")
            raise RuntimeError(f"Gemini embedding failed: {e}")

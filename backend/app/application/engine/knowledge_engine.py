import time
import json
import logging
from typing import AsyncGenerator, Dict, List, Optional
from app.domain.engine import EngineResponse, QueryPlan
from app.domain.repositories import IAssetRepository
from app.infrastructure.ai.failover import FailoverAIProviderProxy
from app.application.engine.query_understanding import QueryUnderstandingService
from app.application.engine.retrieval import RetrievalService
from app.application.engine.ranking import RankingEngine
from app.application.engine.context_assembly import ContextAssemblyService
from app.application.engine.prompt_constructor import PromptConstructor
from app.application.engine.response_validation import ResponseValidationService

logger = logging.getLogger(__name__)

class AIKnowledgeEngine:
    def __init__(self, asset_repo: IAssetRepository):
        self.query_service = QueryUnderstandingService()
        self.retrieval_service = RetrievalService(asset_repo)
        self.ranking_engine = RankingEngine()
        self.context_service = ContextAssemblyService()
        self.prompt_constructor = PromptConstructor()
        self.validation_service = ResponseValidationService()

    async def query_knowledge(
        self,
        query: str,
        workspace_id: str,
        project_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        preferred_provider: str = "ollama"
    ) -> EngineResponse:
        start_time = time.perf_counter()
        
        # 1. Query Understanding
        plan = await self.query_service.analyze_query(query, workspace_id, project_id, collection_id)
        
        # 2. Retrieval
        retrieved = await self.retrieval_service.retrieve_knowledge(plan)
        
        # 3. Ranking
        reranked = await self.ranking_engine.rerank_results(retrieved)
        
        # 4. Context Assembly
        context_str, citations = await self.context_service.assemble_context(reranked)
        
        # 5. Prompt Construction
        messages = self.prompt_constructor.build_prompt(query, context_str, history)
        
        # Extract prompt text and system instructions for failover execution
        system_instr = messages[0]["content"]
        user_prompt = messages[-1]["content"]
        chat_history = messages[1:-1]

        # 6. Execute Provider Call with Failover Setup
        preferred_chain = [preferred_provider, "ollama", "gemini"]
        # De-duplicate chain
        chain = []
        for p in preferred_chain:
            if p not in chain:
                chain.append(p)
                
        provider_proxy = FailoverAIProviderProxy(preferred_order=chain)
        
        raw_response = await provider_proxy.generate_text(
            prompt=user_prompt,
            system_instruction=system_instr,
            history=chat_history
        )

        latency = (time.perf_counter() - start_time) * 1000

        # Construct raw response
        response = EngineResponse(
            response_text=raw_response,
            citations=citations,
            provider_used=chain[0],
            model_used="default",
            latency_ms=latency,
            tokens_used=len(raw_response.split())  # Mock token count estimation
        )

        # 7. Validate citations alignment
        validated_response = await self.validation_service.validate_response(response)
        return validated_response

    async def query_stream(
        self,
        query: str,
        workspace_id: str,
        project_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        preferred_provider: str = "ollama"
    ) -> AsyncGenerator[str, None]:
        # 1. Query Understanding
        plan = await self.query_service.analyze_query(query, workspace_id, project_id, collection_id)
        
        # 2. Retrieval & Ranking
        retrieved = await self.retrieval_service.retrieve_knowledge(plan)
        reranked = await self.ranking_engine.rerank_results(retrieved)
        context_str, citations = await self.context_service.assemble_context(reranked)
        
        # Send initial chunk containing citations metadata so the frontend gets them immediately
        yield f"data: {json.dumps({'citations': [c.dict() for c in citations], 'status': 'started'})}\n\n"
        
        # 3. Prompt Builder
        messages = self.prompt_constructor.build_prompt(query, context_str, history)
        system_instr = messages[0]["content"]
        user_prompt = messages[-1]["content"]
        chat_history = messages[1:-1]

        preferred_chain = [preferred_provider, "ollama", "gemini"]
        chain = []
        for p in preferred_chain:
            if p not in chain:
                chain.append(p)

        provider_proxy = FailoverAIProviderProxy(preferred_order=chain)
        
        # 4. Stream response
        try:
            async for chunk in provider_proxy.generate_stream(
                prompt=user_prompt,
                system_instruction=system_instr,
                history=chat_history
            ):
                yield f"data: {json.dumps({'text': chunk, 'status': 'streaming'})}\n\n"
        except Exception as e:
            logger.error(f"Streaming provider chain exception: {e}")
            yield f"data: {json.dumps({'error': str(e), 'status': 'failed'})}\n\n"
            return

        yield f"data: {json.dumps({'status': 'completed'})}\n\n"

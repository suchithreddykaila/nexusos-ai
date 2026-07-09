import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

# Add backend root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.domain.knowledge import KnowledgeAsset
from app.domain.search import SearchResultItem
from app.application.engine.query_understanding import QueryUnderstandingService
from app.application.engine.retrieval import RetrievalService
from app.application.engine.ranking import RankingEngine
from app.application.engine.context_assembly import ContextAssemblyService
from app.application.engine.prompt_constructor import PromptConstructor
from app.application.engine.response_validation import ResponseValidationService
from app.application.engine.knowledge_engine import AIKnowledgeEngine
from app.domain.engine import EngineResponse, Citation

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.list_assets = AsyncMock()
    repo.get_asset = AsyncMock()
    return repo

@pytest.mark.asyncio
async def test_query_understanding_classification():
    service = QueryUnderstandingService()
    plan = await service.analyze_query("Please compare document A and document B", "ws_123")
    
    assert plan.intent == "compare"
    assert plan.workspace_id == "ws_123"
    assert plan.strategy == "hybrid"

@pytest.mark.asyncio
async def test_retrieval_service_filtering():
    mock_repo = MagicMock()
    mock_repo.list_assets = AsyncMock(return_value=[
        KnowledgeAsset(
            id="asset_1", folder_id=None, workspace_id="ws_123", name="Confidential Contract",
            asset_type="document", status="completed", processing_stage="completed",
            details={}, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
        ),
        KnowledgeAsset(
            id="asset_2", folder_id=None, workspace_id="ws_123", name="Design Specs",
            asset_type="document", status="completed", processing_stage="completed",
            details={}, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
        )
    ])
    
    service = RetrievalService(mock_repo)
    # Search for contract
    from app.domain.engine import QueryPlan
    plan = QueryPlan(original_query="Contract", intent="search", workspace_id="ws_123")
    
    results = await service.retrieve_knowledge(plan)
    assert len(results) == 1
    assert results[0].title == "Confidential Contract"
    assert results[0].score > 0.0

@pytest.mark.asyncio
async def test_ranking_engine_boosts():
    engine = RankingEngine()
    items = [
        SearchResultItem(
            title="Old doc", item_type="document", score=0.6, description="",
            metadata={"details": {"pipeline_status": {"status": "completed"}}}
        )
    ]
    reranked = await engine.rerank_results(items)
    # Verify completed state boost (0.6 + 0.1 = 0.7)
    assert reranked[0].score == 0.7

@pytest.mark.asyncio
async def test_context_assembly_token_budget():
    service = ContextAssemblyService()
    items = [
        SearchResultItem(title="A", item_type="document", score=0.9, description="Desc A", metadata={"asset_id": "a"}),
        SearchResultItem(title="B", item_type="document", score=0.8, description="Desc B", metadata={"asset_id": "b"})
    ]
    # Set small budget (say, 30 chars) to check aggregation cap
    context_str, citations = await service.assemble_context(items, token_budget=30)
    assert "Source 1" in context_str
    assert len(citations) == 1  # Source 2 should be skipped due to token limits

@pytest.mark.asyncio
async def test_response_validation_citations():
    service = ResponseValidationService()
    response = EngineResponse(
        response_text="Based on [cit_1], the system is offline.",
        citations=[
            Citation(id="cit_1", asset_id="1", asset_name="Policy.pdf", snippet="Offline policy"),
            Citation(id="cit_2", asset_id="2", asset_name="Guide.txt", snippet="Unused citation")
        ],
        provider_used="ollama", model_used="llama"
    )
    validated = await service.validate_response(response)
    # Check that unused cit_2 was filtered out
    assert len(validated.citations) == 1
    assert validated.citations[0].id == "cit_1"

@pytest.mark.asyncio
@patch("app.application.engine.knowledge_engine.FailoverAIProviderProxy")
async def test_knowledge_engine_query(mock_proxy_cls, mock_repo):
    mock_proxy = MagicMock()
    mock_proxy.generate_text = AsyncMock(return_value="Mocked response content [cit_1]")
    mock_proxy_cls.return_value = mock_proxy
    
    mock_repo.list_assets = AsyncMock(return_value=[
        KnowledgeAsset(
            id="asset_1", folder_id=None, workspace_id="ws_123", name="Policy Manual",
            asset_type="document", status="completed", processing_stage="completed",
            details={}, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
        )
    ])
    
    engine = AIKnowledgeEngine(mock_repo)
    response = await engine.query_knowledge(
        query="What is the policy?",
        workspace_id="ws_123",
        preferred_provider="ollama"
    )
    
    assert response.response_text == "Mocked response content [cit_1]"
    assert len(response.citations) == 1
    assert response.citations[0].asset_name == "Policy Manual"

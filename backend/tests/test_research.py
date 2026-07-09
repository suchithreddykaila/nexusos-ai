import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

# Add backend root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.domain.knowledge import KnowledgeAsset
from app.domain.research import ResearchSession, ResearchNote
from app.application.services.research_service import ResearchService
from app.application.engine.knowledge_engine import AIKnowledgeEngine
from app.domain.engine import EngineResponse, Citation

@pytest.fixture
def mock_db():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    return session

@pytest.fixture
def mock_engine():
    engine = MagicMock(spec=AIKnowledgeEngine)
    engine.context_service = MagicMock()
    engine.context_service.assemble_context = AsyncMock(return_value=("Mock context", []))
    engine.prompt_constructor = MagicMock()
    engine.prompt_constructor.build_prompt = MagicMock(return_value=[
        {"role": "system", "content": "Instructions"},
        {"role": "user", "content": "Query"}
    ])
    engine.validation_service = MagicMock()
    engine.validation_service.validate_response = AsyncMock(side_effect=lambda x: x)
    return engine

@pytest.mark.asyncio
async def test_create_session(mock_db, mock_engine):
    service = ResearchService(mock_db, mock_engine)
    session = await service.create_session(
        ws_id="ws_123",
        name="Study on Transformers",
        description="Transformer analysis session",
        asset_ids=["asset_1", "asset_2"]
    )
    
    assert session.name == "Study on Transformers"
    assert session.workspace_id == "ws_123"
    assert "asset_1" in session.asset_ids
    assert mock_db.add.called
    assert mock_db.flush.called

@pytest.mark.asyncio
async def test_bibliography_formatting(mock_db, mock_engine):
    service = ResearchService(mock_db, mock_engine)
    
    mock_asset = KnowledgeAsset(
        id="asset_1", folder_id=None, workspace_id="ws_123", name="Neural Networks Intro",
        asset_type="document", status="completed", processing_stage="completed",
        details={
            "document_metadata": {
                "author": "Y. LeCun",
                "publication_year": "2015",
                "publisher": "MIT Press"
            }
        },
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Mock database select return for get_asset inside generate_bibliography
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_asset)
    mock_db.execute.return_value = mock_result
    
    # Generate APA
    apa_list = await service.generate_bibliography(["asset_1"], style="apa")
    assert len(apa_list) == 1
    assert apa_list[0] == "Y. LeCun. (2015). Neural Networks Intro. MIT Press."

    # Generate IEEE
    ieee_list = await service.generate_bibliography(["asset_1"], style="ieee")
    assert len(ieee_list) == 1
    assert ieee_list[0] == "[1] Y. LeCun, \"Neural Networks Intro,\" MIT Press, 2015."

@pytest.mark.asyncio
@patch("app.application.services.research_service.FailoverAIProviderProxy")
async def test_query_selected_sources(mock_proxy_cls, mock_db, mock_engine):
    mock_proxy = MagicMock()
    mock_proxy.generate_text = AsyncMock(return_value="Mocked comparative answer [cit_1]")
    mock_proxy_cls.return_value = mock_proxy
    
    mock_asset = KnowledgeAsset(
        id="asset_1", folder_id=None, workspace_id="ws_123", name="Specs.pdf",
        asset_type="document", status="completed", processing_stage="completed",
        details={}, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_asset)
    mock_db.execute.return_value = mock_result

    service = ResearchService(mock_db, mock_engine)
    response = await service.query_selected_sources(
        query="What are the specs?",
        workspace_id="ws_123",
        asset_ids=["asset_1"]
    )
    
    assert response.response_text == "Mocked comparative answer [cit_1]"
    assert mock_proxy.generate_text.called

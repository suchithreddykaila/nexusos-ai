import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from typing import List, Dict, Any

# Add backend root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.domain.knowledge import KnowledgeAsset
from app.domain.cognitive import ICognitiveProcessor
from app.application.cognitive.pipeline import CognitivePipeline, resolve_dependencies
from app.application.cognitive.processors import (
    ValidatingProcessor,
    ExtractionProcessor,
    ChunkingProcessor,
    EmbeddingProcessor,
    GraphLinkerProcessor
)

@pytest.fixture
def mock_service():
    service = MagicMock()
    service.asset_repo = MagicMock()
    service.asset_repo.get_asset = AsyncMock()
    service.asset_repo.update_asset = AsyncMock()
    service.update_user_asset_status = AsyncMock()
    return service

def test_dependency_topological_resolution():
    p1 = ValidatingProcessor()
    p2 = ExtractionProcessor()
    p3 = ChunkingProcessor()
    p4 = EmbeddingProcessor()
    p5 = GraphLinkerProcessor()
    
    # Sort them
    ordered = resolve_dependencies([p5, p4, p3, p2, p1])
    
    # Assert correct dependency sequence: validation -> extraction -> chunking -> embedding -> graph_linker
    ids = [p.processor_id for p in ordered]
    assert ids == ["validation", "extraction", "chunking", "embedding", "graph_linker"]

@pytest.mark.asyncio
async def test_pipeline_execution_flow(mock_service):
    asset_id = "asset_111"
    ws_id = "ws_123"
    user_id = "user_abc"
    
    mock_asset = KnowledgeAsset(
        id=asset_id,
        folder_id=None,
        workspace_id=ws_id,
        name="contract.pdf",
        asset_type="document",
        status="pending",
        processing_stage="pending",
        details={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    mock_service.asset_repo.get_asset.return_value = mock_asset
    mock_service.update_user_asset_status.return_value = mock_asset
    
    pipeline = CognitivePipeline(mock_service)
    await pipeline.run_pipeline(asset_id, ws_id, user_id)
    
    # Verify execution checkpoints
    assert mock_service.asset_repo.get_asset.called
    assert mock_service.update_user_asset_status.call_count >= 6
    assert mock_service.asset_repo.update_asset.call_count >= 5

@pytest.mark.asyncio
async def test_pipeline_checkpoint_resume(mock_service):
    asset_id = "asset_222"
    ws_id = "ws_123"
    user_id = "user_abc"
    
    # Mock asset that already completed "validation" and "extraction"
    mock_asset = KnowledgeAsset(
        id=asset_id,
        folder_id=None,
        workspace_id=ws_id,
        name="contract.pdf",
        asset_type="document",
        status="processing",
        processing_stage="extraction",
        details={
            "pipeline_status": {
                "status": "processing",
                "completed_processors": ["validation", "extraction"]
            }
        },
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    mock_service.asset_repo.get_asset.return_value = mock_asset
    mock_service.update_user_asset_status.return_value = mock_asset
    
    pipeline = CognitivePipeline(mock_service)
    await pipeline.run_pipeline(asset_id, ws_id, user_id)
    
    # We should only run "chunking", "embedding", and "graph_linker" (3 processors)
    # Plus initial status setup and final completed setup
    assert mock_service.update_user_asset_status.call_count >= 5
    
    # Verify the skipped stages are still in the completed list
    completed = mock_asset.details["pipeline_status"]["completed_processors"]
    assert "validation" in completed
    assert "extraction" in completed
    assert "chunking" in completed
    assert "embedding" in completed
    assert "graph_linker" in completed

@pytest.mark.asyncio
async def test_pipeline_retry_resiliency(mock_service):
    pipeline = CognitivePipeline(mock_service)
    
    mock_processor = MagicMock(spec=ICognitiveProcessor)
    mock_processor.processor_id = "retry_stage"
    mock_processor.priority = 100
    mock_processor.dependencies = []
    
    mock_processor.initialize = AsyncMock()
    mock_processor.validate = AsyncMock(return_value=True)
    mock_processor.can_process = AsyncMock(return_value=True)
    mock_processor.before_execute = AsyncMock(side_effect=lambda x: x)
    mock_processor.after_execute = AsyncMock(side_effect=lambda x: x)
    mock_processor.rollback = AsyncMock()
    mock_processor.cleanup = AsyncMock()
    
    # Fail once, then succeed on second attempt
    mock_processor.execute = AsyncMock(side_effect=[
        ValueError("Transient rate limit"),
        KnowledgeAsset(
            id="a", folder_id=None, workspace_id="w", name="n", asset_type="document",
            status="pending", processing_stage="retry_stage", details={"retried": True},
            created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
        )
    ])
    
    asset = KnowledgeAsset(
        id="a", folder_id=None, workspace_id="w", name="n", asset_type="document",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    
    enriched = await pipeline.execute_processor_with_retry(
        mock_processor, asset, max_retries=3, backoff_delay=0.01
    )
    
    assert enriched.details.get("retried") is True
    assert mock_processor.execute.call_count == 2
    assert mock_processor.rollback.call_count == 1

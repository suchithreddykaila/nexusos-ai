import time
import logging
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Type
from app.domain.cognitive import ICognitiveProcessor
from app.domain.knowledge import KnowledgeAsset, AssetStatus, AssetProcessingStage
from app.application.services.knowledge_service import KnowledgeService
from app.application.cognitive.registry import ProcessorRegistry

logger = logging.getLogger(__name__)

def resolve_dependencies(processors: List[ICognitiveProcessor]) -> List[ICognitiveProcessor]:
    """
    Kahn's Topological Sort Algorithm to resolve execution order.
    """
    proc_map = {p.processor_id: p for p in processors}
    
    # Track in-degrees (number of prerequisites) and adjacency list
    in_degree = {p.processor_id: 0 for p in processors}
    adj = {p.processor_id: [] for p in processors}
    
    for p in processors:
        for dep in p.dependencies:
            if dep in proc_map:
                adj[dep].append(p.processor_id)
                in_degree[p.processor_id] += 1
                
    # Add nodes with 0 in-degree to queue, sorting by priority desc
    queue = [p for p in processors if in_degree[p.processor_id] == 0]
    queue.sort(key=lambda x: x.priority, reverse=True)
    
    sorted_order = []
    
    while queue:
        # Resolve higher priority first if in-degrees match 0
        curr = queue.pop(0)
        sorted_order.append(curr)
        
        for neighbor in adj[curr.processor_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                # Insert and re-sort by priority desc
                queue.append(proc_map[neighbor])
                queue.sort(key=lambda x: x.priority, reverse=True)
                
    if len(sorted_order) != len(processors):
        raise ValueError("Circular dependency detected in Cognitive Processors.")
        
    return sorted_order

class CognitivePipeline:
    def __init__(self, knowledge_service: KnowledgeService):
        self.service = knowledge_service

    async def execute_processor_with_retry(
        self, 
        processor: ICognitiveProcessor, 
        asset: KnowledgeAsset, 
        max_retries: int = 3, 
        backoff_delay: float = 1.0
    ) -> KnowledgeAsset:
        attempt = 0
        await processor.initialize()
        
        while attempt < max_retries:
            try:
                if not await processor.validate(asset) or not await processor.can_process(asset):
                    logger.info(f"Skipping processor {processor.processor_id} for asset {asset.id}")
                    return asset

                asset = await processor.before_execute(asset)
                start = time.perf_counter()
                
                # Core execute run
                asset = await processor.execute(asset, {})
                
                duration = (time.perf_counter() - start) * 1000
                asset = await processor.after_execute(asset)
                
                logger.info(f"Processor {processor.processor_id} completed successfully in {duration:.2f}ms.")
                return asset
            except Exception as e:
                attempt += 1
                logger.warning(
                    f"Processor {processor.processor_id} execution attempt {attempt}/{max_retries} failed: {e}"
                )
                await processor.rollback(asset)
                if attempt >= max_retries:
                    await processor.cleanup()
                    raise e
                await asyncio.sleep(backoff_delay * (2 ** (attempt - 1)))
                
        await processor.cleanup()
        return asset

    async def run_pipeline(self, asset_id: str, ws_id: str, user_id: str):
        logger.info(f"Initiating dynamic cognitive pipeline for asset {asset_id}")
        
        # Load asset
        asset = await self.service.asset_repo.get_asset(asset_id)
        if not asset:
            logger.error(f"Asset {asset_id} not found. Aborting.")
            return

        # Fetch and instantiate all registered processors dynamically
        registered_classes = ProcessorRegistry.get_all()
        processor_instances = [cls() for cls in registered_classes]
        
        # Resolve dependencies
        ordered_processors = resolve_dependencies(processor_instances)

        # Initialize checkpoint details if missing
        if "pipeline_status" not in asset.details:
            asset.details["pipeline_status"] = {
                "status": "pending",
                "completed_processors": [],
                "failed_processor": None
            }

        completed_ids: List[str] = asset.details["pipeline_status"]["completed_processors"]

        # Mark pipeline as processing
        asset = await self.service.update_user_asset_status(
            asset_id=asset_id,
            ws_id=ws_id,
            user_id=user_id,
            status=AssetStatus.PROCESSING.value,
            stage=AssetProcessingStage.PENDING.value
        )
        asset.details["pipeline_status"]["status"] = "processing"
        await self.service.asset_repo.update_asset(asset_id=asset_id, details=asset.details)

        try:
            for processor in ordered_processors:
                p_id = processor.processor_id
                
                # Checkpoint resumability check
                if p_id in completed_ids:
                    logger.info(f"Checkpoint match: skipping completed processor '{p_id}'")
                    continue
                    
                # Update current active stage
                asset = await self.service.update_user_asset_status(
                    asset_id=asset_id,
                    ws_id=ws_id,
                    user_id=user_id,
                    status=AssetStatus.PROCESSING.value,
                    stage=p_id
                )
                
                # Execute processor stage
                asset = await self.execute_processor_with_retry(processor, asset)
                
                # Write Checkpoint save state
                completed_ids.append(p_id)
                asset.details["pipeline_status"]["completed_processors"] = completed_ids
                asset.details["pipeline_status"]["last_checkpoint_at"] = datetime.now(timezone.utc).isoformat()
                
                await self.service.asset_repo.update_asset(
                    asset_id=asset_id,
                    details=asset.details,
                    checksum=asset.checksum
                )

            # Pipeline finished successfully
            asset.details["pipeline_status"]["status"] = "completed"
            asset.details["pipeline_status"]["failed_processor"] = None
            await self.service.asset_repo.update_asset(asset_id=asset_id, details=asset.details)

            await self.service.update_user_asset_status(
                asset_id=asset_id,
                ws_id=ws_id,
                user_id=user_id,
                status=AssetStatus.COMPLETED.value,
                stage=AssetProcessingStage.COMPLETED.value
            )
            logger.info(f"Pipeline finished successfully for asset {asset_id}")

        except Exception as e:
            logger.error(f"Pipeline crashed on asset {asset_id}: {e}")
            
            # Save failed processor details
            asset.details["pipeline_status"]["status"] = "failed"
            # Trace which processor failed
            failed_p_id = None
            for p in ordered_processors:
                if p.processor_id not in completed_ids:
                    failed_p_id = p.processor_id
                    break
            asset.details["pipeline_status"]["failed_processor"] = failed_p_id
            await self.service.asset_repo.update_asset(asset_id=asset_id, details=asset.details)

            await self.service.update_user_asset_status(
                asset_id=asset_id,
                ws_id=ws_id,
                user_id=user_id,
                status=AssetStatus.FAILED.value,
                stage=AssetProcessingStage.PENDING.value
            )

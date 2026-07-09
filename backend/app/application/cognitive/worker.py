import logging
import asyncio
from app.infrastructure.events.dispatcher import event_bus
from app.domain.events import AssetCreatedEvent
from app.application.cognitive.pipeline import CognitivePipeline

logger = logging.getLogger(__name__)

class IngestionWorker:
    def __init__(self, pipeline: CognitivePipeline):
        self.pipeline = pipeline

    def start(self):
        logger.info("Registering IngestionWorker listeners on the Event Bus.")
        event_bus.subscribe(AssetCreatedEvent, self.handle_asset_created)

    async def handle_asset_created(self, event: AssetCreatedEvent):
        logger.info(f"AssetCreatedEvent captured for asset {event.asset_id}. Scheduling background processing.")
        
        # Schedule pipeline execution asynchronously in background task loops
        asyncio.create_task(
            self.pipeline.run_pipeline(
                asset_id=event.asset_id,
                ws_id=event.workspace_id,
                user_id="system_worker"
            )
        )

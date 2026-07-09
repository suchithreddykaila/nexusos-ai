import asyncio
import logging
from typing import Awaitable, Callable, Dict, List, Type
from app.domain.events import DomainEvent

logger = logging.getLogger(__name__)

class EventDispatcher:
    def __init__(self):
        # Maps event class types to list of asynchronous subscriber callbacks
        self._listeners: Dict[Type[DomainEvent], List[Callable[[DomainEvent], Awaitable[None]]]] = {}

    def subscribe(self, event_type: Type[DomainEvent], callback: Callable[[DomainEvent], Awaitable[None]]):
        """
        Register a subscriber callback for a specific DomainEvent type.
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)
            logger.info(f"Registered subscriber '{callback.__name__}' for event: '{event_type.__name__}'")

    async def publish(self, event: DomainEvent):
        """
        Publish a DomainEvent, triggering all registered subscribers asynchronously in the background.
        """
        event_type = type(event)
        if event_type not in self._listeners or not self._listeners[event_type]:
            logger.debug(f"No active subscribers registered for event type: '{event_type.__name__}'")
            return

        logger.info(f"Dispatching event '{event_type.__name__}' [Trace ID: {event.event_id}]")
        
        # Fire subscribers in independent asyncio tasks to decouple execution from the publisher thread
        for callback in self._listeners[event_type]:
            async def safe_execute_task(cb=callback, ev=event):
                try:
                    await cb(ev)
                except Exception as e:
                    logger.error(
                        f"Unhandled exception in subscriber '{cb.__name__}' "
                        f"while handling event '{type(ev).__name__}': {e}", 
                        exc_info=True
                    )

            asyncio.create_task(safe_execute_task())

# Platform-wide event bus singleton instance
event_bus = EventDispatcher()

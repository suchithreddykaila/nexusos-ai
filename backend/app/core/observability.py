import logging
import json
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

def setup_observability_logging():
    """
    Sets up structured JSON logging for unified service parsing in production.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])

class TelemetryTracker:
    """
    Context manager to trace execute latencies across database queries and model generations.
    """
    @staticmethod
    def trace_operation(component: str, action: str):
        class TelemetryContext:
            def __enter__(self):
                self.start = time.perf_counter()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                latency_ms = (time.perf_counter() - self.start) * 1000
                logger.info(
                    f"observability_telemetry: component='{component}' "
                    f"action='{action}' latency_ms={latency_ms:.2f} "
                    f"success={exc_type is None}"
                )
        return TelemetryContext()

# Global telemetry helper
telemetry = TelemetryTracker()

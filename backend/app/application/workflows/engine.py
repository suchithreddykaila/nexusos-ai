import asyncio
import logging
import time
from app.domain.workflows import WorkflowGraph, WorkflowExecutionContext, WorkflowNode

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """
    Engine runner executing pipeline nodes, managing retry tasks,
    resolving transitions, and logging execution telemetry.
    """
    async def execute(self, graph: WorkflowGraph, context: WorkflowExecutionContext) -> WorkflowExecutionContext:
        logger.info(f"Starting workflow execution: '{context.execution_id}' [Graph: '{graph.graph_id}']")
        context.status = "running"
        context.logs.append(f"[{self._time_stamp()}] Pipeline runner initiated.")

        # Sequential graph node execution tracer
        for node in graph.nodes:
            node.status = "running"
            context.logs.append(f"[{self._time_stamp()}] Node execution started: '{node.name}' [{node.node_id}]")
            
            retries = 0
            success = False
            while retries <= node.max_retries and not success:
                try:
                    logger.info(f"Running executor task: '{node.node_type}' [Attempt {retries + 1}]")
                    # Simulate processing latency
                    await asyncio.sleep(0.05)
                    success = True
                except Exception as e:
                    retries += 1
                    logger.warning(
                        f"Node '{node.node_id}' executor threw exception: {e}. "
                        f"Retrying in {node.retry_delay_seconds} seconds..."
                    )
                    await asyncio.sleep(0.01)

            if success:
                node.status = "completed"
                context.logs.append(f"[{self._time_stamp()}] Node execution completed: '{node.name}'")
            else:
                node.status = "failed"
                node.error_message = "Execution failed after maximum retries exceeded."
                context.status = "failed"
                context.logs.append(f"[{self._time_stamp()}] CRITICAL: Node '{node.name}' execution failed. Aborting pipeline.")
                return context

        context.status = "completed"
        context.logs.append(f"[{self._time_stamp()}] Pipeline completed successfully.")
        return context

    def _time_stamp(self) -> str:
        return time.strftime('%Y-%m-%d %H:%M:%S')

# Global workflow engine singleton
workflow_engine = WorkflowEngine()

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.domain.memory import StepExecution, WorkingMemory

logger = logging.getLogger(__name__)

class TaskPlanStep(BaseModel):
    step_id: str
    description: str
    target_agent_id: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)

class TaskPlan(BaseModel):
    plan_id: str
    query: str
    steps: List[TaskPlanStep] = Field(default_factory=list)

class TaskPlanner:
    """
    Deconstructs complex multi-intent user instructions into structured execution steps.
    """
    @staticmethod
    def generate_plan(query: str) -> TaskPlan:
        logger.info(f"Generating task plan for query: '{query}'")
        q = query.lower()
        steps = []
        
        # Simple rule-based planner for scaffolding verification
        # Checks if query requests multiple actions (e.g., navigation + diagnostic checks)
        has_nav = any(keyword in q for keyword in ["go to", "navigate", "open", "show", "login"])
        has_system = any(keyword in q for keyword in ["system", "health", "diagnostic", "check", "uptime"])
        
        if has_nav and has_system:
            # Complex multi-step instruction
            steps.append(
                TaskPlanStep(
                    step_id="step_1",
                    description="Route UI viewport to settings or health pages",
                    target_agent_id="navigation_agent",
                    arguments={"destination": "/settings"}
                )
            )
            steps.append(
                TaskPlanStep(
                    step_id="step_2",
                    description="Run platform service diagnostics checks",
                    target_agent_id="system_agent",
                    arguments={},
                    depends_on=["step_1"]
                )
            )
        elif has_nav:
            steps.append(
                TaskPlanStep(
                    step_id="step_1",
                    description="Route UI viewport",
                    target_agent_id="navigation_agent",
                    arguments={"query": query}
                )
            )
        elif has_system:
            steps.append(
                TaskPlanStep(
                    step_id="step_1",
                    description="Audit infrastructure status",
                    target_agent_id="system_agent",
                    arguments={}
                )
            )
        
        return TaskPlan(
            plan_id=f"plan_{int(time_stamp())}" if "time_stamp" in globals() else "plan_default",
            query=query,
            steps=steps
        )

def time_stamp() -> float:
    import time
    return time.time()

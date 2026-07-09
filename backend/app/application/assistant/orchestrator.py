import logging
from typing import Dict, List, Optional
from app.domain.assistant import SessionMemory, AgentResponse, SpecializedAgent
from app.domain.memory import WorkingMemory, StepExecution
from app.application.assistant.registry import agent_registry
from app.application.assistant.planner import TaskPlanner, TaskPlan
from app.infrastructure.ai.factory import ai_factory

logger = logging.getLogger(__name__)

class NyraOrchestrator:
    """
    Intelligent operating assistant coordinator that schedules execution plans
    across dynamic specialized agents registered with the OS.
    """
    async def process_query(self, query: str, session_memory: SessionMemory) -> AgentResponse:
        logger.info(f"Nyra deconstructing instruction: '{query}'")

        # 1. Generate Task Plan
        plan: TaskPlan = TaskPlanner.generate_plan(query)
        
        # 2. Check if a multi-step plan was planned
        if len(plan.steps) > 1:
            logger.info(f"Multi-agent plan generated with {len(plan.steps)} steps. Initiating task execution loop.")
            combined_texts = []
            final_navigate = None
            final_command = None
            
            # Initialize working memory scratchpad
            working_mem = WorkingMemory(active_plan_id=plan.plan_id)
            
            for step in plan.steps:
                try:
                    agent = agent_registry.get_agent(step.target_agent_id)
                    logger.info(f"Executing plan step '{step.step_id}' using Agent: '{agent.display_name}'")
                    
                    # Track step execution state
                    step_trace = StepExecution(
                        step_id=step.step_id,
                        description=step.description,
                        assigned_agent=agent.unique_id,
                        status="running"
                    )
                    working_mem.steps.append(step_trace)
                    
                    # Execute agent
                    response = await agent.execute(query, session_memory, None)
                    
                    step_trace.status = "completed"
                    step_trace.output_result = response.text
                    
                    combined_texts.append(response.text)
                    if response.navigate_to:
                        final_navigate = response.navigate_to
                    if response.execute_command:
                        final_command = response.execute_command
                        
                except Exception as e:
                    logger.error(f"Execution failure at plan step '{step.step_id}': {e}")
                    combined_texts.append(f"[Step Fail: {step.description} - Error: {e}]")
            
            return AgentResponse(
                text="\n\n".join(combined_texts),
                navigate_to=final_navigate,
                execute_command=final_command,
                confidence_score=0.95,
                metadata={"plan_steps_executed": len(plan.steps)}
            )

        # 3. Single-step / fallback execution path
        logger.info("Plan contains single task. Evaluating registry agents...")
        best_agent: Optional[SpecializedAgent] = None
        best_response: Optional[AgentResponse] = None
        highest_score = 0.0

        for agent in agent_registry.list_agents():
            try:
                response = await agent.execute(query, session_memory, None)
                if response.confidence_score > highest_score:
                    highest_score = response.confidence_score
                    best_agent = agent
                    best_response = response
            except Exception as e:
                logger.error(f"Error evaluating agent '{agent.unique_id}': {e}")

        if best_agent and highest_score >= 0.70:
            logger.info(f"Routed request to Agent: '{best_agent.display_name}' [Score: {highest_score}]")
            return best_response

        # 4. Downstream LLM Provider Fallback
        logger.info("Query does not match registry agents. Routing to default LLM Provider.")
        try:
            provider = ai_factory.get_provider(session_memory.selected_provider)
            system_instruction = (
                "You are Nyra, the intelligent operating assistant for NexusOS AI.\n"
                "You guide users, summarize documents, search databases, and manage workflows.\n"
                "Provide professional, well-formatted, and concise technical responses."
            )
            
            text_response = await provider.generate_text(
                prompt=query,
                system_instruction=system_instruction,
                history=session_memory.conversation_history
            )
            
            return AgentResponse(
                text=text_response,
                confidence_score=0.85,
                metadata={"provider_type": type(provider).__name__}
            )
        except Exception as e:
            logger.error(f"Fallback AI Provider routing failure: {e}")
            return AgentResponse(
                text=f"I was unable to complete your request due to a downstream AI Provider failure: {e}",
                confidence_score=0.0
            )

# Global orchestrator singleton instance
nyra_orchestrator = NyraOrchestrator()

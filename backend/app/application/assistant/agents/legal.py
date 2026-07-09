import logging
from typing import Any, Dict
from app.domain.assistant import AgentDefinition, AgentResult, BaseAgent
from app.infrastructure.tools.registry import tool_registry
from app.application.assistant.registry import register_agent

logger = logging.getLogger(__name__)

@register_agent
class LegalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            definition=AgentDefinition(
                id="legal_agent",
                name="Legal Intelligence Studio Agent",
                description="Specialized agent capable of analyzing contracts, extracting clauses, assessing risk, and generating compliance reports.",
                supported_intents=["analyze", "compare", "explain", "risk", "compliance", "timeline"]
            )
        )
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResult:
        logger.info(f"Legal Agent processing query: {query}")
        intent = context.get("intent", "analyze") if context else "analyze"
        
        tool_results = []
        
        try:
            if intent == "analyze":
                tool = tool_registry.get_tool("analyze_contract")
                res = await tool.execute(context)
                tool_results.append(res)
            elif intent == "compare":
                tool = tool_registry.get_tool("compare_contracts")
                res = await tool.execute(context)
                tool_results.append(res)
            elif intent == "compliance":
                tool = tool_registry.get_tool("generate_compliance_report")
                res = await tool.execute(context)
                tool_results.append(res)
            else:
                return AgentResult(
                    status="completed",
                    message="I can help you with legal analysis, but I need a specific task like analyzing a contract or running a compliance scan.",
                    data={"tool_executions": []}
                )
                
            return AgentResult(
                status="completed",
                message="Legal operation executed successfully.",
                data={"tool_executions": tool_results}
            )
            
        except Exception as e:
            logger.error(f"Legal Agent failed: {e}")
            return AgentResult(
                status="failed",
                message=f"Legal agent encountered an error: {e}",
                data={}
            )

from typing import List, Any
from app.domain.assistant import SpecializedAgent, AgentResponse, SessionMemory
from app.application.assistant.registry import register_agent

@register_agent
class NavigationAgent(SpecializedAgent):
    @property
    def unique_id(self) -> str:
        return "navigation_agent"

    @property
    def display_name(self) -> str:
        return "Navigation Agent"

    @property
    def description(self) -> str:
        return "Specialized in UI navigation, page redirection, and dashboard menu routing."

    @property
    def category(self) -> str:
        return "navigation"

    @property
    def capabilities(self) -> List[str]:
        return ["route_ui", "workspace_redirect"]

    @property
    def supported_tools(self) -> List[str]:
        return ["navigation_tool"]

    @property
    def required_permissions(self) -> List[str]:
        return ["navigate"]

    @property
    def execution_priority(self) -> int:
        return 90

    async def execute(
        self, 
        query: str, 
        session_memory: SessionMemory,
        api_provider: Any
    ) -> AgentResponse:
        q = query.lower()
        route = None
        confidence = 0.0

        if "member" in q or "invite" in q or "teammate" in q:
            route = "/settings"
            confidence = 0.98
        elif "workspace ai" in q or "ai overrides" in q:
            route = "/settings"
            confidence = 0.98
        elif "workspace storage" in q or "workspace activity" in q:
            route = "/settings"
            confidence = 0.98
        elif "setting" in q or "config" in q:
            route = "/settings"
            confidence = 0.98
        elif "document" in q or "file" in q or "upload" in q:
            route = "/documents"
            confidence = 0.95
        elif "workflow" in q or "automate" in q or "pipeline" in q:
            route = "/workflows"
            confidence = 0.95
        elif "graph" in q or "neo4j" in q or "relationship" in q:
            route = "/graph"
            confidence = 0.98
        elif "analytic" in q or "metric" in q or "latency" in q:
            route = "/analytics"
            confidence = 0.98
        elif "dashboard" in q or "home" in q or "overview" in q:
            route = "/"
            confidence = 0.95
        elif "profile" in q or "avatar" in q:
            route = "/profile"
            confidence = 0.98
        elif "security" in q or "password" in q or "session" in q or "device" in q:
            route = "/security"
            confidence = 0.98
        elif "logout" in q or "log out" in q or "sign out" in q:
            return AgentResponse(
                text="Logging you out of the platform...",
                navigate_to="/login",
                execute_command="logout",
                confidence_score=0.99
            )
        elif "login" in q or "signin" in q or "auth" in q:
            route = "/login"
            confidence = 0.98

        if route:
            display_name = route.strip("/").replace("-", " ").title() or "Dashboard"
            return AgentResponse(
                text=f"Routing you directly to the **{display_name}** view.",
                navigate_to=route,
                confidence_score=confidence
            )

        return AgentResponse(
            text="I detected a navigation command, but couldn't resolve the destination route. Try saying 'go to settings' or 'show analytics'.",
            confidence_score=0.3
        )

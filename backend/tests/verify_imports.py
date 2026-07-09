import sys
import os

# Add backend root directory to path for app imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Testing settings and config import...")
    from app.core.config import settings
    print(f"[OK] Settings imported. Project name: {settings.PROJECT_NAME}")

    print("Testing database engine and get_db import...")
    from app.core.database import get_db, engine
    print("[OK] Database imports successful.")

    print("Testing Domain Events schemas...")
    from app.domain.events import DomainEvent, DocumentUploadedEvent
    print("[OK] Domain Events schemas successfully verified.")

    print("Testing Asynchronous Event Dispatcher...")
    from app.infrastructure.events.dispatcher import event_bus
    print("[OK] Event Bus dispatcher successfully verified.")

    print("Testing AI Domain & Registry Modules...")
    from app.domain.ai import AIResponse, ToolCall
    from app.infrastructure.ai.registry import provider_registry
    from app.infrastructure.ai.failover import FailoverAIProviderProxy
    print("[OK] AI layers and provider registry successfully verified.")

    print("Testing Nyra Agent Assistant structures...")
    from app.domain.assistant import SessionMemory, SpecializedAgent
    from app.application.assistant.orchestrator import nyra_orchestrator
    from app.application.assistant.planner import TaskPlanner
    print("[OK] Nyra multi-agent frameworks successfully verified.")

    print("Testing Database Repositories & Adapters...")
    from app.domain.repositories import DocumentRepository
    from app.infrastructure.db.repositories.document import SQLDocumentRepository
    print("[OK] Database repositories patterns successfully verified.")

    print("Testing Telemetry & Observability...")
    from app.core.observability import telemetry, setup_observability_logging
    print("[OK] Telemetry and structured logging successfully verified.")

    print("Testing Tool Execution Framework...")
    from app.domain.tools import BaseTool, ToolResult
    from app.infrastructure.tools import tool_registry, register_tool
    import app.infrastructure.tools.system_tools
    print(f"[OK] Tool registry successfully verified. Registered: {[t.name for t in tool_registry.list_tools()]}")

    print("Testing Layered Memory Architecture...")
    from app.domain.memory import LayeredMemory, WorkingMemory, ShortTermMemory
    print("[OK] Layered memory schemas successfully verified.")

    print("Testing Node-based Workflow Engine...")
    from app.domain.workflows import WorkflowGraph, WorkflowNode
    from app.application.workflows import workflow_engine
    print("[OK] Workflow Engine modules successfully verified.")

    print("Testing Plugin SDK & Universal Search...")
    from app.core.plugins import plugin_manager, BasePlugin
    from app.domain.search import SearchQuery, SearchResult
    print("[OK] Plugins SDK and Search schemas successfully verified.")

    print("Testing Authentication Platform Modules...")
    from app.domain.auth import User, UserSession
    from app.infrastructure.db.models import UserDB, UserSessionDB
    from app.infrastructure.db.repositories.auth_repo import SQLUserRepository, SQLSessionRepository
    from app.application.services.auth_service import AuthService
    from app.api.deps import get_current_user, PermissionGuard
    from app.api.v1.auth import router as auth_router
    from app.api.v1.users import router as users_router
    from app.api.v1.assistant import router as assistant_router
    print("[OK] Authentication, Users, and Assistant routing successfully verified.")

    print("Testing Workspace Platform Modules...")
    from app.domain.workspaces import Workspace, WorkspaceMember
    from app.infrastructure.db.models import WorkspaceDB, WorkspaceMemberDB
    from app.infrastructure.db.repositories.workspace_repo import SQLWorkspaceRepository
    from app.application.services.workspace_service import WorkspaceService
    from app.api.v1.workspaces import router as workspaces_router
    print("[OK] Workspace Multi-Tenancy platform successfully verified.")

    print("Testing Knowledge Organization Platform Modules...")
    from app.domain.knowledge import Project, Collection, Folder, KnowledgeAsset
    from app.infrastructure.db.models import ProjectDB, CollectionDB, FolderDB, KnowledgeAssetDB
    from app.infrastructure.db.repositories.knowledge_repo import SQLKnowledgeRepository, SQLAssetRepository
    from app.application.services.knowledge_service import KnowledgeService
    from app.api.v1.knowledge import router as knowledge_router
    print("[OK] Knowledge Organization platform successfully verified.")

    print("Testing Cognitive Processing Engine Modules...")
    from app.domain.cognitive import ICognitiveProcessor
    from app.application.cognitive.pipeline import CognitivePipeline
    from app.application.cognitive.processors import ValidatingProcessor
    from app.application.cognitive.worker import IngestionWorker
    print("[OK] Cognitive Processing Engine successfully verified.")

    print("Testing AI Knowledge Engine Modules...")
    from app.domain.engine import QueryPlan, Citation, EngineResponse
    from app.application.engine.knowledge_engine import AIKnowledgeEngine
    print("[OK] AI Knowledge Engine successfully verified.")

    print("Testing Research Studio Schemas & Engine Modules...")
    from app.domain.research import ResearchSession, ResearchNote
    from app.application.services.research_service import ResearchService
    from app.api.v1.research import router as research_router
    print("[OK] AI Research Studio components successfully verified.")

    print("Testing Legal Intelligence Studio Schemas & Modules...")
    from app.domain.legal import LegalMatter, ContractAnalysis, ExtractedClause, ComplianceReport
    from app.application.services.legal_service import LegalService
    from app.api.v1.legal import router as legal_router
    from app.infrastructure.tools.legal_tools import AnalyzeContractTool, CompareContractsTool
    import app.application.assistant.agents.legal
    print("[OK] Legal Intelligence Studio components successfully verified.")

    print("\n✅ ALL BACKEND IMPORTS VERIFIED SUCCESSFULLY ✅")
except Exception as e:
    print(f"\n[FAILURE] Evolved architecture import check failed: {e}")
    sys.exit(1)

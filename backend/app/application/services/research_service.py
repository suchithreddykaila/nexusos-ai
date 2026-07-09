import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.research import ResearchSession, ResearchNote
from app.domain.engine import EngineResponse, Citation
from app.domain.search import SearchResultItem
from app.infrastructure.db.models import ResearchSessionDB, ResearchNoteDB, KnowledgeAssetDB
from app.application.engine.knowledge_engine import AIKnowledgeEngine
from app.infrastructure.ai.failover import FailoverAIProviderProxy

logger = logging.getLogger(__name__)

class ResearchService:
    def __init__(self, session: AsyncSession, engine: AIKnowledgeEngine):
        self.session = session
        self.engine = engine

    # --- Session Management ---
    async def create_session(
        self, 
        ws_id: str, 
        name: str, 
        description: Optional[str] = None, 
        asset_ids: List[str] = None
    ) -> ResearchSession:
        db_sess = ResearchSessionDB(
            id=str(uuid.uuid4()),
            workspace_id=ws_id,
            name=name,
            description=description,
            asset_ids=asset_ids or []
        )
        self.session.add(db_sess)
        await self.session.flush()
        return ResearchSession(
            id=db_sess.id,
            workspace_id=db_sess.workspace_id,
            name=db_sess.name,
            description=db_sess.description,
            asset_ids=db_sess.asset_ids,
            created_at=db_sess.created_at or datetime.now(timezone.utc),
            updated_at=db_sess.updated_at or datetime.now(timezone.utc)
        )

    async def get_session(self, session_id: str) -> Optional[ResearchSession]:
        res = await self.session.execute(select(ResearchSessionDB).where(ResearchSessionDB.id == session_id))
        db_sess = res.scalar_one_or_none()
        if not db_sess:
            return None
        return ResearchSession(
            id=db_sess.id,
            workspace_id=db_sess.workspace_id,
            name=db_sess.name,
            description=db_sess.description,
            asset_ids=db_sess.asset_ids,
            created_at=db_sess.created_at or datetime.now(timezone.utc),
            updated_at=db_sess.updated_at or datetime.now(timezone.utc)
        )

    # --- Notes Notepad ---
    async def create_note(
        self, 
        session_id: str, 
        title: str, 
        content: str, 
        linked_asset_ids: List[str] = None
    ) -> ResearchNote:
        db_note = ResearchNoteDB(
            id=str(uuid.uuid4()),
            session_id=session_id,
            title=title,
            content=content,
            linked_asset_ids=linked_asset_ids or []
        )
        self.session.add(db_note)
        await self.session.flush()
        return ResearchNote(
            id=db_note.id,
            session_id=db_note.session_id,
            title=db_note.title,
            content=db_note.content,
            linked_asset_ids=db_note.linked_asset_ids,
            created_at=db_note.created_at or datetime.now(timezone.utc),
            updated_at=db_note.updated_at or datetime.now(timezone.utc)
        )

    async def list_notes(self, session_id: str) -> List[ResearchNote]:
        res = await self.session.execute(select(ResearchNoteDB).where(ResearchNoteDB.session_id == session_id))
        return [
            ResearchNote(
                id=n.id,
                session_id=n.session_id,
                title=n.title,
                content=n.content,
                linked_asset_ids=n.linked_asset_ids,
                created_at=n.created_at or datetime.now(timezone.utc),
                updated_at=n.updated_at or datetime.now(timezone.utc)
            ) for n in res.scalars().all()
        ]

    async def update_note(
        self, 
        note_id: str, 
        title: Optional[str] = None, 
        content: Optional[str] = None, 
        linked_asset_ids: Optional[List[str]] = None
    ) -> ResearchNote:
        vals = {"updated_at": datetime.now(timezone.utc)}
        if title is not None: vals["title"] = title
        if content is not None: vals["content"] = content
        if linked_asset_ids is not None: vals["linked_asset_ids"] = linked_asset_ids

        await self.session.execute(update(ResearchNoteDB).where(ResearchNoteDB.id == note_id).values(**vals))
        res = await self.session.execute(select(ResearchNoteDB).where(ResearchNoteDB.id == note_id))
        n = res.scalar_one()
        return ResearchNote(
            id=n.id,
            session_id=n.session_id,
            title=n.title,
            content=n.content,
            linked_asset_ids=n.linked_asset_ids,
            created_at=n.created_at or datetime.now(timezone.utc),
            updated_at=n.updated_at or datetime.now(timezone.utc)
        )

    async def delete_note(self, note_id: str) -> bool:
        await self.session.execute(delete(ResearchNoteDB).where(ResearchNoteDB.id == note_id))
        return True

    # --- Multi-Document Focused Retrieval ---
    async def query_selected_sources(
        self,
        query: str,
        workspace_id: str,
        asset_ids: List[str],
        preferred_provider: str = "ollama"
    ) -> EngineResponse:
        retrieved_items = []
        for asset_id in asset_ids:
            res = await self.session.execute(select(KnowledgeAssetDB).where(KnowledgeAssetDB.id == asset_id))
            asset = res.scalar_one_or_none()
            if asset:
                snippet = f"Document: [{asset.name}]\n"
                if "system_metadata" in asset.details:
                    snippet += f"Mime-Type: {asset.details['system_metadata'].get('mime_type')}\n"
                if "document_metadata" in asset.details:
                    snippet += f"Details: {asset.details['document_metadata']}\n"
                retrieved_items.append(SearchResultItem(
                    title=asset.name,
                    item_type="document",
                    score=1.0,
                    description=snippet,
                    metadata={"asset_id": asset.id, "workspace_id": asset.workspace_id, "details": asset.details}
                ))

        context_str, citations = await self.engine.context_service.assemble_context(retrieved_items)
        messages = self.engine.prompt_constructor.build_prompt(
            query=query,
            context_str=context_str
        )
        system_instr = messages[0]["content"]
        user_prompt = messages[-1]["content"]

        provider_proxy = FailoverAIProviderProxy(preferred_order=[preferred_provider, "ollama", "gemini"])
        raw_response = await provider_proxy.generate_text(prompt=user_prompt, system_instruction=system_instr)

        response = EngineResponse(
            response_text=raw_response,
            citations=citations,
            provider_used=preferred_provider,
            model_used="default"
        )
        return await self.engine.validation_service.validate_response(response)

    # --- Bibliography formatting (APA, IEEE) ---
    async def generate_bibliography(self, asset_ids: List[str], style: str = "apa") -> List[str]:
        bibliography = []
        for index, asset_id in enumerate(asset_ids):
            res = await self.session.execute(select(KnowledgeAssetDB).where(KnowledgeAssetDB.id == asset_id))
            asset = res.scalar_one_or_none()
            if not asset:
                continue

            # Load default metadata
            author = "Unknown Author"
            year = "2026"
            publisher = "NexusOS Knowledge Repository"
            
            if "document_metadata" in asset.details:
                meta = asset.details["document_metadata"]
                author = meta.get("author", author)
                year = meta.get("publication_year", year)
                publisher = meta.get("publisher", publisher)

            title = asset.name

            if style.lower() == "apa":
                ref = f"{author}. ({year}). {title}. {publisher}."
            elif style.lower() == "ieee":
                ref = f"[{index+1}] {author}, \"{title},\" {publisher}, {year}."
            elif style.lower() == "mla":
                ref = f"{author}. {title}. {publisher}, {year}."
            elif style.lower() == "bibtex":
                ref = (
                    f"@misc{{doc_{asset_id[:8]},\n"
                    f"  author = {{{author}}},\n"
                    f"  title = {{{title}}},\n"
                    f"  year = {{{year}}},\n"
                    f"  publisher = {{{publisher}}}\n"
                    f"}}"
                )
            else:
                ref = f"{author}. {title}. ({year})."
            bibliography.append(ref)
        return bibliography

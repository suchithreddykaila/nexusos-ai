from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.domain.auth import User
from app.domain.assistant import SessionMemory
from app.application.assistant.orchestrator import nyra_orchestrator
from pydantic import BaseModel

router = APIRouter(prefix="/assistant", tags=["assistant"])

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    text: str
    navigate_to: Optional[str] = None
    execute_command: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_nyra(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    # Construct SessionMemory state mapping user preferences
    selected_provider = "ollama"
    if current_user.preferences:
        selected_provider = current_user.preferences.default_provider

    memory = SessionMemory(
        selected_provider=selected_provider,
        conversation_history=[]
    )

    response = await nyra_orchestrator.process_query(payload.query, memory)

    return ChatResponse(
        text=response.text,
        navigate_to=response.navigate_to,
        execute_command=response.execute_command
    )

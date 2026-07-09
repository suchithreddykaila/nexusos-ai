from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.workspaces import router as workspaces_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.research import router as research_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.TAGLINE,
    version="1.0.0"
)

# Register REST routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(assistant_router, prefix=settings.API_V1_STR)
app.include_router(workspaces_router, prefix=settings.API_V1_STR)
app.include_router(knowledge_router, prefix=settings.API_V1_STR)
app.include_router(research_router, prefix=settings.API_V1_STR)


# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production environments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "default_provider": settings.DEFAULT_PROVIDER,
        "config": {
            "gemini_configured": settings.GEMINI_API_KEY is not None,
            "ollama_url": settings.OLLAMA_BASE_URL,
            "postgres_host": settings.POSTGRES_HOST,
            "chroma_host": settings.CHROMA_HOST,
            "neo4j_uri": settings.NEO4J_URI
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

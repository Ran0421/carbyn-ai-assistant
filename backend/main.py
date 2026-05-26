from fastapi import FastAPI
from backend.api.routes import router  # correct: routes.py is inside backend/api/
 
app = FastAPI(
    title="Industrial AI Assistant",
    description="Multimodal RAG-powered maintenance assistant",
    version="2.0"
)
 
app.include_router(router)
 
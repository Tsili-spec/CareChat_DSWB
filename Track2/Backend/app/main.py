


from fastapi import FastAPI

from app.api import chatbot, feedback, patient, transcription
from app.core.jwt_auth import create_access_token, verify_token
from app.db.database import create_tables, check_database_connection
from app.services.llm_service import llm_service

# Import models to register them with SQLAlchemy
from app.models import user, conversation

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Initialize database and RAG service on startup"""
    try:
        print("Initializing database...")
        create_tables()
        print("✅ Database tables created/verified successfully")
        
        print("Initializing RAG service...")
        await llm_service.initialize_rag()
        print("✅ RAG service initialized successfully")
        
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        # Continue anyway to allow the app to start

@app.get("/")
async def root():
    return {"message": "Welcome to CareChat Track2 Backend!"}

@app.get("/health/llm")
async def llm_health():
    """Get health status of all LLM providers"""
    from app.services.llm_service import llm_service
    return llm_service.get_health_status()

app.include_router(chatbot.router)
app.include_router(feedback.router)
app.include_router(patient.router, prefix="/api", tags=["Patient"])
app.include_router(transcription.router, prefix="/api", tags=["Transcription"])

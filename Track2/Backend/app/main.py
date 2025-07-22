


from fastapi import FastAPI

from app.api import chatbot, feedback, patient
from app.core.jwt_auth import create_access_token, verify_token
from app.db.database import create_tables, check_database_connection

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        print("Initializing database...")
        create_tables()
        print("✅ Database tables created/verified successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        # Continue anyway to allow the app to start

@app.get("/")
async def root():
    return {"message": "Welcome to CareChat Track2 Backend!"}

app.include_router(chatbot.router)
app.include_router(feedback.router)
app.include_router(patient.router, prefix="/api", tags=["Patient"])

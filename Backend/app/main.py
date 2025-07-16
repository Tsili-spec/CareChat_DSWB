from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import feedback, reminder, patient
from app.db.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Welcome to CareChat API! Available services: Feedback, Reminder."
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(reminder.router, prefix="/api", tags=["Reminder"])
app.include_router(patient.router, prefix="/api", tags=["Patient"])

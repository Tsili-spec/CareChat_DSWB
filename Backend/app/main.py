from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.api import feedback, reminder, patient
from app.db.database import Base, engine
import time
import os

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create tables
logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)
logger.info("Database tables created.")

app = FastAPI(
    title="CareChat API",
    description="API for patient reminders and feedback system.",
    version="1.0.0"
)

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url}")
    try:
        request_body = await request.json()
        logger.info(f"Request Body: {request_body}")
    except Exception:
        logger.info("Request Body: (No JSON body or unable to parse)")

    # Process the request
    response = await call_next(request)
    
    # Log response details
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Response Status: {response.status_code}")
    logger.info(f"Response Time: {process_time:.2f}ms")
    
    return response

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

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, conversations, feedback, reminders, analytics, chatbot, track1_feedback

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"]) 
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(track1_feedback.router, prefix="/track1-feedback", tags=["Track1 Feedback"])
api_router.include_router(chatbot.router, prefix="/chat", tags=["Chatbot"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

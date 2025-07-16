from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class FeedbackBase(BaseModel):
    patient_id: UUID
    feedback_text: Optional[str] = None
    translated_text: Optional[str] = None
    rating: Optional[int] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    language: Optional[str] = None
    status: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    feedback_id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class FeedbackBase(BaseModel):
    patient_id: UUID
    rating: Optional[int] = None
    feedback_text: Optional[str] = None
    audio: Optional[str] = None
    language: str
    sentiment: Optional[str] = None
    topic: Optional[str] = None
    urgency: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    feedback_id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FeedbackBase(BaseModel):
    """Base schema for Feedback"""
    patient_id: str = Field(description="Patient's unique identifier")
    rating: Optional[int] = Field(
        None, 
        ge=1, 
        le=5, 
        description="Rating from 1 to 5"
    )
    feedback_text: Optional[str] = Field(
        None, 
        description="Original feedback text"
    )
    translated_text: Optional[str] = Field(
        None, 
        description="Translated feedback text (if applicable)"
    )
    language: str = Field(description="Language of the feedback")
    sentiment: Optional[str] = Field(
        None, 
        description="Sentiment analysis result (positive, negative, neutral)"
    )
    topic: Optional[str] = Field(
        None, 
        description="Extracted topic from feedback"
    )
    urgency: Optional[str] = Field(
        None, 
        description="Urgency level (urgent, not urgent)"
    )

class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback"""
    pass

class Feedback(FeedbackBase):
    """Schema for feedback response"""
    feedback_id: str = Field(description="Feedback's unique identifier")
    created_at: Optional[datetime] = Field(description="Feedback creation timestamp")

    class Config:
        from_attributes = True

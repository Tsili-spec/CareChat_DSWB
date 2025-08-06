"""
Feedback-related schemas for collecting and managing user feedback
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from .base import BaseResponse


class FeedbackType(str, Enum):
    """Feedback type enumeration"""
    SATISFACTION = "satisfaction"
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    GENERAL = "general"


class FeedbackStatus(str, Enum):
    """Feedback status enumeration"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SentimentType(str, Enum):
    """Sentiment analysis result"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class FeedbackEntry(BaseModel):
    """Individual feedback entry"""
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Rating from 1-5")
    comment: Optional[str] = Field(default=None, max_length=1000, description="Feedback comment")
    category: Optional[str] = Field(default=None, max_length=100, description="Feedback category")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Feedback timestamp")


class FeedbackSessionCreateRequest(BaseModel):
    """Create feedback session request"""
    conversation_id: Optional[str] = Field(default=None, description="Related conversation ID")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    title: Optional[str] = Field(default=None, max_length=200, description="Feedback title")
    description: Optional[str] = Field(default=None, max_length=2000, description="Detailed feedback description")
    entries: List[FeedbackEntry] = Field(default=[], description="Feedback entries")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "60f7b1b3b3f3b3b3b3b3b3b3",
                "feedback_type": "satisfaction",
                "title": "Great experience with health consultation",
                "description": "The AI assistant was very helpful and provided accurate information",
                "entries": [
                    {
                        "rating": 5,
                        "comment": "Excellent service",
                        "category": "overall_experience"
                    },
                    {
                        "rating": 4,
                        "comment": "Fast response time",
                        "category": "response_time"
                    }
                ],
                "metadata": {"source": "mobile_app", "version": "1.0.0"}
            }
        }


class FeedbackSessionResponse(BaseResponse):
    """Feedback session response"""
    user_id: str = Field(..., description="User who provided feedback")
    conversation_id: Optional[str] = Field(default=None, description="Related conversation ID")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    title: Optional[str] = Field(default=None, description="Feedback title")
    description: Optional[str] = Field(default=None, description="Feedback description")
    status: FeedbackStatus = Field(default=FeedbackStatus.PENDING, description="Feedback status")
    entries: List[FeedbackEntry] = Field(..., description="Feedback entries")
    sentiment: Optional[SentimentType] = Field(default=None, description="Analyzed sentiment")
    average_rating: Optional[float] = Field(default=None, description="Average rating across entries")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    response_from_admin: Optional[str] = Field(default=None, description="Admin response to feedback")
    resolved_at: Optional[datetime] = Field(default=None, description="Resolution timestamp")


class FeedbackSessionUpdateRequest(BaseModel):
    """Update feedback session request"""
    title: Optional[str] = Field(default=None, max_length=200, description="Feedback title")
    description: Optional[str] = Field(default=None, max_length=2000, description="Feedback description")
    status: Optional[FeedbackStatus] = Field(default=None, description="Feedback status")
    response_from_admin: Optional[str] = Field(default=None, description="Admin response")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class FeedbackEntryCreateRequest(BaseModel):
    """Add feedback entry request"""
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Rating from 1-5")
    comment: Optional[str] = Field(default=None, max_length=1000, description="Feedback comment")
    category: Optional[str] = Field(default=None, max_length=100, description="Feedback category")


class FeedbackSearchRequest(BaseModel):
    """Feedback search request"""
    query: Optional[str] = Field(default=None, description="Search query")
    feedback_type: Optional[FeedbackType] = Field(default=None, description="Feedback type filter")
    status: Optional[FeedbackStatus] = Field(default=None, description="Status filter")
    sentiment: Optional[SentimentType] = Field(default=None, description="Sentiment filter")
    rating_min: Optional[int] = Field(default=None, ge=1, le=5, description="Minimum rating filter")
    rating_max: Optional[int] = Field(default=None, ge=1, le=5, description="Maximum rating filter")
    created_after: Optional[datetime] = Field(default=None, description="Created after date filter")
    created_before: Optional[datetime] = Field(default=None, description="Created before date filter")


class FeedbackStatsResponse(BaseModel):
    """Feedback statistics response"""
    total_feedback: int = Field(..., description="Total feedback sessions")
    pending_feedback: int = Field(..., description="Pending feedback")
    resolved_feedback: int = Field(..., description="Resolved feedback")
    average_rating: float = Field(..., description="Overall average rating")
    feedback_by_type: Dict[str, int] = Field(..., description="Feedback grouped by type")
    feedback_by_sentiment: Dict[str, int] = Field(..., description="Feedback grouped by sentiment")
    monthly_feedback_trend: List[Dict[str, Any]] = Field(..., description="Monthly feedback trend")
    top_categories: List[Dict[str, Any]] = Field(..., description="Top feedback categories")


# Track1-style feedback schemas
class Track1FeedbackCreate(BaseModel):
    """Schema for Track1-style feedback creation"""
    patient_id: str = Field(..., description="Patient ID")
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Rating from 1-5")
    feedback_text: str = Field(..., description="Feedback text content")
    language: str = Field(..., description="Language code (en, fr, es)")


class Track1FeedbackResponse(BaseModel):
    """Schema for Track1-style feedback response"""
    feedback_id: str = Field(..., description="Feedback ID")
    patient_id: str = Field(..., description="Patient ID")
    rating: Optional[int] = Field(default=None, description="Rating from 1-5")
    feedback_text: str = Field(..., description="Original feedback text")
    translated_text: str = Field(..., description="Translated feedback text (to English)")
    language: str = Field(..., description="Detected language")
    sentiment: str = Field(..., description="Sentiment analysis result")
    topic: Optional[str] = Field(default=None, description="Extracted topic for negative feedback")
    urgency: str = Field(..., description="Urgency level (urgent/not urgent)")
    created_at: datetime = Field(..., description="Creation timestamp")


class Track1AudioFeedbackResponse(Track1FeedbackResponse):
    """Schema for Track1-style audio feedback response"""
    audio_file_path: str = Field(..., description="Path to saved audio file")
    transcription_confidence: float = Field(..., description="Transcription confidence score")
    transcription_duration: float = Field(..., description="Audio duration in seconds")

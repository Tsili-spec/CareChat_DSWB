"""
Feedback Models for MongoDB
Defines feedback session and related data structures
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class FeedbackSession(BaseModel):
    """Feedback session model for Track1 feedback functionality"""
    id: str = Field(..., description="Unique feedback session identifier")
    user_id: str = Field(..., description="User ID who created the session")
    session_type: str = Field(..., description="Session type: text, audio, mixed")
    title: str = Field(..., description="Feedback session title")
    status: str = Field(default="active", description="Session status: active, completed, archived")
    
    # Text feedback data
    text_feedback: Optional[str] = Field(default=None, description="Text feedback content")
    
    # Audio feedback data
    audio_files: List[Dict[str, Any]] = Field(default_factory=list, description="List of audio file metadata")
    transcriptions: List[Dict[str, Any]] = Field(default_factory=list, description="Audio transcriptions")
    translations: List[Dict[str, Any]] = Field(default_factory=list, description="Audio translations")
    
    # Analysis results
    sentiment_analysis: Optional[Dict[str, Any]] = Field(default=None, description="Sentiment analysis results")
    feedback_summary: Optional[str] = Field(default=None, description="AI-generated feedback summary")
    key_insights: List[str] = Field(default_factory=list, description="Key insights extracted")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional session metadata")
    processing_status: str = Field(default="pending", description="Processing status: pending, processing, completed, failed")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Session completion timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AudioFile(BaseModel):
    """Audio file model for feedback sessions"""
    id: str = Field(..., description="Unique audio file identifier")
    session_id: str = Field(..., description="Parent feedback session ID")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Stored file path")
    file_size: int = Field(..., description="File size in bytes")
    duration: Optional[float] = Field(default=None, description="Audio duration in seconds")
    format: str = Field(..., description="Audio format: mp3, wav, etc.")
    
    # Processing status
    transcription_status: str = Field(default="pending", description="Transcription status")
    translation_status: str = Field(default="pending", description="Translation status")
    
    # Results
    transcription: Optional[str] = Field(default=None, description="Audio transcription")
    translation: Optional[str] = Field(default=None, description="Audio translation")
    confidence_score: Optional[float] = Field(default=None, description="Transcription confidence")
    detected_language: Optional[str] = Field(default=None, description="Detected audio language")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional file metadata")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

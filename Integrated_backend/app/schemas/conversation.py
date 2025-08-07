"""
Conversation and Chat Message Pydantic schemas for MongoDB/Beanie
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from fastapi import UploadFile

class ChatMessageCreate(BaseModel):
    user_id: str = Field(..., description="The user's patient ID")
    message: str = Field(..., min_length=1, max_length=5000, description="The user's message")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID (if continuing)")
    provider: Optional[Literal["gemini", "groq"]] = Field(default="groq", description="LLM provider to use")

class ChatMessageResponse(BaseModel):
    message_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    model_used: Optional[str] = None

class AudioChatRequest(BaseModel):
    user_id: str = Field(..., description="The user's patient ID")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID (if continuing)")
    provider: Optional[Literal["gemini", "groq"]] = Field(default="groq", description="LLM provider to use")

class AudioChatResponse(BaseModel):
    conversation_id: str
    transcribed_text: str
    detected_language: str
    transcription_confidence: float
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    provider: str = "groq"

class ConversationResponse(BaseModel):
    conversation_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int

class ChatResponse(BaseModel):
    conversation_id: str
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    provider: str = "groq"

class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    title: Optional[str] = None
    messages: List[ChatMessageResponse]
    created_at: datetime
    updated_at: datetime

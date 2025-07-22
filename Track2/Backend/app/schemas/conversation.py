"""
Conversation and Chat Message Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ChatMessageCreate(BaseModel):
    user_id: UUID = Field(..., description="The user's patient ID")
    message: str = Field(..., min_length=1, max_length=5000, description="The user's message")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID (if continuing)")

class ChatMessageResponse(BaseModel):
    message_id: UUID
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    model_used: Optional[str] = None

class ConversationResponse(BaseModel):
    conversation_id: UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int

class ChatResponse(BaseModel):
    conversation_id: UUID
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    provider: str = "gemini"

class ConversationHistoryResponse(BaseModel):
    conversation_id: UUID
    title: Optional[str] = None
    messages: List[ChatMessageResponse]
    created_at: datetime
    updated_at: datetime

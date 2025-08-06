"""
Conversation-related schemas for chat management and messaging
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from .base import BaseResponse


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Message type enumeration"""
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"


class ConversationStatus(str, Enum):
    """Conversation status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MessageContent(BaseModel):
    """Message content structure"""
    text: Optional[str] = Field(default=None, description="Text content")
    audio_url: Optional[str] = Field(default=None, description="Audio file URL")
    image_url: Optional[str] = Field(default=None, description="Image file URL")
    document_url: Optional[str] = Field(default=None, description="Document file URL")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class Message(BaseModel):
    """Individual message in a conversation"""
    role: MessageRole = Field(..., description="Message role")
    content: MessageContent = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Message type")


# Chat-specific schemas for Track2 functionality
class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat message"""
    message: str = Field(..., description="User message content")
    conversation_id: Optional[str] = Field(default=None, description="Existing conversation ID")
    provider: Optional[Literal["gemini", "groq", "openai"]] = Field(default="gemini", description="LLM provider to use")


class TranscriptionInfo(BaseModel):
    """Transcription information"""
    original_text: str = Field(..., description="Original transcribed text")
    detected_language: str = Field(..., description="Detected language code")
    confidence: float = Field(..., description="Transcription confidence score")


class ChatResponse(BaseModel):
    """Schema for chat response"""
    response: str = Field(..., description="AI response content")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(..., description="Response timestamp")
    model_used: Optional[str] = Field(default=None, description="AI model used")
    provider: str = Field(..., description="LLM provider used")
    token_count: int = Field(default=0, description="Token count for response")
    transcription: Optional[TranscriptionInfo] = Field(default=None, description="Transcription info if from audio")


class ChatMessageResponse(BaseModel):
    """Schema for individual chat message response"""
    message_id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    model_used: Optional[str] = Field(default=None, description="AI model used (for assistant messages)")
    token_count: Optional[int] = Field(default=None, description="Token count (for assistant messages)")


class ConversationInfo(BaseModel):
    """Basic conversation information"""
    conversation_id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
    title: Optional[str] = Field(default=None, description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ConversationHistoryResponse(BaseModel):
    """Schema for conversation history response"""
    conversation: ConversationInfo = Field(..., description="Conversation information")
    messages: List[ChatMessageResponse] = Field(..., description="List of messages in conversation")


class ConversationListResponse(BaseModel):
    """Schema for listing conversations"""
    conversations: List[ConversationInfo] = Field(..., description="List of conversations")
    total_count: int = Field(..., description="Total number of conversations")


class ConversationUpdateRequest(BaseModel):
    """Schema for updating conversation"""
    title: str = Field(..., description="New conversation title")


class ConversationCreateRequest(BaseModel):
    """Create new conversation request"""
    title: Optional[str] = Field(default=None, max_length=200, description="Conversation title")
    initial_message: Optional[str] = Field(default=None, description="Initial message to start conversation")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Conversation context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Health Consultation",
                "initial_message": "Hello, I need help with my health concerns",
                "context": {"source": "mobile_app", "language": "en"}
            }
        }


class ConversationResponse(BaseResponse):
    """Conversation response"""
    user_id: str = Field(..., description="User ID who owns this conversation")
    title: Optional[str] = Field(default=None, description="Conversation title")
    status: ConversationStatus = Field(..., description="Conversation status")
    message_count: int = Field(default=0, description="Number of messages in conversation")
    last_message: Optional[Message] = Field(default=None, description="Last message in conversation")
    context: Dict[str, Any] = Field(default={}, description="Conversation context")
    tags: List[str] = Field(default=[], description="Conversation tags")


class ConversationUpdateRequest(BaseModel):
    """Update conversation request"""
    title: Optional[str] = Field(default=None, max_length=200, description="Conversation title")
    status: Optional[ConversationStatus] = Field(default=None, description="Conversation status")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Conversation context")
    tags: Optional[List[str]] = Field(default=None, description="Conversation tags")


class MessageCreateRequest(BaseModel):
    """Add message to conversation request"""
    content: MessageContent = Field(..., description="Message content")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Message type")
    role: MessageRole = Field(default=MessageRole.USER, description="Message role")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": {
                    "text": "I have been experiencing headaches for the past few days",
                    "metadata": {"urgency": "medium"}
                },
                "message_type": "text",
                "role": "user"
            }
        }


class MessageResponse(BaseModel):
    """Message response"""
    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    role: MessageRole = Field(..., description="Message role")
    content: MessageContent = Field(..., description="Message content")
    message_type: MessageType = Field(..., description="Message type")
    timestamp: datetime = Field(..., description="Message timestamp")
    processed_by: Optional[str] = Field(default=None, description="AI model that processed this message")


class ConversationSearchRequest(BaseModel):
    """Conversation search request"""
    query: Optional[str] = Field(default=None, description="Search query")
    status: Optional[ConversationStatus] = Field(default=None, description="Status filter")
    created_after: Optional[datetime] = Field(default=None, description="Created after date filter")
    created_before: Optional[datetime] = Field(default=None, description="Created before date filter")
    tags: Optional[List[str]] = Field(default=None, description="Tags filter")


class ConversationStatsResponse(BaseModel):
    """Conversation statistics response"""
    total_conversations: int = Field(..., description="Total conversations")
    active_conversations: int = Field(..., description="Active conversations")
    completed_conversations: int = Field(..., description="Completed conversations")
    average_messages_per_conversation: float = Field(..., description="Average messages per conversation")
    conversations_by_status: Dict[str, int] = Field(..., description="Conversations grouped by status")
    conversations_this_month: int = Field(..., description="New conversations this month")

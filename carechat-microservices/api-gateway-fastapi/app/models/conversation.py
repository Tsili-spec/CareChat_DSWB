"""
Conversation Models for MongoDB
Defines data structures for conversations and messages
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Message model for conversation messages"""
    id: str = Field(..., description="Unique message identifier")
    conversation_id: str = Field(..., description="Parent conversation ID")
    role: str = Field(..., description="Message role: user, assistant, system")
    content: str = Field(..., description="Message content")
    content_type: str = Field(default="text", description="Content type: text, audio, image")
    token_count: Optional[int] = Field(default=None, description="Estimated token count")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional message metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Conversation(BaseModel):
    """Conversation model for chatbot conversations"""
    id: str = Field(..., description="Unique conversation identifier")
    user_id: str = Field(..., description="User who owns this conversation")
    title: str = Field(..., description="Conversation title")
    status: str = Field(default="active", description="Conversation status: active, archived, deleted")
    message_count: int = Field(default=0, description="Total number of messages")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional conversation metadata")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Conversation settings")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationWithMessages(Conversation):
    """Conversation model with embedded messages"""
    messages: List[Message] = Field(default_factory=list, description="Conversation messages")


class ConversationSummary(BaseModel):
    """Conversation summary for listing views"""
    id: str
    title: str
    message_count: int
    last_activity: datetime
    status: str
    preview: Optional[str] = None  # Last message preview

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

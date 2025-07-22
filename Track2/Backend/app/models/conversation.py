"""
Conversation and Chat History Models
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class Conversation(Base):
    __tablename__ = "conversations"
    
    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.patient_id"), nullable=False)
    title = Column(String(200), nullable=True)  # Optional conversation title
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign key relationships
    # Note: Relationships removed to avoid circular imports
    # Use explicit queries to get related data

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Optional metadata
    model_used = Column(String(50), nullable=True)  # e.g., 'gemini-2.0-flash'
    token_count = Column(Integer, nullable=True)
    
    # Foreign key relationship
    # Note: Relationship removed to avoid circular imports

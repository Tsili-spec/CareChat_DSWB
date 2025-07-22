"""
Conversation Memory Service
Handles chat history storage and retrieval for context-aware conversations
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
import logging

from app.models.conversation import Conversation, ChatMessage
from app.models.user import User

logger = logging.getLogger(__name__)

class ConversationMemoryService:
    def __init__(self, max_context_messages: int = 10):
        """
        Initialize the conversation memory service
        
        Args:
            max_context_messages: Maximum number of previous messages to include in context
        """
        self.max_context_messages = max_context_messages
    
    def get_or_create_conversation(self, db: Session, user_id: UUID, conversation_id: Optional[UUID] = None) -> Conversation:
        """
        Get existing conversation or create a new one
        
        Args:
            db: Database session
            user_id: Patient ID
            conversation_id: Existing conversation ID (optional)
            
        Returns:
            Conversation object
        """
        if conversation_id:
            # Try to get existing conversation
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id,
                Conversation.patient_id == user_id
            ).first()
            
            if conversation:
                return conversation
            else:
                logger.warning(f"Conversation {conversation_id} not found for user {user_id}, creating new one")
        
        # Create new conversation
        conversation = Conversation(
            patient_id=user_id,
            title=None  # Will be auto-generated based on first message
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Created new conversation {conversation.conversation_id} for user {user_id}")
        return conversation
    
    def add_message(self, db: Session, conversation_id: UUID, role: str, content: str, model_used: Optional[str] = None) -> ChatMessage:
        """
        Add a message to the conversation
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            role: 'user' or 'assistant'
            content: Message content
            model_used: LLM model used (for assistant messages)
            
        Returns:
            ChatMessage object
        """
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            model_used=model_used
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Update conversation's updated_at timestamp
        conversation = db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()
        if conversation:
            db.commit()  # This will trigger the onupdate for updated_at
        
        return message
    
    def get_conversation_context(self, db: Session, conversation_id: UUID) -> List[ChatMessage]:
        """
        Get recent messages from a conversation for context
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            List of recent ChatMessage objects
        """
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(
            desc(ChatMessage.timestamp)
        ).limit(self.max_context_messages).all()
        
        # Reverse to get chronological order (oldest first)
        return list(reversed(messages))
    
    def format_context_for_llm(self, messages: List[ChatMessage]) -> str:
        """
        Format conversation history for LLM context
        
        Args:
            messages: List of ChatMessage objects
            
        Returns:
            Formatted context string
        """
        if not messages:
            return ""
        
        context_lines = ["Previous conversation context:"]
        
        for message in messages:
            role = "Human" if message.role == "user" else "Assistant"
            context_lines.append(f"{role}: {message.content}")
        
        context_lines.append("\nCurrent message:")
        return "\n".join(context_lines)
    
    def get_user_conversations(self, db: Session, user_id: UUID, limit: int = 20) -> List[Conversation]:
        """
        Get all conversations for a user
        
        Args:
            db: Database session
            user_id: Patient ID
            limit: Maximum number of conversations to return
            
        Returns:
            List of Conversation objects
        """
        conversations = db.query(Conversation).filter(
            Conversation.patient_id == user_id
        ).order_by(
            desc(Conversation.updated_at)
        ).limit(limit).all()
        
        return conversations
    
    def auto_generate_title(self, first_message: str) -> str:
        """
        Generate a conversation title based on the first message
        
        Args:
            first_message: First user message in the conversation
            
        Returns:
            Generated title (max 50 chars)
        """
        # Simple title generation - take first 50 chars and clean up
        title = first_message.strip()
        if len(title) > 47:
            title = title[:47] + "..."
        
        return title
    
    def update_conversation_title(self, db: Session, conversation_id: UUID, title: str):
        """
        Update conversation title
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            title: New title
        """
        conversation = db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id
        ).first()
        
        if conversation:
            conversation.title = title
            db.commit()
    
    def get_conversation_messages(self, db: Session, conversation_id: UUID) -> List[ChatMessage]:
        """
        Get all messages for a conversation
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            List of ChatMessage objects ordered by timestamp
        """
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.timestamp).all()
        
        return messages
    
    def get_conversation_message_count(self, db: Session, conversation_id: UUID) -> int:
        """
        Get the number of messages in a conversation
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            Number of messages
        """
        count = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).count()
        
        return count

# Global instance
conversation_memory = ConversationMemoryService()

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
    def __init__(self, max_context_messages: int = 5):  # Reduced from 10 to 5
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
        Format conversation history for LLM context with healthcare system instructions
        Uses smart truncation and summarization for longer conversations
        
        Args:
            messages: List of ChatMessage objects
            
        Returns:
            Formatted context string with system instructions
        """
        # Shortened healthcare system instructions for longer conversations
        if len(messages) > 5:
            system_instructions = """You are a healthcare professional assistant working for Douala General Hospital(Hôpital Général de Douala) in Douala, Cameroon. Explain medical information in simple, compassionate terms.
- Interpret clinician summaries in layperson language
- Include disclaimer: "Please refer to your healthcare provider at Douala General Hospital for medical decisions"
- Keep responses under 200 words, be concise
- Use bullet points when helpful
- Always reference Douala General hospital when talking of or referring individual to their healthcare provider"""
        else:
            # Full instructions for shorter conversations
            system_instructions = """You are a **healthcare professional assistant working for Douala General Hospital(Hôpital Général de Douala) in Douala, Cameroon** whose role is to **explain medical information** in simple, compassionate terms.

**Your responsibilities:**
- Interpret clinicians' summaries of diagnoses, treatments, medications.
- Explain them in layperson-friendly language.
- Clarify common side effects, follow-up care, and lifestyle advice empathetically.
- Always **include a disclaimer**: "Please refer to your healthcare provider for medical decisions."

**IMPORTANT - Don't Do:**
- Don't generate new clinical diagnoses or treatment plans.
- Don't provide medical advice beyond interpreting clinician input.

**Response Guidelines:**
- Keep responses under 200 words maximum.
- Be straight to the point and concise.
- Use short, clear bullet points when helpful.
- If you're uncertain, say: "I'm not sure—please check with your provider."
- Keep a warm, respectful tone.
-Always reference Douala General hospital when talking of or referring individual to their healthcare provider
"""
        
        if not messages:
            return system_instructions + "\n\nCurrent message:"
        
        # Smart context summarization for longer conversations
        if len(messages) > 3:
            # Summarize older messages, keep recent ones in full
            recent_messages = messages[-2:]  # Last 2 messages in full
            older_messages = messages[:-2]   # Older messages to summarize
            
            context_lines = [system_instructions, "\nPrevious conversation summary:"]
            
            # Add summarized older context
            if older_messages:
                topics = []
                for msg in older_messages:
                    if msg.role == "user":
                        # Extract key topics from user messages (first 50 chars)
                        topic = msg.content[:50].strip()
                        if len(msg.content) > 50:
                            topic += "..."
                        topics.append(f"User asked about: {topic}")
                
                context_lines.append("Earlier topics: " + "; ".join(topics[-2:]))  # Last 2 topics
            
            # Add recent messages in full
            context_lines.append("\nRecent messages:")
            for message in recent_messages:
                role = "Human" if message.role == "user" else "Assistant"
                # Truncate long messages in context
                content = message.content[:200] + "..." if len(message.content) > 200 else message.content
                context_lines.append(f"{role}: {content}")
        else:
            # Short conversations - include all messages
            context_lines = [system_instructions, "\nPrevious conversation context:"]
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
    
    def delete_user_data(self, db: Session, user_id: UUID) -> dict:
        """
        Delete all user data including conversations and messages
        
        Args:
            db: Database session
            user_id: Patient ID to delete
            
        Returns:
            Dictionary with deletion summary
        """
        try:
            # Get user's conversations first for count
            conversations = db.query(Conversation).filter(
                Conversation.patient_id == user_id
            ).all()
            
            conversation_count = len(conversations)
            message_count = 0
            
            # Delete all messages in user's conversations FIRST (to avoid FK constraint)
            for conv in conversations:
                messages = db.query(ChatMessage).filter(
                    ChatMessage.conversation_id == conv.conversation_id
                ).all()
                message_count += len(messages)
                
                # Delete messages first
                for message in messages:
                    db.delete(message)
            
            # Commit message deletions before deleting conversations
            db.commit()
            
            # Now delete conversations (no more FK constraint issues)
            db.query(Conversation).filter(
                Conversation.patient_id == user_id
            ).delete()
            
            # Commit conversation deletions
            db.commit()
            
            # Finally, delete user
            from app.models.user import User
            user = db.query(User).filter(User.patient_id == user_id).first()
            if user:
                db.delete(user)
            
            db.commit()
            
            return {
                "user_deleted": True,
                "conversations_deleted": conversation_count,
                "messages_deleted": message_count,
                "message": f"Successfully deleted user {user_id} and all associated data"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise
    
    def delete_conversation(self, db: Session, conversation_id: UUID, user_id: UUID) -> dict:
        """
        Delete a specific conversation and all its messages
        
        Args:
            db: Database session
            conversation_id: Conversation ID to delete
            user_id: Patient ID (for ownership verification)
            
        Returns:
            Dictionary with deletion summary
        """
        try:
            # Verify conversation exists and belongs to user
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id,
                Conversation.patient_id == user_id
            ).first()
            
            if not conversation:
                return {
                    "conversation_deleted": False,
                    "messages_deleted": 0,
                    "error": "Conversation not found or access denied"
                }
            
            # Count and delete messages
            messages = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conversation_id
            ).all()
            
            message_count = len(messages)
            
            for message in messages:
                db.delete(message)
            
            # Delete conversation
            db.delete(conversation)
            db.commit()
            
            return {
                "conversation_deleted": True,
                "messages_deleted": message_count,
                "message": f"Successfully deleted conversation {conversation_id} with {message_count} messages"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")
            raise
    
    def delete_message(self, db: Session, message_id: UUID, user_id: UUID) -> dict:
        """
        Delete a specific message from a conversation
        
        Args:
            db: Database session
            message_id: Message ID to delete
            user_id: Patient ID (for ownership verification)
            
        Returns:
            Dictionary with deletion summary
        """
        try:
            # Find message and verify ownership through conversation
            message = db.query(ChatMessage).join(
                Conversation, ChatMessage.conversation_id == Conversation.conversation_id
            ).filter(
                ChatMessage.message_id == message_id,
                Conversation.patient_id == user_id
            ).first()
            
            if not message:
                return {
                    "message_deleted": False,
                    "error": "Message not found or access denied"
                }
            
            conversation_id = message.conversation_id
            db.delete(message)
            
            # Update conversation timestamp
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            if conversation:
                db.commit()  # This triggers updated_at
            
            return {
                "message_deleted": True,
                "message": f"Successfully deleted message {message_id}"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting message {message_id}: {str(e)}")
            raise

# Global instance
conversation_memory = ConversationMemoryService()

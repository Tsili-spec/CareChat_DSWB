"""
Conversation Memory Service for MongoDB with Beanie ODM
Handles chat history storage and retrieval for context-aware conversations
"""
from typing import List, Optional
from app.models.models import Conversation, ChatMessage, Patient
from datetime import datetime
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

class ConversationMemoryService:
    def __init__(self, max_context_messages: int = 5):
        """
        Initialize the conversation memory service
        
        Args:
            max_context_messages: Maximum number of previous messages to include in context
        """
        self.max_context_messages = max_context_messages
    
    async def get_or_create_conversation(self, user_id: str, conversation_id: Optional[str] = None) -> Conversation:
        """
        Get existing conversation or create a new one
        
        Args:
            user_id: Patient ID
            conversation_id: Existing conversation ID (optional)
            
        Returns:
            Conversation object
        """
        if conversation_id:
            # Try to get existing conversation
            try:
                conversation = await Conversation.find_one(
                    Conversation.id == ObjectId(conversation_id),
                    Conversation.patient_id == user_id
                )
                
                if conversation:
                    return conversation
                else:
                    logger.warning(f"Conversation {conversation_id} not found for user {user_id}, creating new one")
            except Exception as e:
                logger.warning(f"Error finding conversation {conversation_id}: {e}, creating new one")
        
        # Create new conversation
        conversation = Conversation(
            patient_id=user_id,
            title=None  # Will be auto-generated based on first message
        )
        await conversation.insert()
        
        logger.info(f"Created new conversation {conversation.id} for user {user_id}")
        return conversation
    
    async def add_message(self, conversation_id: str, role: str, content: str, model_used: Optional[str] = None) -> ChatMessage:
        """
        Add a message to the conversation
        
        Args:
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
        
        await message.insert()
        
        # Update conversation's updated_at timestamp
        conversation = await Conversation.find_one(Conversation.id == ObjectId(conversation_id))
        if conversation:
            conversation.updated_at = datetime.utcnow()
            await conversation.save()
        
        return message
    
    async def get_conversation_context(self, conversation_id: str) -> List[ChatMessage]:
        """
        Get recent messages from a conversation for context
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of recent ChatMessage objects
        """
        try:
            # Debug logging
            logger.info(f"Getting context for conversation_id: {conversation_id}")
            
            messages = await ChatMessage.find(
                ChatMessage.conversation_id == conversation_id
            ).sort(-ChatMessage.timestamp).limit(self.max_context_messages).to_list()
            
            logger.info(f"Found {len(messages)} messages for context")
            
            # Reverse to get chronological order (oldest first)
            return list(reversed(messages))
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return []
    
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
            system_instructions = """You are a multilingual healthcare professional assistant working for Douala General Hospital(Hôpital Général de Douala) in Douala, Cameroon. Explain medical information in simple, compassionate terms.
- Interpret clinician summaries in layperson language
- Include disclaimer: "Please refer to your healthcare provider at Douala General Hospital for medical decisions"
- Keep responses under 200 words, be concise
- Use bullet points when helpful
- If you are prompted in English reply in English and if you are prompted in French, reply in French
- Always reference Douala General hospital when talking of or referring individual to their healthcare provider"""
        else:
            # Full instructions for shorter conversations
            system_instructions = """You are a **multilingual healthcare professional assistant working for Douala General Hospital(Hôpital Général de Douala) in Douala, Cameroon** whose role is to **explain medical information** in simple, compassionate terms.

**Your responsibilities:**
- Interpret clinicians' summaries of diagnoses, treatments, medications.
- Explain them in layperson-friendly language.
- Clarify common side effects, follow-up care, and lifestyle advice empathetically.
- Always **include a disclaimer**: "Please refer to your healthcare provider for medical decisions."

**IMPORTANT - Don't Do:**
- Don't generate new clinical diagnoses or treatment plans.
- Don't provide medical advice beyond interpreting clinician input.

**Response Guidelines:**
- If you are prompted in English reply in English and if you are prompted in French, reply in French
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
    
    async def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Conversation]:
        """
        Get all conversations for a user
        
        Args:
            user_id: Patient ID
            limit: Maximum number of conversations to return
            
        Returns:
            List of Conversation objects
        """
        conversations = await Conversation.find(
            Conversation.patient_id == user_id
        ).sort(-Conversation.updated_at).limit(limit).to_list()
        
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
    
    async def update_conversation_title(self, conversation_id: str, title: str):
        """
        Update conversation title
        
        Args:
            conversation_id: Conversation ID
            title: New title
        """
        conversation = await Conversation.find_one(Conversation.id == ObjectId(conversation_id))
        
        if conversation:
            conversation.title = title
            await conversation.save()
    
    async def get_conversation_messages(self, conversation_id: str) -> List[ChatMessage]:
        """
        Get all messages for a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of ChatMessage objects ordered by timestamp
        """
        try:
            logger.info(f"Getting all messages for conversation_id: {conversation_id}")
            
            messages = await ChatMessage.find(
                ChatMessage.conversation_id == conversation_id
            ).sort(ChatMessage.timestamp).to_list()
            
            logger.info(f"Found {len(messages)} total messages")
            return messages
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []
    
    async def get_conversation_message_count(self, conversation_id: str) -> int:
        """
        Get the number of messages in a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Number of messages
        """
        count = await ChatMessage.find(ChatMessage.conversation_id == conversation_id).count()
        return count
    
    async def delete_conversation(self, conversation_id: str, user_id: str) -> dict:
        """
        Delete a specific conversation and all its messages
        
        Args:
            conversation_id: Conversation ID to delete
            user_id: Patient ID (for ownership verification)
            
        Returns:
            Dictionary with deletion summary
        """
        try:
            # Verify conversation exists and belongs to user
            conversation = await Conversation.find_one(
                Conversation.id == ObjectId(conversation_id),
                Conversation.patient_id == user_id
            )
            
            if not conversation:
                return {
                    "conversation_deleted": False,
                    "messages_deleted": 0,
                    "error": "Conversation not found or access denied"
                }
            
            # Count and delete messages
            messages = await ChatMessage.find(ChatMessage.conversation_id == conversation_id).to_list()
            message_count = len(messages)
            
            # Delete all messages
            await ChatMessage.find(ChatMessage.conversation_id == conversation_id).delete()
            
            # Delete conversation
            await conversation.delete()
            
            return {
                "conversation_deleted": True,
                "messages_deleted": message_count,
                "message": f"Successfully deleted conversation {conversation_id} with {message_count} messages"
            }
            
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")
            raise
    
    async def delete_message(self, message_id: str, user_id: str) -> dict:
        """
        Delete a specific message from a conversation
        
        Args:
            message_id: Message ID to delete
            user_id: Patient ID (for ownership verification)
            
        Returns:
            Dictionary with deletion summary
        """
        try:
            # Find message
            message = await ChatMessage.find_one(ChatMessage.id == ObjectId(message_id))
            
            if not message:
                return {
                    "message_deleted": False,
                    "error": "Message not found"
                }
            
            # Verify ownership through conversation
            conversation = await Conversation.find_one(
                Conversation.id == ObjectId(message.conversation_id),
                Conversation.patient_id == user_id
            )
            
            if not conversation:
                return {
                    "message_deleted": False,
                    "error": "Access denied"
                }
            
            conversation_id = message.conversation_id
            await message.delete()
            
            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            await conversation.save()
            
            return {
                "message_deleted": True,
                "message": f"Successfully deleted message {message_id}"
            }
            
        except Exception as e:
            logger.error(f"Error deleting message {message_id}: {str(e)}")
            raise

# Global instance
conversation_memory = ConversationMemoryService()

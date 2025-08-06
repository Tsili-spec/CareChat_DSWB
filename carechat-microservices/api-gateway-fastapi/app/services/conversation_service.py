"""
Conversation Service for managing chatbot conversations
Handles conversation state, message history, and context management
Based on Track2 implementation adapted for MongoDB
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..schemas.conversation import ConversationCreateRequest, MessageCreateRequest
from ..db.database import db

logger = logging.getLogger(__name__)

class ConversationService:
    """
    Comprehensive conversation management service
    Handles conversation lifecycle, message threading, context management
    """
    
    def __init__(self, database: AsyncIOMotorDatabase = None):
        self.db = database or db.database
        self.conversations_collection = self.db.conversations
        self.messages_collection = self.db.messages
        
        # Configuration
        self.max_context_messages = 20  # Last N messages for context
        self.max_message_length = 8000  # Token limit consideration
        
    async def create_conversation(self, conversation_data: ConversationCreateRequest) -> str:
        """Create a new conversation with enhanced metadata"""
        try:
            conversation_id = str(uuid.uuid4())
            
            # Create conversation document
            conversation = {
                "id": conversation_id,
                "user_id": "system",  # We'll get this from JWT or pass it separately
                "title": conversation_data.title or self._generate_conversation_title(),
                "status": "active",  # active, archived, deleted
                "message_count": 0,
                "last_activity": datetime.utcnow(),
                "metadata": {
                    **(conversation_data.context or {}),
                    "source": "api",
                    "version": "1.0"
                },
                "settings": {
                    "model_preference": "auto",
                    "rag_enabled": True,
                    "language": "en"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await self.conversations_collection.insert_one(conversation)
            logger.info(f"✅ Created conversation {conversation_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"❌ Error creating conversation: {e}")
            raise
    
    def _generate_conversation_title(self) -> str:
        """Generate a friendly conversation title"""
        titles = [
            "Healthcare Chat",
            "Medical Consultation", 
            "Health Questions",
            "Care Discussion",
            "Medical Query"
        ]
        import random
        return random.choice(titles)
    
    async def add_message(self, conversation_id: str, message_data: MessageCreateRequest) -> Dict[str, Any]:
        """Add a message to conversation with enhanced tracking"""
        try:
            message_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            # Create message document
            message = {
                "id": message_id,
                "conversation_id": conversation_id,
                "role": message_data.role.value,  # Extract enum value
                "content": message_data.content.text or "",  # Extract text content
                "content_type": message_data.message_type.value,  # Extract enum value
                "token_count": self._estimate_tokens(message_data.content.text or ""),
                "metadata": {
                    **(message_data.content.metadata or {}),
                    "processed_at": timestamp,
                    "source": "chat_api"
                },
                "timestamp": timestamp,
                "created_at": timestamp
            }
            
            # Store message in messages collection
            await self.messages_collection.insert_one(message)
            
            # Update conversation metadata
            await self.conversations_collection.update_one(
                {"id": conversation_id},
                {
                    "$inc": {"message_count": 1},
                    "$set": {
                        "last_activity": timestamp,
                        "updated_at": timestamp
                    }
                }
            )
            
            logger.info(f"✅ Added {message_data.role.value} message {message_id} to conversation {conversation_id}")
            return message
            
        except Exception as e:
            logger.error(f"❌ Error adding message: {e}")
            raise
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)"""
        return len(text) // 4
    
    async def get_conversation(self, conversation_id: str, include_messages: bool = False) -> Optional[Dict[str, Any]]:
        """Get conversation with optional message inclusion"""
        try:
            conversation = await self.conversations_collection.find_one({"id": conversation_id})
            
            if conversation and include_messages:
                # Fetch recent messages
                messages = await self.get_conversation_history(conversation_id)
                conversation["messages"] = messages
            
            return conversation
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation: {e}")
            return None
    
    async def get_conversation_history(self, conversation_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get conversation message history with smart limiting"""
        try:
            if limit is None:
                limit = self.max_context_messages
            
            cursor = self.messages_collection.find(
                {"conversation_id": conversation_id}
            ).sort("timestamp", 1).limit(limit)
            
            messages = await cursor.to_list(length=limit)
            
            logger.debug(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation history: {e}")
            return []
    
    async def get_context_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get messages suitable for AI context (filtered and optimized)"""
        try:
            # Get recent messages
            messages = await self.get_conversation_history(conversation_id, self.max_context_messages)
            
            # Filter and optimize for AI context
            context_messages = []
            total_tokens = 0
            
            for message in reversed(messages):  # Start from most recent
                token_count = message.get("token_count", self._estimate_tokens(message.get("content", "")))
                
                # Skip if would exceed token limit
                if total_tokens + token_count > 4000:  # Leave room for response
                    break
                
                # Format for AI context
                context_msg = {
                    "role": message["role"],
                    "content": message["content"],
                    "timestamp": message["timestamp"]
                }
                
                context_messages.insert(0, context_msg)  # Maintain chronological order
                total_tokens += token_count
            
            logger.debug(f"Prepared {len(context_messages)} messages for AI context (~{total_tokens} tokens)")
            return context_messages
            
        except Exception as e:
            logger.error(f"❌ Error getting context messages: {e}")
            return []
    
    async def get_user_conversations(self, user_id: str, limit: int = 20, status: str = "active") -> List[Dict[str, Any]]:
        """Get user conversations with filtering and pagination"""
        try:
            query = {"user_id": user_id}
            if status:
                query["status"] = status
            
            cursor = self.conversations_collection.find(query).sort("last_activity", -1).limit(limit)
            conversations = await cursor.to_list(length=limit)
            
            # Add summary info
            for conv in conversations:
                conv["summary"] = {
                    "message_count": conv.get("message_count", 0),
                    "last_activity": conv.get("last_activity"),
                    "duration_days": (datetime.utcnow() - conv.get("created_at", datetime.utcnow())).days
                }
            
            logger.info(f"Retrieved {len(conversations)} conversations for user {user_id}")
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Error getting user conversations: {e}")
            return []
    
    async def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title"""
        try:
            result = await self.conversations_collection.update_one(
                {"id": conversation_id},
                {
                    "$set": {
                        "title": title,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Error updating conversation title: {e}")
            return False
    
    async def archive_conversation(self, conversation_id: str) -> bool:
        """Archive a conversation (soft delete)"""
        try:
            result = await self.conversations_collection.update_one(
                {"id": conversation_id},
                {
                    "$set": {
                        "status": "archived",
                        "archived_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Error archiving conversation: {e}")
            return False
    
    async def delete_conversation(self, conversation_id: str, hard_delete: bool = False) -> bool:
        """Delete conversation (soft by default, hard if specified)"""
        try:
            if hard_delete:
                # Delete messages first
                await self.messages_collection.delete_many({"conversation_id": conversation_id})
                # Delete conversation
                result = await self.conversations_collection.delete_one({"id": conversation_id})
                logger.info(f"Hard deleted conversation {conversation_id}")
            else:
                # Soft delete - mark as deleted
                result = await self.conversations_collection.update_one(
                    {"id": conversation_id},
                    {
                        "$set": {
                            "status": "deleted",
                            "deleted_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                logger.info(f"Soft deleted conversation {conversation_id}")
            
            return result.modified_count > 0 or result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error deleting conversation: {e}")
            return False
    
    async def get_conversation_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get conversation statistics"""
        try:
            pipeline = []
            
            if user_id:
                pipeline.append({"$match": {"user_id": user_id}})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_conversations": {"$sum": 1},
                        "active_conversations": {
                            "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                        },
                        "archived_conversations": {
                            "$sum": {"$cond": [{"$eq": ["$status", "archived"]}, 1, 0]}
                        },
                        "total_messages": {"$sum": "$message_count"},
                        "avg_messages_per_conversation": {"$avg": "$message_count"}
                    }
                }
            ])
            
            cursor = self.conversations_collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            if result:
                return result[0]
            else:
                return {
                    "total_conversations": 0,
                    "active_conversations": 0,
                    "archived_conversations": 0,
                    "total_messages": 0,
                    "avg_messages_per_conversation": 0
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting conversation stats: {e}")
            return {}
    
    async def cleanup_old_conversations(self, days_old: int = 30) -> int:
        """Clean up old inactive conversations"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Archive old inactive conversations
            result = await self.conversations_collection.update_many(
                {
                    "last_activity": {"$lt": cutoff_date},
                    "status": "active"
                },
                {
                    "$set": {
                        "status": "archived",
                        "archived_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            archived_count = result.modified_count
            logger.info(f"Archived {archived_count} old conversations")
            return archived_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up conversations: {e}")
            return 0
import logging
from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID, uuid4

from app.db.database import get_conversations_collection, get_messages_collection

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Service for managing conversation memory and context"""
    
    async def get_or_create_conversation(
        self, 
        user_id: str, 
        conversation_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Get existing conversation or create new one
        
        Args:
            user_id: User ID
            conversation_id: Optional existing conversation ID
        
        Returns:
            Conversation document
        """
        try:
            conversations_collection = await get_conversations_collection()
            
            if conversation_id:
                # Try to get existing conversation
                conversation = await conversations_collection.find_one({
                    "conversation_id": conversation_id,
                    "user_id": user_id
                })
                
                if conversation:
                    return conversation
            
            # Create new conversation
            new_conversation = {
                "conversation_id": str(uuid4()),
                "user_id": user_id,
                "title": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await conversations_collection.insert_one(new_conversation)
            if result.inserted_id:
                logger.info(f"Created new conversation: {new_conversation['conversation_id']} for user: {user_id}")
                return new_conversation
            else:
                raise Exception("Failed to create conversation")
                
        except Exception as e:
            logger.error(f"Error getting/creating conversation: {e}")
            raise e
    
    async def get_conversation_context(
        self, 
        conversation_id: str, 
        limit: int = 10
    ) -> List[Dict[str, any]]:
        """
        Get conversation context (previous messages)
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of previous messages
        """
        try:
            messages_collection = await get_messages_collection()
            
            messages = await messages_collection.find({
                "conversation_id": conversation_id
            }).sort("timestamp", 1).limit(limit).to_list(length=limit)
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return []
    
    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        model_used: Optional[str] = None,
        token_count: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Save a message to the conversation
        
        Args:
            conversation_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            model_used: LLM model used (for assistant messages)
            token_count: Token count (for assistant messages)
        
        Returns:
            Saved message document
        """
        try:
            messages_collection = await get_messages_collection()
            
            message = {
                "message_id": str(uuid4()),
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow(),
                "model_used": model_used,
                "token_count": token_count
            }
            
            result = await messages_collection.insert_one(message)
            if result.inserted_id:
                # Update conversation timestamp
                await self._update_conversation_timestamp(conversation_id)
                return message
            else:
                raise Exception("Failed to save message")
                
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise e
    
    async def get_conversation_history(
        self, 
        user_id: str, 
        conversation_id: str
    ) -> Dict[str, any]:
        """
        Get full conversation history
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
        
        Returns:
            Conversation with messages
        """
        try:
            conversations_collection = await get_conversations_collection()
            messages_collection = await get_messages_collection()
            
            # Get conversation
            conversation = await conversations_collection.find_one({
                "conversation_id": conversation_id,
                "user_id": user_id
            })
            
            if not conversation:
                raise Exception("Conversation not found")
            
            # Get messages
            messages = await messages_collection.find({
                "conversation_id": conversation_id
            }).sort("timestamp", 1).to_list(length=None)
            
            return {
                "conversation": conversation,
                "messages": messages
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            raise e
    
    async def list_user_conversations(
        self, 
        user_id: str, 
        limit: int = 20
    ) -> List[Dict[str, any]]:
        """
        List all conversations for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations to return
        
        Returns:
            List of conversations
        """
        try:
            conversations_collection = await get_conversations_collection()
            
            conversations = await conversations_collection.find({
                "user_id": user_id
            }).sort("updated_at", -1).limit(limit).to_list(length=limit)
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error listing user conversations: {e}")
            return []
    
    async def update_conversation_title(
        self, 
        conversation_id: str, 
        title: str,
        user_id: str
    ) -> bool:
        """
        Update conversation title
        
        Args:
            conversation_id: Conversation ID
            title: New title
            user_id: User ID (for authorization)
        
        Returns:
            Success boolean
        """
        try:
            conversations_collection = await get_conversations_collection()
            
            result = await conversations_collection.update_one({
                "conversation_id": conversation_id,
                "user_id": user_id
            }, {
                "$set": {
                    "title": title,
                    "updated_at": datetime.utcnow()
                }
            })
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating conversation title: {e}")
            return False
    
    async def delete_conversation(
        self, 
        conversation_id: str, 
        user_id: str
    ) -> bool:
        """
        Delete a conversation and all its messages
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (for authorization)
        
        Returns:
            Success boolean
        """
        try:
            conversations_collection = await get_conversations_collection()
            messages_collection = await get_messages_collection()
            
            # Delete messages first
            await messages_collection.delete_many({
                "conversation_id": conversation_id
            })
            
            # Delete conversation
            result = await conversations_collection.delete_one({
                "conversation_id": conversation_id,
                "user_id": user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
    
    async def _update_conversation_timestamp(self, conversation_id: str):
        """Update conversation updated_at timestamp"""
        try:
            conversations_collection = await get_conversations_collection()
            await conversations_collection.update_one({
                "conversation_id": conversation_id
            }, {
                "$set": {"updated_at": datetime.utcnow()}
            })
        except Exception as e:
            logger.error(f"Error updating conversation timestamp: {e}")

# Global instance
conversation_memory = ConversationMemory()

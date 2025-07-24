"""
Multi-LLM Chat endpoint for CareChat with Conversational Memory and RAG
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.llm_service import llm_service
from app.services.conversation_service import conversation_memory
from app.schemas.conversation import ChatMessageCreate, ChatResponse, ConversationHistoryResponse, ConversationResponse
from app.db.database import get_db
import logging
from typing import List

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

# Initialize RAG service on module load
@router.on_event("startup")
async def initialize_rag():
    """Initialize RAG service for enhanced responses"""
    try:
        await llm_service.initialize_rag()
        logger.info("RAG service initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize RAG service: {e}")
        # Continue without RAG if initialization fails

@router.post("/", response_model=ChatResponse)
async def chat_with_memory(request: ChatMessageCreate, db: Session = Depends(get_db)):
    """
    Send a message to Gemini AI with conversational memory.
    
    Uses conversation history to maintain context across multiple messages.
    If this is the first message you are sending then set the conversation_id to null.
    conversation_id: null
    """
    try:
        logger.info(f"Chat request from user {request.user_id} with message length: {len(request.message)}")
        
        # Get or create conversation
        conversation = conversation_memory.get_or_create_conversation(
            db=db,
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
        
        # Get conversation context (previous messages)
        context_messages = conversation_memory.get_conversation_context(
            db=db,
            conversation_id=conversation.conversation_id
        )
        
        # Add user message to conversation
        user_message = conversation_memory.add_message(
            db=db,
            conversation_id=conversation.conversation_id,
            role="user",
            content=request.message
        )
        
        # Format context for LLM
        context = conversation_memory.format_context_for_llm(context_messages)
        
        # Prepare prompt with context
        if context:
            full_prompt = f"{context}\nHuman: {request.message}"
        else:
            full_prompt = request.message
        
        # Generate title for new conversations
        if not conversation.title and len(context_messages) == 0:
            title = conversation_memory.auto_generate_title(request.message)
            conversation_memory.update_conversation_title(
                db=db,
                conversation_id=conversation.conversation_id,
                title=title
            )
        
        # Get response from specified LLM provider with healthcare guidelines
        response_text = await llm_service.generate_response(
            full_prompt,
            provider=request.provider,
            temperature=0.3
        )
        
        # Add assistant message to conversation
        model_name = f"{request.provider}-2.0-flash" if request.provider == "gemini" else "llama-4-maverick-17b"
        assistant_message = conversation_memory.add_message(
            db=db,
            conversation_id=conversation.conversation_id,
            role="assistant",
            content=response_text,
            model_used=model_name
        )
        
        return ChatResponse(
            conversation_id=conversation.conversation_id,
            user_message={
                "message_id": user_message.message_id,
                "role": user_message.role,
                "content": user_message.content,
                "timestamp": user_message.timestamp,
                "model_used": user_message.model_used
            },
            assistant_message={
                "message_id": assistant_message.message_id,
                "role": assistant_message.role,
                "content": assistant_message.content,
                "timestamp": assistant_message.timestamp,
                "model_used": assistant_message.model_used
            },
            provider=request.provider
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat service error: {str(e)}"
        )

@router.get("/conversations/{user_id}", response_model=List[ConversationResponse])
async def get_user_conversations(user_id: str, db: Session = Depends(get_db)):
    """Get all conversations for a user"""
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
        
        conversations = conversation_memory.get_user_conversations(db=db, user_id=user_uuid)
        
        result = []
        for conv in conversations:
            message_count = conversation_memory.get_conversation_message_count(db=db, conversation_id=conv.conversation_id)
            result.append(ConversationResponse(
                conversation_id=conv.conversation_id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count
            ))
        
        return result
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{user_id}/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(user_id: str, conversation_id: str, db: Session = Depends(get_db)):
    """Get full conversation history"""
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
        conv_uuid = UUID(conversation_id)
        
        # Get conversation and verify ownership
        from app.models.conversation import Conversation
        conversation = db.query(Conversation).filter(
            Conversation.conversation_id == conv_uuid,
            Conversation.patient_id == user_uuid
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages using the conversation service
        messages_data = conversation_memory.get_conversation_messages(db=db, conversation_id=conv_uuid)
        
        messages = []
        for msg in messages_data:
            messages.append({
                "message_id": msg.message_id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "model_used": msg.model_used
            })
        
        return ConversationHistoryResponse(
            conversation_id=conversation.conversation_id,
            title=conversation.title,
            messages=messages,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversations/{user_id}/{conversation_id}")
async def delete_conversation(user_id: str, conversation_id: str, db: Session = Depends(get_db)):
    """
    Delete a specific conversation and all its messages
    
    **How it works:**
    1. Validates the user_id and conversation_id formats
    2. Verifies the conversation exists and belongs to the specified user
    3. Deletes all messages within the conversation
    4. Deletes the conversation record itself
    5. Returns a summary of what was deleted
    
    **Security:** Only the conversation owner can delete their conversations.
    Attempting to delete another user's conversation will result in a 404 error.
    """
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
        conv_uuid = UUID(conversation_id)
        
        # Delete conversation using conversation service
        deletion_result = conversation_memory.delete_conversation(
            db=db, 
            conversation_id=conv_uuid, 
            user_id=user_uuid
        )
        
        if not deletion_result.get("conversation_deleted"):
            raise HTTPException(
                status_code=404, 
                detail=deletion_result.get("error", "Conversation not found")
            )
        
        logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "conversation_id": conversation_id,
            **deletion_result
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/messages/{user_id}/{message_id}")
async def delete_message(user_id: str, message_id: str, db: Session = Depends(get_db)):
    """
    Delete a specific message from a conversation
    
    **How it works:**
    1. Validates the user_id and message_id formats
    2. Finds the message and verifies it belongs to the user's conversation
    3. Deletes the message from the database
    4. Updates the conversation's last modified timestamp
    5. Returns confirmation of deletion
    
    **Security:** Only messages from the user's own conversations can be deleted.
    The system verifies ownership through the conversation relationship.
    
    **Note:** Deleting messages may affect conversation context for future AI responses.
    """
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
        msg_uuid = UUID(message_id)
        
        # Delete message using conversation service
        deletion_result = conversation_memory.delete_message(
            db=db,
            message_id=msg_uuid,
            user_id=user_uuid
        )
        
        if not deletion_result.get("message_deleted"):
            raise HTTPException(
                status_code=404,
                detail=deletion_result.get("error", "Message not found")
            )
        
        logger.info(f"Deleted message {message_id} for user {user_id}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "message_id": message_id,
            **deletion_result
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

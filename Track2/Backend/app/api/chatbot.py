"""
Gemini Chat endpoint for CareChat with Conversational Memory
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.llm_service import gemini_service
from app.services.conversation_service import conversation_memory
from app.schemas.conversation import ChatMessageCreate, ChatResponse, ConversationHistoryResponse, ConversationResponse
from app.db.database import get_db
import logging
from typing import List

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=ChatResponse)
async def chat_with_memory(request: ChatMessageCreate, db: Session = Depends(get_db)):
    """
    Send a message to Gemini AI with conversational memory.
    
    Uses conversation history to maintain context across multiple messages.
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
        
        # Get response from Gemini
        response_text = await gemini_service.generate_response(full_prompt)
        
        # Add assistant message to conversation
        assistant_message = conversation_memory.add_message(
            db=db,
            conversation_id=conversation.conversation_id,
            role="assistant",
            content=response_text,
            model_used="gemini-2.0-flash"
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
            provider="gemini"
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

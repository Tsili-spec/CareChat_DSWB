"""
Chatbot endpoints for Track2 functionality
Multi-LLM chat with conversational memory and RAG
"""
from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile, Form
from typing import Optional, List, Literal
import logging
from datetime import datetime

from app.schemas.conversation import (
    ChatMessageCreate,
    ChatResponse, 
    ConversationHistoryResponse,
    ConversationListResponse,
    ConversationUpdateRequest
)
from app.services.llm_service import llm_service
from app.services.conversation_service import conversation_memory
from app.services.transcription import transcribe_and_translate, save_audio_file
from app.api.deps import get_current_user
from app.models import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ChatResponse)
async def chat_with_memory(
    request: ChatMessageCreate, 
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to AI with conversational memory.
    
    Uses conversation history to maintain context across multiple messages.
    If this is the first message, set conversation_id to null.
    """
    try:
        logger.info(f"Chat request from user {current_user.user_id} with message length: {len(request.message)}")
        
        # Get or create conversation
        conversation = await conversation_memory.get_or_create_conversation(
            user_id=str(current_user.user_id),
            conversation_id=request.conversation_id
        )
        
        # Get conversation context (previous messages)
        context_messages = await conversation_memory.get_conversation_context(
            conversation_id=conversation["conversation_id"]
        )
        
        # Save user message
        await conversation_memory.save_message(
            conversation_id=conversation["conversation_id"],
            role="user",
            content=request.message
        )
        
        # Generate AI response
        response_data = await llm_service.generate_response(
            message=request.message,
            context_messages=context_messages,
            provider=request.provider or "gemini",
            user_id=str(current_user.user_id)
        )
        
        # Save AI response
        await conversation_memory.save_message(
            conversation_id=conversation["conversation_id"],
            role="assistant",
            content=response_data["content"],
            model_used=response_data.get("model_used"),
            token_count=response_data.get("token_count")
        )
        
        return ChatResponse(
            response=response_data["content"],
            conversation_id=conversation["conversation_id"],
            timestamp=datetime.utcnow(),
            model_used=response_data.get("model_used"),
            provider=response_data["provider"],
            token_count=response_data.get("token_count", 0)
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat service error: {str(e)}"
        )

@router.post("/transcribe", response_model=ChatResponse)
async def transcribe_and_chat(
    audio: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    provider: Optional[Literal["gemini", "groq", "openai"]] = Form("groq"),
    current_user: User = Depends(get_current_user)
):
    """
    Transcribe audio file to text using Whisper model and then process through chat.
    
    Parameters:
    - audio: Audio file (MP3, WAV, M4A, FLAC, etc.)
    - conversation_id: Existing conversation ID (optional)
    - provider: LLM provider to use for chat response (default: groq)
    
    Returns:
    - Transcription results and chat response
    """
    try:
        # Validate audio file
        if not audio.filename:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        # Check file extension
        allowed_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm'}
        file_extension = audio.filename.split('.')[-1].lower() if '.' in audio.filename else ''
        
        if f'.{file_extension}' not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio format. Supported formats: {', '.join(allowed_extensions)}"
            )
        
        # Read audio file
        audio_content = await audio.read()
        if len(audio_content) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Save audio file for processing
        file_path = save_audio_file(audio_content, f"{current_user.user_id}_{audio.filename}")
        
        # Transcribe audio
        transcription_result = transcribe_and_translate(audio_content)
        
        if not transcription_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcription_result.get('error', 'Unknown error')}"
            )
        
        transcribed_text = transcription_result["original_text"]
        detected_language = transcription_result["detected_language"]
        
        # Process transcribed text through chat
        chat_request = ChatMessageCreate(
            message=transcribed_text,
            conversation_id=conversation_id,
            provider=provider
        )
        
        # Get or create conversation
        conversation = await conversation_memory.get_or_create_conversation(
            user_id=str(current_user.user_id),
            conversation_id=conversation_id
        )
        
        # Get conversation context
        context_messages = await conversation_memory.get_conversation_context(
            conversation_id=conversation["conversation_id"]
        )
        
        # Save transcribed message
        await conversation_memory.save_message(
            conversation_id=conversation["conversation_id"],
            role="user",
            content=transcribed_text
        )
        
        # Generate AI response
        response_data = await llm_service.generate_response(
            message=transcribed_text,
            context_messages=context_messages,
            provider=provider or "gemini",
            user_id=str(current_user.user_id)
        )
        
        # Save AI response
        await conversation_memory.save_message(
            conversation_id=conversation["conversation_id"],
            role="assistant",
            content=response_data["content"],
            model_used=response_data.get("model_used"),
            token_count=response_data.get("token_count")
        )
        
        return ChatResponse(
            response=response_data["content"],
            conversation_id=conversation["conversation_id"],
            timestamp=datetime.utcnow(),
            model_used=response_data.get("model_used"),
            provider=response_data["provider"],
            token_count=response_data.get("token_count", 0),
            transcription={
                "original_text": transcribed_text,
                "detected_language": detected_language,
                "confidence": transcription_result.get("confidence", 0.0)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in transcribe and chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription and chat service error: {str(e)}"
        )

@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """List all conversations for the current user"""
    try:
        conversations = await conversation_memory.list_user_conversations(
            user_id=str(current_user.user_id),
            limit=limit
        )
        
        return ConversationListResponse(
            conversations=conversations,
            total_count=len(conversations)
        )
        
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversations: {str(e)}"
        )

@router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get full conversation history"""
    try:
        history = await conversation_memory.get_conversation_history(
            user_id=str(current_user.user_id),
            conversation_id=conversation_id
        )
        
        return ConversationHistoryResponse(
            conversation=history["conversation"],
            messages=history["messages"]
        )
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation not found or access denied"
        )

@router.put("/conversations/{conversation_id}", response_model=dict)
async def update_conversation(
    conversation_id: str,
    request: ConversationUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update conversation title"""
    try:
        success = await conversation_memory.update_conversation_title(
            conversation_id=conversation_id,
            title=request.title,
            user_id=str(current_user.user_id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )
        
        return {"message": "Conversation updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating conversation: {str(e)}"
        )

@router.delete("/conversations/{conversation_id}", response_model=dict)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation and all its messages"""
    try:
        success = await conversation_memory.delete_conversation(
            conversation_id=conversation_id,
            user_id=str(current_user.user_id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )

@router.get("/health/llm")
async def llm_health():
    """Get health status of all LLM providers"""
    try:
        return llm_service.get_health_status()
    except Exception as e:
        logger.error(f"Error getting LLM health status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting health status: {str(e)}"
        )

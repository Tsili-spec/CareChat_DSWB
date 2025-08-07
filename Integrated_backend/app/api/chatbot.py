"""
Multi-LLM Chat endpoint for CareChat with Conversational Memory and RAG
Adapted for MongoDB with Beanie ODM
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.services.llm_service import llm_service
from app.services.conversation_service import conversation_memory
from app.services.rag_service import rag_service
from app.services.transcription import transcribe_audio
from app.schemas.conversation import (
    ChatMessageCreate, ChatResponse, ConversationHistoryResponse, 
    ConversationResponse, AudioChatRequest, AudioChatResponse, ChatMessageResponse
)
from app.models.models import Patient, Conversation, ChatMessage
import logging
from typing import List, Optional
from bson import ObjectId

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=ChatResponse)
async def chat_with_memory(request: ChatMessageCreate):
    """
    Send a message to AI with conversational memory.
    
    Uses conversation history to maintain context across multiple messages.
    If this is the first message you are sending then set the conversation_id to null.
    conversation_id: null
    """
    try:
        logger.info(f"Chat request from user {request.user_id} with message length: {len(request.message)}")
        
        # Verify user exists
        try:
            patient = await Patient.find_one(Patient.id == ObjectId(request.user_id))
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")
        except Exception:
            # Try with string ID if ObjectId fails
            patient = await Patient.find_one(Patient.patient_id == request.user_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")
            # Use the string patient_id for consistency
            request.user_id = patient.patient_id or str(patient.id)
        
        # Get or create conversation
        conversation = await conversation_memory.get_or_create_conversation(
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
        
        # Get conversation context (previous messages)
        context_messages = await conversation_memory.get_conversation_context(
            conversation_id=str(conversation.id)
        )
        
        # Add user message to conversation
        user_message = await conversation_memory.add_message(
            conversation_id=str(conversation.id),
            role="user",
            content=request.message
        )
        
        # Format context for LLM
        context = conversation_memory.format_context_for_llm(context_messages)
        
        # Prepare base prompt with context
        if context:
            base_prompt = f"{context}\nHuman: {request.message}"
        else:
            base_prompt = request.message
        
        # Enhance prompt with RAG if medical context is relevant
        enhanced_prompt = await rag_service.get_rag_enhanced_prompt(
            user_message=request.message,
            base_prompt=base_prompt
        )
        
        # Generate title for new conversations
        if not conversation.title and len(context_messages) == 0:
            title = conversation_memory.auto_generate_title(request.message)
            await conversation_memory.update_conversation_title(
                conversation_id=str(conversation.id),
                title=title
            )
        
        # Get response from specified LLM provider with healthcare guidelines
        response_text = await llm_service.generate_response(
            enhanced_prompt,
            provider=request.provider,
            temperature=0.3
        )
        
        # Add assistant message to conversation
        model_name = f"{request.provider}-2.0-flash" if request.provider == "gemini" else "gemma2-9b-it"
        assistant_message = await conversation_memory.add_message(
            conversation_id=str(conversation.id),
            role="assistant",
            content=response_text,
            model_used=model_name
        )
        
        return ChatResponse(
            conversation_id=str(conversation.id),
            user_message=ChatMessageResponse(
                message_id=str(user_message.id),
                role=user_message.role,
                content=user_message.content,
                timestamp=user_message.timestamp,
                model_used=user_message.model_used
            ),
            assistant_message=ChatMessageResponse(
                message_id=str(assistant_message.id),
                role=assistant_message.role,
                content=assistant_message.content,
                timestamp=assistant_message.timestamp,
                model_used=assistant_message.model_used
            ),
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

@router.post("/audio", response_model=AudioChatResponse)
async def chat_with_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    user_id: str = Form(..., description="The user's patient ID"),
    conversation_id: Optional[str] = Form(None, description="Existing conversation ID (if continuing)"),
    provider: Optional[str] = Form("groq", description="LLM provider to use")
):
    """
    Send an audio message to AI with conversational memory.
    
    This endpoint:
    1. Receives an audio file from the frontend
    2. Transcribes the audio to text using Whisper
    3. Processes the transcribed text through the same chat logic as the text endpoint
    4. Returns both the transcription details and chat response
    
    Supported audio formats: WAV, MP3, M4A, FLAC, OGG
    """
    try:
        logger.info(f"Audio chat request from user {user_id}, file: {audio.filename}")
        
        # Validate provider
        if provider not in ["gemini", "groq"]:
            provider = "groq"
        
        # Validate audio file
        if not audio.filename:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        # Check file size (limit to 25MB)
        if audio.size and audio.size > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large (max 25MB)")
        
        # Read audio file
        audio_data = await audio.read()
        if not audio_data:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Transcribe audio
        logger.info("Transcribing audio...")
        transcription_result = transcribe_audio(audio_data)
        
        if not transcription_result["text"].strip():
            raise HTTPException(status_code=400, detail="Could not transcribe audio or audio is silent")
        
        transcribed_text = transcription_result["text"].strip()
        detected_language = transcription_result["language"]
        confidence = transcription_result["confidence"]
        
        logger.info(f"Transcription successful: '{transcribed_text[:50]}...' (language: {detected_language}, confidence: {confidence:.2f})")
        
        # Verify user exists
        try:
            patient = await Patient.find_one(Patient.id == ObjectId(user_id))
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")
        except Exception:
            # Try with string ID if ObjectId fails
            patient = await Patient.find_one(Patient.patient_id == user_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")
            # Use the string patient_id for consistency
            user_id = patient.patient_id or str(patient.id)
        
        # Get or create conversation
        conversation = await conversation_memory.get_or_create_conversation(
            user_id=user_id,
            conversation_id=conversation_id
        )
        
        # Get conversation context (previous messages)
        context_messages = await conversation_memory.get_conversation_context(
            conversation_id=str(conversation.id)
        )
        
        # Add user message to conversation
        user_message = await conversation_memory.add_message(
            conversation_id=str(conversation.id),
            role="user",
            content=transcribed_text
        )
        
        # Format context for LLM
        context = conversation_memory.format_context_for_llm(context_messages)
        
        # Prepare base prompt with context
        if context:
            base_prompt = f"{context}\nHuman: {transcribed_text}"
        else:
            base_prompt = transcribed_text
        
        # Enhance prompt with RAG if medical context is relevant
        enhanced_prompt = await rag_service.get_rag_enhanced_prompt(
            user_message=transcribed_text,
            base_prompt=base_prompt
        )
        
        # Generate title for new conversations
        if not conversation.title and len(context_messages) == 0:
            title = conversation_memory.auto_generate_title(transcribed_text)
            await conversation_memory.update_conversation_title(
                conversation_id=str(conversation.id),
                title=title
            )
        
        # Get response from specified LLM provider with healthcare guidelines
        response_text = await llm_service.generate_response(
            enhanced_prompt,
            provider=provider,
            temperature=0.3
        )
        
        # Add assistant message to conversation
        model_name = f"{provider}-2.0-flash" if provider == "gemini" else "gemma2-9b-it"
        assistant_message = await conversation_memory.add_message(
            conversation_id=str(conversation.id),
            role="assistant",
            content=response_text,
            model_used=model_name
        )
        
        return AudioChatResponse(
            conversation_id=str(conversation.id),
            transcribed_text=transcribed_text,
            detected_language=detected_language,
            transcription_confidence=confidence,
            user_message=ChatMessageResponse(
                message_id=str(user_message.id),
                role=user_message.role,
                content=user_message.content,
                timestamp=user_message.timestamp,
                model_used=user_message.model_used
            ),
            assistant_message=ChatMessageResponse(
                message_id=str(assistant_message.id),
                role=assistant_message.role,
                content=assistant_message.content,
                timestamp=assistant_message.timestamp,
                model_used=assistant_message.model_used
            ),
            provider=provider
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Audio chat service error: {str(e)}"
        )

@router.get("/conversations/{user_id}", response_model=List[ConversationResponse])
async def get_user_conversations(user_id: str):
    """Get all conversations for a user"""
    try:
        # Verify user exists
        try:
            patient = await Patient.find_one(Patient.id == ObjectId(user_id))
            if not patient:
                patient = await Patient.find_one(Patient.patient_id == user_id)
                if not patient:
                    raise HTTPException(status_code=404, detail="Patient not found")
                user_id = patient.patient_id or str(patient.id)
        except Exception:
            patient = await Patient.find_one(Patient.patient_id == user_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")
        
        conversations = await conversation_memory.get_user_conversations(user_id=user_id)
        
        result = []
        for conv in conversations:
            message_count = await conversation_memory.get_conversation_message_count(
                conversation_id=str(conv.id)
            )
            result.append(ConversationResponse(
                conversation_id=str(conv.id),
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count
            ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{user_id}/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(user_id: str, conversation_id: str):
    """Get full conversation history"""
    try:
        # Verify user exists
        try:
            patient = await Patient.find_one(Patient.id == ObjectId(user_id))
            if not patient:
                patient = await Patient.find_one(Patient.patient_id == user_id)
                if not patient:
                    raise HTTPException(status_code=404, detail="Patient not found")
                user_id = patient.patient_id or str(patient.id)
        except Exception:
            patient = await Patient.find_one(Patient.patient_id == user_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get conversation and verify ownership
        try:
            conversation = await Conversation.find_one(
                Conversation.id == ObjectId(conversation_id),
                Conversation.patient_id == user_id
            )
        except Exception:
            conversation = await Conversation.find_one(
                Conversation.patient_id == user_id
            )
            if conversation and str(conversation.id) != conversation_id:
                conversation = None
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages using the conversation service
        messages_data = await conversation_memory.get_conversation_messages(
            conversation_id=str(conversation.id)
        )
        
        messages = []
        for msg in messages_data:
            messages.append(ChatMessageResponse(
                message_id=str(msg.id),
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                model_used=msg.model_used
            ))
        
        return ConversationHistoryResponse(
            conversation_id=str(conversation.id),
            title=conversation.title,
            messages=messages,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversations/{user_id}/{conversation_id}")
async def delete_conversation(user_id: str, conversation_id: str):
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
        # Verify user exists
        try:
            patient = await Patient.find_one(Patient.id == ObjectId(user_id))
            if not patient:
                patient = await Patient.find_one(Patient.patient_id == user_id)
                if not patient:
                    raise HTTPException(status_code=404, detail="Patient not found")
                user_id = patient.patient_id or str(patient.id)
        except Exception:
            patient = await Patient.find_one(Patient.patient_id == user_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")
        
        # Delete conversation using conversation service
        deletion_result = await conversation_memory.delete_conversation(
            conversation_id=conversation_id, 
            user_id=user_id
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/messages/{user_id}/{message_id}")
async def delete_message(user_id: str, message_id: str):
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
        # Verify user exists
        try:
            patient = await Patient.find_one(Patient.id == ObjectId(user_id))
            if not patient:
                patient = await Patient.find_one(Patient.patient_id == user_id)
                if not patient:
                    raise HTTPException(status_code=404, detail="Patient not found")
                user_id = patient.patient_id or str(patient.id)
        except Exception:
            patient = await Patient.find_one(Patient.patient_id == user_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")
        
        # Delete message using conversation service
        deletion_result = await conversation_memory.delete_message(
            message_id=message_id,
            user_id=user_id
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Import ChatMessageResponse here to avoid circular imports
from app.schemas.conversation import ChatMessageResponse

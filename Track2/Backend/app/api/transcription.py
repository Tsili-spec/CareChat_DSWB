from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, Literal
import os
import logging

from app.services.transcription_translation import transcribe_simple
from app.services.llm_service import llm_service
from app.services.conversation_service import conversation_memory
from app.schemas.conversation import ChatMessageCreate, ChatResponse, ChatMessageResponse
from app.db.database import get_db

router = APIRouter(tags=["Transcription"])
logger = logging.getLogger(__name__)

# Create upload directory if it doesn't exist
UPLOAD_DIR = "upload"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/transcribe/")
async def transcribe_audio_endpoint(
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    provider: Optional[Literal["gemini", "groq"]] = Form("groq"),
    db: Session = Depends(get_db)
):
    """
    Transcribe audio file to text using Whisper model and then process through chat.
    
    Parameters:
    - audio: Audio file (MP3, WAV, M4A, FLAC, etc.)
    - user_id: User's patient ID
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
        file_extension = os.path.splitext(audio.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Read audio data
        audio_bytes = await audio.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Check file size (limit to 25MB)
        max_size = 25 * 1024 * 1024  # 25MB
        if len(audio_bytes) > max_size:
            raise HTTPException(status_code=400, detail="Audio file too large. Maximum size is 25MB")
        
        # Step 1: Transcribe audio
        transcription_result = transcribe_simple(audio_bytes)
        transcribed_text = transcription_result["text"]
        
        if not transcribed_text.strip():
            raise HTTPException(status_code=400, detail="Could not transcribe audio or audio contains no speech")
        
        # Step 2: Process transcribed text through chat
        try:
            # Convert user_id to UUID
            user_uuid = UUID(user_id)
            conversation_uuid = UUID(conversation_id) if conversation_id else None
            
            # Create chat request with transcribed text
            chat_request = ChatMessageCreate(
                user_id=user_uuid,
                message=transcribed_text,
                conversation_id=conversation_uuid,
                provider=provider
            )
            
            # Get or create conversation
            conversation = conversation_memory.get_or_create_conversation(
                db=db,
                user_id=chat_request.user_id,
                conversation_id=chat_request.conversation_id
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
                content=chat_request.message
            )
            
            # Format context for LLM
            context = conversation_memory.format_context_for_llm(context_messages)
            
            # Prepare prompt with context
            if context:
                full_prompt = f"{context}\nHuman: {chat_request.message}"
            else:
                full_prompt = chat_request.message
            
            # Generate title for new conversations
            if not conversation.title and len(context_messages) == 0:
                title = conversation_memory.auto_generate_title(chat_request.message)
                conversation_memory.update_conversation_title(
                    db=db,
                    conversation_id=conversation.conversation_id,
                    title=title
                )
            
            # Get response from specified LLM provider
            response_text = await llm_service.generate_response(
                full_prompt,
                provider=chat_request.provider,
                temperature=0.3
            )
            
            # Add assistant message to conversation
            model_name = f"{chat_request.provider}-2.0-flash" if chat_request.provider == "gemini" else "llama-4-maverick-17b"
            assistant_message = conversation_memory.add_message(
                db=db,
                conversation_id=conversation.conversation_id,
                role="assistant",
                content=response_text,
                model_used=model_name
            )
            
            # Create chat response
            user_message_response = ChatMessageResponse(
                message_id=user_message.message_id,
                role=user_message.role,
                content=user_message.content,
                timestamp=user_message.timestamp,
                model_used=user_message.model_used
            )
            
            assistant_message_response = ChatMessageResponse(
                message_id=assistant_message.message_id,
                role=assistant_message.role,
                content=assistant_message.content,
                timestamp=assistant_message.timestamp,
                model_used=assistant_message.model_used
            )
            
            chat_response = ChatResponse(
                conversation_id=conversation.conversation_id,
                user_message=user_message_response,
                assistant_message=assistant_message_response,
                provider=chat_request.provider
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid user_id or conversation_id format: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
        
        # Format combined response
        response_data = {
            "status": "success",
            "filename": audio.filename,
            "file_size_bytes": len(audio_bytes),
            "transcription": {
                "text": transcription_result["text"],
                "detected_language": transcription_result["language"],
                "confidence": transcription_result["confidence"],
                "segments": transcription_result.get("segments", [])
            },
            "chat_response": {
                "conversation_id": str(chat_response.conversation_id),
                "user_message": {
                    "message_id": str(chat_response.user_message.message_id),
                    "role": chat_response.user_message.role,
                    "content": chat_response.user_message.content,
                    "timestamp": chat_response.user_message.timestamp.isoformat(),
                    "model_used": chat_response.user_message.model_used
                },
                "assistant_message": {
                    "message_id": str(chat_response.assistant_message.message_id),
                    "role": chat_response.assistant_message.role,
                    "content": chat_response.assistant_message.content,
                    "timestamp": chat_response.assistant_message.timestamp.isoformat(),
                    "model_used": chat_response.assistant_message.model_used
                },
                "provider": chat_response.provider
            }
        }
        
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Transcription endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/transcribe/simple/")
async def simple_transcribe(audio: UploadFile = File(...)):
    """
    Simple transcription endpoint that returns only the transcribed text.
    
    Parameters:
    - audio: Audio file
    
    Returns:
    - Simple response with transcribed text
    """
    try:
        # Validate and read audio
        if not audio.filename:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        audio_bytes = await audio.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Transcribe
        result = transcribe_simple(audio_bytes)
        
        return {
            "transcribed_text": result["text"],
            "detected_language": result["language"],
            "confidence": result["confidence"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Simple transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.get("/transcribe/supported-formats/")
async def get_supported_formats():
    """
    Get list of supported audio formats.
    
    Returns:
    - List of supported audio file extensions
    """
    return {
        "supported_formats": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"],
        "max_file_size_mb": 25,
        "supported_languages": "99+ languages (auto-detected by Whisper)",
        "transcription_model": "OpenAI Whisper (small)"
    }

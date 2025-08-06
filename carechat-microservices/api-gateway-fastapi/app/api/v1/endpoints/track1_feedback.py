"""
Track1-style feedback endpoints for text and audio feedback with analysis
Based on Track1 implementation with sentiment analysis and topic extraction
"""
from fastapi import APIRouter, HTTPException, Depends, status, Form, File, UploadFile
from typing import Optional
import logging
from datetime import datetime
import os

from app.services.analysis import analyze_feedback
from app.services.transcription import transcribe_and_translate, save_audio_file
from app.services.translation import translate_text, detect_language
from app.schemas.feedback import (
    Track1FeedbackCreate,
    Track1FeedbackResponse,
    Track1AudioFeedbackResponse
)
from app.db.database import get_feedback_sessions_collection
from app.api.deps import get_current_user
from app.models import User

router = APIRouter()
logger = logging.getLogger(__name__)

# Create upload directory if it doesn't exist
UPLOAD_DIR = "upload"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/text", response_model=Track1FeedbackResponse)
async def create_text_feedback(
    patient_id: str = Form(...),
    rating: Optional[int] = Form(None),
    feedback_text: str = Form(...),
    language: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Create text-only feedback with sentiment analysis
    Based on Track1 implementation
    """
    try:
        # Process language
        lang = language.lower()
        if lang in ["en", "eng", "english"]:
            detected_language = "en"
            translated_text = feedback_text
        elif lang in ["fr", "fra", "french"]:
            detected_language = "fr"
            translated_text = translate_text(feedback_text, "fr", "en")
        elif lang in ["es", "esp", "spanish"]:
            detected_language = "es"
            translated_text = translate_text(feedback_text, "es", "en")
        else:
            detected_language = detect_language(feedback_text)
            translated_text = translate_text(feedback_text, detected_language, "en")

        # Analyze feedback
        analysis = analyze_feedback(text=translated_text, rating=rating)
        sentiment = analysis.get("sentiment")
        topic = analysis.get("topics") if analysis.get("sentiment") == "negative" else None
        urgency = "urgent" if analysis.get("urgent_flag") else "not urgent"

        # Create feedback document
        feedback_doc = {
            "feedback_id": str(datetime.utcnow().timestamp()).replace(".", ""),
            "patient_id": patient_id,
            "user_id": str(current_user.user_id),
            "rating": rating,
            "feedback_text": feedback_text,
            "translated_text": translated_text,
            "language": detected_language,
            "sentiment": sentiment,
            "topic": topic,
            "urgency": urgency,
            "feedback_type": "text",
            "created_at": datetime.utcnow()
        }

        # Save to database
        feedback_collection = await get_feedback_sessions_collection()
        result = await feedback_collection.insert_one(feedback_doc)

        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save feedback"
            )

        logger.info(f"Text feedback created: {feedback_doc['feedback_id']} for patient: {patient_id}")

        return Track1FeedbackResponse(
            feedback_id=feedback_doc["feedback_id"],
            patient_id=feedback_doc["patient_id"],
            rating=feedback_doc["rating"],
            feedback_text=feedback_doc["feedback_text"],
            translated_text=feedback_doc["translated_text"],
            language=feedback_doc["language"],
            sentiment=feedback_doc["sentiment"],
            topic=feedback_doc["topic"],
            urgency=feedback_doc["urgency"],
            created_at=feedback_doc["created_at"]
        )

    except Exception as e:
        logger.error(f"Error creating text feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating feedback: {str(e)}"
        )

@router.post("/audio", response_model=Track1AudioFeedbackResponse)
async def create_audio_feedback(
    patient_id: str = Form(...),
    rating: Optional[int] = Form(None),
    language: str = Form(...),
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Create audio feedback with transcription and sentiment analysis
    Based on Track1 implementation
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

        # Read and save audio file
        audio_content = await audio.read()
        if len(audio_content) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        file_location = save_audio_file(audio_content, f"{patient_id}_{audio.filename}")

        # Transcribe and translate audio
        transcription_result = transcribe_and_translate(audio_content)
        
        if not transcription_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcription_result.get('error', 'Unknown error')}"
            )

        feedback_text = transcription_result["original_text"]
        detected_language = transcription_result["detected_language"]
        translated_text = transcription_result["translations"].get("en", feedback_text)

        # Set rating to 0 if None
        if rating is None:
            rating = 0

        # Analyze feedback
        analysis = analyze_feedback(text=translated_text, rating=rating)
        sentiment = analysis.get("sentiment")
        topic = analysis.get("topics") if analysis.get("sentiment") == "negative" else None
        urgency = "urgent" if analysis.get("urgent_flag") else "not urgent"

        # Create feedback document
        feedback_doc = {
            "feedback_id": str(datetime.utcnow().timestamp()).replace(".", ""),
            "patient_id": patient_id,
            "user_id": str(current_user.user_id),
            "rating": rating,
            "feedback_text": feedback_text,
            "translated_text": translated_text,
            "language": detected_language,
            "sentiment": sentiment,
            "topic": topic,
            "urgency": urgency,
            "feedback_type": "audio",
            "audio_file_path": file_location,
            "transcription_confidence": transcription_result.get("confidence", 0.0),
            "transcription_duration": transcription_result.get("duration", 0.0),
            "created_at": datetime.utcnow()
        }

        # Save to database
        feedback_collection = await get_feedback_sessions_collection()
        result = await feedback_collection.insert_one(feedback_doc)

        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save feedback"
            )

        logger.info(f"Audio feedback created: {feedback_doc['feedback_id']} for patient: {patient_id}")

        return Track1AudioFeedbackResponse(
            feedback_id=feedback_doc["feedback_id"],
            patient_id=feedback_doc["patient_id"],
            rating=feedback_doc["rating"],
            feedback_text=feedback_doc["feedback_text"],
            translated_text=feedback_doc["translated_text"],
            language=feedback_doc["language"],
            sentiment=feedback_doc["sentiment"],
            topic=feedback_doc["topic"],
            urgency=feedback_doc["urgency"],
            audio_file_path=feedback_doc["audio_file_path"],
            transcription_confidence=feedback_doc["transcription_confidence"],
            transcription_duration=feedback_doc["transcription_duration"],
            created_at=feedback_doc["created_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating audio feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating audio feedback: {str(e)}"
        )

@router.get("/{feedback_id}", response_model=Track1FeedbackResponse)
async def get_feedback(
    feedback_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get feedback by ID"""
    try:
        feedback_collection = await get_feedback_sessions_collection()
        
        feedback = await feedback_collection.find_one({
            "feedback_id": feedback_id,
            "user_id": str(current_user.user_id)
        })
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )

        return Track1FeedbackResponse(
            feedback_id=feedback["feedback_id"],
            patient_id=feedback["patient_id"],
            rating=feedback["rating"],
            feedback_text=feedback["feedback_text"],
            translated_text=feedback["translated_text"],
            language=feedback["language"],
            sentiment=feedback["sentiment"],
            topic=feedback["topic"],
            urgency=feedback["urgency"],
            created_at=feedback["created_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving feedback: {str(e)}"
        )

@router.get("/", response_model=list)
async def list_feedback(
    patient_id: Optional[str] = None,
    sentiment: Optional[str] = None,
    urgency: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """List feedback with optional filters"""
    try:
        feedback_collection = await get_feedback_sessions_collection()
        
        # Build query
        query = {"user_id": str(current_user.user_id)}
        if patient_id:
            query["patient_id"] = patient_id
        if sentiment:
            query["sentiment"] = sentiment
        if urgency:
            query["urgency"] = urgency

        # Get feedback
        cursor = feedback_collection.find(query).sort("created_at", -1).limit(limit)
        feedback_list = []
        
        async for feedback_doc in cursor:
            feedback_list.append(Track1FeedbackResponse(
                feedback_id=feedback_doc["feedback_id"],
                patient_id=feedback_doc["patient_id"],
                rating=feedback_doc["rating"],
                feedback_text=feedback_doc["feedback_text"],
                translated_text=feedback_doc["translated_text"],
                language=feedback_doc["language"],
                sentiment=feedback_doc["sentiment"],
                topic=feedback_doc["topic"],
                urgency=feedback_doc["urgency"],
                created_at=feedback_doc["created_at"]
            ))

        return feedback_list

    except Exception as e:
        logger.error(f"Error listing feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing feedback: {str(e)}"
        )

@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete feedback by ID"""
    try:
        feedback_collection = await get_feedback_sessions_collection()
        
        result = await feedback_collection.delete_one({
            "feedback_id": feedback_id,
            "user_id": str(current_user.user_id)
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )

        return {"message": "Feedback deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting feedback: {str(e)}"
        )

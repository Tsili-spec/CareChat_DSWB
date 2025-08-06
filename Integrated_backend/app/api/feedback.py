from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, status
from typing import List, Optional
import os
from app.schemas.feedback import Feedback, FeedbackCreate
from app.models.models import Feedback as FeedbackModel
from app.services.analysis import analyze_feedback
from app.services.transcription_translation import transcribe_and_translate
from app.services.translation import translate_text
from app.db.database import get_db
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Create upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "upload")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/feedback/", 
             response_model=Feedback,
             summary="Submit text feedback",
             description="Submit text feedback with analysis")
async def create_feedback(
    patient_id: str = Form(..., description="Patient's unique identifier"),
    rating: Optional[int] = Form(None, description="Rating from 1-5"),
    feedback_text: str = Form(..., description="Feedback text"),
    language: str = Form(..., description="Language of feedback (en, fr, etc.)")
):
    """
    Submit text feedback.
    
    **Request Body (Form Data):**
    - patient_id: Patient's unique identifier (required)
    - rating: Rating from 1-5 (optional)
    - feedback_text: Feedback text content (required)
    - language: Language code (required)
    
    **Response:** Feedback object with analysis results
    
    **Errors:**
    - 422: Validation errors
    """
    try:
        # Process language and translation
        lang = language.lower()
        if lang in ["en", "eng", "english"]:
            detected_language = "en"
            translated_text = feedback_text
        elif lang in ["fr", "fra", "french"]:
            detected_language = "fr"
            translated_text = translate_text(feedback_text, "fr", "en")
        else:
            detected_language = lang
            translated_text = feedback_text

        # Analyze feedback
        analysis = analyze_feedback(text=translated_text, rating=rating)
        sentiment = analysis.get("sentiment")
        topics = analysis.get("topics")
        topic = topics if analysis.get("sentiment") == "negative" and topics != 'Unidentified' else None
        urgency = "urgent" if analysis.get("urgent_flag") else "not urgent"
        
        # Create feedback record
        db_feedback = FeedbackModel(
            patient_id=patient_id,
            rating=rating,
            feedback_text=feedback_text,
            translated_text=translated_text,
            language=detected_language,
            sentiment=sentiment,
            topic=str(topic) if topic else None,
            urgency=urgency
        )
        
        await db_feedback.insert()
        logger.info(f"Text feedback created successfully with ID: {str(db_feedback.id)}")
        
        return Feedback(
            feedback_id=str(db_feedback.id),
            patient_id=db_feedback.patient_id,
            rating=db_feedback.rating,
            feedback_text=db_feedback.feedback_text,
            translated_text=db_feedback.translated_text,
            language=db_feedback.language,
            sentiment=db_feedback.sentiment,
            topic=db_feedback.topic,
            urgency=db_feedback.urgency,
            created_at=db_feedback.created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating text feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing feedback: {str(e)}"
        )

@router.post("/feedback/audio/", 
             response_model=Feedback,
             summary="Submit audio feedback",
             description="Submit audio feedback with transcription and analysis")
async def create_audio_feedback(
    patient_id: str = Form(..., description="Patient's unique identifier"),
    rating: Optional[int] = Form(None, description="Rating from 1-5"),
    language: str = Form(..., description="Expected language of audio"),
    audio: UploadFile = File(..., description="Audio file")
):
    """
    Submit audio feedback.
    
    **Request Body (Form Data):**
    - patient_id: Patient's unique identifier (required)
    - rating: Rating from 1-5 (optional)
    - language: Expected language of audio (required)
    - audio: Audio file (required)
    
    **Response:** Feedback object with transcription and analysis
    
    **Errors:**
    - 422: Validation errors
    """
    try:
        # Save uploaded audio file
        file_location = os.path.join(UPLOAD_DIR, f"{patient_id}_{audio.filename}")
        with open(file_location, "wb") as f:
            content = await audio.read()
            f.write(content)

        # Read file for transcription
        with open(file_location, "rb") as f:
            audio_bytes = f.read()

        # Transcribe and translate
        result = transcribe_and_translate(audio_bytes)
        feedback_text = result["original_text"]
        detected_language = result["detected_language"]
        translated_text = result["translations"].get("en", feedback_text)

        # Set rating to 0 if None for analysis
        analysis_rating = rating if rating is not None else None

        # Analyze feedback
        analysis = analyze_feedback(text=translated_text, rating=analysis_rating)
        sentiment = analysis.get("sentiment")
        topics = analysis.get("topics")
        topic = topics if analysis.get("sentiment") == "negative" and topics != 'Unidentified' else None
        urgency = "urgent" if analysis.get("urgent_flag") else "not urgent"
        
        # Create feedback record
        db_feedback = FeedbackModel(
            patient_id=patient_id,
            rating=rating,
            feedback_text=feedback_text,
            translated_text=translated_text,
            language=detected_language,
            sentiment=sentiment,
            topic=str(topic) if topic else None,
            urgency=urgency
        )
        
        await db_feedback.insert()
        logger.info(f"Audio feedback created successfully with ID: {str(db_feedback.id)}")
        
        # Clean up uploaded file
        try:
            os.remove(file_location)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup uploaded file: {cleanup_error}")
        
        return Feedback(
            feedback_id=str(db_feedback.id),
            patient_id=db_feedback.patient_id,
            rating=db_feedback.rating,
            feedback_text=db_feedback.feedback_text,
            translated_text=db_feedback.translated_text,
            language=db_feedback.language,
            sentiment=db_feedback.sentiment,
            topic=db_feedback.topic,
            urgency=db_feedback.urgency,
            created_at=db_feedback.created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating audio feedback: {e}")
        # Clean up uploaded file on error
        try:
            if 'file_location' in locals():
                os.remove(file_location)
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing audio feedback: {str(e)}"
        )

@router.get("/feedback/{feedback_id}", 
            response_model=Feedback,
            summary="Get specific feedback",
            description="Get specific feedback by ID")
async def read_feedback(feedback_id: str):
    """
    Get specific feedback by ID.
    
    **Path Parameters:**
    - feedback_id: Feedback's unique identifier
    
    **Response:** Feedback object
    
    **Errors:**
    - 404: Feedback not found
    """
    try:
        from bson import ObjectId
        feedback = await FeedbackModel.get(ObjectId(feedback_id))
    except Exception:
        feedback = None
        
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    return Feedback(
        feedback_id=str(feedback.id),
        patient_id=feedback.patient_id,
        rating=feedback.rating,
        feedback_text=feedback.feedback_text,
        translated_text=feedback.translated_text,
        language=feedback.language,
        sentiment=feedback.sentiment,
        topic=feedback.topic,
        urgency=feedback.urgency,
        created_at=feedback.created_at
    )

@router.get("/feedback/", 
            response_model=List[Feedback],
            summary="List all feedback",
            description="List all feedback")
async def list_feedback():
    """
    List all feedback.
    
    **Response:** Array of Feedback objects
    """
    try:
        feedbacks = await FeedbackModel.find().to_list()
        
        return [
            Feedback(
                feedback_id=str(feedback.id),
                patient_id=feedback.patient_id,
                rating=feedback.rating,
                feedback_text=feedback.feedback_text,
                translated_text=feedback.translated_text,
                language=feedback.language,
                sentiment=feedback.sentiment,
                topic=feedback.topic,
                urgency=feedback.urgency,
                created_at=feedback.created_at
            ) for feedback in feedbacks
        ]
        
    except Exception as e:
        logger.error(f"Error listing feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving feedback"
        )

@router.delete("/feedback/{feedback_id}",
               summary="Delete feedback",
               description="Delete feedback by ID")
async def delete_feedback(feedback_id: str):
    """
    Delete feedback.
    
    **Path Parameters:**
    - feedback_id: Feedback's unique identifier
    
    **Response:** Success confirmation
    
    **Errors:**
    - 404: Feedback not found
    """
    try:
        from bson import ObjectId
        feedback = await FeedbackModel.get(ObjectId(feedback_id))
    except Exception:
        feedback = None
        
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    await feedback.delete()
    logger.info(f"Feedback {feedback_id} deleted successfully")
    
    return {"ok": True, "message": "Feedback deleted successfully"}

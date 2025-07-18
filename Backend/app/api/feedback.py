from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Feedback as FeedbackModel
from app.schemas.feedback import Feedback, FeedbackCreate
from app.services.analysis import analyze_feedback
from app.services.transcription_translation import transcribe_and_translate


import os
from fastapi import UploadFile
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "upload")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


# 1. Text-only feedback endpoint
@router.post("/feedback/", response_model=Feedback)
async def create_feedback(
    patient_id: str = Form(...),
    rating: int = Form(None),
    feedback_text: str = Form(...),
    language: str = Form(...),
    db: Session = Depends(get_db)
):
    lang = language.lower()
    if lang in ["en", "eng", "english"]:
        detected_language = "en"
        translated_text = feedback_text
    elif lang in ["fr", "fra", "french"]:
        from app.services.translation import translate_text
        detected_language = "fr"
        translated_text = translate_text(feedback_text, "fr", "en")
    else:
        detected_language = lang
        translated_text = feedback_text

    analysis = analyze_feedback(text=translated_text, rating=rating)
    sentiment = analysis.get("sentiment")
    topic = analysis.get("topics") if analysis.get("sentiment") == "negative" else None
    urgency = "urgent" if analysis.get("urgent_flag") else "not urgent"
    db_feedback = FeedbackModel(
        patient_id=patient_id,
        rating=rating,
        feedback_text=feedback_text,
        translated_text=translated_text,
        language=detected_language,
        sentiment=sentiment,
        topic=topic,
        urgency=urgency
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

# 2. Audio feedback endpoint
@router.post("/feedback/audio/", response_model=Feedback)
async def create_audio_feedback(
    patient_id: str = Form(...),
    rating: int = Form(None),
    language: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save uploaded audio file
    file_location = os.path.join(UPLOAD_DIR, f"{patient_id}_{audio.filename}")
    with open(file_location, "wb") as f:
        content = await audio.read()
        f.write(content)

    # Read file for transcription
    with open(file_location, "rb") as f:
        audio_bytes = f.read()

    result = transcribe_and_translate(audio_bytes)
    feedback_text = result["original_text"]
    detected_language = result["detected_language"]
    translated_text = result["translations"].get("en", feedback_text)

    # Set rating to 0 if None
    if rating is None:
        rating = 0

    analysis = analyze_feedback(text=translated_text, rating=rating)
    sentiment = analysis.get("sentiment")
    topic = analysis.get("topics") if analysis.get("sentiment") == "negative" else None
    urgency = "urgent" if analysis.get("urgent_flag") else "not urgent"
    db_feedback = FeedbackModel(
        patient_id=patient_id,
        rating=rating,
        feedback_text=feedback_text,
        translated_text=translated_text,
        language=detected_language,
        sentiment=sentiment,
        topic=topic,
        urgency=urgency
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("/feedback/{feedback_id}", response_model=Feedback)
def read_feedback(feedback_id: str, db: Session = Depends(get_db)):
    feedback = db.query(FeedbackModel).filter(FeedbackModel.feedback_id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

@router.get("/feedback/", response_model=list[Feedback])
def list_feedback(db: Session = Depends(get_db)):
    return db.query(FeedbackModel).all()

@router.delete("/feedback/{feedback_id}")
def delete_feedback(feedback_id: str, db: Session = Depends(get_db)):
    feedback = db.query(FeedbackModel).filter(FeedbackModel.feedback_id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    db.delete(feedback)
    db.commit()
    return {"ok": True}

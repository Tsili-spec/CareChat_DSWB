from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Feedback as FeedbackModel
from app.schemas.feedback import Feedback, FeedbackCreate
from app.services.analysis import analyze_feedback
from app.services.translation import translate_to_english

router = APIRouter()

@router.post("/feedback/", response_model=Feedback)
async def create_feedback(
    patient_id: str = Form(...),
    rating: int = Form(None),
    feedback_text: str = Form(None),
    language: str = Form(...),
    # audio removed
    db: Session = Depends(get_db)
):
    if feedback_text:
        translated_text = translate_to_english(feedback_text, language)
        # Always analyze the translated (English) text
        analysis = analyze_feedback(text=translated_text, rating=rating)
        sentiment = analysis.get("sentiment")
        topic = analysis.get("topics") if analysis.get("sentiment") == "negative" else None
        urgency = "urgent" if analysis.get("urgent_flag") else "not urgent"
        text_for_analysis = translated_text
    else:
        text_for_analysis = ""
        translated_text = ""
        analysis = analyze_feedback(rating=rating)
        sentiment = analysis.get("sentiment")
        topic = None
        urgency = None
    db_feedback = FeedbackModel(
        patient_id=patient_id,
        rating=rating,
        feedback_text=text_for_analysis,
        translated_text=translated_text,
        language=language,
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

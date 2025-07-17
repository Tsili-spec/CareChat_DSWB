from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Feedback as FeedbackModel
from app.schemas.feedback import Feedback, FeedbackCreate
from app.services.analysis import analyze_feedback

router = APIRouter()

@router.post("/feedback/", response_model=Feedback)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    analysis = analyze_feedback(text=feedback.feedback_text, rating=feedback.rating)
    sentiment = analysis.get("sentiment")
    topic = analysis.get("topics") if analysis.get("sentiment") == "negative" else None
    urgency = "urgent" if analysis.get("urgent_flag") else "not urgent"
    db_feedback = FeedbackModel(
        patient_id=feedback.patient_id,
        rating=feedback.rating,
        feedback_text=feedback.feedback_text,
        translated_text=feedback.feedback_text,  # translation not implemented
        language=feedback.language,
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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Feedback as FeedbackModel
from app.schemas.feedback import Feedback, FeedbackCreate

router = APIRouter()

@router.post("/feedback/", response_model=Feedback)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    db_feedback = FeedbackModel(**feedback.dict())
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

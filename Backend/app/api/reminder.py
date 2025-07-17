from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Reminder as ReminderModel
from app.schemas.reminder import Reminder, ReminderCreate
from datetime import datetime

router = APIRouter()

@router.post("/reminder/", response_model=Reminder)
def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    try:
        db_reminder = ReminderModel(
            patient_id=reminder.patient_id,
            message=reminder.message,
            scheduled_time=reminder.scheduled_time,
            days=reminder.days,
            status=reminder.status,
            created_at=datetime.utcnow()
        )
        db.add(db_reminder)
        db.commit()
        db.refresh(db_reminder)
        return db_reminder
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating reminder: {str(e)}")

@router.get("/reminder/{patient_id}", response_model=list[Reminder])
def read_reminders_for_patient(patient_id: str, db: Session = Depends(get_db)):
    reminders = db.query(ReminderModel).filter(ReminderModel.patient_id == patient_id).all()
    if not reminders:
        raise HTTPException(status_code=404, detail="No reminders found for this patient")
    return reminders

@router.get("/reminder/", response_model=list[Reminder])
def list_reminders(db: Session = Depends(get_db)):
    return db.query(ReminderModel).all()

@router.delete("/reminder/{reminder_id}")
def delete_reminder(reminder_id: str, db: Session = Depends(get_db)):
    reminder = db.query(ReminderModel).filter(ReminderModel.reminder_id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(reminder)
    db.commit()
    return {"ok": True}

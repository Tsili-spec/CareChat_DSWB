from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Reminder as ReminderModel
from app.schemas.reminder import Reminder, ReminderCreate

router = APIRouter()

@router.post("/reminder/", response_model=Reminder)
def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    db_reminder = ReminderModel(**reminder.dict())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@router.get("/reminder/{reminder_id}", response_model=Reminder)
def read_reminder(reminder_id: str, db: Session = Depends(get_db)):
    reminder = db.query(ReminderModel).filter(ReminderModel.reminder_id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

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

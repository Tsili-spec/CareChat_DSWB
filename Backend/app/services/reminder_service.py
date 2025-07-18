from sqlalchemy.orm import Session
from app.models.models import Reminder as ReminderModel, Patient
from app.schemas.reminder import ReminderCreate
from datetime import datetime
from uuid import UUID
from typing import List, Optional

class ReminderService:
    
    @staticmethod
    def create_reminder(db: Session, reminder_data: ReminderCreate) -> ReminderModel:
        """
        Create a new reminder for a patient
        """
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.patient_id == reminder_data.patient_id).first()
        if not patient:
            raise ValueError("Patient not found")
        
        # Create new reminder
        db_reminder = ReminderModel(
            patient_id=reminder_data.patient_id,
            title=reminder_data.title,
            message=reminder_data.message,
            scheduled_time=reminder_data.scheduled_time,
            days=reminder_data.days,
            status=reminder_data.status,
            created_at=datetime.utcnow()
        )
        
        db.add(db_reminder)
        db.commit()
        db.refresh(db_reminder)
        return db_reminder
    
    @staticmethod
    def get_patient_reminders(db: Session, patient_id: UUID) -> List[ReminderModel]:
        """
        Get all reminders for a specific patient
        """
        return db.query(ReminderModel).filter(
            ReminderModel.patient_id == patient_id
        ).order_by(ReminderModel.created_at.desc()).all()
    
    @staticmethod
    def get_reminder_by_id(db: Session, reminder_id: UUID) -> Optional[ReminderModel]:
        """
        Get a specific reminder by ID
        """
        return db.query(ReminderModel).filter(
            ReminderModel.reminder_id == reminder_id
        ).first()
    
    @staticmethod
    def get_active_patient_reminders(db: Session, patient_id: UUID) -> List[ReminderModel]:
        """
        Get only active reminders for a patient
        """
        return db.query(ReminderModel).filter(
            ReminderModel.patient_id == patient_id,
            ReminderModel.status == "active"
        ).order_by(ReminderModel.created_at.desc()).all()
    
    @staticmethod
    def update_reminder_status(db: Session, reminder_id: UUID, status: str) -> Optional[ReminderModel]:
        """
        Update the status of a reminder
        """
        reminder = db.query(ReminderModel).filter(
            ReminderModel.reminder_id == reminder_id
        ).first()
        
        if reminder:
            db.query(ReminderModel).filter(
                ReminderModel.reminder_id == reminder_id
            ).update({"status": status})
            db.commit()
            db.refresh(reminder)
        
        return reminder
    
    @staticmethod
    def delete_reminder(db: Session, reminder_id: UUID) -> bool:
        """
        Delete a reminder
        """
        reminder = db.query(ReminderModel).filter(
            ReminderModel.reminder_id == reminder_id
        ).first()
        
        if reminder:
            db.delete(reminder)
            db.commit()
            return True
        
        return False

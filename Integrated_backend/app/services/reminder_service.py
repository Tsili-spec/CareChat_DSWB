from typing import List, Optional
from app.models.models import Reminder as ReminderModel, ReminderDelivery as ReminderDeliveryModel
from app.schemas.reminder import ReminderCreate, ReminderDeliveryCreate
from app.services.sms_service import sms_service
from app.services.patient_service import PatientService
from app.core.logging_config import get_logger
from datetime import datetime

logger = get_logger(__name__)

class ReminderService:
    """Service for managing reminders"""
    
    @staticmethod
    async def create_reminder(reminder_data: ReminderCreate) -> ReminderModel:
        """Create a new reminder"""
        try:
            reminder = ReminderModel(
                patient_id=reminder_data.patient_id,
                title=reminder_data.title,
                message=reminder_data.message,
                scheduled_time=reminder_data.scheduled_time,
                days=reminder_data.days,
                status=reminder_data.status,
                created_at=datetime.utcnow()
            )
            
            await reminder.insert()
            logger.info(f"Reminder created successfully with ID: {reminder.reminder_id}")
            return reminder
            
        except Exception as e:
            logger.error(f"Failed to create reminder: {e}")
            raise
    
    @staticmethod
    async def get_reminder_by_id(reminder_id: str) -> Optional[ReminderModel]:
        """Get reminder by ID"""
        return await ReminderModel.find_one({"reminder_id": reminder_id})
    
    @staticmethod
    async def get_patient_reminders(patient_id: str) -> List[ReminderModel]:
        """Get all reminders for a patient"""
        return await ReminderModel.find({"patient_id": patient_id}).to_list()
    
    @staticmethod
    async def get_active_reminders() -> List[ReminderModel]:
        """Get all active reminders"""
        return await ReminderModel.find({"status": "active"}).to_list()
    
    @staticmethod
    async def update_reminder_status(reminder_id: str, status: str) -> Optional[ReminderModel]:
        """Update reminder status"""
        reminder = await ReminderService.get_reminder_by_id(reminder_id)
        if reminder:
            reminder.status = status
            await reminder.save()
            logger.info(f"Reminder {reminder_id} status updated to {status}")
        return reminder
    
    @staticmethod
    async def delete_reminder(reminder_id: str) -> bool:
        """Delete a reminder"""
        reminder = await ReminderService.get_reminder_by_id(reminder_id)
        if reminder:
            await reminder.delete()
            logger.info(f"Reminder {reminder_id} deleted successfully")
            return True
        return False
    
    @staticmethod
    async def send_reminder_notification(reminder: ReminderModel) -> dict:
        """Send reminder notification via SMS"""
        try:
            # Get patient information
            patient = await PatientService.get_patient_by_id(reminder.patient_id)
            if not patient:
                logger.error(f"Patient not found for reminder {reminder.reminder_id}")
                return {
                    "success": False,
                    "message": "Patient not found"
                }
            
            # Send SMS
            result = await sms_service.send_reminder_sms(
                patient.phone_number,
                reminder.title,
                reminder.message
            )
            
            # Record delivery attempt
            delivery_record = ReminderDeliveryModel(
                reminder_id=reminder.reminder_id,
                sent_at=datetime.utcnow(),
                delivery_status=result["delivery_status"],
                provider_response=result.get("provider_response", "")
            )
            await delivery_record.insert()
            
            logger.info(f"Reminder notification sent for reminder {reminder.reminder_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to send reminder notification: {e}")
            return {
                "success": False,
                "message": f"Failed to send notification: {str(e)}"
            }
    
    @staticmethod
    async def get_reminder_deliveries(reminder_id: str) -> List[ReminderDeliveryModel]:
        """Get delivery records for a reminder"""
        return await ReminderDeliveryModel.find({"reminder_id": reminder_id}).to_list()

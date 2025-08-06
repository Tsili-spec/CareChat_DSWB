from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.reminder import Reminder, ReminderCreate, ReminderDelivery
from app.services.reminder_service import ReminderService
from app.services.reminder_scheduler import reminder_scheduler
from app.db.database import get_db
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/reminder/",
             response_model=Reminder,
             status_code=status.HTTP_201_CREATED,
             summary="Create a new reminder",
             description="Create a new reminder for a patient")
async def create_reminder(reminder_data: ReminderCreate):
    """
    Create a new reminder for a patient.
    
    **Example request:**
    ```json
    {
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Take Morning Medication",
        "message": "Please take your morning medication with breakfast",
        "scheduled_time": ["2024-01-15T08:00:00Z"],
        "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
        "status": "active"
    }
    ```
    
    **Response:** Reminder object
    
    **Errors:**
    - 422: Validation errors
    """
    try:
        reminder = await ReminderService.create_reminder(reminder_data)
        
        return Reminder(
            reminder_id=reminder.reminder_id,
            patient_id=reminder.patient_id,
            title=reminder.title,
            message=reminder.message,
            scheduled_time=reminder.scheduled_time,
            days=reminder.days,
            status=reminder.status,
            created_at=reminder.created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating reminder: {str(e)}"
        )

@router.get("/reminder/{reminder_id}",
            response_model=Reminder,
            summary="Get specific reminder",
            description="Get specific reminder by ID")
async def get_reminder(reminder_id: str):
    """
    Get specific reminder by ID.
    
    **Path Parameters:**
    - reminder_id: Reminder's unique identifier
    
    **Response:** Reminder object
    
    **Errors:**
    - 404: Reminder not found
    """
    reminder = await ReminderService.get_reminder_by_id(reminder_id)
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    return Reminder(
        reminder_id=reminder.reminder_id,
        patient_id=reminder.patient_id,
        title=reminder.title,
        message=reminder.message,
        scheduled_time=reminder.scheduled_time,
        days=reminder.days,
        status=reminder.status,
        created_at=reminder.created_at
    )

@router.get("/reminder/patient/{patient_id}",
            response_model=List[Reminder],
            summary="Get patient reminders",
            description="Get all reminders for a specific patient")
async def get_patient_reminders(patient_id: str):
    """
    Get all reminders for a specific patient.
    
    **Path Parameters:**
    - patient_id: Patient's unique identifier
    
    **Response:** Array of Reminder objects
    """
    try:
        reminders = await ReminderService.get_patient_reminders(patient_id)
        
        return [
            Reminder(
                reminder_id=reminder.reminder_id,
                patient_id=reminder.patient_id,
                title=reminder.title,
                message=reminder.message,
                scheduled_time=reminder.scheduled_time,
                days=reminder.days,
                status=reminder.status,
                created_at=reminder.created_at
            ) for reminder in reminders
        ]
        
    except Exception as e:
        logger.error(f"Error getting patient reminders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving reminders"
        )

@router.get("/reminder/",
            response_model=List[Reminder],
            summary="List all reminders",
            description="List all reminders in the system")
async def list_reminders():
    """
    List all reminders in the system.
    
    **Response:** Array of Reminder objects
    """
    try:
        from app.models.models import Reminder as ReminderModel
        
        reminders = await ReminderModel.find().to_list()
        
        return [
            Reminder(
                reminder_id=reminder.reminder_id,
                patient_id=reminder.patient_id,
                title=reminder.title,
                message=reminder.message,
                scheduled_time=reminder.scheduled_time,
                days=reminder.days,
                status=reminder.status,
                created_at=reminder.created_at
            ) for reminder in reminders
        ]
        
    except Exception as e:
        logger.error(f"Error listing reminders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving reminders"
        )

@router.put("/reminder/{reminder_id}/status",
            response_model=Reminder,
            summary="Update reminder status",
            description="Update the status of a reminder")
async def update_reminder_status(reminder_id: str, status: str):
    """
    Update the status of a reminder.
    
    **Path Parameters:**
    - reminder_id: Reminder's unique identifier
    
    **Query Parameters:**
    - status: New status (active, inactive, completed, etc.)
    
    **Response:** Updated Reminder object
    
    **Errors:**
    - 404: Reminder not found
    """
    reminder = await ReminderService.update_reminder_status(reminder_id, status)
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    return Reminder(
        reminder_id=reminder.reminder_id,
        patient_id=reminder.patient_id,
        title=reminder.title,
        message=reminder.message,
        scheduled_time=reminder.scheduled_time,
        days=reminder.days,
        status=reminder.status,
        created_at=reminder.created_at
    )

@router.delete("/reminder/{reminder_id}",
               summary="Delete reminder",
               description="Delete a reminder")
async def delete_reminder(reminder_id: str):
    """
    Delete a reminder.
    
    **Path Parameters:**
    - reminder_id: Reminder's unique identifier
    
    **Response:** Success confirmation
    
    **Errors:**
    - 404: Reminder not found
    """
    success = await ReminderService.delete_reminder(reminder_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    return {"message": "Reminder deleted successfully"}

@router.post("/reminder/{reminder_id}/send",
             summary="Send reminder notification",
             description="Manually send a reminder notification")
async def send_reminder_notification(reminder_id: str):
    """
    Manually send a reminder notification.
    
    **Path Parameters:**
    - reminder_id: Reminder's unique identifier
    
    **Response:** Delivery status
    
    **Errors:**
    - 404: Reminder not found
    """
    reminder = await ReminderService.get_reminder_by_id(reminder_id)
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    result = await ReminderService.send_reminder_notification(reminder)
    return result

@router.get("/reminder/{reminder_id}/deliveries",
            response_model=List[ReminderDelivery],
            summary="Get reminder delivery history",
            description="Get delivery history for a reminder")
async def get_reminder_deliveries(reminder_id: str):
    """
    Get delivery history for a reminder.
    
    **Path Parameters:**
    - reminder_id: Reminder's unique identifier
    
    **Response:** Array of ReminderDelivery objects
    
    **Errors:**
    - 404: Reminder not found
    """
    # First check if reminder exists
    reminder = await ReminderService.get_reminder_by_id(reminder_id)
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    try:
        deliveries = await ReminderService.get_reminder_deliveries(reminder_id)
        
        return [
            ReminderDelivery(
                delivery_id=delivery.delivery_id,
                reminder_id=delivery.reminder_id,
                delivery_status=delivery.delivery_status,
                provider_response=delivery.provider_response,
                sent_at=delivery.sent_at
            ) for delivery in deliveries
        ]
        
    except Exception as e:
        logger.error(f"Error getting reminder deliveries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving delivery history"
        )

# Scheduler management endpoints
@router.post("/reminder/start-scheduler",
             summary="Start reminder scheduler",
             description="Start the automated reminder scheduler")
async def start_reminder_scheduler():
    """
    Start the automated reminder scheduler.
    
    **Response:** Status message
    """
    try:
        result = await reminder_scheduler.start_scheduler()
        return result
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting scheduler: {str(e)}"
        )

@router.post("/reminder/stop-scheduler",
             summary="Stop reminder scheduler",
             description="Stop the automated reminder scheduler")
async def stop_reminder_scheduler():
    """
    Stop the automated reminder scheduler.
    
    **Response:** Status message
    """
    try:
        result = reminder_scheduler.stop_scheduler()
        return result
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stopping scheduler: {str(e)}"
        )

@router.get("/reminder/scheduler-status",
            summary="Get scheduler status",
            description="Get the current status of the reminder scheduler")
async def get_scheduler_status():
    """
    Get the current status of the reminder scheduler.
    
    **Response:** Scheduler status information
    """
    return reminder_scheduler.get_status()

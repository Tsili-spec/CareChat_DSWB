from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Reminder as ReminderModel
from app.schemas.reminder import Reminder, ReminderCreate
from app.services.reminder_service import ReminderService
from app.services.reminder_scheduler import reminder_scheduler
from app.services.sms_service import sms_service
from uuid import UUID
from typing import List, Dict, Any

router = APIRouter()

@router.post("/reminder/", 
             response_model=Reminder,
             summary="Create a new reminder",
             description="Create a new reminder for a patient with scheduled times and days")
def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    """
    Create a new reminder for a patient.
    
    **Required fields:**
    - **patient_id**: UUID of the patient (must exist in database)
    - **title**: Short title for the reminder (max 200 characters)
    - **message**: Detailed reminder message
    - **scheduled_time**: List of datetime objects when reminder should be sent
    - **days**: List of days when reminder is active (e.g., ["Monday", "Wednesday", "Friday"])
    - **status**: Reminder status ("active", "inactive", "completed", "cancelled")
    
    **Example request body:**
    ```json
    {
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Take Morning Medication",
        "message": "Please take your blood pressure medication with breakfast",
        "scheduled_time": ["2024-01-15T08:00:00Z", "2024-01-16T08:00:00Z"],
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "status": "active"
    }
    ```
    
    **Returns:** The created reminder with generated ID and creation timestamp.
    
    **Errors:**
    - 404: Patient not found
    - 400: Invalid data or creation error
    """
    try:
        db_reminder = ReminderService.create_reminder(db, reminder)
        return db_reminder
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating reminder: {str(e)}")

@router.get("/reminder/patient/{patient_id}", 
            response_model=List[Reminder],
            summary="Get all reminders for a patient",
            description="Retrieve all reminders for a specific patient, ordered by creation date (newest first)")
def get_patient_reminders(patient_id: UUID, db: Session = Depends(get_db)):
    """
    Get all reminders for a specific patient.
    
    **Path Parameters:**
    - **patient_id**: UUID of the patient
    
    **Example:**
    ```
    GET /api/reminder/patient/123e4567-e89b-12d3-a456-426614174000
    ```
    
    **Returns:** List of all reminders for the patient, ordered by creation date (newest first).
    
    **Response Example:**
    ```json
    [
        {
            "reminder_id": "456e7890-e89b-12d3-a456-426614174001",
            "patient_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Take Morning Medication",
            "message": "Please take your blood pressure medication with breakfast",
            "scheduled_time": ["2024-01-15T08:00:00Z"],
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "status": "active",
            "created_at": "2024-01-10T10:30:00Z"
        }
    ]
    ```
    
    **Errors:**
    - 404: No reminders found for this patient
    """
    reminders = ReminderService.get_patient_reminders(db, patient_id)
    if not reminders:
        raise HTTPException(status_code=404, detail="No reminders found for this patient")
    return reminders

@router.get("/reminder/patient/{patient_id}/active", 
            response_model=List[Reminder],
            summary="Get active reminders for a patient",
            description="Retrieve only active reminders for a specific patient")
def get_active_patient_reminders(patient_id: UUID, db: Session = Depends(get_db)):
    """
    Get only active reminders for a specific patient.
    
    **Path Parameters:**
    - **patient_id**: UUID of the patient
    
    **Example:**
    ```
    GET /api/reminder/patient/123e4567-e89b-12d3-a456-426614174000/active
    ```
    
    **Returns:** List of active reminders only (status = "active").
    
    **Use Case:** Perfect for mobile apps that only need to show current active reminders.
    
    **Errors:**
    - 404: No active reminders found for this patient
    """
    reminders = ReminderService.get_active_patient_reminders(db, patient_id)
    if not reminders:
        raise HTTPException(status_code=404, detail="No active reminders found for this patient")
    return reminders

# =============================================================================
# SMS NOTIFICATION ENDPOINTS (Must come before parameterized routes)
# =============================================================================

@router.get("/reminder/sms-status",
            summary="Get SMS service status",
            description="Check if SMS notifications are properly configured and working")
def get_sms_service_status() -> Dict[str, Any]:
    """
    Check the status of the SMS notification service.
    
    **Use Cases:**
    - System health monitoring
    - Troubleshooting SMS issues
    - Configuration validation
    
    **Returns:** SMS service configuration status.
    
    **Response Example:**
    ```json
    {
        "sms_configured": true,
        "scheduler_running": false,
        "twilio_account": "AC810a610...",
        "twilio_number": "+1234567890",
        "status": "ready"
    }
    ```
    """
    try:
        return {
            "sms_configured": sms_service.is_configured(),
            "scheduler_running": reminder_scheduler.is_running,
            "twilio_account": sms_service.account_sid[:10] + "..." if sms_service.account_sid else None,
            "twilio_number": sms_service.twilio_number,
            "status": "ready" if sms_service.is_configured() else "not_configured"
        }
        
    except Exception as e:
        return {
            "sms_configured": False,
            "scheduler_running": False,
            "error": str(e),
            "status": "error"
        }

@router.get("/reminder/upcoming", 
            summary="Get upcoming reminders",
            description="Get reminders scheduled for the next 24 hours with SMS timing")
def get_upcoming_reminders(
    hours_ahead: int = Query(default=24, ge=1, le=168, description="Hours ahead to look (1-168)"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get reminders that are scheduled to be sent in the next specified hours.
    
    **Query Parameters:**
    - **hours_ahead**: How many hours ahead to look (1-168, default: 24)
    
    **Example:**
    ```
    GET /api/reminder/upcoming?hours_ahead=48
    ```
    
    **Use Cases:**
    - Dashboard showing upcoming notifications
    - SMS scheduling preview
    - Patient care planning
    
    **Returns:** List of upcoming reminders with timing information.
    
    **Response Example:**
    ```json
    [
        {
            "reminder_id": "123e4567-e89b-12d3-a456-426614174000",
            "patient_name": "John Doe",
            "patient_phone": "+1234567890",
            "title": "Take Morning Medication",
            "message": "Take your blood pressure medication",
            "next_occurrence": "2024-01-16T08:00:00Z",
            "days": ["Monday", "Wednesday", "Friday"],
            "scheduled_time": "2024-01-15T08:00:00Z"
        }
    ]
    ```
    """
    try:
        upcoming = reminder_scheduler.get_upcoming_reminders(db, hours_ahead)
        return upcoming
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get upcoming reminders: {str(e)}")

@router.post("/reminder/start-scheduler",
             summary="Start SMS reminder scheduler",
             description="Start the background scheduler for automatic SMS reminders")
def start_reminder_scheduler() -> Dict[str, Any]:
    """
    Start the automatic SMS reminder scheduler.
    
    **Use Cases:**
    - Initialize SMS reminder system
    - Restart scheduler after maintenance
    - Enable automatic notifications
    
    **Returns:** Scheduler status.
    
    **Response Example:**
    ```json
    {
        "success": true,
        "message": "Reminder scheduler started",
        "status": "starting"
    }
    ```
    
    **Note:** This endpoint should be restricted to admin users in production.
    """
    try:
        if reminder_scheduler.is_running:
            return {
                "success": False,
                "message": "Reminder scheduler is already running",
                "status": "already_running"
            }
        
        # Start scheduler in background
        import asyncio
        asyncio.create_task(reminder_scheduler.start_scheduler())
        
        return {
            "success": True,
            "message": "Reminder scheduler started",
            "status": "starting"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")

@router.post("/reminder/stop-scheduler",
             summary="Stop SMS reminder scheduler", 
             description="Stop the background scheduler for automatic SMS reminders")
def stop_reminder_scheduler() -> Dict[str, Any]:
    """
    Stop the automatic SMS reminder scheduler.
    
    **Use Cases:**
    - Maintenance mode
    - Emergency stop of notifications
    - System shutdown
    
    **Returns:** Scheduler status.
    
    **Response Example:**
    ```json
    {
        "success": true,
        "message": "Reminder scheduler stopped",
        "status": "stopped"
    }
    ```
    
    **Note:** This endpoint should be restricted to admin users in production.
    """
    try:
        reminder_scheduler.stop_scheduler()
        
        return {
            "success": True,
            "message": "Reminder scheduler stopped",
            "status": "stopped"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")

@router.post("/reminder/{reminder_id}/send-sms", 
             summary="Send SMS reminder immediately",
             description="Manually trigger an SMS reminder to be sent immediately")
def send_reminder_sms_now(reminder_id: UUID, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Send a specific reminder via SMS immediately.
    
    **Use Cases:**
    - Manual testing of SMS functionality
    - Immediate reminder for urgent situations
    - Troubleshooting SMS delivery
    
    **Path Parameters:**
    - **reminder_id**: UUID of the reminder to send
    
    **Example:**
    ```
    POST /api/reminder/123e4567-e89b-12d3-a456-426614174000/send-sms
    ```
    
    **Returns:** SMS delivery status and tracking information.
    
    **Response Example:**
    ```json
    {
        "success": true,
        "message_sid": "SM1234567890abcdef",
        "status": "queued",
        "reminder_id": "123e4567-e89b-12d3-a456-426614174000",
        "patient_name": "John Doe",
        "phone_number": "+1234567890",
        "sent_immediately": true,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    ```
    
    **Errors:**
    - 404: Reminder not found or not active
    - 500: SMS service error
    """
    try:
        result = reminder_scheduler.send_immediate_reminder(db, str(reminder_id))
        
        if not result['success']:
            if "not found" in result.get('error', '').lower():
                raise HTTPException(status_code=404, detail=result['error'])
            else:
                raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")

@router.get("/reminder/{reminder_id}", 
            response_model=Reminder,
            summary="Get a specific reminder",
            description="Retrieve a specific reminder by its ID")
def get_reminder(reminder_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific reminder by ID.
    
    **Path Parameters:**
    - **reminder_id**: UUID of the reminder
    
    **Example:**
    ```
    GET /api/reminder/456e7890-e89b-12d3-a456-426614174001
    ```
    
    **Returns:** Complete reminder details.
    
    **Use Case:** Get full details of a specific reminder for editing or viewing.
    
    **Errors:**
    - 404: Reminder not found
    """
    reminder = ReminderService.get_reminder_by_id(db, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

@router.put("/reminder/{reminder_id}/status",
            summary="Update reminder status",
            description="Update the status of a specific reminder")
def update_reminder_status(
    reminder_id: UUID, 
    status: str = Query(..., description="New status for the reminder", 
                       regex="^(active|inactive|completed|cancelled)$",
                       example="active"), 
    db: Session = Depends(get_db)
):
    """
    Update the status of a reminder.
    
    **Path Parameters:**
    - **reminder_id**: UUID of the reminder to update
    
    **Query Parameters:**
    - **status**: New status (must be one of: "active", "inactive", "completed", "cancelled")
    
    **Example:**
    ```
    PUT /api/reminder/456e7890-e89b-12d3-a456-426614174001/status?status=completed
    ```
    
    **Valid status values:**
    - **active**: Reminder is currently active and will be sent
    - **inactive**: Reminder is temporarily disabled
    - **completed**: Reminder has been completed (for one-time reminders)
    - **cancelled**: Reminder has been cancelled and won't be sent
    
    **Returns:** Success message with updated status.
    
    **Response Example:**
    ```json
    {
        "message": "Reminder status updated successfully",
        "reminder_id": "456e7890-e89b-12d3-a456-426614174001",
        "status": "completed"
    }
    ```
    
    **Errors:**
    - 404: Reminder not found
    - 422: Invalid status value
    """
    reminder = ReminderService.update_reminder_status(db, reminder_id, status)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder status updated successfully", "reminder_id": reminder_id, "status": status}

@router.delete("/reminder/{reminder_id}",
               summary="Delete a reminder",
               description="Permanently delete a specific reminder")
def delete_reminder(reminder_id: UUID, db: Session = Depends(get_db)):
    """
    Permanently delete a reminder.
    
    **Path Parameters:**
    - **reminder_id**: UUID of the reminder to delete
    
    **Example:**
    ```
    DELETE /api/reminder/456e7890-e89b-12d3-a456-426614174001
    ```
    
    **⚠️ Warning:** This action is permanent and cannot be undone.
    
    **Alternative:** Consider updating the status to "cancelled" instead of deleting.
    
    **Returns:** Success confirmation message.
    
    **Response Example:**
    ```json
    {
        "message": "Reminder deleted successfully"
    }
    ```
    
    **Errors:**
    - 404: Reminder not found
    """
    success = ReminderService.delete_reminder(db, reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder deleted successfully"}

@router.get("/reminder/", 
            response_model=List[Reminder],
            summary="List all reminders (Admin)",
            description="Get all reminders in the system - Admin only endpoint")
def list_all_reminders(
    limit: int = Query(100, description="Maximum number of reminders to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of reminders to skip", ge=0),
    status: str = Query(None, description="Filter by status", 
                       regex="^(active|inactive|completed|cancelled)$"),
    db: Session = Depends(get_db)
):
    """
    Get all reminders in the system (Admin endpoint).
    
    **Query Parameters:**
    - **limit**: Maximum number of reminders to return (1-1000, default: 100)
    - **offset**: Number of reminders to skip for pagination (default: 0)
    - **status**: Optional filter by status ("active", "inactive", "completed", "cancelled")
    
    **Examples:**
    ```
    GET /api/reminder/                           # Get first 100 reminders
    GET /api/reminder/?limit=50&offset=100       # Get reminders 101-150
    GET /api/reminder/?status=active             # Get only active reminders
    ```
    
    **Use Case:** 
    - Admin dashboard to view all reminders
    - System monitoring and analytics
    - Bulk operations on reminders
    
    **Returns:** List of reminders with pagination support.
    
    **Note:** This endpoint should be restricted to admin users in production.
    """
    query = db.query(ReminderModel)
    
    if status:
        query = query.filter(ReminderModel.status == status)
    
    return query.offset(offset).limit(limit).all()

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.db.database import (
    get_smart_reminders_collection,
    get_reminder_deliveries_collection,
    get_notification_templates_collection
)
from app.models import (
    User,
    SmartReminder,
    ReminderDelivery,
    NotificationTemplate
)
from app.schemas.reminder import (
    SmartReminderCreateRequest,
    SmartReminderResponse,
    SmartReminderUpdateRequest
)
from app.api.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=SmartReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: SmartReminderCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new smart reminder"""
    reminders_collection = await get_smart_reminders_collection()
    
    # Create smart reminder
    reminder = SmartReminder(
        user_id=current_user.user_id,
        reminder_type=reminder_data.reminder_type,
        title=reminder_data.title,
        content=reminder_data.content,
        scheduled_time=reminder_data.scheduled_time,
        recurrence_pattern=reminder_data.recurrence_pattern,
        priority_level=reminder_data.priority_level,
        delivery_channels=reminder_data.delivery_channels,
        conditions=reminder_data.conditions or {},
        metadata=reminder_data.metadata or {}
    )
    
    # Insert reminder
    reminder_dict = reminder.dict(by_alias=True, exclude_none=True)
    result = await reminders_collection.insert_one(reminder_dict)
    
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reminder"
        )
    
    logger.info(f"New smart reminder created: {reminder.reminder_id} for user: {current_user.user_id}")
    
    return SmartReminderResponse(
        reminder_id=reminder.reminder_id,
        user_id=reminder.user_id,
        reminder_type=reminder.reminder_type,
        title=reminder.title,
        scheduled_time=reminder.scheduled_time,
        status=reminder.status,
        priority_level=reminder.priority_level,
        delivery_channels=reminder.delivery_channels,
        created_at=reminder.created_at,
        updated_at=reminder.updated_at
    )


@router.get("/", response_model=List[SmartReminderResponse])
async def get_reminders(
    skip: int = Query(0, ge=0, description="Number of reminders to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of reminders to retrieve"),
    reminder_type: Optional[str] = Query(None, description="Filter by reminder type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority_level: Optional[str] = Query(None, description="Filter by priority level"),
    current_user: User = Depends(get_current_user)
):
    """Get user's smart reminders with pagination and filtering"""
    reminders_collection = await get_smart_reminders_collection()
    
    # Build query
    query = {"user_id": current_user.user_id}
    if reminder_type:
        query["reminder_type"] = reminder_type
    if status:
        query["status"] = status
    if priority_level:
        query["priority_level"] = priority_level
    
    # Get reminders
    cursor = reminders_collection.find(query).sort("scheduled_time", 1).skip(skip).limit(limit)
    reminders = []
    
    async for reminder_doc in cursor:
        reminder = SmartReminder(**reminder_doc)
        reminders.append(SmartReminderResponse(
            reminder_id=reminder.reminder_id,
            user_id=reminder.user_id,
            reminder_type=reminder.reminder_type,
            title=reminder.title,
            scheduled_time=reminder.scheduled_time,
            status=reminder.status,
            priority_level=reminder.priority_level,
            delivery_channels=reminder.delivery_channels,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at
        ))
    
    return reminders


@router.get("/upcoming", response_model=List[SmartReminderResponse])
async def get_upcoming_reminders(
    hours: int = Query(24, ge=1, le=168, description="Hours ahead to check"),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming reminders within specified hours"""
    reminders_collection = await get_smart_reminders_collection()
    
    # Calculate time range
    now = datetime.utcnow()
    future_time = now + timedelta(hours=hours)
    
    # Build query for upcoming active reminders
    query = {
        "user_id": current_user.user_id,
        "status": "active",
        "scheduled_time": {
            "$gte": now,
            "$lte": future_time
        }
    }
    
    # Get upcoming reminders
    cursor = reminders_collection.find(query).sort("scheduled_time", 1)
    reminders = []
    
    async for reminder_doc in cursor:
        reminder = SmartReminder(**reminder_doc)
        reminders.append(SmartReminderResponse(
            reminder_id=reminder.reminder_id,
            user_id=reminder.user_id,
            reminder_type=reminder.reminder_type,
            title=reminder.title,
            scheduled_time=reminder.scheduled_time,
            status=reminder.status,
            priority_level=reminder.priority_level,
            delivery_channels=reminder.delivery_channels,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at
        ))
    
    return reminders


@router.get("/{reminder_id}", response_model=SmartReminder)
async def get_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get reminder by ID"""
    reminders_collection = await get_smart_reminders_collection()
    
    reminder_doc = await reminders_collection.find_one({
        "reminder_id": reminder_id,
        "user_id": current_user.user_id
    })
    
    if not reminder_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    return SmartReminder(**reminder_doc)


@router.put("/{reminder_id}", response_model=SmartReminderResponse)
async def update_reminder(
    reminder_id: str,
    reminder_update: SmartReminderUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update reminder"""
    reminders_collection = await get_smart_reminders_collection()
    
    # Check if reminder exists and belongs to user
    reminder_doc = await reminders_collection.find_one({
        "reminder_id": reminder_id,
        "user_id": current_user.user_id
    })
    
    if not reminder_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    # Build update data
    update_data = {}
    if reminder_update.title is not None:
        update_data["title"] = reminder_update.title
    if reminder_update.content is not None:
        update_data["content"] = reminder_update.content
    if reminder_update.scheduled_time is not None:
        update_data["scheduled_time"] = reminder_update.scheduled_time
    if reminder_update.status is not None:
        update_data["status"] = reminder_update.status
    if reminder_update.priority_level is not None:
        update_data["priority_level"] = reminder_update.priority_level
    if reminder_update.delivery_channels is not None:
        update_data["delivery_channels"] = reminder_update.delivery_channels
    if reminder_update.recurrence_pattern is not None:
        update_data["recurrence_pattern"] = reminder_update.recurrence_pattern
    if reminder_update.conditions is not None:
        update_data["conditions"] = reminder_update.conditions
    if reminder_update.metadata is not None:
        update_data["metadata"] = reminder_update.metadata
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        # Update reminder
        result = await reminders_collection.update_one(
            {"reminder_id": reminder_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
    
    # Get updated reminder
    updated_reminder_doc = await reminders_collection.find_one({"reminder_id": reminder_id})
    updated_reminder = SmartReminder(**updated_reminder_doc)
    
    logger.info(f"Reminder updated: {reminder_id}")
    
    return SmartReminderResponse(
        reminder_id=updated_reminder.reminder_id,
        user_id=updated_reminder.user_id,
        reminder_type=updated_reminder.reminder_type,
        title=updated_reminder.title,
        scheduled_time=updated_reminder.scheduled_time,
        status=updated_reminder.status,
        priority_level=updated_reminder.priority_level,
        delivery_channels=updated_reminder.delivery_channels,
        created_at=updated_reminder.created_at,
        updated_at=updated_reminder.updated_at
    )


@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete reminder"""
    reminders_collection = await get_smart_reminders_collection()
    
    # Check if reminder exists and belongs to user
    result = await reminders_collection.delete_one({
        "reminder_id": reminder_id,
        "user_id": current_user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    logger.info(f"Reminder deleted: {reminder_id}")
    
    return {"message": "Reminder deleted successfully"}


@router.post("/{reminder_id}/snooze")
async def snooze_reminder(
    reminder_id: str,
    snooze_minutes: int = Query(15, ge=1, le=1440, description="Minutes to snooze"),
    current_user: User = Depends(get_current_user)
):
    """Snooze reminder for specified minutes"""
    reminders_collection = await get_smart_reminders_collection()
    
    # Check if reminder exists and belongs to user
    reminder_doc = await reminders_collection.find_one({
        "reminder_id": reminder_id,
        "user_id": current_user.user_id
    })
    
    if not reminder_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    # Calculate new scheduled time
    current_time = reminder_doc["scheduled_time"]
    if isinstance(current_time, str):
        current_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
    
    new_scheduled_time = current_time + timedelta(minutes=snooze_minutes)
    
    # Update reminder
    result = await reminders_collection.update_one(
        {"reminder_id": reminder_id},
        {
            "$set": {
                "scheduled_time": new_scheduled_time,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    logger.info(f"Reminder snoozed: {reminder_id} for {snooze_minutes} minutes")
    
    return {
        "message": f"Reminder snoozed for {snooze_minutes} minutes",
        "new_scheduled_time": new_scheduled_time
    }


@router.get("/{reminder_id}/deliveries")
async def get_reminder_deliveries(
    reminder_id: str,
    skip: int = Query(0, ge=0, description="Number of deliveries to skip"),
    limit: int = Query(50, ge=1, le=500, description="Number of deliveries to retrieve"),
    current_user: User = Depends(get_current_user)
):
    """Get delivery history for reminder"""
    # First verify reminder belongs to user
    reminders_collection = await get_smart_reminders_collection()
    reminder_doc = await reminders_collection.find_one({
        "reminder_id": reminder_id,
        "user_id": current_user.user_id
    })
    
    if not reminder_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    # Get deliveries
    deliveries_collection = await get_reminder_deliveries_collection()
    cursor = deliveries_collection.find(
        {"reminder_id": reminder_id}
    ).sort("delivery_time", -1).skip(skip).limit(limit)
    
    deliveries = []
    async for delivery_doc in cursor:
        delivery = ReminderDelivery(**delivery_doc)
        deliveries.append(delivery)
    
    return {
        "reminder_id": reminder_id,
        "deliveries": deliveries
    }


@router.get("/templates/")
async def get_notification_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    current_user: User = Depends(get_current_user)
):
    """Get notification templates"""
    templates_collection = await get_notification_templates_collection()
    
    # Build query
    query = {}
    if template_type:
        query["template_type"] = template_type
    
    cursor = templates_collection.find(query)
    templates = []
    
    async for template_doc in cursor:
        template = NotificationTemplate(**template_doc)
        templates.append(template)
    
    return templates

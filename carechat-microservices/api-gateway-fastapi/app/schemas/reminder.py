"""
Smart reminder schemas for scheduling and managing user reminders
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, time
from enum import Enum
from pydantic import BaseModel, Field
from .base import BaseResponse


class ReminderType(str, Enum):
    """Reminder type enumeration"""
    MEDICATION = "medication"
    APPOINTMENT = "appointment"
    HEALTH_CHECK = "health_check"
    EXERCISE = "exercise"
    DIET = "diet"
    CUSTOM = "custom"


class ReminderStatus(str, Enum):
    """Reminder status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DeliveryMethod(str, Enum):
    """Delivery method enumeration"""
    SMS = "sms"
    EMAIL = "email"
    PUSH_NOTIFICATION = "push_notification"
    VOICE_CALL = "voice_call"


class RecurrencePattern(str, Enum):
    """Recurrence pattern enumeration"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ReminderDeliveryStatus(str, Enum):
    """Delivery status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"


class ReminderSchedule(BaseModel):
    """Reminder scheduling configuration"""
    pattern: RecurrencePattern = Field(..., description="Recurrence pattern")
    start_date: datetime = Field(..., description="Start date for reminders")
    end_date: Optional[datetime] = Field(default=None, description="End date for reminders")
    time_of_day: time = Field(..., description="Time of day to send reminder")
    days_of_week: Optional[List[int]] = Field(default=None, description="Days of week (0=Monday, 6=Sunday)")
    interval_days: Optional[int] = Field(default=None, description="Interval in days for custom patterns")


class SmartReminderCreateRequest(BaseModel):
    """Create smart reminder request"""
    title: str = Field(..., max_length=200, description="Reminder title")
    message: str = Field(..., max_length=1000, description="Reminder message")
    reminder_type: ReminderType = Field(..., description="Type of reminder")
    schedule: ReminderSchedule = Field(..., description="Reminder schedule")
    delivery_methods: List[DeliveryMethod] = Field(..., description="Delivery methods")
    priority: int = Field(default=1, ge=1, le=5, description="Priority level (1=low, 5=high)")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Take Blood Pressure Medication",
                "message": "Time to take your morning blood pressure medication (Lisinopril 10mg)",
                "reminder_type": "medication",
                "schedule": {
                    "pattern": "daily",
                    "start_date": "2025-08-06T08:00:00Z",
                    "end_date": "2025-12-31T23:59:59Z",
                    "time_of_day": "08:00:00",
                    "days_of_week": None,
                    "interval_days": None
                },
                "delivery_methods": ["sms", "push_notification"],
                "priority": 4,
                "metadata": {
                    "medication_name": "Lisinopril",
                    "dosage": "10mg",
                    "doctor": "Dr. Smith"
                }
            }
        }


class SmartReminderResponse(BaseResponse):
    """Smart reminder response"""
    user_id: str = Field(..., description="User who owns this reminder")
    title: str = Field(..., description="Reminder title")
    message: str = Field(..., description="Reminder message")
    reminder_type: ReminderType = Field(..., description="Type of reminder")
    status: ReminderStatus = Field(..., description="Reminder status")
    schedule: ReminderSchedule = Field(..., description="Reminder schedule")
    delivery_methods: List[DeliveryMethod] = Field(..., description="Delivery methods")
    priority: int = Field(..., description="Priority level")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    next_delivery: Optional[datetime] = Field(default=None, description="Next scheduled delivery")
    total_deliveries: int = Field(default=0, description="Total number of deliveries")
    successful_deliveries: int = Field(default=0, description="Successful deliveries")
    last_delivery: Optional[datetime] = Field(default=None, description="Last delivery timestamp")


class SmartReminderUpdateRequest(BaseModel):
    """Update smart reminder request"""
    title: Optional[str] = Field(default=None, max_length=200, description="Reminder title")
    message: Optional[str] = Field(default=None, max_length=1000, description="Reminder message")
    status: Optional[ReminderStatus] = Field(default=None, description="Reminder status")
    schedule: Optional[ReminderSchedule] = Field(default=None, description="Reminder schedule")
    delivery_methods: Optional[List[DeliveryMethod]] = Field(default=None, description="Delivery methods")
    priority: Optional[int] = Field(default=None, ge=1, le=5, description="Priority level")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ReminderDeliveryCreateRequest(BaseModel):
    """Create reminder delivery request"""
    reminder_id: str = Field(..., description="Reminder ID")
    scheduled_for: datetime = Field(..., description="Scheduled delivery time")
    delivery_method: DeliveryMethod = Field(..., description="Delivery method")
    recipient: str = Field(..., description="Recipient (phone/email)")


class ReminderDeliveryResponse(BaseResponse):
    """Reminder delivery response"""
    reminder_id: str = Field(..., description="Reminder ID")
    user_id: str = Field(..., description="User ID")
    scheduled_for: datetime = Field(..., description="Scheduled delivery time")
    delivered_at: Optional[datetime] = Field(default=None, description="Actual delivery time")
    delivery_method: DeliveryMethod = Field(..., description="Delivery method")
    recipient: str = Field(..., description="Recipient")
    status: ReminderDeliveryStatus = Field(..., description="Delivery status")
    message_content: str = Field(..., description="Delivered message content")
    response_received: Optional[str] = Field(default=None, description="User response to reminder")
    error_message: Optional[str] = Field(default=None, description="Error message if delivery failed")


class ReminderSearchRequest(BaseModel):
    """Reminder search request"""
    query: Optional[str] = Field(default=None, description="Search query")
    reminder_type: Optional[ReminderType] = Field(default=None, description="Reminder type filter")
    status: Optional[ReminderStatus] = Field(default=None, description="Status filter")
    priority_min: Optional[int] = Field(default=None, ge=1, le=5, description="Minimum priority filter")
    priority_max: Optional[int] = Field(default=None, ge=1, le=5, description="Maximum priority filter")
    created_after: Optional[datetime] = Field(default=None, description="Created after date filter")
    created_before: Optional[datetime] = Field(default=None, description="Created before date filter")
    next_delivery_after: Optional[datetime] = Field(default=None, description="Next delivery after filter")
    next_delivery_before: Optional[datetime] = Field(default=None, description="Next delivery before filter")


class ReminderStatsResponse(BaseModel):
    """Reminder statistics response"""
    total_reminders: int = Field(..., description="Total reminders")
    active_reminders: int = Field(..., description="Active reminders")
    completed_reminders: int = Field(..., description="Completed reminders")
    overdue_reminders: int = Field(..., description="Overdue reminders")
    reminders_by_type: Dict[str, int] = Field(..., description="Reminders grouped by type")
    delivery_success_rate: float = Field(..., description="Overall delivery success rate")
    upcoming_deliveries_today: int = Field(..., description="Deliveries scheduled for today")
    upcoming_deliveries_week: int = Field(..., description="Deliveries scheduled for this week")

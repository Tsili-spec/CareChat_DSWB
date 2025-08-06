"""
Reminder Models for MongoDB
Defines reminder and notification data structures
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Reminder(BaseModel):
    """Reminder model for healthcare reminders"""
    id: str = Field(..., description="Unique reminder identifier")
    user_id: str = Field(..., description="User ID who owns the reminder")
    title: str = Field(..., description="Reminder title")
    description: Optional[str] = Field(default=None, description="Reminder description")
    reminder_type: str = Field(..., description="Type: medication, appointment, exercise, etc.")
    
    # Scheduling
    scheduled_time: datetime = Field(..., description="When the reminder should trigger")
    recurrence_pattern: Optional[str] = Field(default=None, description="Recurrence pattern: daily, weekly, monthly")
    recurrence_end: Optional[datetime] = Field(default=None, description="When recurrence ends")
    
    # Status
    status: str = Field(default="active", description="Status: active, completed, cancelled, snoozed")
    is_completed: bool = Field(default=False, description="Whether reminder is completed")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    
    # Notification settings
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels: email, sms, push")
    notification_sent: bool = Field(default=False, description="Whether notification was sent")
    notification_sent_at: Optional[datetime] = Field(default=None, description="Notification send time")
    
    # Snooze functionality
    snooze_until: Optional[datetime] = Field(default=None, description="Snoozed until timestamp")
    snooze_count: int = Field(default=0, description="Number of times snoozed")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional reminder metadata")
    tags: List[str] = Field(default_factory=list, description="Reminder tags")
    priority: str = Field(default="medium", description="Priority: low, medium, high, urgent")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SmartReminder(BaseModel):
    """Smart reminder model with AI-powered features"""
    id: str = Field(..., description="Unique smart reminder identifier")
    user_id: str = Field(..., description="User ID who owns the reminder")
    title: str = Field(..., description="Reminder title")
    description: Optional[str] = Field(default=None, description="Reminder description")
    reminder_type: str = Field(..., description="Type: medication, appointment, exercise, etc.")
    
    # AI features
    is_smart: bool = Field(default=True, description="Whether this is an AI-powered reminder")
    ai_generated: bool = Field(default=False, description="Whether content was AI-generated")
    smart_scheduling: bool = Field(default=False, description="Whether to use AI for optimal scheduling")
    
    # Scheduling
    scheduled_time: datetime = Field(..., description="When the reminder should trigger")
    recurrence_pattern: Optional[str] = Field(default=None, description="Recurrence pattern")
    timezone: str = Field(default="UTC", description="User timezone")
    
    # Status and tracking
    status: str = Field(default="active", description="Status: active, completed, cancelled, snoozed")
    completion_rate: float = Field(default=0.0, description="Historical completion rate")
    adherence_score: float = Field(default=0.0, description="Adherence score 0-1")
    
    # Smart features
    difficulty_level: str = Field(default="medium", description="Difficulty: easy, medium, hard")
    importance_score: float = Field(default=0.5, description="Importance score 0-1")
    urgency_score: float = Field(default=0.5, description="Urgency score 0-1")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional reminder metadata")
    tags: List[str] = Field(default_factory=list, description="Reminder tags")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReminderDelivery(BaseModel):
    """Reminder delivery tracking model"""
    id: str = Field(..., description="Unique delivery identifier")
    reminder_id: str = Field(..., description="Related reminder ID")
    user_id: str = Field(..., description="Target user ID")
    
    # Delivery details
    delivery_method: str = Field(..., description="Method: push, email, sms")
    delivery_status: str = Field(default="pending", description="Status: pending, sent, delivered, failed")
    delivery_attempts: int = Field(default=0, description="Number of attempts")
    
    # Response tracking
    user_response: Optional[str] = Field(default=None, description="User response action")
    response_time: Optional[datetime] = Field(default=None, description="When user responded")
    completion_confirmed: bool = Field(default=False, description="Whether completion was confirmed")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Delivery metadata")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    
    # Timestamps
    scheduled_at: datetime = Field(..., description="Scheduled delivery time")
    sent_at: Optional[datetime] = Field(default=None, description="Actual send time")
    delivered_at: Optional[datetime] = Field(default=None, description="Delivery confirmation time")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NotificationTemplate(BaseModel):
    """Notification template model"""
    id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Template name")
    template_type: str = Field(..., description="Type: reminder, alert, welcome")
    
    # Template content
    title_template: str = Field(..., description="Title template with placeholders")
    message_template: str = Field(..., description="Message template with placeholders")
    
    # Channels
    supported_channels: List[str] = Field(default_factory=list, description="Supported channels")
    default_channel: str = Field(default="push", description="Default delivery channel")
    
    # Personalization
    personalization_enabled: bool = Field(default=True, description="Whether to personalize content")
    placeholders: List[str] = Field(default_factory=list, description="Available placeholders")
    
    # Status
    is_active: bool = Field(default=True, description="Whether template is active")
    usage_count: int = Field(default=0, description="Number of times used")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Template metadata")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Notification(BaseModel):
    """Notification model for tracking sent notifications"""
    id: str = Field(..., description="Unique notification identifier")
    user_id: str = Field(..., description="Target user ID")
    reminder_id: Optional[str] = Field(default=None, description="Related reminder ID")
    
    # Content
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    notification_type: str = Field(..., description="Type: reminder, alert, info")
    
    # Delivery
    channel: str = Field(..., description="Delivery channel: email, sms, push")
    delivery_status: str = Field(default="pending", description="Status: pending, sent, failed, delivered")
    delivery_attempts: int = Field(default=0, description="Number of delivery attempts")
    
    # Response tracking
    is_read: bool = Field(default=False, description="Whether notification was read")
    read_at: Optional[datetime] = Field(default=None, description="Read timestamp")
    action_taken: Optional[str] = Field(default=None, description="Action taken by user")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional notification metadata")
    
    # Timestamps
    scheduled_at: datetime = Field(..., description="Scheduled delivery time")
    sent_at: Optional[datetime] = Field(default=None, description="Actual send time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

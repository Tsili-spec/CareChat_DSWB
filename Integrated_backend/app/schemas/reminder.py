from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ReminderBase(BaseModel):
    """Base schema for Reminder"""
    patient_id: str = Field(description="Patient's unique identifier")
    title: str = Field(max_length=200, description="Reminder title")
    message: str = Field(description="Reminder message")
    scheduled_time: List[datetime] = Field(
        default_factory=list, 
        description="List of scheduled times"
    )
    days: List[str] = Field(
        default_factory=list, 
        description="Days of the week for recurring reminders"
    )
    status: str = Field(default="active", description="Reminder status")

class ReminderCreate(ReminderBase):
    """Schema for creating reminder"""
    pass

class Reminder(ReminderBase):
    """Schema for reminder response"""
    reminder_id: str = Field(description="Reminder's unique identifier")
    created_at: Optional[datetime] = Field(description="Reminder creation timestamp")

    class Config:
        from_attributes = True

class ReminderDeliveryBase(BaseModel):
    """Base schema for Reminder Delivery"""
    reminder_id: str = Field(description="Reminder's unique identifier")
    delivery_status: str = Field(description="Delivery status")
    provider_response: Optional[str] = Field(
        None, 
        description="Response from SMS/notification provider"
    )

class ReminderDeliveryCreate(ReminderDeliveryBase):
    """Schema for creating reminder delivery record"""
    pass

class ReminderDelivery(ReminderDeliveryBase):
    """Schema for reminder delivery response"""
    delivery_id: str = Field(description="Delivery record's unique identifier")
    sent_at: Optional[datetime] = Field(description="Delivery timestamp")

    class Config:
        from_attributes = True

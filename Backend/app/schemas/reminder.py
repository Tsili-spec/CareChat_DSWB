from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class ReminderBase(BaseModel):
    patient_id: UUID
    reminder_type: Optional[str] = None
    message: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    channel: Optional[str] = None
    status: Optional[str] = None
    attempts: Optional[int] = None

class ReminderCreate(ReminderBase):
    pass

class Reminder(ReminderBase):
    reminder_id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

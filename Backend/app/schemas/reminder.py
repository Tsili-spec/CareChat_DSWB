from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ReminderBase(BaseModel):
    patient_id: UUID
    message: str
    scheduled_time: List[datetime]
    days: List[str]
    status: str

class ReminderCreate(ReminderBase):
    pass

class Reminder(ReminderBase):
    reminder_id: UUID
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

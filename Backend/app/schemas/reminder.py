from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ReminderBase(BaseModel):
    patient_id: UUID = Field(
        description="UUID of the patient this reminder belongs to",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    title: str = Field(
        min_length=1, 
        max_length=200,
        description="Short, descriptive title for the reminder",
        examples=["Take Morning Medication"]
    )
    message: str = Field(
        min_length=1,
        description="Detailed reminder message or instructions",
        examples=["Please take your blood pressure medication with breakfast and a full glass of water"]
    )
    scheduled_time: List[datetime] = Field(
        description="List of specific times when the reminder should be sent",
        examples=[["2024-01-15T08:00:00Z", "2024-01-16T08:00:00Z"]]
    )
    days: List[str] = Field(
        description="List of days when reminder is active (e.g., weekdays, specific days)",
        examples=[["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]]
    )
    status: str = Field(
        description="Current status of the reminder",
        pattern="^(active|inactive|completed|cancelled)$",
        examples=["active"]
    )

class ReminderCreate(ReminderBase):
    """
    Schema for creating a new reminder.
    
    **Example Usage:**
    ```json
    {
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Take Evening Medication",
        "message": "Take your diabetes medication 30 minutes before dinner",
        "scheduled_time": ["2024-01-15T18:30:00Z"],
        "days": ["Monday", "Wednesday", "Friday"],
        "status": "active"
    }
    ```
    """
    pass

class Reminder(ReminderBase):
    """
    Complete reminder object returned from the API.
    
    **Additional Fields:**
    - reminder_id: Auto-generated unique identifier
    - created_at: Timestamp when reminder was created
    """
    reminder_id: UUID = Field(
        description="Unique identifier for the reminder",
        examples=["456e7890-e89b-12d3-a456-426614174001"]
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the reminder was created",
        examples=["2024-01-10T10:30:00Z"]
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "reminder_id": "456e7890-e89b-12d3-a456-426614174001",
                "patient_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Take Morning Medication",
                "message": "Please take your blood pressure medication with breakfast",
                "scheduled_time": ["2024-01-15T08:00:00Z", "2024-01-16T08:00:00Z"],
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "status": "active",
                "created_at": "2024-01-10T10:30:00Z"
            }
        }
    }

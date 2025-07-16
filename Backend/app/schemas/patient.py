from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    preferred_language: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    patient_id: UUID
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

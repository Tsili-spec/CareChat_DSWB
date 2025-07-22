# Pydantic: user-related I/O
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

class UserSignup(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    phone_number: str = Field(..., min_length=8, max_length=20)
    email: Optional[EmailStr] = None
    preferred_language: str = Field(default="en", max_length=10)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    phone_number: str = Field(..., min_length=8, max_length=20)
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    patient_id: UUID
    full_name: str
    phone_number: str
    email: Optional[str]
    preferred_language: str

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    patient: UserResponse

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800

# Legacy support
class UserCreate(BaseModel):
    name: str
    email: str
    phone_number: str
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str

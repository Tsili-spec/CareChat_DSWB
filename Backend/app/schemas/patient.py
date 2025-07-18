from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from typing import Optional
from datetime import datetime

class PatientBase(BaseModel):
    first_name: str = Field(
        min_length=1,
        max_length=100,
        description="Patient's first name",
        examples=["John"]
    )
    last_name: str = Field(
        min_length=0,
        max_length=100,
        description="Patient's last name",
        examples=["Doe"]
    )
    phone_number: str = Field(
        min_length=8,
        max_length=20,
        description="Patient's phone number (required for login)",
        examples=["+237123456789"]
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Patient's email address (optional)",
        examples=["john.doe@example.com"]
    )
    preferred_language: Optional[str] = Field(
        default="en",
        max_length=10,
        description="Patient's preferred language code",
        examples=["en", "fr"]
    )

class PatientCreate(PatientBase):
    """
    Schema for creating a new patient account.
    
    **Required fields:**
    - first_name, last_name: Patient's full name
    - phone_number: Used as unique identifier for login
    - password: Minimum 6 characters for security
    
    **Optional fields:**
    - email: For notifications and recovery
    - preferred_language: Default is 'en' (English)
    """
    password: str = Field(
        min_length=6,
        description="Password for the account (minimum 6 characters)",
        examples=["SecurePass123"]
    )

class PatientLogin(BaseModel):
    """
    Schema for patient login.
    
    **Authentication Method:**
    Uses phone_number as username and password for authentication.
    """
    phone_number: str = Field(
        description="Patient's phone number (used as username)",
        examples=["+237123456789"]
    )
    password: str = Field(
        description="Patient's password",
        examples=["SecurePass123"]
    )

class PatientResponse(PatientBase):
    """
    Patient information returned after successful authentication.
    Excludes sensitive information like password hash.
    """
    patient_id: UUID = Field(
        description="Unique identifier for the patient",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the account was created",
        examples=["2024-01-10T10:30:00Z"]
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "patient_id": "123e4567-e89b-12d3-a456-426614174000",
                "first_name": "John",
                "last_name": "Doe", 
                "phone_number": "+237123456789",
                "email": "john.doe@example.com",
                "preferred_language": "en",
                "created_at": "2024-01-10T10:30:00Z"
            }
        }
    }

class Patient(PatientResponse):
    """Alias for backward compatibility"""
    pass

class LoginResponse(BaseModel):
    """
    Response schema for successful login.
    
    **Tokens:**
    - access_token: Short-lived token for API requests (30 minutes)
    - refresh_token: Long-lived token for getting new access tokens (7 days)
    
    **Usage:**
    Include access_token in Authorization header: "Bearer {access_token}"
    """
    access_token: str = Field(
        description="JWT access token for API authentication",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    refresh_token: str = Field(
        description="JWT refresh token for obtaining new access tokens",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
        examples=["bearer"]
    )
    patient: PatientResponse = Field(
        description="Patient information"
    )
    expires_in: int = Field(
        description="Access token expiration time in seconds",
        examples=[1800]
    )

class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str = Field(
        description="Valid refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )

class TokenResponse(BaseModel):
    """Response schema for token refresh"""
    access_token: str = Field(
        description="New JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type",
        examples=["bearer"]
    )
    expires_in: int = Field(
        description="Access token expiration time in seconds",
        examples=[1800]
    )

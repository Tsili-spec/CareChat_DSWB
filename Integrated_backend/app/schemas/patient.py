from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class PatientBase(BaseModel):
    """Base schema for Patient"""
    full_name: str = Field(
        min_length=1,
        max_length=200,
        description="Patient's full name",
        examples=["John Doe"]
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
    - full_name: Patient's complete name
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

class Patient(PatientBase):
    """Schema for patient response (excluding sensitive data)"""
    patient_id: str = Field(description="Patient's unique identifier")
    created_at: Optional[datetime] = Field(description="Account creation timestamp")

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    patient: Patient = Field(description="Patient information")

class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str = Field(description="JWT refresh token")

class RefreshTokenResponse(BaseModel):
    """Schema for refresh token response"""
    access_token: str = Field(description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")

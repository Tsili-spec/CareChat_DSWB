"""
Authentication-related schemas for login, registration, and token management
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from .base import SuccessResponse


class UserRegistration(BaseModel):
    """User registration request"""
    full_name: str = Field(..., min_length=2, max_length=200, description="User's full name")
    phone_number: str = Field(..., pattern=r"^\+?[1-9]\d{8,14}$", description="Phone number for login")
    email: Optional[EmailStr] = Field(default=None, description="Email address (optional)")
    password: str = Field(..., min_length=6, max_length=128, description="Password")
    preferred_language: str = Field(default="en", max_length=10, description="Preferred language code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "phone_number": "+237123456789",
                "email": "john.doe@example.com",
                "password": "securepassword",
                "preferred_language": "en"
            }
        }


class UserLogin(BaseModel):
    """User login request"""
    phone_number: str = Field(..., description="Phone number")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+237123456789",
                "password": "securepassword"
            }
        }


class TokenResponse(BaseModel):
    """Token response after successful authentication"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 691200
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, max_length=128, description="New password")


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    phone_number: str = Field(..., description="Phone number")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    phone_number: str = Field(..., description="Phone number")
    reset_code: str = Field(..., description="Reset code sent via SMS")
    new_password: str = Field(..., min_length=6, max_length=128, description="New password")


class LogoutResponse(SuccessResponse):
    """Logout response"""
    pass

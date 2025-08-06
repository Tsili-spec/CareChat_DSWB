"""
User Model for MongoDB
Defines user data structure and authentication
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    """User model for authentication and profile management"""
    id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    hashed_password: str = Field(..., description="Hashed password")
    is_active: bool = Field(default=True, description="User account status")
    is_verified: bool = Field(default=False, description="Email verification status")
    phone_number: Optional[str] = Field(default=None, description="User phone number")
    avatar_url: Optional[str] = Field(default=None, description="User avatar image URL")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LoginHistory(BaseModel):
    """Login history tracking model"""
    id: str = Field(..., description="Unique login record identifier")
    user_id: str = Field(..., description="User ID reference")
    ip_address: str = Field(..., description="Login IP address")
    user_agent: str = Field(..., description="Browser/client user agent")
    location: Optional[str] = Field(default=None, description="Geographic location")
    success: bool = Field(..., description="Login success status")
    failure_reason: Optional[str] = Field(default=None, description="Failure reason if unsuccessful")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Login attempt timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

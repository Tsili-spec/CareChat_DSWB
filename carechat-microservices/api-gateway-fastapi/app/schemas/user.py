"""
User-related schemas for profile management and user operations
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from .base import BaseResponse, EmergencyContact, UserLocation


class UserProfile(BaseModel):
    """User profile information"""
    full_name: str = Field(..., min_length=2, max_length=200, description="User's full name")
    phone_number: str = Field(..., pattern=r"^\+?[1-9]\d{8,14}$", description="Phone number")
    email: Optional[EmailStr] = Field(default=None, description="Email address")
    preferred_language: str = Field(default="en", max_length=10, description="Preferred language code")
    location: Optional[UserLocation] = Field(default=None, description="User location")
    emergency_contact: Optional[EmergencyContact] = Field(default=None, description="Emergency contact")
    medical_conditions: Optional[List[str]] = Field(default=[], description="Medical conditions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "phone_number": "+237123456789",
                "email": "john.doe@example.com",
                "preferred_language": "en",
                "location": {
                    "city": "Douala",
                    "region": "Littoral",
                    "country": "Cameroon"
                },
                "emergency_contact": {
                    "name": "Jane Doe",
                    "phone": "+237987654321",
                    "relationship": "Spouse"
                },
                "medical_conditions": ["Diabetes", "Hypertension"]
            }
        }


class UserResponse(BaseResponse):
    """User response with profile information"""
    full_name: str = Field(..., description="User's full name")
    phone_number: str = Field(..., description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    preferred_language: str = Field(..., description="Preferred language code")
    location: Optional[UserLocation] = Field(default=None, description="User location")
    emergency_contact: Optional[EmergencyContact] = Field(default=None, description="Emergency contact")
    medical_conditions: List[str] = Field(default=[], description="Medical conditions")
    is_active: bool = Field(..., description="Whether user account is active")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")


class UserUpdateRequest(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=200, description="User's full name")
    email: Optional[EmailStr] = Field(default=None, description="Email address")
    preferred_language: Optional[str] = Field(default=None, max_length=10, description="Preferred language code")
    location: Optional[UserLocation] = Field(default=None, description="User location")
    emergency_contact: Optional[EmergencyContact] = Field(default=None, description="Emergency contact")
    medical_conditions: Optional[List[str]] = Field(default=None, description="Medical conditions")


class UserCreateRequest(BaseModel):
    """Admin user creation request"""
    full_name: str = Field(..., min_length=2, max_length=200, description="User's full name")
    phone_number: str = Field(..., pattern=r"^\+?[1-9]\d{8,14}$", description="Phone number")
    email: Optional[EmailStr] = Field(default=None, description="Email address")
    password: str = Field(..., min_length=6, max_length=128, description="Password")
    preferred_language: str = Field(default="en", max_length=10, description="Preferred language code")
    location: Optional[UserLocation] = Field(default=None, description="User location")
    emergency_contact: Optional[EmergencyContact] = Field(default=None, description="Emergency contact")
    medical_conditions: Optional[List[str]] = Field(default=[], description="Medical conditions")


class UserSearchRequest(BaseModel):
    """User search request"""
    query: Optional[str] = Field(default=None, description="Search query")
    phone_number: Optional[str] = Field(default=None, description="Phone number filter")
    email: Optional[str] = Field(default=None, description="Email filter")
    is_active: Optional[bool] = Field(default=None, description="Active status filter")
    created_after: Optional[datetime] = Field(default=None, description="Created after date filter")
    created_before: Optional[datetime] = Field(default=None, description="Created before date filter")


class UserStatsResponse(BaseModel):
    """User statistics response"""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    new_users_this_month: int = Field(..., description="New users this month")
    users_with_emergency_contact: int = Field(..., description="Users with emergency contact")
    users_by_region: dict = Field(..., description="Users grouped by region")

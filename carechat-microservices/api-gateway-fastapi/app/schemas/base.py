"""
Base schemas and common models used across the API
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.is_instance_schema(cls),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)


class BaseResponse(BaseModel):
    """Base response model with common fields"""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


# Common embedded schemas
class EmergencyContact(BaseModel):
    """Emergency contact information"""
    name: str = Field(..., max_length=200, description="Contact name")
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$", description="Contact phone number")
    relationship: str = Field(..., max_length=100, description="Relationship to user")


class UserLocation(BaseModel):
    """User location information"""
    city: str = Field(..., max_length=100, description="City")
    region: str = Field(..., max_length=100, description="Region/State")
    country: str = Field(default="Cameroon", max_length=100, description="Country")
    timezone: Optional[str] = Field(default=None, max_length=50, description="Timezone")

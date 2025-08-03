from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"

class Department(str, Enum):
    BLOOD_BANK = "Blood Bank"
    LABORATORY = "Laboratory"
    CLINICAL = "Clinical"
    ADMINISTRATION = "Administration"

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    role: UserRole = UserRole.STAFF
    phone: Optional[str] = Field(None, max_length=20)
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower()
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone number must contain only digits and common separators')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        # Check for at least one digit
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    role: Optional[UserRole] = None
    department: Optional[Department] = None
    phone: Optional[str] = Field(None, max_length=20)
    position: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    
    # Permissions
    can_manage_inventory: Optional[bool] = None
    can_view_forecasts: Optional[bool] = None
    can_manage_donors: Optional[bool] = None
    can_access_reports: Optional[bool] = None
    can_manage_users: Optional[bool] = None
    can_view_analytics: Optional[bool] = None

class UserResponse(UserBase):
    user_id: uuid.UUID
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Permissions
    can_manage_inventory: bool
    can_view_forecasts: bool
    can_manage_donors: bool
    can_access_reports: bool
    can_manage_users: bool
    can_view_analytics: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    role: str
    permissions: dict

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None

class ChangePassword(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    confirm_new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        # Check for at least one digit
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        # Check for at least one digit
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserPermissions(BaseModel):
    can_manage_inventory: bool
    can_view_forecasts: bool
    can_manage_donors: bool
    can_access_reports: bool
    can_manage_users: bool
    can_view_analytics: bool

from fastapi import FastAPI
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin.admin import admin
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import os

from app.core.config import settings as app_settings
from app.core.security import SecurityUtils
from app.models.user import User
from app.models.blood_collection import BloodCollection
from app.models.blood_usage import BloodUsage
from app.models.blood_stock import BloodStock


class UserAdminRead(BaseModel):
    user_id: uuid.UUID
    username: str
    email: str
    full_name: str
    role: str
    department: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    can_manage_inventory: bool
    can_view_forecasts: bool
    can_manage_donors: bool
    can_access_reports: bool
    can_manage_users: bool
    can_view_analytics: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    # Show hashed password (read-only)
    hashed_password: Optional[str] = None

    class Config:
        from_attributes = True


class UserAdminCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str  # Plain password for creation
    role: str = "staff"
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    can_manage_inventory: bool = False
    can_view_forecasts: bool = True
    can_manage_donors: bool = False
    can_access_reports: bool = True
    can_manage_users: bool = False
    can_view_analytics: bool = True

    class Config:
        from_attributes = True


class UserAdminUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None  # Optional password for updates
    role: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    can_manage_inventory: Optional[bool] = None
    can_view_forecasts: Optional[bool] = None
    can_manage_donors: Optional[bool] = None
    can_access_reports: Optional[bool] = None
    can_manage_users: Optional[bool] = None
    can_view_analytics: Optional[bool] = None

    class Config:
        from_attributes = True


def configure_admin(app: FastAPI):
    """Configure FastAPI-Amis-Admin interface without authentication"""
    
    # Admin settings for PostgreSQL with explicit English localization
    admin_settings = Settings(
        database_url_async=app_settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        debug=True,
        site_title="Blood Bank Management System - Admin",
        site_icon="fas fa-heart",
        site_description="Admin Panel for Blood Bank Management",
        language="en_US",
        locale="en_US",
        timezone="UTC",
        amis_theme="cxd",  # Use default theme
    )
    
    # Create admin site
    site = AdminSite(settings=admin_settings)
    
    # Force English locale at the site level
    import os
    os.environ['FASTAPI_AMIS_ADMIN_LANGUAGE'] = 'en_US'
    os.environ['FASTAPI_AMIS_ADMIN_LOCALE'] = 'en_US'
    
    # User Management Admin with Custom Password Handling
    @site.register_admin
    class UserAdmin(admin.ModelAdmin):
        model = User
        page_schema = "User Management"
        pk_name = "user_id"  # Specify the custom primary key
        
        list_display = [
            User.user_id, User.username, User.email, User.full_name,
            User.role, User.is_active, User.created_at
        ]
        search_fields = [User.username, User.email, User.full_name]
        list_filter = [User.role, User.is_active]
        
        # Form fields including password for create/update operations
        form_columns = [
            User.username, User.email, User.full_name,
            User.role, User.is_active
        ]
        
        # Custom form configuration to include password field
        async def get_create_columns(self):
            columns = list(self.form_columns)
            # Add password field for create form
            columns.append("password")
            return columns
        
        async def get_update_columns(self):
            columns = list(self.form_columns)
            # Add password field for update form (optional)
            columns.append("password")
            return columns
        
        page_size = 20
        page_size_options = [10, 20, 50, 100]
        
        # Override create method to handle password hashing
        async def create(self, obj_data: dict):
            # Extract password from the data
            password = obj_data.pop('password', None)
            
            # Create the user object
            user = User(**obj_data)
            
            # Hash the password if provided
            if password:
                user.password_hash = SecurityUtils.hash_password(password)
            
            # Add to database
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        
        # Override update method to handle password hashing
        async def update(self, obj_data: dict, obj_id):
            # Get the existing user
            user = await self.db.get(User, obj_id)
            if not user:
                return None
            
            # Extract password from the data
            password = obj_data.pop('password', None)
            
            # Update user fields
            for field, value in obj_data.items():
                setattr(user, field, value)
            
            # Update password if provided (only if not empty)
            if password and password.strip():
                user.password_hash = SecurityUtils.hash_password(password)
            
            # Save changes
            await self.db.commit()
            await self.db.refresh(user)
            return user
            """Override create to hash password"""
            # Hash the password before saving
            if hasattr(obj, 'password') and obj.password:
                obj.hashed_password = User.hash_password(obj.password)
                delattr(obj, 'password')  # Remove plain password
            return await super().create(request, obj)
        
        async def update(self, request, pk, obj):
            """Override update to hash password if provided"""
            # Get existing user
            existing_user = await self.get_obj(request, pk)
            
            # If password is provided, hash it
            if hasattr(obj, 'password') and obj.password:
                existing_user.hashed_password = User.hash_password(obj.password)
                delattr(obj, 'password')  # Remove plain password
            
            # Update other fields
            for field, value in obj.__dict__.items():
                if value is not None and hasattr(existing_user, field):
                    setattr(existing_user, field, value)
            
            return await super().update(request, pk, existing_user)
        
        async def get_obj(self, request, pk):
            """Override to include hashed password in read operations"""
            obj = await super().get_obj(request, pk)
            # Show first 20 characters of hashed password for reference
            if obj and hasattr(obj, 'hashed_password'):
                obj.password_preview = f"{obj.hashed_password[:20]}..." if obj.hashed_password else "No password set"
            return obj

    # Blood Collection Management Admin
    @site.register_admin  
    class BloodCollectionAdmin(admin.ModelAdmin):
        model = BloodCollection
        page_schema = "Blood Collection Management"
        pk_name = "donation_record_id"  # Specify the custom primary key
        
        list_display = [
            BloodCollection.donation_record_id, BloodCollection.blood_type,
            BloodCollection.collection_site, BloodCollection.donation_date,
            BloodCollection.collection_volume_ml, BloodCollection.donor_age,
            BloodCollection.donor_gender
        ]
        search_fields = [
            BloodCollection.blood_type, BloodCollection.collection_site,
            BloodCollection.donor_occupation
        ]
        list_filter = [
            BloodCollection.blood_type, BloodCollection.collection_site,
            BloodCollection.donor_gender
        ]
        
        # Form fields
        form_columns = [
            BloodCollection.donor_age, BloodCollection.donor_gender,
            BloodCollection.donor_occupation, BloodCollection.blood_type,
            BloodCollection.collection_site, BloodCollection.donation_date,
            BloodCollection.expiry_date, BloodCollection.collection_volume_ml,
            BloodCollection.hemoglobin_g_dl
        ]
        
        page_size = 25
        page_size_options = [10, 25, 50, 100]

    # Blood Usage Management Admin
    @site.register_admin
    class BloodUsageAdmin(admin.ModelAdmin):
        model = BloodUsage
        page_schema = "Blood Usage Management"
        pk_name = "usage_id"  # Specify the custom primary key
        
        list_display = [
            BloodUsage.usage_id, BloodUsage.blood_group, BloodUsage.purpose,
            BloodUsage.department, BloodUsage.volume_given_out,
            BloodUsage.usage_date, BloodUsage.individual_name
        ]
        search_fields = [
            BloodUsage.purpose, BloodUsage.department, BloodUsage.individual_name,
            BloodUsage.patient_location
        ]
        list_filter = [
            BloodUsage.blood_group, BloodUsage.purpose, BloodUsage.department
        ]
        
        # Form fields
        form_columns = [
            BloodUsage.purpose, BloodUsage.department, BloodUsage.blood_group,
            BloodUsage.volume_given_out, BloodUsage.usage_date,
            BloodUsage.individual_name, BloodUsage.patient_location
        ]
        
        page_size = 25
        page_size_options = [10, 25, 50, 100]

    # Blood Stock Management Admin
    @site.register_admin
    class BloodStockAdmin(admin.ModelAdmin):
        model = BloodStock
        page_schema = "Blood Stock Management"
        pk_name = "stock_id"  # Specify the custom primary key
        
        list_display = [
            BloodStock.stock_id, BloodStock.blood_group, BloodStock.stock_date,
            BloodStock.total_available, BloodStock.total_near_expiry,
            BloodStock.total_expired
        ]
        search_fields = [BloodStock.blood_group]
        list_filter = [BloodStock.blood_group]
        
        # Form fields
        form_columns = [
            BloodStock.blood_group, BloodStock.stock_date,
            BloodStock.total_available, BloodStock.total_near_expiry,
            BloodStock.total_expired
        ]
        
        page_size = 20
        page_size_options = [10, 20, 50, 100]
    
    # Mount admin to the app directly without authentication
    site.mount_app(app)
    
    return site
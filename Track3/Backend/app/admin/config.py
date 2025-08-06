from fastapi import FastAPI
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin.admin import admin
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.core.config import settings as app_settings
from app.models.user import User
from app.models.blood_collection import BloodCollection
from app.models.blood_usage import BloodUsage
from app.models.blood_stock import BloodStock


# Custom schemas for admin interface to handle nullable fields
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

    class Config:
        from_attributes = True


class UserAdminCreate(BaseModel):
    username: str
    email: str
    full_name: str
    role: str = "staff"
    department: Optional[str] = None
    is_active: bool = True
    can_manage_inventory: bool = False
    can_view_forecasts: bool = True
    can_manage_donors: bool = False
    can_access_reports: bool = True
    can_manage_users: bool = False
    can_view_analytics: bool = True

    class Config:
        from_attributes = True


def configure_admin(app: FastAPI):
    """Configure FastAPI-Amis-Admin interface"""
    
    # Mount admin static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Admin settings for PostgreSQL
    admin_settings = Settings(
        database_url_async=app_settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        debug=True,
        site_title="Blood Bank Management System",
        site_icon="fas fa-heart",
        site_description="Comprehensive Blood Bank Management and Analytics Platform",
        language="en_US",
        locale="en_US",
    )
    
    # Create admin site
    site = AdminSite(settings=admin_settings)
    
    # User Management Admin
    @site.register_admin
    class UserAdmin(admin.ModelAdmin):
        model = User
        page_schema = "User Management"
        pk_name = "user_id"  # Specify the custom primary key
        schema_read = UserAdminRead
        schema_create = UserAdminCreate
        schema_update = UserAdminCreate
        
        # Customize displayed columns
        list_display = [
            User.user_id, User.username, User.email, User.full_name, 
            User.role, User.is_active, User.created_at
        ]
        search_fields = [User.username, User.email, User.full_name]
        list_filter = [User.role, User.is_active]
        
        # Form fields for creating/editing
        form_columns = [
            User.username, User.email, User.full_name, User.role,
            User.department, User.is_active, User.can_manage_inventory, 
            User.can_view_forecasts, User.can_manage_donors, User.can_access_reports, 
            User.can_manage_users, User.can_view_analytics
        ]
        
        # Pagination
        page_size = 20
        page_size_options = [10, 20, 50, 100]

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
    
    # Mount admin to the app
    site.mount_app(app)
    
    return site
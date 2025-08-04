from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin.admin import admin
from fastapi_amis_admin.amis import Form, InputText, InputPassword, Page, ActionType
from starlette.staticfiles import StaticFiles
from starlette.responses import Response, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import os
from sqlalchemy.orm import Session

from app.core.config import settings as app_settings
from app.models.user import User
from app.models.blood_collection import BloodCollection
from app.models.blood_usage import BloodUsage
from app.models.blood_stock import BloodStock
from app.db.database import get_db
from app.core.security import SecurityUtils
from app.core.jwt_auth import JWTManager


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


class AdminAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle admin authentication"""
    
    def __init__(self, app, admin_site):
        super().__init__(app)
        self.admin_site = admin_site
        
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for login page, static files, and non-admin routes
        if (request.url.path.startswith('/admin/login') or 
            request.url.path.startswith('/static') or
            not request.url.path.startswith('/admin')):
            return await call_next(request)
            
        # Check if user is authenticated
        admin_token = request.cookies.get('admin_session')
        if not admin_token:
            return RedirectResponse(url='/admin/login', status_code=302)
            
        # Verify token (simplified - in production use proper JWT verification)
        try:
            payload = JWTManager.decode_token(admin_token)
            user_id = payload.get('sub')
            if not user_id:
                return RedirectResponse(url='/admin/login', status_code=302)
                
            # Check if user exists and is admin
            db = next(get_db())
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user or user.role not in ['admin', 'manager']:
                return RedirectResponse(url='/admin/login', status_code=302)
                
            # Add user to request state
            request.state.current_user = user
            
        except Exception:
            return RedirectResponse(url='/admin/login', status_code=302)
            
        return await call_next(request)


def create_admin_login_page():
    """Create admin login page"""
    return Page(
        title="Blood Bank Admin Login",
        body=Form(
            title="Admin Authentication",
            mode="horizontal",
            api="/admin/api/login",
            redirect="/admin/",
            body=[
                InputText(
                    name="username",
                    label="Username",
                    required=True,
                    placeholder="Enter your username"
                ),
                InputPassword(
                    name="password", 
                    label="Password",
                    required=True,
                    placeholder="Enter your password"
                )
            ],
            actions=[
                ActionType.Submit(
                    label="Login",
                    level="primary"
                )
            ]
        )
    )


async def admin_login_api(request: Request):
    """Handle admin login API"""
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return {"status": 1, "msg": "Username and password are required"}
            
        # Get database session
        db = next(get_db())
        
        # Find user
        user = db.query(User).filter(User.username == username).first()
        
        if not user or not user.verify_password(password):
            return {"status": 1, "msg": "Invalid username or password"}
            
        # Check if user has admin privileges
        if user.role not in ['admin', 'manager']:
            return {"status": 1, "msg": "Access denied. Admin privileges required."}
            
        # Generate admin session token
        token_data = {"sub": str(user.user_id), "role": user.role}
        token = JWTManager.create_access_token(token_data)
        
        # Return success response with cookie
        from fastapi.responses import JSONResponse
        response = JSONResponse({
            "status": 0,
            "msg": "Login successful",
            "data": {
                "user": user.username,
                "role": user.role
            }
        })
        
        response.set_cookie(
            key="admin_session",
            value=token,
            max_age=3600 * 24,  # 24 hours
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        return response
        
    except Exception as e:
        return {"status": 1, "msg": f"Login failed: {str(e)}"}


async def admin_logout_api(request: Request):
    """Handle admin logout"""
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_session")
    return response


def configure_admin(app: FastAPI):
    """Configure FastAPI-Amis-Admin interface with authentication"""
    
    # Mount admin static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Admin settings for PostgreSQL with explicit English localization
    admin_settings = Settings(
        database_url_async=app_settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        debug=True,
        site_title="Blood Bank Management System - Admin",
        site_icon="fas fa-heart",
        site_description="Secure Admin Panel for Blood Bank Management",
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
    
    # Add authentication routes BEFORE mounting the admin
    @app.get("/admin/login")
    async def admin_login_page(request: Request):
        """Display admin login page"""
        from fastapi.templating import Jinja2Templates
        
        # Simple HTML login page
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Blood Bank Admin Login</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }
                .login-container {
                    background: white;
                    padding: 2rem;
                    border-radius: 10px;
                    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                    width: 100%;
                    max-width: 400px;
                }
                .login-header {
                    text-align: center;
                    margin-bottom: 2rem;
                }
                .login-header h1 {
                    color: #333;
                    margin: 0;
                    font-size: 1.8rem;
                }
                .login-header p {
                    color: #666;
                    margin: 0.5rem 0 0 0;
                }
                .form-group {
                    margin-bottom: 1rem;
                }
                .form-group label {
                    display: block;
                    margin-bottom: 0.5rem;
                    color: #555;
                    font-weight: bold;
                }
                .form-group input {
                    width: 100%;
                    padding: 0.75rem;
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    font-size: 1rem;
                    transition: border-color 0.3s;
                    box-sizing: border-box;
                }
                .form-group input:focus {
                    outline: none;
                    border-color: #667eea;
                }
                .login-btn {
                    width: 100%;
                    padding: 0.75rem;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 1rem;
                    cursor: pointer;
                    transition: transform 0.2s;
                }
                .login-btn:hover {
                    transform: translateY(-2px);
                }
                .error-msg {
                    color: #e74c3c;
                    margin-top: 1rem;
                    padding: 0.5rem;
                    background: #ffeaea;
                    border-radius: 5px;
                    display: none;
                }
                .success-msg {
                    color: #27ae60;
                    margin-top: 1rem;
                    padding: 0.5rem;
                    background: #eafaf1;
                    border-radius: 5px;
                    display: none;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="login-header">
                    <h1>🩸 Blood Bank Admin</h1>
                    <p>Secure Administration Panel</p>
                </div>
                <form id="loginForm">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="login-btn">Login</button>
                    <div id="errorMsg" class="error-msg"></div>
                    <div id="successMsg" class="success-msg"></div>
                </form>
            </div>
            
            <script>
                document.getElementById('loginForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;
                    const errorMsg = document.getElementById('errorMsg');
                    const successMsg = document.getElementById('successMsg');
                    
                    // Hide previous messages
                    errorMsg.style.display = 'none';
                    successMsg.style.display = 'none';
                    
                    try {
                        const response = await fetch('/admin/api/login', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ username, password })
                        });
                        
                        const data = await response.json();
                        
                        if (data.status === 0) {
                            successMsg.textContent = 'Login successful! Redirecting...';
                            successMsg.style.display = 'block';
                            setTimeout(() => {
                                window.location.href = '/admin/';
                            }, 1000);
                        } else {
                            errorMsg.textContent = data.msg || 'Login failed';
                            errorMsg.style.display = 'block';
                        }
                    } catch (error) {
                        errorMsg.textContent = 'Network error. Please try again.';
                        errorMsg.style.display = 'block';
                    }
                });
            </script>
        </body>
        </html>
        """
        return Response(content=html_content, media_type="text/html")
    
    @app.post("/admin/api/login")
    async def admin_login_endpoint(request: Request):
        """Handle admin login API"""
        return await admin_login_api(request)
    
    @app.get("/admin/logout")
    async def admin_logout_endpoint(request: Request):
        """Handle admin logout"""
        return await admin_logout_api(request)
    
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
    
    # Add authentication middleware
    app.add_middleware(AdminAuthMiddleware, admin_site=site)
    
    # Mount admin to the app
    site.mount_app(app)
    
    return site
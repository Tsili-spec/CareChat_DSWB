from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserResponse, UserLogin, Token, UserUpdate,
    ChangePassword, ForgotPassword, ResetPassword, UserPermissions
)
from app.core.jwt_auth import JWTManager
from app.core.auth import get_current_user, require_role
from app.core.config import settings
from app.core.security import SecurityUtils
from typing import List

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user data (without password)
        
    Raises:
        HTTPException: If username or email already exists
    """
    
    # Check if username already exists
    existing_user = db.query(User).filter(
        User.username == user_data.username.lower()
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if employee_id already exists (if provided)
    if user_data.employee_id:
        existing_employee = db.query(User).filter(
            User.employee_id == user_data.employee_id
        ).first()
        
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already registered"
            )
    
    # Create new user
    hashed_password = User.hash_password(user_data.password)
    
    new_user = User(
        username=user_data.username.lower(),
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        department=user_data.department,
        phone=user_data.phone,
        employee_id=user_data.employee_id,
        position=user_data.position,
        can_manage_inventory=user_data.can_manage_inventory,
        can_view_forecasts=user_data.can_view_forecasts,
        can_manage_donors=user_data.can_manage_donors,
        can_access_reports=user_data.can_access_reports,
        can_manage_users=user_data.can_manage_users,
        can_view_analytics=user_data.can_view_analytics
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token
    
    Args:
        login_data: User login credentials
        db: Database session
        
    Returns:
        JWT access token and user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    
    # Get user by username
    user = db.query(User).filter(
        User.username == login_data.username.lower()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Account is locked. Try again after {user.locked_until.strftime('%Y-%m-%d %H:%M:%S')}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not user.verify_password(login_data.password):
        # Increment failed login attempts
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        
        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated"
        )
    
    # Reset failed login attempts and update last login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_data = {
        "sub": user.username,
        "user_id": user.id
    }
    
    access_token = JWTManager.create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    # Prepare user permissions
    permissions = {
        "can_manage_inventory": user.can_manage_inventory,
        "can_view_forecasts": user.can_view_forecasts,
        "can_manage_donors": user.can_manage_donors,
        "can_access_reports": user.can_access_reports,
        "can_manage_users": user.can_manage_users,
        "can_view_analytics": user.can_view_analytics
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": JWTManager.get_token_expiry_time(),
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "permissions": permissions
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile
    
    Args:
        current_user: Current authenticated user (from dependency)
        
    Returns:
        User profile data
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    
    Args:
        user_update: Updated user data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user profile
    """
    
    # Update allowed fields
    update_data = user_update.dict(exclude_unset=True)
    
    # Remove role and permission updates for non-admin users
    if current_user.role != "admin":
        restricted_fields = ["role", "can_manage_inventory", "can_manage_donors", 
                           "can_manage_users", "is_active"]
        for field in restricted_fields:
            update_data.pop(field, None)
    
    # Check email uniqueness if being updated
    if "email" in update_data:
        existing_email = db.query(User).filter(
            User.email == update_data["email"],
            User.id != current_user.id
        ).first()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered by another user"
            )
    
    # Update user fields
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/change-password")
def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    Args:
        password_data: Current and new password data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    
    # Verify current password
    if not current_user.verify_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = User.hash_password(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/refresh", response_model=Token)
def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh user's access token
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        New JWT access token
    """
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_data = {
        "sub": current_user.username,
        "user_id": current_user.id
    }
    
    new_access_token = JWTManager.create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    # Prepare user permissions
    permissions = {
        "can_manage_inventory": current_user.can_manage_inventory,
        "can_view_forecasts": current_user.can_view_forecasts,
        "can_manage_donors": current_user.can_manage_donors,
        "can_access_reports": current_user.can_access_reports,
        "can_manage_users": current_user.can_manage_users,
        "can_view_analytics": current_user.can_view_analytics
    }
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": JWTManager.get_token_expiry_time(),
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "permissions": permissions
    }

@router.post("/logout")
def logout_user(current_user: User = Depends(get_current_user)):
    """
    Logout current user (client-side token removal)
    
    Note: With JWT, logout is primarily handled client-side
    by removing the token. Server-side logout would require
    token blacklisting (not implemented in this basic version).
    """
    return {"message": "Successfully logged out"}

# Admin endpoints
@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only)
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        List of users
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (Admin only)
    
    Args:
        user_id: User ID to retrieve
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        User data
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Update user by ID (Admin only)
    
    Args:
        user_id: User ID to update
        user_update: Updated user data
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        Updated user data
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    
    # Check email uniqueness if being updated
    if "email" in update_data:
        existing_email = db.query(User).filter(
            User.email == update_data["email"],
            User.id != user_id
        ).first()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered by another user"
            )
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Delete user by ID (Admin only)
    
    Args:
        user_id: User ID to delete
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        Success message
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.username} deleted successfully"}

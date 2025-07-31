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

router = APIRouter(prefix="/auth")

def assign_permissions_by_role(role: str) -> dict:
    """
    Automatically assign permissions based on user role
    
    Args:
        role: User role (admin, manager, staff, viewer)
        
    Returns:
        Dictionary of permissions for the role
    """
    role_permissions = {
        "admin": {
            "can_manage_inventory": True,
            "can_view_forecasts": True,
            "can_manage_donors": True,
            "can_access_reports": True,
            "can_manage_users": True,
            "can_view_analytics": True
        },
        "manager": {
            "can_manage_inventory": True,
            "can_view_forecasts": True,
            "can_manage_donors": True,
            "can_access_reports": True,
            "can_manage_users": False,
            "can_view_analytics": True
        },
        "staff": {
            "can_manage_inventory": False,
            "can_view_forecasts": True,
            "can_manage_donors": True,
            "can_access_reports": True,
            "can_manage_users": False,
            "can_view_analytics": True
        },
        "viewer": {
            "can_manage_inventory": False,
            "can_view_forecasts": True,
            "can_manage_donors": False,
            "can_access_reports": True,
            "can_manage_users": False,
            "can_view_analytics": True
        }
    }
    
    return role_permissions.get(role.lower(), role_permissions["staff"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account with automatic permission assignment based on role
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user data (without password)
        
    Raises:
        HTTPException: If username or email already exists or invalid role
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
    
    # Validate role
    valid_roles = ["admin", "manager", "staff", "viewer"]
    if user_data.role.lower() not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Automatically assign permissions based on role
    permissions = assign_permissions_by_role(user_data.role)
    
    # Create new user with automatic permission assignment
    hashed_password = User.hash_password(user_data.password)
    
    new_user = User(
        username=user_data.username.lower(),
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        phone=user_data.phone,
        can_manage_inventory=permissions["can_manage_inventory"],
        can_view_forecasts=permissions["can_view_forecasts"],
        can_manage_donors=permissions["can_manage_donors"],
        can_access_reports=permissions["can_access_reports"],
        can_manage_users=permissions["can_manage_users"],
        can_view_analytics=permissions["can_view_analytics"]
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
    
    # Verify password
    if not user.verify_password(login_data.password):
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
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token and refresh token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_data = {
        "sub": user.username,
        "user_id": str(user.user_id)
    }
    
    access_token = JWTManager.create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    refresh_token = JWTManager.create_refresh_token(data=token_data)
    
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
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": JWTManager.get_token_expiry_time(),
        "user_id": str(user.user_id),
        "username": user.username,
        "role": user.role,
        "permissions": permissions
    }

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
    user_id: str,
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
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user_by_id(
    user_id: str,
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
    user = db.query(User).filter(User.user_id == user_id).first()
    
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
            User.user_id != user_id
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
    user_id: str,
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
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.username} deleted successfully"}

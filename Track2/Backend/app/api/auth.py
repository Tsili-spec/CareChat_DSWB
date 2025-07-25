from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserSignup, UserLogin, UserResponse, LoginResponse, 
    TokenRefresh, TokenResponse, UserCreate, UserOut
)
from app.core.jwt_auth import create_access_token, create_refresh_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.auth import get_current_patient
from passlib.context import CryptContext
from datetime import timedelta
from typing import Optional
import logging

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """Register new patient account using phone number as unique identifier"""
    try:
        # Check if phone number already exists
        existing_user = db.query(User).filter(User.phone_number == user_data.phone_number).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Check if email already exists (if provided)
        if user_data.email:
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Hash password
        hashed_password = pwd_context.hash(user_data.password)
        
        # Create new user
        db_user = User(
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            email=user_data.email,
            preferred_language=user_data.preferred_language,
            password_hash=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"New patient registered: {db_user.patient_id}")
        
        return UserResponse(
            patient_id=db_user.patient_id,
            full_name=db_user.full_name,
            phone_number=db_user.phone_number,
            email=db_user.email,
            preferred_language=db_user.preferred_language
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number or email already exists"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", response_model=LoginResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate patient using phone number and password"""
    try:
        # Find user by phone number
        db_user = db.query(User).filter(User.phone_number == login_data.phone_number).first()
        
        if not db_user or not pwd_context.verify(login_data.password, db_user.password_hash):
            logger.warning(f"Failed login attempt for phone: {login_data.phone_number}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone number or password"
            )
        
        # Generate tokens
        access_token = create_access_token(
            data={"sub": str(db_user.patient_id)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(data={"sub": str(db_user.patient_id)})
        
        logger.info(f"Successful login for patient: {db_user.patient_id}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            patient=UserResponse(
                patient_id=db_user.patient_id,
                full_name=db_user.full_name,
                phone_number=db_user.phone_number,
                email=db_user.email,
                preferred_language=db_user.preferred_language
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Generate new access token using refresh token"""
    try:
        # Verify refresh token
        payload = verify_token(token_data.refresh_token, "refresh")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        patient_id = payload.get("sub")
        if patient_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify patient still exists
        db_user = db.query(User).filter(User.patient_id == patient_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Patient not found"
            )
        
        # Generate new access token
        new_access_token = create_access_token(
            data={"sub": patient_id},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"Token refreshed for patient: {patient_id}")
        
        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_patient: User = Depends(get_current_patient)):
    """Get current authenticated patient profile"""
    return UserResponse(
        patient_id=current_patient.patient_id,
        full_name=current_patient.full_name,
        phone_number=current_patient.phone_number,
        email=current_patient.email,
        preferred_language=current_patient.preferred_language
    )

# Legacy endpoints for backward compatibility
@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Legacy registration endpoint"""
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        full_name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserOut(
        id=int(str(db_user.patient_id).replace('-', '')[:8], 16),  # Convert UUID to int for legacy
        name=db_user.full_name,
        email=db_user.email,
        phone_number=db_user.phone_number
    )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserSignup, UserLogin, UserResponse, LoginResponse, 
    TokenRefresh, TokenResponse
)
from app.core.jwt_auth import create_access_token, create_refresh_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from passlib.context import CryptContext
from datetime import timedelta
from typing import List
from uuid import UUID
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

@router.get("/patients", response_model=List[UserResponse])
async def get_all_patients(db: Session = Depends(get_db)):
    """Get all patients in the system - No authorization required"""
    try:
        patients = db.query(User).all()
        
        return [
            UserResponse(
                patient_id=patient.patient_id,
                full_name=patient.full_name,
                phone_number=patient.phone_number,
                email=patient.email,
                preferred_language=patient.preferred_language
            )
            for patient in patients
        ]
        
    except Exception as e:
        logger.error(f"Error fetching patients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/patients/{patient_id}", response_model=UserResponse)
async def get_patient_by_id(patient_id: UUID, db: Session = Depends(get_db)):
    """Get a specific patient by their patient_id - No authorization required"""
    try:
        patient = db.query(User).filter(User.patient_id == patient_id).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        return UserResponse(
            patient_id=patient.patient_id,
            full_name=patient.full_name,
            phone_number=patient.phone_number,
            email=patient.email,
            preferred_language=patient.preferred_language
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a patient and all associated data (conversations, messages)
    
    **How it works:**
    1. Verifies the patient exists in the database
    2. Deletes all messages from the patient's conversations
    3. Deletes all conversations belonging to the patient  
    4. Deletes the patient record itself
    5. Returns a summary of deleted data
    
    **Security Note:** This permanently deletes all patient data and cannot be undone.
    Use with caution and ensure proper authorization in production.
    """
    try:
        from app.services.conversation_service import conversation_memory
        
        # Check if patient exists
        patient = db.query(User).filter(User.patient_id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Delete all patient data using conversation service
        deletion_result = conversation_memory.delete_user_data(db=db, user_id=patient_id)
        
        logger.info(f"Deleted patient {patient_id} and all associated data")
        
        return {
            "status": "success",
            "patient_id": str(patient_id),
            **deletion_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete patient: {str(e)}"
        )

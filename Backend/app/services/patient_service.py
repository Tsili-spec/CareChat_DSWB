from sqlalchemy.orm import Session
from app.models.models import Patient as PatientModel
from app.schemas.patient import PatientCreate, PatientLogin
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, status
from uuid import UUID
from typing import Optional
import os
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "refreshsecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class PatientService:
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password for storing in the database"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str, secret_key: str = SECRET_KEY) -> Optional[dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def create_patient(db: Session, patient_data: PatientCreate) -> PatientModel:
        """
        Create a new patient account
        """
        logger.info(f"Attempting to create patient with phone: {patient_data.phone_number}")
        
        # Check if patient already exists
        existing_patient = db.query(PatientModel).filter(
            (PatientModel.phone_number == patient_data.phone_number) | 
            (PatientModel.email == patient_data.email)
        ).first()
        
        if existing_patient:
            if existing_patient.phone_number == patient_data.phone_number:
                logger.warning(f"Patient creation failed: phone number {patient_data.phone_number} already exists.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A patient with this phone number already exists"
                )
            else:
                logger.warning(f"Patient creation failed: email {patient_data.email} already exists.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A patient with this email already exists"
                )
        
        # Hash the password
        hashed_password = PatientService.get_password_hash(patient_data.password)
        
        # Create patient record
        db_patient = PatientModel(
            first_name=patient_data.first_name,
            last_name=patient_data.last_name,
            phone_number=patient_data.phone_number,
            email=patient_data.email,
            preferred_language=patient_data.preferred_language or "en",
            password_hash=hashed_password,
            created_at=datetime.utcnow()
        )
        
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        
        logger.info(f"Patient created successfully with ID: {db_patient.patient_id}")
        return db_patient
    
    @staticmethod
    def authenticate_patient(db: Session, login_data: PatientLogin) -> Optional[PatientModel]:
        """
        Authenticate a patient using phone number and password
        """
        logger.info(f"Authentication attempt for phone: {login_data.phone_number}")
        
        patient = db.query(PatientModel).filter(
            PatientModel.phone_number == login_data.phone_number
        ).first()
        
        if not patient:
            logger.warning(f"Authentication failed for phone {login_data.phone_number}: patient not found.")
            return None
        
        if not PatientService.verify_password(login_data.password, patient.password_hash):
            logger.warning(f"Authentication failed for patient {patient.patient_id}: invalid password.")
            return None
        
        logger.info(f"Patient {patient.patient_id} authenticated successfully.")
        return patient
    
    @staticmethod
    def get_patient_by_id(db: Session, patient_id: UUID) -> Optional[PatientModel]:
        """Get a patient by their ID"""
        return db.query(PatientModel).filter(
            PatientModel.patient_id == patient_id
        ).first()
    
    @staticmethod
    def get_patient_by_phone(db: Session, phone_number: str) -> Optional[PatientModel]:
        """Get a patient by their phone number"""
        return db.query(PatientModel).filter(
            PatientModel.phone_number == phone_number
        ).first()
    
    @staticmethod
    def create_login_response(patient: PatientModel) -> dict:
        """
        Create a complete login response with tokens and patient info
        """
        # Create tokens
        access_token = PatientService.create_access_token({"sub": str(patient.patient_id)})
        refresh_token = PatientService.create_refresh_token({"sub": str(patient.patient_id)})
        
        # Patient info (excluding sensitive data)
        patient_info = {
            "patient_id": str(patient.patient_id),
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "phone_number": patient.phone_number,
            "email": patient.email,
            "preferred_language": patient.preferred_language,
            "created_at": patient.created_at
        }
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            "patient": patient_info
        }
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> dict:
        """
        Generate a new access token using a valid refresh token
        """
        payload = PatientService.verify_token(refresh_token, REFRESH_SECRET_KEY)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        patient_id = payload.get("sub")
        if not patient_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Verify patient still exists
        patient = PatientService.get_patient_by_id(db, UUID(patient_id))
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Patient not found"
            )
        
        # Create new access token
        new_access_token = PatientService.create_access_token({"sub": patient_id})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @staticmethod
    def get_current_patient(db: Session, token: str) -> PatientModel:
        """
        Get the current authenticated patient from access token
        """
        payload = PatientService.verify_token(token)
        
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        patient_id = payload.get("sub")
        if not patient_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        patient = PatientService.get_patient_by_id(db, UUID(patient_id))
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Patient not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return patient 
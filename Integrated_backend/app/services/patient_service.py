from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from app.core.config import settings
from app.models.models import Patient as PatientModel
from app.schemas.patient import PatientCreate, PatientLogin
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PatientService:
    """Service class for patient authentication and management"""
    
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
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    def verify_token(token: str, secret_key: str = None) -> Optional[dict]:
        """Verify and decode a JWT token"""
        if secret_key is None:
            secret_key = settings.JWT_SECRET_KEY
            
        try:
            payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    async def create_patient(patient_data: PatientCreate) -> PatientModel:
        """Create a new patient account"""
        logger.info(f"Attempting to create patient with phone: {patient_data.phone_number}")
        
        # Check if patient already exists
        existing_patient = await PatientModel.find_one(
            {"$or": [
                {"phone_number": patient_data.phone_number},
                {"email": patient_data.email} if patient_data.email else {"_id": None}
            ]}
        )
        
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
            full_name=patient_data.full_name,
            phone_number=patient_data.phone_number,
            email=patient_data.email,
            preferred_language=patient_data.preferred_language or "en",
            password_hash=hashed_password,
            created_at=datetime.utcnow()
        )
        
        await db_patient.insert()
        
        logger.info(f"Patient created successfully with ID: {db_patient.patient_id}")
        return db_patient
    
    @staticmethod
    async def authenticate_patient(login_data: PatientLogin) -> Optional[PatientModel]:
        """Authenticate a patient using phone number and password"""
        logger.info(f"Authentication attempt for phone: {login_data.phone_number}")
        
        patient = await PatientModel.find_one({"phone_number": login_data.phone_number})
        
        if not patient:
            logger.warning(f"Authentication failed for phone {login_data.phone_number}: patient not found.")
            return None
        
        if not PatientService.verify_password(login_data.password, patient.password_hash):
            logger.warning(f"Authentication failed for patient {patient.patient_id}: invalid password.")
            return None
        
        logger.info(f"Patient {patient.patient_id} authenticated successfully.")
        return patient
    
    @staticmethod
    def create_login_response(patient: PatientModel) -> dict:
        """Create a complete login response with tokens and patient info"""
        # Create tokens
        access_token = PatientService.create_access_token({"sub": str(patient.patient_id)})
        refresh_token = PatientService.create_refresh_token({"sub": str(patient.patient_id)})
        
        # Patient info (excluding sensitive data)
        patient_info = {
            "patient_id": str(patient.patient_id),
            "full_name": patient.full_name,
            "phone_number": patient.phone_number,
            "email": patient.email,
            "preferred_language": patient.preferred_language,
            "created_at": patient.created_at
        }
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            "patient": patient_info
        }
    
    @staticmethod
    async def get_current_patient(db, token: str) -> PatientModel:
        """Get the current authenticated patient from access token"""
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
        
        patient = await PatientModel.find_one({"patient_id": patient_id})
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Patient not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return patient
    
    @staticmethod
    async def get_patient_by_id(patient_id: str) -> Optional[PatientModel]:
        """Get patient by ID"""
        return await PatientModel.find_one({"patient_id": patient_id})
    
    @staticmethod
    async def refresh_access_token(refresh_token: str) -> dict:
        """Generate new access token using refresh token"""
        payload = PatientService.verify_token(refresh_token, settings.JWT_REFRESH_SECRET_KEY)
        
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
        patient = await PatientService.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Patient not found"
            )
        
        # Generate new access token
        access_token = PatientService.create_access_token({"sub": patient_id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

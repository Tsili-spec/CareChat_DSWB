# CareChat Backend - Authentication, Account Creation, and Feedback Systems Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [File Structure](#file-structure)
3. [Authentication System](#authentication-system)
4. [Account Creation System](#account-creation-system)
5. [Feedback System](#feedback-system)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)
8. [Code Documentation](#code-documentation)

## System Overview

The CareChat Backend is a FastAPI-based RESTful API that provides healthcare patient management services including authentication, account creation, and feedback collection with advanced analysis capabilities. The system supports multilingual feedback (English and French), audio feedback transcription, sentiment analysis, and topic extraction.

### Key Features:
- **JWT-based Authentication**: Secure token-based authentication with access and refresh tokens
- **Account Management**: Complete patient registration and profile management
- **Multilingual Feedback**: Support for text and audio feedback in multiple languages
- **AI-Powered Analysis**: Sentiment analysis, topic extraction, and urgency detection
- **SMS Integration**: Twilio-based SMS notifications (for reminders)
- **Database Migrations**: Alembic-based database versioning

## File Structure

```
Backend/
├── app/
│   ├── __init__.py                    # Package initialization
│   ├── main.py                        # FastAPI application entry point
│   ├── api/                          # API route handlers
│   │   ├── dashboard.py              # Dashboard API endpoints
│   │   ├── feedback.py               # Feedback management endpoints
│   │   ├── patient.py                # Patient/authentication endpoints
│   │   └── reminder.py               # Reminder management endpoints
│   ├── core/                         # Core application components
│   │   ├── auth.py                   # Authentication dependencies
│   │   ├── config.py                 # Application configuration
│   │   └── logging_config.py         # Logging configuration
│   ├── db/                           # Database components
│   │   ├── __init__.py               # Database package init
│   │   └── database.py               # Database connection and session management
│   ├── models/                       # Database models
│   │   └── models.py                 # SQLAlchemy ORM models
│   ├── schemas/                      # Pydantic schemas
│   │   ├── feedback.py               # Feedback data validation schemas
│   │   ├── patient.py                # Patient data validation schemas
│   │   └── reminder.py               # Reminder data validation schemas
│   └── services/                     # Business logic services
│       ├── analysis.py               # Feedback analysis (sentiment, topics, urgency)
│       ├── patient_service.py        # Patient authentication and management
│       ├── reminder_scheduler.py     # Reminder scheduling service
│       ├── reminder_service.py       # Reminder management service
│       ├── sms_service.py            # SMS notification service
│       ├── transcription.py          # Audio transcription service
│       ├── transcription_translation.py # Combined transcription and translation
│       └── translation.py           # Text translation service
├── alembic/                          # Database migrations
│   ├── env.py                        # Alembic environment configuration
│   ├── script.py.mako               # Migration script template
│   └── versions/                     # Migration version files
├── logs/                             # Application logs
├── upload/                           # File upload storage
├── alembic.ini                       # Alembic configuration
├── requirements.txt                  # Python dependencies
└── start.sh                         # Application startup script
```

## Authentication System

### Overview
The authentication system uses JWT (JSON Web Tokens) with a dual-token approach:
- **Access Token**: Short-lived (30 minutes) for API requests
- **Refresh Token**: Long-lived (7 days) for obtaining new access tokens

### Implementation Details

#### 1. Password Security
```python
# Located in: app/services/patient_service.py

# Password hashing using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@staticmethod
def get_password_hash(password: str) -> str:
    """Hash a password for storing in the database"""
    return pwd_context.hash(password)

@staticmethod
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

#### 2. JWT Token Management
```python
# Located in: app/services/patient_service.py

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "refreshsecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

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
```

#### 3. Authentication Dependencies
```python
# Located in: app/core/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security scheme for JWT Bearer token
security = HTTPBearer()

async def get_current_patient(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> PatientModel:
    """
    Dependency to get the current authenticated patient.
    
    **Usage in endpoints:**
    ```python
    @router.get("/protected-endpoint")
    def protected_route(current_patient: PatientModel = Depends(get_current_patient)):
        # Only authenticated patients can access this
        return {"patient_id": current_patient.patient_id}
    ```
    
    **Authentication:**
    - Requires "Authorization: Bearer {access_token}" header
    - Validates JWT token and returns patient object
    - Raises 401 if token is invalid/expired
    """
    token = credentials.credentials
    return PatientService.get_current_patient(db, token)

async def get_current_patient_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[PatientModel]:
    """
    Optional authentication dependency.
    Returns patient if authenticated, None if not.
    
    **Usage:**
    For endpoints that can work with or without authentication.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        return PatientService.get_current_patient(db, token)
    except HTTPException:
        return None
```

#### 4. Token Verification
```python
# Located in: app/services/patient_service.py

@staticmethod
def verify_token(token: str, secret_key: str = SECRET_KEY) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

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
```

## Account Creation System

### Patient Registration Process

#### 1. Patient Schema Definition
```python
# Located in: app/schemas/patient.py

class PatientBase(BaseModel):
    full_name: str = Field(
        min_length=1,
        max_length=200,
        description="Patient's full name",
        examples=["John Doe"]
    )
    phone_number: str = Field(
        min_length=8,
        max_length=20,
        description="Patient's phone number (required for login)",
        examples=["+237123456789"]
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Patient's email address (optional)",
        examples=["john.doe@example.com"]
    )
    preferred_language: Optional[str] = Field(
        default="en",
        max_length=10,
        description="Patient's preferred language code",
        examples=["en", "fr"]
    )

class PatientCreate(PatientBase):
    """
    Schema for creating a new patient account.
    
    **Required fields:**
    - full_name: Patient's complete name
    - phone_number: Used as unique identifier for login
    - password: Minimum 6 characters for security
    
    **Optional fields:**
    - email: For notifications and recovery
    - preferred_language: Default is 'en' (English)
    """
    password: str = Field(
        min_length=6,
        description="Password for the account (minimum 6 characters)",
        examples=["SecurePass123"]
    )
```

#### 2. Patient Registration Service
```python
# Located in: app/services/patient_service.py

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
        full_name=patient_data.full_name,
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
```

#### 3. Registration API Endpoint
```python
# Located in: app/api/patient.py

@router.post("/signup", 
             response_model=Patient, 
             status_code=status.HTTP_201_CREATED,
             summary="Register a new patient",
             description="Create a new patient account with phone number as unique identifier")
def signup(patient: PatientCreate, db: Session = Depends(get_db)):
    """
    Register a new patient account.
    
    **Authentication Method:**
    - Phone number is used as the unique identifier for login
    - Email is optional but recommended for account recovery
    - Password must be at least 6 characters
    
    **Example request:**
    ```json
    {
        "full_name": "John Doe",
        "phone_number": "+237123456789",
        "email": "john.doe@example.com",
        "preferred_language": "en",
        "password": "SecurePass123"
    }
    ```
    
    **Returns:** Patient information (excluding password)
    
    **Errors:**
    - 400: Patient with phone number or email already exists
    - 422: Validation errors (missing fields, invalid format)
    """
    try:
        db_patient = PatientService.create_patient(db, patient)
        return db_patient
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating patient account: {str(e)}"
        )
```

### Login Process

#### 1. Login Schema
```python
# Located in: app/schemas/patient.py

class PatientLogin(BaseModel):
    """
    Schema for patient login.
    
    **Authentication Method:**
    Uses phone_number as username and password for authentication.
    """
    phone_number: str = Field(
        description="Patient's phone number (used as username)",
        examples=["+237123456789"]
    )
    password: str = Field(
        description="Patient's password",
        examples=["SecurePass123"]
    )
```

#### 2. Authentication Service
```python
# Located in: app/services/patient_service.py

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
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        "patient": patient_info
    }
```

#### 3. Login API Endpoint
```python
# Located in: app/api/patient.py

@router.post("/login", 
             response_model=LoginResponse,
             summary="Patient login",
             description="Authenticate patient and receive access tokens")
def login(login_data: PatientLogin, db: Session = Depends(get_db)):
    """
    Authenticate a patient and receive access tokens.
    
    **Authentication:**
    - Uses phone_number as username
    - Returns JWT tokens for API access
    - Access token expires in 30 minutes
    - Refresh token expires in 7 days
    
    **Example request:**
    ```json
    {
        "phone_number": "+237123456789",
        "password": "SecurePass123"
    }
    ```
    
    **Example response:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 1800,
        "patient": {
            "patient_id": "123e4567-e89b-12d3-a456-426614174000",
            "full_name": "John Doe",
            "phone_number": "+237123456789",
            "email": "john.doe@example.com",
            "preferred_language": "en"
        }
    }
    ```
    
    **Usage:**
    Include access_token in Authorization header: "Bearer {access_token}"
    
    **Errors:**
    - 401: Invalid phone number or password
    - 422: Validation errors
    """
    patient = PatientService.authenticate_patient(db, login_data)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password"
        )
    
    return PatientService.create_login_response(patient)
```

## Feedback System

### Overview
The feedback system supports both text and audio feedback with advanced analysis capabilities including sentiment analysis, topic extraction, and urgency detection. It handles multilingual input (English and French) with automatic translation.

### Key Components

#### 1. Feedback Schema
```python
# Located in: app/schemas/feedback.py

class FeedbackBase(BaseModel):
    patient_id: UUID
    rating: Optional[int] = None
    feedback_text: Optional[str] = None
    translated_text: Optional[str] = None
    language: str
    sentiment: Optional[str] = None
    topic: Optional[str] = None
    urgency: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    feedback_id: UUID
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
```

#### 2. Feedback Analysis Engine
```python
# Located in: app/services/analysis.py

import re
import spacy
import numpy as np
from textblob import TextBlob
from typing import List, Optional, Dict, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the English language model
nlp = spacy.load('en_core_web_md')

def preprocess(text: str) -> str:
    text = text.lower()                                 # Convert to lowercase
    text = re.sub(r"[^\w\s]", "", text)                 # Remove punctuation
    text = re.sub(r"\s+", " ", text)                    # remove whitespace
    return text.strip()

def get_sentiment_from_text(text: str) -> str:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

def get_sentiment_from_rating(rating: int) -> str:
    if rating >= 4:
        return "positive"
    elif rating == 3:
        return "neutral"
    else:
        return "negative"

class TopicAnalyzer:
    def __init__(self):
        self.topic_keywords = {
            "wait_time": ["wait", "delay", "queue", "slow", "time"],
            "staff_attitude": ["rude", "impolite", "shout", "disrespect", "unfriendly", "care", 
                             "attitude", "behavior", "manner", "treatment", "service", "doctor", "nurse"],
            "medication": ["drug", "pill", "prescription", "medication", "dose", "tablet", "medicine", 
                         "treatment", "pharmacy", "prescribe"],
            "cost": ["expensive", "bill", "cost", "money", "price", "payment", "charge", "fee", "afford", 
                    "insurance", "financial"]
        }
        # Create word vectors for each keyword
        self.topic_word_vectors = {}
        for topic, keywords in self.topic_keywords.items():
            self.topic_word_vectors[topic] = [nlp(word) for word in keywords]

    def _get_text_similarity(self, text: str, topic: str) -> float:
        # Process the input text
        doc = nlp(text.lower())
        
        # Calculate similarity between each word in text and topic keywords
        max_similarities = []
        for token in doc:
            if not token.is_stop and not token.is_punct:
                similarities = [token.similarity(keyword) for keyword in self.topic_word_vectors[topic]]
                if similarities:
                    max_similarities.append(max(similarities))
        
        # Return average of top similarities if any found
        return sum(max_similarities) / len(max_similarities) if max_similarities else 0.0

    def extract_topics(self, text: str, similarity_threshold: float = 0.45) -> List[str]:
        found_topics = []
        text = text.lower()
        
        # Calculate similarity scores for each topic
        topic_similarities = {}
        for topic in self.topic_keywords.keys():
            similarity = self._get_text_similarity(text, topic)
            if similarity > similarity_threshold:
                topic_similarities[topic] = similarity
        
        # Sort topics by similarity score
        sorted_topics = sorted(topic_similarities.items(), key=lambda x: x[1], reverse=True)
        found_topics = [topic for topic, score in sorted_topics]
        
        return found_topics

def flag_urgent(text: str) -> bool:
    urgent_keywords = [
        "wrong drug", "bleeding", "dying", "emergency",
        "critical", "injury", "pain", "severe", "unconscious", "collapsed"
    ]
    return any(word in text for word in urgent_keywords)

class FeedbackAnalyzer:
    def __init__(self):
        self.topic_analyzer = TopicAnalyzer()

    def analyze_feedback(self, text: Optional[str] = None, rating: Optional[int] = None) -> dict:
        # Case 1: No input at all
        if not text and rating is None:
            return {"error": "No input text or rating provided."}

        result = {}
        clean_text = preprocess(text) if text else ""

        # Case 2: Use NLP sentiment if text is given (regardless of rating)
        if text and clean_text.strip():  # ensure text is not just spaces
            nlp_sentiment = get_sentiment_from_text(clean_text)
            result["sentiment"] = nlp_sentiment
            
        # Case 3: If no text (or just empty spaces), fallback to rating sentiment
        elif rating is not None:
            rating_sentiment = get_sentiment_from_rating(rating)
            result["sentiment"] = rating_sentiment
        
        # Case 4: Topics are analyzed for all text feedback, with confidence scores
        if text and clean_text.strip():
            topics = self.topic_analyzer.extract_topics(clean_text)
            result["topics"] = topics if topics else 'Unidentified'
            result["urgent_flag"] = flag_urgent(clean_text)

        return result

# Create a global instance for backward compatibility
feedback_analyzer = FeedbackAnalyzer()

def analyze_feedback(text: Optional[str] = None, rating: Optional[int] = None) -> dict:
    """
    Backward compatibility function that maintains the original API
    """
    return feedback_analyzer.analyze_feedback(text=text, rating=rating)
```

#### 3. Transcription and Translation Services
```python
# Located in: app/services/transcription_translation.py

# --- Service API ---
from app.services.transcription import transcribe_audio
from app.services.translation import translate_text

def transcribe_and_translate(audio_data: bytes) -> dict:
    """Transcribe audio and translate French to English, leave English as is."""
    transcription = transcribe_audio(audio_data)
    original_text = transcription["text"]
    detected_language = transcription["language"]
    confidence = transcription["confidence"]
    translations = {}
    if detected_language == "fr":
        translations["en"] = translate_text(original_text, "fr", "en")
    elif detected_language == "en":
        translations["en"] = original_text
    else:
        translations[detected_language] = original_text
    return {
        "original_text": original_text,
        "detected_language": detected_language,
        "confidence": confidence,
        "translations": translations
    }
```

#### 4. Feedback API Endpoints
```python
# Located in: app/api/feedback.py

from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Feedback as FeedbackModel
from app.schemas.feedback import Feedback, FeedbackCreate
from app.services.analysis import analyze_feedback
from app.services.transcription_translation import transcribe_and_translate

import os
from fastapi import UploadFile
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "upload")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

# 1. Text-only feedback endpoint
@router.post("/feedback/", response_model=Feedback)
async def create_feedback(
    patient_id: str = Form(...),
    rating: int = Form(None),
    feedback_text: str = Form(...),
    language: str = Form(...),
    db: Session = Depends(get_db)
):
    lang = language.lower()
    if lang in ["en", "eng", "english"]:
        detected_language = "en"
        translated_text = feedback_text
    elif lang in ["fr", "fra", "french"]:
        from app.services.translation import translate_text
        detected_language = "fr"
        translated_text = translate_text(feedback_text, "fr", "en")
    else:
        detected_language = lang
        translated_text = feedback_text

    analysis = analyze_feedback(text=translated_text, rating=rating)
    sentiment = analysis.get("sentiment")
    topic = analysis.get("topics") if analysis.get("sentiment") == "negative" else None
    urgency = "urgent" if analysis.get("urgent_flag") else "not urgent"
    db_feedback = FeedbackModel(
        patient_id=patient_id,
        rating=rating,
        feedback_text=feedback_text,
        translated_text=translated_text,
        language=detected_language,
        sentiment=sentiment,
        topic=topic,
        urgency=urgency
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

# 2. Audio feedback endpoint
@router.post("/feedback/audio/", response_model=Feedback)
async def create_audio_feedback(
    patient_id: str = Form(...),
    rating: int = Form(None),
    language: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save uploaded audio file
    file_location = os.path.join(UPLOAD_DIR, f"{patient_id}_{audio.filename}")
    with open(file_location, "wb") as f:
        content = await audio.read()
        f.write(content)

    # Read file for transcription
    with open(file_location, "rb") as f:
        audio_bytes = f.read()

    result = transcribe_and_translate(audio_bytes)
    feedback_text = result["original_text"]
    detected_language = result["detected_language"]
    translated_text = result["translations"].get("en", feedback_text)

    # Set rating to 0 if None
    if rating is None:
        rating = 0

    analysis = analyze_feedback(text=translated_text, rating=rating)
    sentiment = analysis.get("sentiment")
    topic = analysis.get("topics") if analysis.get("sentiment") == "negative" else None
    urgency = "urgent" if analysis.get("urgent_flag") else "not urgent"
    db_feedback = FeedbackModel(
        patient_id=patient_id,
        rating=rating,
        feedback_text=feedback_text,
        translated_text=translated_text,
        language=detected_language,
        sentiment=sentiment,
        topic=topic,
        urgency=urgency
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("/feedback/{feedback_id}", response_model=Feedback)
def read_feedback(feedback_id: str, db: Session = Depends(get_db)):
    feedback = db.query(FeedbackModel).filter(FeedbackModel.feedback_id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

@router.get("/feedback/", response_model=list[Feedback])
def list_feedback(db: Session = Depends(get_db)):
    return db.query(FeedbackModel).all()

@router.delete("/feedback/{feedback_id}")
def delete_feedback(feedback_id: str, db: Session = Depends(get_db)):
    feedback = db.query(FeedbackModel).filter(FeedbackModel.feedback_id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    db.delete(feedback)
    db.commit()
    return {"ok": True}
```

## Database Schema

### Database Models
```python
# Located in: app/models/models.py

from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.database import Base

class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(200))
    phone_number = Column(String(20))
    email = Column(String(255))
    preferred_language = Column(String(10))
    created_at = Column(TIMESTAMP)
    password_hash = Column(String(255))

class Feedback(Base):
    __tablename__ = "feedback"
    feedback_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id"))
    feedback_text = Column(Text)
    translated_text = Column(Text)
    rating = Column(Integer)
    sentiment = Column(String(20))
    topic = Column(String(50), nullable=True)
    urgency = Column(String(10), nullable=True)
    language = Column(String(10))
    created_at = Column(TIMESTAMP)

class Reminder(Base):
    __tablename__ = "reminders"
    reminder_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id"))
    title = Column(String(200))
    message = Column(Text)
    scheduled_time = Column(ARRAY(TIMESTAMP))
    days = Column(ARRAY(String(20)))
    status = Column(String(20))
    created_at = Column(TIMESTAMP)

class ReminderDelivery(Base):
    __tablename__ = "reminder_delivery"
    delivery_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reminder_id = Column(UUID(as_uuid=True), ForeignKey("reminders.reminder_id"))
    sent_at = Column(TIMESTAMP)
    delivery_status = Column(String(20))
    provider_response = Column(Text)
```

### Database Configuration
```python
# Located in: app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

load_dotenv()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Database Migrations
The system uses Alembic for database migrations:

```ini
# Located in: alembic.ini (key configuration)

[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql://feedback_reminder_database_9h4d_user:peNEi6symiAQ5TUpjqAI5t2PfGQvp3MJ@dpg-d1sibmbe5dus73b2k67g-a.oregon-postgres.render.com/feedback_reminder_database_9h4d
```

Migration files in `alembic/versions/`:
- `2e3440831511_update_reminders_table_for_multiple_.py`
- `cb834569503b_add_title_column_to_reminders.py`
- `cf2aa9130cdb_add_title_column_to_reminders_table.py`

## API Endpoints

### Authentication Endpoints

#### 1. **POST /api/signup**
- **Purpose**: Register a new patient account
- **Authentication**: None required
- **Request Body**:
  ```json
  {
    "full_name": "John Doe",
    "phone_number": "+237123456789",
    "email": "john.doe@example.com",
    "preferred_language": "en",
    "password": "SecurePass123"
  }
  ```
- **Response**: Patient object (excluding password)
- **Status Codes**: 201 (Created), 400 (Duplicate), 422 (Validation Error)

#### 2. **POST /api/login**
- **Purpose**: Authenticate patient and receive access tokens
- **Authentication**: None required
- **Request Body**:
  ```json
  {
    "phone_number": "+237123456789",
    "password": "SecurePass123"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "patient": {
      "patient_id": "123e4567-e89b-12d3-a456-426614174000",
      "full_name": "John Doe",
      "phone_number": "+237123456789",
      "email": "john.doe@example.com",
      "preferred_language": "en"
    }
  }
  ```
- **Status Codes**: 200 (Success), 401 (Invalid credentials)

#### 3. **POST /api/refresh**
- **Purpose**: Get new access token using refresh token
- **Authentication**: None required
- **Request Body**:
  ```json
  {
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
  ```
- **Status Codes**: 200 (Success), 401 (Invalid token)

### Patient Management Endpoints

#### 4. **GET /api/me**
- **Purpose**: Get patient profile by ID (query parameter)
- **Authentication**: None required
- **Query Parameters**: `patient_id` (UUID)
- **Response**: Patient object
- **Status Codes**: 200 (Success), 404 (Not found)

#### 5. **GET /api/patient/{patient_id}**
- **Purpose**: Get specific patient by ID (path parameter)
- **Authentication**: None required
- **Path Parameters**: `patient_id` (UUID)
- **Response**: Patient object
- **Status Codes**: 200 (Success), 404 (Not found)

#### 6. **GET /api/patient/**
- **Purpose**: List all patients with pagination
- **Authentication**: None required
- **Query Parameters**: 
  - `limit` (1-1000, default: 100)
  - `offset` (default: 0)
- **Response**: Array of Patient objects
- **Status Codes**: 200 (Success)

#### 7. **DELETE /api/patient/{patient_id}**
- **Purpose**: Permanently delete patient account
- **Authentication**: None required
- **Path Parameters**: `patient_id` (UUID)
- **Response**: Success confirmation
- **Status Codes**: 200 (Success), 404 (Not found)

### Feedback Endpoints

#### 8. **POST /api/feedback/**
- **Purpose**: Submit text feedback
- **Authentication**: None required
- **Request Body** (Form Data):
  - `patient_id` (string, required)
  - `rating` (integer, optional)
  - `feedback_text` (string, required)
  - `language` (string, required)
- **Response**: Feedback object with analysis results
- **Status Codes**: 200 (Success), 422 (Validation Error)

#### 9. **POST /api/feedback/audio/**
- **Purpose**: Submit audio feedback
- **Authentication**: None required
- **Request Body** (Form Data):
  - `patient_id` (string, required)
  - `rating` (integer, optional)
  - `language` (string, required)
  - `audio` (file, required)
- **Response**: Feedback object with transcription and analysis
- **Status Codes**: 200 (Success), 422 (Validation Error)

#### 10. **GET /api/feedback/{feedback_id}**
- **Purpose**: Get specific feedback by ID
- **Authentication**: None required
- **Path Parameters**: `feedback_id` (UUID)
- **Response**: Feedback object
- **Status Codes**: 200 (Success), 404 (Not found)

#### 11. **GET /api/feedback/**
- **Purpose**: List all feedback
- **Authentication**: None required
- **Response**: Array of Feedback objects
- **Status Codes**: 200 (Success)

#### 12. **DELETE /api/feedback/{feedback_id}**
- **Purpose**: Delete feedback
- **Authentication**: None required
- **Path Parameters**: `feedback_id` (UUID)
- **Response**: Success confirmation
- **Status Codes**: 200 (Success), 404 (Not found)

## Application Configuration

### Main Application Setup
```python
# Located in: app/main.py

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.api import feedback, reminder, patient, dashboard
from app.db.database import Base, engine
from app.services.sms_service import sms_service
from app.services.reminder_scheduler import reminder_scheduler
import time
import os
import asyncio

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create tables
logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)
logger.info("Database tables created.")

app = FastAPI(
    title="CareChat API",
    description="API for patient reminders and feedback system with SMS notifications.",
    version="1.0.0"
)

# SMS Service startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    logger.info("🚀 Starting CareChat API...")
    
    # Check SMS service configuration
    if sms_service.is_configured():
        logger.info("✅ SMS service configured successfully")
        logger.info(f"   Twilio Account: {sms_service.account_sid[:10]}...")
        logger.info(f"   Twilio Number: {sms_service.twilio_number}")
    else:
        logger.warning("⚠️  SMS service not configured - check environment variables")
        logger.warning("   Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER, MY_NUMBER")
    
    # Note: Scheduler is started manually via API endpoint for better control
    logger.info("📅 Reminder scheduler ready (start via /api/reminder/start-scheduler)")
    logger.info("🎉 CareChat API startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 Shutting down CareChat API...")
    
    # Stop reminder scheduler if running
    if reminder_scheduler.is_running:
        reminder_scheduler.stop_scheduler()
        logger.info("📅 Reminder scheduler stopped")
    
    logger.info("👋 CareChat API shutdown complete!")

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url}")
    try:
        request_body = await request.json()
        logger.info(f"Request Body: {request_body}")
    except Exception:
        logger.info("Request Body: (No JSON body or unable to parse)")

    # Process the request
    response = await call_next(request)
    
    # Log response details
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Response Status: {response.status_code}")
    logger.info(f"Response Time: {process_time:.2f}ms")
    
    return response

@app.get("/")
def root():
    return {
        "message": "Welcome to CareChat API! Available services: Feedback, Reminder."
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(reminder.router, prefix="/api", tags=["Reminder"])
app.include_router(patient.router, prefix="/api", tags=["Patient"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
```

### Configuration Settings
```python
# Located in: app/core/config.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    CORS_ORIGINS: list = ["*"]

settings = Settings()
```

### Dependencies
```text
# Located in: requirements.txt

pydub
openai-whisper
torch
deep-translator

# FastAPI backend
fastapi
uvicorn

# Database
sqlalchemy
psycopg2-binary

# Pydantic for schema validation
pydantic
pydantic[email]

# Translation service
textblob

# NLP and ML for advanced analysis
spacy
scikit-learn

# Other utilities
python-dotenv

# Pydantic settings
pydantic-settings

# FastAPI form data support
python-multipart

# Twilio SMS/voice integration
twilio

# Authentication & Security
python-jose
passlib
bcrypt

# Database Migrations
alembic

numpy
```

## Security Considerations

### 1. Password Security
- **Hashing**: Uses bcrypt with salt for password hashing
- **Minimum Length**: Enforces minimum 6-character password requirement
- **Storage**: Passwords are never stored in plain text

### 2. JWT Token Security
- **Dual Token System**: Separate access and refresh tokens
- **Short-lived Access Tokens**: 30-minute expiration reduces exposure
- **Token Type Validation**: Verifies token type (access vs refresh)
- **Secret Key Management**: Uses environment variables for secret keys

### 3. API Security
- **CORS Configuration**: Configurable CORS origins
- **Input Validation**: Pydantic schemas validate all input data
- **Error Handling**: Secure error messages that don't leak sensitive information

### 4. Database Security
- **Environment Variables**: Database credentials stored in environment variables
- **UUID Primary Keys**: Uses UUIDs instead of sequential IDs
- **Input Sanitization**: SQLAlchemy ORM prevents SQL injection

## Deployment and Operations

### 1. Database Migrations
```bash
# Generate new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### 2. Environment Variables Required
```env
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=your-secret-key
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_NUMBER=your-twilio-number
MY_NUMBER=your-phone-number
```

### 3. Application Startup
```bash
# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or use the provided script
./start.sh
```

## Monitoring and Logging

The application includes comprehensive logging:
- **Request/Response Logging**: All HTTP requests and responses
- **Authentication Events**: Login attempts, token operations
- **Error Logging**: Detailed error information with context
- **Performance Monitoring**: Request processing times

Logs are stored in the `logs/` directory and include:
- Request details (method, URL, body)
- Response status codes and processing times
- Authentication events and errors
- Service initialization and shutdown events

This documentation provides a complete overview of the authentication, account creation, and feedback systems implemented in the CareChat Backend. The system is designed with security, scalability, and maintainability in mind, supporting multilingual operations and advanced feedback analysis capabilities.

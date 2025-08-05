

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Patient as PatientModel
from app.schemas.patient import (
    Patient, PatientCreate, PatientLogin, LoginResponse, 
    TokenResponse, RefreshTokenRequest
)
from app.services.patient_service import PatientService
from uuid import UUID
from typing import List

router = APIRouter()

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

@router.post("/refresh", 
             response_model=TokenResponse,
             summary="Refresh access token",
             description="Get a new access token using a valid refresh token")
def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Get a new access token using a valid refresh token.
    
    **Usage:**
    When your access token expires, use this endpoint to get a new one
    without requiring the patient to log in again.
    
    **Example request:**
    ```json
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    
    **Example response:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 1800
    }
    ```
    
    **Errors:**
    - 401: Invalid or expired refresh token
    - 401: Patient not found
    """
    return PatientService.refresh_access_token(db, refresh_data.refresh_token)

'''@router.post("/patient/", response_model=Patient)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(patient.password)
    patient_data = patient.model_dump()
    patient_data.pop("password")
    db_patient = PatientModel(**patient_data, password_hash=hashed_password)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient'''

@router.get("/me", 
            response_model=Patient,
            summary="Get patient profile by ID",
            description="Get patient profile by providing patient ID in query parameter")
def get_my_profile(
    patient_id: UUID = Query(..., description="Patient ID to get profile for"),
    db: Session = Depends(get_db)
):
    """
    Get a patient profile by ID.
    
    **Query Parameters:**
    - patient_id: UUID of the patient
    
    **Open Access:** No authentication required
    
    **Example:**
    ```
    GET /api/me?patient_id=123e4567-e89b-12d3-a456-426614174000
    ```
    
    **Returns:** Complete patient profile information
    
    **Use Case:** Get patient info for displaying in mobile app profile screen
    
    **Errors:**
    - 404: Patient not found
    """
    patient = db.query(PatientModel).filter(PatientModel.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.get("/patient/{patient_id}", 
            response_model=Patient,
            summary="Get patient by ID",
            description="Get a specific patient by their ID - Open access")
def read_patient(patient_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific patient by their ID.
    
    **Path Parameters:**
    - patient_id: UUID of the patient
    
    **Open Access:** No authentication required
    
    **Example:**
    ```
    GET /api/patient/123e4567-e89b-12d3-a456-426614174000
    ```
    
    **Returns:** Complete patient profile information
    
    **Errors:**
    - 404: Patient not found
    """
    patient = db.query(PatientModel).filter(PatientModel.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.get("/patient/", 
            response_model=List[Patient],
            summary="List all patients",
            description="Get a list of all patients - Open access")
def list_patients(
    limit: int = Query(100, description="Maximum number of patients to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of patients to skip", ge=0),
    db: Session = Depends(get_db)
):
    """
    Get a list of all patients.
    
    **Query Parameters:**
    - limit: Maximum number of patients to return (1-1000, default: 100)
    - offset: Number of patients to skip for pagination (default: 0)
    
    **Open Access:** No authentication required
    
    **Examples:**
    ```
    GET /api/patient/                    # Get first 100 patients
    GET /api/patient/?limit=50&offset=100 # Get patients 101-150
    ```
    
    **Returns:** List of all patients with pagination support
    """
    return db.query(PatientModel).offset(offset).limit(limit).all()

@router.delete("/patient/{patient_id}",
               summary="Delete patient account",
               description="Permanently delete a patient account - Open access")
def delete_patient(patient_id: UUID, db: Session = Depends(get_db)):
    """
    Permanently delete a patient account.
    
    **Path Parameters:**
    - patient_id: UUID of the patient to delete
    
    **Open Access:** No authentication required
    
    **⚠️ Warning:** This action is permanent and cannot be undone.
    
    **Example:**
    ```
    DELETE /api/patient/123e4567-e89b-12d3-a456-426614174000
    ```
    
    **Returns:** Success confirmation message
    
    **Errors:**
    - 404: Patient not found
    """
    patient = db.query(PatientModel).filter(PatientModel.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db.delete(patient)
    db.commit()
    return {"message": "Patient account deleted successfully"}



# -------------------- Imports --------------------
from fastapi import APIRouter, Depends, HTTPException, status, Body, Form
from app.schemas.patient import Patient, PatientCreate, PatientLogin
import os
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Patient as PatientModel
from app.schemas.patient import Patient, PatientCreate
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt

# -------------------- Config & Setup --------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "refreshsecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
router = APIRouter()

# -------------------- Utility Functions --------------------
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

# -------------------- Endpoints --------------------
@router.post("/signup", response_model=Patient, status_code=status.HTTP_201_CREATED)
def signup(patient: PatientCreate, db: Session = Depends(get_db)):
    existing = db.query(PatientModel).filter(
        (PatientModel.email == patient.email) | (PatientModel.phone_number == patient.phone_number)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient already exists")
    hashed_password = get_password_hash(patient.password)
    db_patient = PatientModel(
        first_name=patient.first_name,
        last_name=patient.last_name,
        phone_number=patient.phone_number,
        email=patient.email,
        preferred_language=patient.preferred_language,
        password_hash=hashed_password
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.post("/login")
def login(login_data: PatientLogin, db: Session = Depends(get_db)):
    patient = db.query(PatientModel).filter(PatientModel.phone_number == login_data.mobile_number).first()
    if not patient or not verify_password(login_data.password, patient.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(patient.patient_id)})
    refresh_token = create_refresh_token({"sub": str(patient.patient_id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(refresh_token: str = Form(...)):
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        patient_id = payload.get("sub")
        if patient_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        new_access_token = create_access_token({"sub": patient_id})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

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

@router.get("/patient/{patient_id}", response_model=Patient)
def read_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(PatientModel).filter(PatientModel.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.get("/patient/", response_model=list[Patient])
def list_patients(db: Session = Depends(get_db)):
    return db.query(PatientModel).all()

@router.patch("/patient/{patient_id}", response_model=Patient)
def partial_update_patient(patient_id: str, patient_update: dict = Body(...), db: Session = Depends(get_db)):
    patient = db.query(PatientModel).filter(PatientModel.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in patient_update.items():
        if hasattr(patient, key):
            setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/patient/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(PatientModel).filter(PatientModel.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return {"ok": True}

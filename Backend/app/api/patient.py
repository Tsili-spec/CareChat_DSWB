from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Patient as PatientModel
from app.schemas.patient import Patient, PatientCreate
from fastapi import Body

router = APIRouter()

@router.post("/patient/", response_model=Patient)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = PatientModel(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

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

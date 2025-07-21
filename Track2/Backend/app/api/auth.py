from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.jwt_auth import create_access_token
from passlib.context import CryptContext
from datetime import timedelta

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"sub": db_user.email}, expires_delta=timedelta(minutes=30))
    refresh_token = create_access_token({"sub": db_user.email}, expires_delta=timedelta(days=7))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "phone_number": db_user.phone_number
        }
    }

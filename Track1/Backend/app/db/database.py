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

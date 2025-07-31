from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.database import Base

class BloodCollection(Base):
    """Blood donation/collection records"""
    __tablename__ = "blood_collections"
    
    # Primary key - UUID as specified
    donation_record_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Donor information
    donor_age = Column(Integer, nullable=False)
    donor_gender = Column(String(1), nullable=False)  # M/F
    donor_occupation = Column(String(100))
    
    # Blood information - using blood_type as specified
    blood_type = Column(String(10), nullable=False, index=True)  # A+, A-, B+, B-, AB+, AB-, O+, O-
    collection_site = Column(String(200), nullable=False)
    
    # Collection details - changed to Date only (no time)
    donation_date = Column(Date, nullable=False, index=True)
    expiry_date = Column(Date, nullable=False)
    collection_volume_ml = Column(Float, nullable=False)
    hemoglobin_g_dl = Column(Float, nullable=False)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    
    # Audit timestamps (keep datetime for audit purposes)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    stock_entries = relationship("BloodStock", back_populates="collection")
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<BloodCollection(id={self.donation_record_id}, blood_type={self.blood_type}, volume={self.collection_volume_ml}ml)>"

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.database import Base

class BloodStock(Base):
    """Blood stock tracking with audit trail - Total volume table"""
    __tablename__ = "blood_stock"
    
    # Primary key - UUID as specified (only one primary key needed)
    stock_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Blood information
    blood_group = Column(String(10), nullable=False, index=True)  # A+, A-, B+, B-, AB+, AB-, O+, O-
    volume_in_stock = Column(Float, nullable=False)  # current total volume available
    
    # Time - timestamp for this stock record
    time = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    
    # Foreign keys to track source/destination (nullable as specified)
    donation_record_id = Column(UUID(as_uuid=True), ForeignKey('blood_collections.donation_record_id'), nullable=True)
    usage_record_id = Column(UUID(as_uuid=True), ForeignKey('blood_usage.usage_id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    collection = relationship("BloodCollection", back_populates="stock_entries")
    usage = relationship("BloodUsage", back_populates="stock_entries")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_blood_stock_blood_group_time', 'blood_group', 'time'),
        Index('idx_blood_stock_donation_ref', 'donation_record_id'),
        Index('idx_blood_stock_usage_ref', 'usage_record_id'),
    )
    
    def __repr__(self):
        return f"<BloodStock(id={self.stock_id}, blood_group={self.blood_group}, volume={self.volume_in_stock}ml)>"

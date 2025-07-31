import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base
from app.core.security import SecurityUtils
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    hashed_password = Column(String(100), nullable=False)
    
    # Role-based access control
    role = Column(String(50), default="staff")  # admin, manager, staff, viewer
    department = Column(String(100))  # Blood Bank, Laboratory, Clinical
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # Permissions
    can_manage_inventory = Column(Boolean, default=False)
    can_view_forecasts = Column(Boolean, default=True)
    can_manage_donors = Column(Boolean, default=False)
    can_access_reports = Column(Boolean, default=True)
    can_manage_users = Column(Boolean, default=False)
    can_view_analytics = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    
    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"
    
    def verify_password(self, password: str) -> bool:
        """Verify user password against stored hash"""
        return SecurityUtils.verify_password(password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Generate password hash using bcrypt"""
        return SecurityUtils.hash_password(password)
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == "admin"
    
    @property
    def is_manager(self) -> bool:
        """Check if user has manager or admin role"""
        return self.role in ["admin", "manager"]
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if self.is_admin:
            return True
        return getattr(self, permission, False)
    
    def can_access_department(self, department: str) -> bool:
        """Check if user can access specific department"""
        if self.is_admin:
            return True
        return self.department == department or self.department is None

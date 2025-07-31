#!/usr/bin/env python3
"""
Database initialization script for Blood Bank Management System
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import Base, engine, SessionLocal
from app.models.user import User
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        return False

def create_admin_user():
    """Create default admin user"""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if admin_user:
            logger.info("ℹ️ Admin user already exists")
            return True
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@bloodbank.com",
            full_name="System Administrator",
            hashed_password=User.hash_password("Admin123!"),
            role="admin",
            department="Administration",
            is_active=True,
            is_verified=True,
            can_manage_inventory=True,
            can_view_forecasts=True,
            can_manage_donors=True,
            can_access_reports=True,
            can_manage_users=True,
            can_view_analytics=True,
            employee_id="ADMIN001",
            position="System Administrator"
        )
        
        db.add(admin)
        db.commit()
        
        logger.info("✅ Admin user created successfully")
        logger.info("📧 Username: admin")
        logger.info("🔑 Password: Admin123!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def create_sample_users():
    """Create sample users for testing"""
    db = SessionLocal()
    try:
        sample_users = [
            {
                "username": "manager1",
                "email": "manager@bloodbank.com",
                "full_name": "Blood Bank Manager",
                "password": "Manager123!",
                "role": "manager",
                "department": "Blood Bank",
                "employee_id": "MGR001",
                "position": "Blood Bank Manager",
                "can_manage_inventory": True,
                "can_manage_donors": True,
            },
            {
                "username": "staff1",
                "email": "staff@bloodbank.com",
                "full_name": "Blood Bank Staff",
                "password": "Staff123!",
                "role": "staff",
                "department": "Blood Bank",
                "employee_id": "STF001",
                "position": "Laboratory Technician",
                "can_manage_inventory": False,
                "can_manage_donors": True,
            },
            {
                "username": "viewer1",
                "email": "viewer@bloodbank.com",
                "full_name": "Report Viewer",
                "password": "Viewer123!",
                "role": "viewer",
                "department": "Clinical",
                "employee_id": "VWR001",
                "position": "Clinical Coordinator",
                "can_manage_inventory": False,
                "can_manage_donors": False,
            }
        ]
        
        created_count = 0
        
        for user_data in sample_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            
            if existing_user:
                logger.info(f"ℹ️ User {user_data['username']} already exists")
                continue
            
            # Create user
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=User.hash_password(user_data["password"]),
                role=user_data["role"],
                department=user_data["department"],
                employee_id=user_data["employee_id"],
                position=user_data["position"],
                is_active=True,
                is_verified=True,
                can_manage_inventory=user_data.get("can_manage_inventory", False),
                can_view_forecasts=True,
                can_manage_donors=user_data.get("can_manage_donors", False),
                can_access_reports=True,
                can_manage_users=False,
                can_view_analytics=True
            )
            
            db.add(user)
            created_count += 1
        
        db.commit()
        
        if created_count > 0:
            logger.info(f"✅ Created {created_count} sample users")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating sample users: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main initialization function"""
    logger.info("🚀 Initializing Blood Bank Management System Database...")
    
    # Create tables
    if not create_tables():
        logger.error("❌ Failed to create database tables")
        sys.exit(1)
    
    # Create admin user
    if not create_admin_user():
        logger.error("❌ Failed to create admin user")
        sys.exit(1)
    
    # Create sample users
    if not create_sample_users():
        logger.error("❌ Failed to create sample users")
        sys.exit(1)
    
    logger.info("✅ Database initialization completed successfully!")
    logger.info("🌐 You can now start the server with: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()

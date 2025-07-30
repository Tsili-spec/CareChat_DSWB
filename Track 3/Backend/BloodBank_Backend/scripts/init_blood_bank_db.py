#!/usr/bin/env python3
"""
Blood Bank Database Schema Initialization
Creates tables and sets up initial data for blood bank management system
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import subprocess
import sys

# Install required packages if not installed
try:
    from sqlalchemy import create_engine, text
except ImportError:
    print("Installing SQLAlchemy...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlalchemy", "psycopg2-binary"])
    from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.database import Base
from app.models.user import User
from app.models.blood_donation import BloodDonation
from app.models.blood_usage import BloodUsage
from app.models.blood_inventory import BloodInventory, BloodInventoryTransaction
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_blood_bank_tables():
    """
    Initialize blood bank database tables
    """
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        logger.info("🩸 Initializing Blood Bank Management System Database Schema...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Blood bank database tables created successfully")
        
        # Initialize blood group inventory records
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            
            for blood_group in blood_groups:
                # Check if inventory record already exists
                existing = db.query(BloodInventory).filter(
                    BloodInventory.blood_group == blood_group
                ).first()
                
                if not existing:
                    inventory = BloodInventory(
                        blood_group=blood_group,
                        current_volume_ml=0.0,
                        current_units=0,
                        minimum_stock_ml=2000.0,  # 2 liters minimum
                        maximum_stock_ml=10000.0,  # 10 liters maximum
                        reorder_point_ml=3000.0,   # 3 liters reorder point
                        storage_temperature_min=2.0,
                        storage_temperature_max=6.0
                    )
                    db.add(inventory)
                    logger.info(f"📊 Created inventory record for blood group {blood_group}")
                else:
                    logger.info(f"ℹ️ Inventory record for {blood_group} already exists")
            
            db.commit()
            logger.info("✅ Blood group inventory records initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing inventory records: {e}")
            db.rollback()
        finally:
            db.close()
        
        logger.info("🎉 Blood Bank Management System database initialization completed!")
        
        # Display system information
        print("\n" + "="*70)
        print("🩸 BLOOD BANK MANAGEMENT SYSTEM - DATABASE INITIALIZED")
        print("="*70)
        print("📋 Database Tables Created:")
        print("   • users - User accounts and authentication")
        print("   • blood_donations - Blood collection records")
        print("   • blood_usage - Blood distribution/usage records")
        print("   • blood_inventory - Current stock levels by blood group")
        print("   • blood_inventory_transactions - Audit trail of stock changes")
        print("\n📊 Blood Group Inventory Initialized:")
        print("   • A+, A-, B+, B-, AB+, AB-, O+, O-")
        print("   • Default thresholds: Min 2L, Reorder 3L, Max 10L")
        print("   • Storage temperature: 2-6°C")
        print("\n🔗 API Endpoints Available:")
        print("   • /api/v1/blood-bank/donations - Donation management")
        print("   • /api/v1/blood-bank/usage - Usage/distribution tracking")
        print("   • /api/v1/blood-bank/inventory - Stock level monitoring")
        print("   • /api/v1/blood-bank/alerts - Low stock & expiry alerts")
        print("   • /api/v1/blood-bank/analytics - Dashboard analytics")
        print("\n🌐 Access Points:")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • System Status: http://localhost:8000/api/v1/blood-bank/system/status")
        print("   • Health Check: http://localhost:8000/health")
        print("\n🔐 Default Admin Credentials:")
        print("   • Username: admin")
        print("   • Password: Admin123!")
        print("="*70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize blood bank database: {e}")
        return False

if __name__ == "__main__":
    success = init_blood_bank_tables()
    if success:
        logger.info("🎯 Blood bank system is ready for operation!")
    else:
        logger.error("💥 Blood bank system initialization failed!")
        sys.exit(1)

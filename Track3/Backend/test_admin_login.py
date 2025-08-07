#!/usr/bin/env python3
"""
Admin Login Test Script for Blood Bank Management System
"""

import sys
import os
from pathlib import Path
import requests
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import get_db
from app.models.user import User

def check_admin_users():
    """Check what admin users exist in the database"""
    print("🔍 Checking admin users in database...")
    db = next(get_db())
    
    admin_users = db.query(User).filter(User.role.in_(['admin', 'manager'])).all()
    print(f"Found {len(admin_users)} admin/manager users:")
    
    for user in admin_users:
        print(f"  - Username: {user.username}")
        print(f"    Role: {user.role}")
        print(f"    Email: {user.email}")
        print(f"    Active: {user.is_active}")
        print(f"    Password hash: {user.hashed_password[:20]}...")
        print()
    
    db.close()
    return admin_users

def test_admin_login(username, password):
    """Test admin login via API"""
    print(f"🔑 Testing admin login for user: {username}")
    
    login_url = "http://localhost:8000/admin/api/login"
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 0:
                print("✅ Login successful!")
                return True
            else:
                print(f"❌ Login failed: {data.get('msg')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_password_verification(username, password):
    """Test password verification directly"""
    print(f"🔐 Testing password verification for user: {username}")
    
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        print(f"❌ User '{username}' not found")
        db.close()
        return False
    
    is_valid = user.verify_password(password)
    print(f"Password verification result: {is_valid}")
    
    db.close()
    return is_valid

def create_admin_user_if_needed():
    """Create default admin user if it doesn't exist"""
    print("👤 Creating default admin user if needed...")
    
    db = next(get_db())
    admin_user = db.query(User).filter(User.username == "admin").first()
    
    if admin_user:
        print("ℹ️ Admin user already exists")
        db.close()
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
        can_view_analytics=True
    )
    
    try:
        db.add(admin)
        db.commit()
        print("✅ Default admin user created successfully")
        print("   Username: admin")
        print("   Password: Admin123!")
        db.close()
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        db.close()
        return False

def main():
    """Main test function"""
    print("🩸 Blood Bank Admin Login Test")
    print("=" * 40)
    
    # Check existing admin users
    admin_users = check_admin_users()
    
    # Create default admin if needed
    create_admin_user_if_needed()
    
    # Test credentials
    test_credentials = [
        ("admin", "Admin123!"),
        ("frank", "Frank123"),  # Correct password for frank
        ("frank", "Admin123!"),
        ("frank", "password"),
        ("frank", "frank123")
    ]
    
    print("\n🧪 Testing login credentials...")
    print("-" * 30)
    
    for username, password in test_credentials:
        print(f"\nTesting: {username} / {password}")
        
        # Test password verification
        password_valid = test_password_verification(username, password)
        
        if password_valid:
            print("✅ Password verification passed")
            # Test API login
            api_login = test_admin_login(username, password)
            if api_login:
                print(f"✅ Admin login successful for {username}")
                break
        else:
            print("❌ Password verification failed")
    
    print("\n📝 Summary:")
    print("- Admin panel URL: http://localhost:8000/admin")
    print("- Try the credentials that passed the tests above")
    
if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.core.security import verify_password

# Test database connection and user lookup
try:
    db = next(get_db())
    
    # Check if user exists
    user = db.query(User).filter(User.username == "testadmin").first()
    if user:
        print(f"User found: {user.username}, user_id: {user.user_id}")
        print(f"User active: {user.is_active}")
        
        # Test password verification
        test_password = "TestPass123!"
        is_valid = verify_password(test_password, user.password_hash)
        print(f"Password valid: {is_valid}")
        
    else:
        print("User not found")
        
    db.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

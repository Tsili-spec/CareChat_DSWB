#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User

try:
    db = next(get_db())
    
    # List all users
    users = db.query(User).all()
    print(f"Total users: {len(users)}")
    
    for user in users:
        print(f"Username: {user.username}, user_id: {user.user_id}, active: {user.is_active}")
        
    db.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

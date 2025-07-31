#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import Settings
from app.core.jwt_auth import JWTManager

# Test settings
settings = Settings()
print(f"JWT_SECRET_KEY: {settings.JWT_SECRET_KEY}")
print(f"JWT_REFRESH_SECRET_KEY: {settings.JWT_REFRESH_SECRET_KEY}")
print(f"DATABASE_URL: {settings.DATABASE_URL}")

# Test token creation
test_data = {
    "sub": "testuser",
    "user_id": "123e4567-e89b-12d3-a456-426614174000"
}

try:
    access_token = JWTManager.create_access_token(test_data)
    print(f"Access token created successfully: {access_token[:50]}...")
    
    refresh_token = JWTManager.create_refresh_token(test_data)
    print(f"Refresh token created successfully: {refresh_token[:50]}...")
    
    # Test token verification
    decoded = JWTManager.verify_token(access_token)
    print(f"Token verification successful: {decoded}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

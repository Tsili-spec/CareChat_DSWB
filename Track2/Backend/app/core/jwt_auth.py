# JWT Authentication setup
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional, Dict, Any

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "refreshsecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[Dict[Any, Any]]:
    try:
        secret_key = SECRET_KEY if token_type == "access" else REFRESH_SECRET_KEY
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None

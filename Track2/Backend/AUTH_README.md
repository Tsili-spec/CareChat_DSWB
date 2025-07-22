# CareChat Authentication API Documentation

## Overview
The CareChat authentication system provides comprehensive JWT-based authentication with signup, login, token refresh, and protected endpoint access using phone numbers as the primary identifier.

## API Endpoints

### 1. Patient Signup
**POST** `/signup`

Register a new patient account using phone number as unique identifier.

**Request Body:**
```json
{
    "full_name": "John Doe",
    "phone_number": "+237123456789",
    "email": "john.doe@example.com",
    "preferred_language": "en",
    "password": "SecurePass123"
}
```

**Response (201):**
```json
{
    "patient_id": "123e4567-e89b-12d3-a456-426614174000",
    "full_name": "John Doe",
    "phone_number": "+237123456789",
    "email": "john.doe@example.com",
    "preferred_language": "en"
}
```

### 2. Patient Login
**POST** `/login`

Authenticate a patient and receive JWT tokens.

**Request Body:**
```json
{
    "phone_number": "+237123456789",
    "password": "SecurePass123"
}
```

**Response (200):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "patient": {
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "full_name": "John Doe",
        "phone_number": "+237123456789",
        "email": "john.doe@example.com",
        "preferred_language": "en"
    }
}
```

### 3. Token Refresh
**POST** `/refresh`

Generate a new access token using a refresh token.

**Request Body:**
```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### 4. Get Current Patient Profile
**GET** `/me`

Get the authenticated patient's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
    "patient_id": "123e4567-e89b-12d3-a456-426614174000",
    "full_name": "John Doe",
    "phone_number": "+237123456789",
    "email": "john.doe@example.com",
    "preferred_language": "en"
}
```

## Protected Endpoints Examples

### Required Authentication
**GET** `/protected/profile`

Requires valid access token in Authorization header.

### Optional Authentication
**GET** `/protected/optional-auth`

Works with or without authentication, providing different responses.

## Security Features

### Token System
- **Access Token**: 30-minute expiration, used for API access
- **Refresh Token**: 7-day expiration, used to generate new access tokens
- **Algorithm**: HS256
- **Separate Secret Keys**: Different keys for access and refresh tokens

### Password Security
- **Hashing**: Bcrypt with automatic salt
- **Minimum Length**: 6 characters
- **Secure Verification**: Constant-time comparison

### Validation
- **Phone Number**: 8-20 characters, unique identifier
- **Email**: Optional, validated format, unique if provided
- **Names**: Full name required in single field
- **Language**: Default to "en" if not specified

## Usage Examples

### Python Client Example
```python
import requests

# Signup
signup_data = {
    "full_name": "John Doe", 
    "phone_number": "+237123456789",
    "email": "john@example.com",
    "password": "SecurePass123"
}
response = requests.post("http://localhost:8000/signup", json=signup_data)
patient = response.json()

# Login
login_data = {
    "phone_number": "+237123456789",
    "password": "SecurePass123"
}
login_response = requests.post("http://localhost:8000/login", json=login_data)
tokens = login_response.json()

# Access protected endpoint
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
profile = requests.get("http://localhost:8000/me", headers=headers)

# Refresh token
refresh_data = {"refresh_token": tokens['refresh_token']}
new_token = requests.post("http://localhost:8000/refresh", json=refresh_data)
```

### cURL Examples
```bash
# Signup
curl -X POST "http://localhost:8000/signup" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"John Doe","phone_number":"+237123456789","password":"SecurePass123"}'

# Login
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+237123456789","password":"SecurePass123"}'

# Protected endpoint
curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Error Responses

- **400**: Duplicate phone number/email, validation errors
- **401**: Invalid credentials, expired tokens
- **404**: Patient not found
- **422**: Request validation errors
- **500**: Internal server errors

## Environment Variables

Set these in your `.env` file:
```bash
JWT_SECRET_KEY=your_super_secure_secret_key_here
JWT_REFRESH_SECRET_KEY=your_refresh_secret_key_here
DATABASE_URL=postgresql://user:password@localhost/dbname
```

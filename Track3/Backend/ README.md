# 🩸 Blood Bank Management System - Authentication Documentation

## 🔐 JWT Authentication System Implementation

### 📋 Overview

The Blood Bank Management System implements a comprehensive JWT (JSON Web Token) based authentication system designed for healthcare environments. This system provides secure user management, role-based access control, and robust security features essential for medical data management.
## Deployment
Backend was deployed using render where CI/CD pipeline is done automatically any change triggers a build. link below
link : https://blood-management-system-xplx.onrender.com/docs
Note: server may need to restart when it has been idle for long.
### 🏗️ Authentication Architecture

```
Authentication Flow
├── 🔑 JWT Token Management (HS256 Algorithm)
├── 🛡️ Password Security (Bcrypt Hashing)
├── 👤 User Registration & Login
├── 🔒 Protected Route Middleware
├── 👥 Role-Based Access Control (RBAC)
├── 🚪 Permission-Based Authorization
└── ⏰ Token Expiration & Refresh
```

### 🌳 Project Structure

```
BloodBank_Backend/
├── 📁 app/                          # Core Application Code
│   ├── 📄 __init__.py              # Python package marker
│   ├── 📄 main.py                  # FastAPI application entry point
│   │
│   ├── 📁 api/                     # API Route Handlers
│   │   ├── 📄 __init__.py         # Package marker
│   │   └── 📄 auth.py             # Authentication endpoints
│   │
│   ├── 📁 core/                   # Core Configuration & Utilities
│   │   ├── 📄 __init__.py         # Package marker
│   │   ├── 📄 config.py           # Application settings & environment variables
│   │   ├── 📄 jwt_auth.py         # JWT token management utilities
│   │   ├── 📄 auth.py             # Authentication helper functions
│   │   └── 📄 security.py         # Security utilities and password hashing
│   │
│   ├── 📁 db/                     # Database Configuration
│   │   ├── 📄 __init__.py         # Package marker
│   │   └── 📄 database.py         # SQLAlchemy database connection & session
│   │
│   ├── 📁 models/                 # SQLAlchemy ORM Models
│   │   ├── 📄 __init__.py         # Package marker
│   │   └── 📄 user.py             # User account database model
│   │
│   └── 📁 schemas/                # Pydantic Request/Response Schemas
│       ├── 📄 __init__.py         # Package marker
│       └── 📄 user.py             # User data validation schemas
│
├── 📁 scripts/                   # Utility Scripts
│   ├── 📄 __init__.py            # Package marker
│   └── 📄 init_db.py             # Database initialization script
│
├── 📁 tests/                     # Unit & Integration Tests
│   ├── 📄 __init__.py           # Package marker
│   └── 📄 test_auth.py          # Authentication endpoint tests
│
├── 📄 requirements.txt           # Python package dependencies
├── 📄 .env.example              # Environment template file
└── 📄 README.md                 # This documentation file
```

## 🚀 Quick Start Guide

### 1. **Environment Setup**

#### Create Virtual Environment
```bash
# Create and activate virtual environment
python -m venv bloodbank_env
source bloodbank_env/bin/activate  # On Windows: bloodbank_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configurations
nano .env
```

#### Sample .env Configuration
```env
# Application Settings
DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production-minimum-32-chars

# Database Configuration (Render PostgreSQL)
POSTGRES_SERVER=dpg-d24j80f5r7bs73a68s40-a.oregon-postgres.render.com
POSTGRES_USER=blood_bank_system_user
POSTGRES_PASSWORD=1ztEjzCXwJCwJrndkyGcpcyJ2VM5WosZ
POSTGRES_DB=blood_bank_system
POSTGRES_PORT=5432

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
ALGORITHM=HS256

# CORS Settings
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","http://127.0.0.1:3000"]
```

### 2. **Database Initialization**

```bash
# Initialize database and create default users
python scripts/init_db.py
```

This script will:
- ✅ Create all database tables
- 👤 Create default admin user
- 👥 Create sample users for testing
- 📊 Display login credentials

### 3. **Start the Server**

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. **Access the API**

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 👥 User Roles & Permissions

### 🎭 Role Hierarchy

| Role | Level | Description |
|------|-------|-------------|
| **Admin** | 4 | Full system access, user management |
| **Manager** | 3 | Department management, inventory oversight |
| **Staff** | 2 | Daily operations, data entry |
| **Viewer** | 1 | Read-only access, reports viewing |

### 🔑 Permission Matrix

| Permission | Admin | Manager | Staff | Viewer |
|------------|-------|---------|-------|--------|
| `can_manage_users` | ✅ | ❌ | ❌ | ❌ |
| `can_manage_inventory` | ✅ | ✅ | ❌ | ❌ |
| `can_manage_donors` | ✅ | ✅ | ✅ | ❌ |
| `can_access_reports` | ✅ | ✅ | ✅ | ✅ |
| `can_view_forecasts` | ✅ | ✅ | ✅ | ✅ |
| `can_view_analytics` | ✅ | ✅ | ✅ | ✅ |

> **📖 For comprehensive RBAC documentation including endpoint-specific permissions, access control examples, and implementation details, see [RBAC_GUIDE.md](./RBAC_GUIDE.md)**

## 🔧 Authentication Implementation Details

### 📊 Database Schema

#### User Model (`app/models/user.py`)
```python
class User(Base):
    __tablename__ = "users"
    
    # Primary Fields
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    hashed_password = Column(String(100), nullable=False)
    
    # Role & Department
    role = Column(String(50), default="staff")
    department = Column(String(100))
    
    # Status
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
    
    # Professional Info
    employee_id = Column(String(50), unique=True)
    position = Column(String(100))
    phone = Column(String(20))
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    # Audit
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### 🔐 Security Features

#### 1. **Password Security**
- **Bcrypt Hashing**: Industry-standard password hashing
- **Salt Generation**: Unique salt for each password
- **Password Requirements**: 
  - Minimum 8 characters
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 digit

#### 2. **JWT Token Security**
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: Configurable (default: 7 days)
- **Payload**: User ID, username, expiration
- **Verification**: Automatic token validation on protected routes

#### 3. **Account Security**
- **Failed Login Protection**: Account locks after 5 failed attempts
- **Lockout Duration**: 30 minutes automatic unlock
- **Session Tracking**: Last login timestamp
- **Active Status**: Ability to deactivate accounts

#### 4. **Input Validation**
- **Pydantic Schemas**: Automatic request validation
- **Email Format**: Valid email format enforcement
- **Username Rules**: Alphanumeric, hyphens, underscores only
- **Phone Validation**: Phone number format validation

### 🛡️ Security Dependencies

#### Authentication Middleware (`app/core/auth.py`)
```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extract and validate JWT token, return authenticated user"""
    
def require_role(required_role: str):
    """Dependency factory for role-based access control"""
    
def require_permission(permission: str):
    """Dependency factory for permission-based access control"""
```

## 📡 API Endpoints

### 🔓 Public Endpoints

#### **Register User**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "johnsmith",
  "email": "john.smith@hospital.com",
  "full_name": "John Smith",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "role": "staff",
  "department": "Blood Bank",
  "employee_id": "EMP001",
  "position": "Laboratory Technician"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "johnsmith",
  "email": "john.smith@hospital.com",
  "full_name": "John Smith",
  "role": "staff",
  "department": "Blood Bank",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-01-29T10:30:00.000Z",
  "can_manage_inventory": false,
  "can_view_forecasts": true,
  "can_manage_donors": false,
  "can_access_reports": true,
  "can_manage_users": false,
  "can_view_analytics": true
}
```

#### **Login User**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "johnsmith",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user_id": 1,
  "username": "johnsmith",
  "role": "staff",
  "permissions": {
    "can_manage_inventory": false,
    "can_view_forecasts": true,
    "can_manage_donors": false,
    "can_access_reports": true,
    "can_manage_users": false,
    "can_view_analytics": true
  }
}
```

### 🔒 Protected Endpoints

#### **Get Current User Profile**
```http
GET /api/v1/auth/me
Authorization: Bearer <your_token_here>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johnsmith",
  "email": "john.smith@hospital.com",
  "full_name": "John Smith",
  "role": "staff",
  "department": "Blood Bank",
  "employee_id": "EMP001",
  "position": "Laboratory Technician",
  "phone": "+1234567890",
  "is_active": true,
  "is_verified": false,
  "last_login": "2025-01-29T15:45:00.000Z",
  "created_at": "2025-01-29T10:30:00.000Z",
  "can_manage_inventory": false,
  "can_view_forecasts": true,
  "can_manage_donors": false,
  "can_access_reports": true,
  "can_manage_users": false,
  "can_view_analytics": true
}
```

#### **Update Profile**
```http
PUT /api/v1/auth/me
Authorization: Bearer <your_token_here>
Content-Type: application/json

{
  "full_name": "John H. Smith",
  "phone": "+1234567890",
  "position": "Senior Laboratory Technician"
}
```

#### **Change Password**
```http
POST /api/v1/auth/change-password
Authorization: Bearer <your_token_here>
Content-Type: application/json

{
  "current_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "confirm_new_password": "NewSecurePass456!"
}
```

#### **Refresh Token**
```http
POST /api/v1/auth/refresh
Authorization: Bearer <your_token_here>
```

#### **Logout**
```http
POST /api/v1/auth/logout
Authorization: Bearer <your_token_here>
```

### 👑 Admin-Only Endpoints

#### **List All Users**
```http
GET /api/v1/auth/users?skip=0&limit=50
Authorization: Bearer <admin_token_here>
```

#### **Get User by ID**
```http
GET /api/v1/auth/users/123
Authorization: Bearer <admin_token_here>
```

#### **Update User**
```http
PUT /api/v1/auth/users/123
Authorization: Bearer <admin_token_here>
Content-Type: application/json

{
  "role": "manager",
  "can_manage_inventory": true,
  "is_active": true
}
```

#### **Delete User**
```http
DELETE /api/v1/auth/users/123
Authorization: Bearer <admin_token_here>
```

## 🧪 Testing Guide

### **Run Authentication Tests**
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all authentication tests
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::TestAuthentication::test_register_user_success -v

# Run with coverage
pytest tests/test_auth.py --cov=app --cov-report=html
```

### **Manual Testing with cURL**

#### 1. **Register a Test User**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "TestPass123!",
    "confirm_password": "TestPass123!",
    "role": "staff",
    "department": "Blood Bank"
  }'
```

#### 2. **Login and Get Token**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

#### 3. **Access Protected Endpoint**
```bash
# Replace <token> with actual token from login response
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <token>"
```

#### 4. **Test Protected Route**
```bash
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer <token>"
```

## 🚀 Default Users & Credentials

After running `python scripts/init_db.py`, the following users are created:

### 👑 **Administrator**
- **Username**: `admin`
- **Password**: `Admin123!`
- **Email**: `admin@bloodbank.com`
- **Role**: `admin`
- **Permissions**: All permissions enabled

### 👨‍💼 **Manager**
- **Username**: `manager1`
- **Password**: `Manager123!`
- **Email**: `manager@bloodbank.com`
- **Role**: `manager`
- **Department**: Blood Bank

### 👨‍⚕️ **Staff Member**
- **Username**: `staff1`
- **Password**: `Staff123!`
- **Email**: `staff@bloodbank.com`
- **Role**: `staff`
- **Department**: Blood Bank

### 👁️ **Viewer**
- **Username**: `viewer1`
- **Password**: `Viewer123!`
- **Email**: `viewer@bloodbank.com`
- **Role**: `viewer`
- **Department**: Clinical

## 🔧 Configuration Options

### **JWT Settings**
```python
# app/core/config.py
SECRET_KEY: str = "your-secret-key"           # JWT signing key
ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080      # Token validity (7 days)
ALGORITHM: str = "HS256"                      # JWT algorithm
```

### **Security Settings**
```python
# Account lockout after failed attempts
FAILED_LOGIN_ATTEMPTS_LIMIT: int = 5
LOCKOUT_DURATION_MINUTES: int = 30

# Password requirements
MIN_PASSWORD_LENGTH: int = 8
REQUIRE_UPPERCASE: bool = True
REQUIRE_LOWERCASE: bool = True
REQUIRE_DIGITS: bool = True
```

### **Database Connection**
```python
DATABASE_URL: str = "postgresql://user:pass@host:port/db"
POSTGRES_SERVER: str = "your-postgres-host"
POSTGRES_USER: str = "your-username"
POSTGRES_PASSWORD: str = "your-password"
POSTGRES_DB: str = "your-database"
POSTGRES_PORT: int = 5432
```

## 🚨 Error Handling

### **Common Authentication Errors**

#### **401 Unauthorized**
```json
{
  "detail": "Invalid username or password",
  "status_code": 401
}
```

#### **401 Token Invalid**
```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

#### **403 Forbidden**
```json
{
  "detail": "Access denied. Required role: admin",
  "status_code": 403
}
```

#### **400 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters long",
      "type": "value_error"
    }
  ],
  "status_code": 422
}
```

#### **423 Account Locked**
```json
{
  "detail": "Account is locked. Try again after 2025-01-29 16:30:00",
  "status_code": 401
}
```

## 🔐 Security Best Practices

### **Production Deployment Checklist**

#### 1. **Environment Security**
- [ ] Use strong, unique SECRET_KEY (32+ characters)
- [ ] Set DEBUG=False in production
- [ ] Use HTTPS/TLS for all connections
- [ ] Configure proper CORS origins
- [ ] Use environment variables for sensitive data

#### 2. **Database Security**
- [ ] Use strong database passwords
- [ ] Enable SSL for database connections
- [ ] Regular database backups
- [ ] Limit database user permissions

#### 3. **Application Security**
- [ ] Implement rate limiting
- [ ] Use secure headers (HSTS, CSP)
- [ ] Regular security updates
- [ ] Monitor failed login attempts
- [ ] Implement audit logging

#### 4. **Token Security**
- [ ] Shorter token expiration in production (15-30 minutes)
- [ ] Implement token blacklisting for logout
- [ ] Consider refresh token mechanism
- [ ] Monitor token usage patterns

### **Security Headers Example**
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Force HTTPS in production
if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
    )
```

## 📊 Monitoring & Logging

### **Health Check Endpoint**
```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### **Logging Configuration**
```python
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log authentication events
logger = logging.getLogger(__name__)
logger.info(f"User {username} logged in successfully")
logger.warning(f"Failed login attempt for user {username}")
```

## 🔄 Integration Examples

### **Frontend Integration (JavaScript/React)**

#### **Authentication Service**
```javascript
class AuthService {
  constructor() {
    this.baseURL = 'http://localhost:8000/api/v1';
    this.token = localStorage.getItem('access_token');
  }

  async login(username, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      this.token = data.access_token;
      localStorage.setItem('access_token', this.token);
      localStorage.setItem('user_data', JSON.stringify({
        user_id: data.user_id,
        username: data.username,
        role: data.role,
        permissions: data.permissions
      }));
      return data;
    }
    
    throw new Error('Login failed');
  }

  async makeAuthenticatedRequest(endpoint, options = {}) {
    const defaultOptions = {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      ...defaultOptions,
    });

    if (response.status === 401) {
      this.logout();
      throw new Error('Authentication required');
    }

    return response;
  }

  logout() {
    this.token = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
  }

  isAuthenticated() {
    return !!this.token;
  }

  getUserData() {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }

  hasPermission(permission) {
    const userData = this.getUserData();
    return userData?.permissions?.[permission] || false;
  }

  hasRole(role) {
    const userData = this.getUserData();
    return userData?.role === role;
  }
}

// Usage example
const authService = new AuthService();

// Login
try {
  const loginData = await authService.login('admin', 'Admin123!');
  console.log('Login successful:', loginData);
} catch (error) {
  console.error('Login failed:', error);
}

// Make authenticated request
try {
  const response = await authService.makeAuthenticatedRequest('/auth/me');
  const userData = await response.json();
  console.log('User data:', userData);
} catch (error) {
  console.error('Request failed:', error);
}
```

### **Flutter Integration (Dart)**

#### **Authentication Service**
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  String? _token;

  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
  }

  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
    _token = token;
  }

  Future<Map<String, dynamic>?> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await _saveToken(data['access_token']);
      
      // Save user data
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('user_data', jsonEncode({
        'user_id': data['user_id'],
        'username': data['username'],
        'role': data['role'],
        'permissions': data['permissions'],
      }));
      
      return data;
    }
    
    return null;
  }

  Future<http.Response> makeAuthenticatedRequest(
    String endpoint, {
    String method = 'GET',
    Map<String, dynamic>? body,
  }) async {
    await _loadToken();
    
    final headers = {
      'Authorization': 'Bearer $_token',
      'Content-Type': 'application/json',
    };

    late http.Response response;
    
    switch (method.toUpperCase()) {
      case 'GET':
        response = await http.get(Uri.parse('$baseUrl$endpoint'), headers: headers);
        break;
      case 'POST':
        response = await http.post(
          Uri.parse('$baseUrl$endpoint'),
          headers: headers,
          body: body != null ? jsonEncode(body) : null,
        );
        break;
      case 'PUT':
        response = await http.put(
          Uri.parse('$baseUrl$endpoint'),
          headers: headers,
          body: body != null ? jsonEncode(body) : null,
        );
        break;
      case 'DELETE':
        response = await http.delete(Uri.parse('$baseUrl$endpoint'), headers: headers);
        break;
    }

    if (response.statusCode == 401) {
      await logout();
      throw Exception('Authentication required');
    }

    return response;
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('user_data');
    _token = null;
  }

  Future<bool> isAuthenticated() async {
    await _loadToken();
    return _token != null;
  }

  Future<Map<String, dynamic>?> getUserData() async {
    final prefs = await SharedPreferences.getInstance();
    final userDataString = prefs.getString('user_data');
    return userDataString != null ? jsonDecode(userDataString) : null;
  }

  Future<bool> hasPermission(String permission) async {
    final userData = await getUserData();
    return userData?['permissions']?[permission] ?? false;
  }

  Future<bool> hasRole(String role) async {
    final userData = await getUserData();
    return userData?['role'] == role;
  }
}

// Usage example
class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final AuthService _authService = AuthService();
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  Future<void> _login() async {
    try {
      final loginData = await _authService.login(
        _usernameController.text,
        _passwordController.text,
      );

      if (loginData != null) {
        // Navigate to dashboard
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => DashboardPage()),
        );
      }
    } catch (error) {
      // Show error message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Login failed: $error')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Login')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _usernameController,
              decoration: InputDecoration(labelText: 'Username'),
            ),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(labelText: 'Password'),
              obscureText: true,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _login,
              child: Text('Login'),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 🆘 Troubleshooting

### **Common Issues & Solutions**

#### **1. Database Connection Failed**
```bash
# Check database connection
python -c "
from app.db.database import engine
try:
    engine.connect()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

#### **2. Token Verification Failed**
```bash
# Check token expiration
python -c "
import jwt
from app.core.config import settings

token = 'your_token_here'
try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f'✅ Token valid, expires: {payload.get(\"exp\")}')
except jwt.ExpiredSignatureError:
    print('❌ Token expired')
except jwt.InvalidTokenError:
    print('❌ Token invalid')
"
```

#### **3. Permission Denied Errors**
```bash
# Check user permissions
python -c "
from app.db.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == 'your_username').first()
if user:
    print(f'Role: {user.role}')
    print(f'Can manage inventory: {user.can_manage_inventory}')
    print(f'Can manage users: {user.can_manage_users}')
else:
    print('User not found')
db.close()
"
```

#### **4. Environment Variables Not Loading**
```bash
# Check environment variables
python -c "
from app.core.config import settings
print(f'Database URL: {settings.DATABASE_URL}')
print(f'Secret Key length: {len(settings.SECRET_KEY)}')
print(f'Debug mode: {settings.DEBUG}')
"
```

## 📞 Support & Contact

For questions, issues, or contributions:

- **GitHub Issues**: Create an issue for bugs or feature requests
- **Documentation**: Refer to this README for implementation details
- **Email**: Contact the development team for urgent issues

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**🩸 Blood Bank Management System** - Secure, scalable, and reliable healthcare data management.

*Last updated: January 29, 2025*

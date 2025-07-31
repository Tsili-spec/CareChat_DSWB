import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db, Base
from app.models.user import User
import tempfile
import os

# Create a temporary database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "role": "staff",
        "department": "Blood Bank"
    }

@pytest.fixture
def admin_user_data():
    return {
        "username": "admintest",
        "email": "admin@example.com",
        "full_name": "Admin Test",
        "password": "AdminPass123!",
        "confirm_password": "AdminPass123!",
        "role": "admin",
        "department": "Administration",
        "can_manage_users": True
    }

class TestAuthentication:
    
    def test_register_user_success(self, test_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "hashed_password" not in data  # Password should not be returned
        assert data["is_active"] == True
    
    def test_register_user_duplicate_username(self, test_user_data):
        """Test registration with duplicate username"""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register with same username
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    def test_register_user_duplicate_email(self, test_user_data):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register with same email but different username
        duplicate_email_data = test_user_data.copy()
        duplicate_email_data["username"] = "different_username"
        
        response = client.post("/api/v1/auth/register", json=duplicate_email_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_register_user_invalid_password(self, test_user_data):
        """Test registration with invalid password"""
        invalid_password_data = test_user_data.copy()
        invalid_password_data["password"] = "weak"
        invalid_password_data["confirm_password"] = "weak"
        
        response = client.post("/api/v1/auth/register", json=invalid_password_data)
        
        assert response.status_code == 422
    
    def test_register_user_password_mismatch(self, test_user_data):
        """Test registration with password mismatch"""
        mismatch_data = test_user_data.copy()
        mismatch_data["confirm_password"] = "DifferentPass123!"
        
        response = client.post("/api/v1/auth/register", json=mismatch_data)
        
        assert response.status_code == 422
    
    def test_login_success(self, test_user_data):
        """Test successful login"""
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == test_user_data["username"]
        assert "expires_in" in data
        assert "permissions" in data
    
    def test_login_invalid_username(self):
        """Test login with invalid username"""
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, test_user_data):
        """Test login with invalid password"""
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to login with wrong password
        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_get_current_user_success(self, test_user_data):
        """Test getting current user profile with valid token"""
        # Register and login user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
    
    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_get_current_user_no_token(self):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_protected_route_success(self, test_user_data):
        """Test accessing protected route with valid token"""
        # Register and login user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # Access protected route
        response = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["username"] == test_user_data["username"]
    
    def test_protected_route_unauthorized(self):
        """Test accessing protected route without token"""
        response = client.get("/protected")
        
        assert response.status_code == 401
    
    def test_refresh_token_success(self, test_user_data):
        """Test token refresh with valid token"""
        # Register and login user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == test_user_data["username"]
    
    def test_logout_success(self, test_user_data):
        """Test logout with valid token"""
        # Register and login user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # Logout
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
    
    def test_change_password_success(self, test_user_data):
        """Test password change with valid current password"""
        # Register and login user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # Change password
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewPass123!",
            "confirm_new_password": "NewPass123!"
        }
        
        response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json=password_data
        )
        
        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]
    
    def test_change_password_wrong_current(self, test_user_data):
        """Test password change with wrong current password"""
        # Register and login user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # Try to change password with wrong current password
        password_data = {
            "current_password": "WrongPass123!",
            "new_password": "NewPass123!",
            "confirm_new_password": "NewPass123!"
        }
        
        response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json=password_data
        )
        
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]

class TestAdminEndpoints:
    
    def test_list_users_as_admin(self, admin_user_data):
        """Test listing users as admin"""
        # Register admin user
        client.post("/api/v1/auth/register", json=admin_user_data)
        
        # Login as admin
        login_response = client.post("/api/v1/auth/login", json={
            "username": admin_user_data["username"],
            "password": admin_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # List users
        response = client.get(
            "/api/v1/auth/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_users_as_non_admin(self, test_user_data):
        """Test listing users as non-admin (should fail)"""
        # Register regular user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login as regular user
        login_response = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # Try to list users (should fail)
        response = client.get(
            "/api/v1/auth/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403

# Cleanup
def teardown_module():
    """Clean up test database"""
    if os.path.exists("./test.db"):
        os.remove("./test.db")

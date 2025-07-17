import requests

BASE_URL = "http://127.0.0.1:8000/api"

signup_data = {
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "1234567890",
    "email": "testuser@example.com",
    "preferred_language": "en",
    "password": "TestPassword123"
}

# Test signup
signup_resp = requests.post(f"{BASE_URL}/signup", json=signup_data)
print("Signup response:", signup_resp.status_code, signup_resp.json())

# Test login
login_data = {
    "username": signup_data["email"],
    "password": signup_data["password"]
}
login_resp = requests.post(f"{BASE_URL}/login", data=login_data)
print("Login response:", login_resp.status_code, login_resp.json())

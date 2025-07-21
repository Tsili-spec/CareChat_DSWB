import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_post_feedback_rating_only():
    # Create a dummy patient first
    patient_data = {
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "1234567890",
        "email": "testuser@example.com",
        "preferred_language": "en"
    }
    patient_resp = client.post("/api/patient/", json=patient_data)
    assert patient_resp.status_code == 200
    patient_id = patient_resp.json()["patient_id"]

    # Post feedback with only rating
    feedback_data = {
        "patient_id": patient_id,
        "rating": 4,
        "language": "en"
    }
    response = client.post("/api/feedback/", data=feedback_data)
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["rating"] == 4
    assert resp_json["sentiment"] == "positive"
    assert resp_json["patient_id"] == patient_id

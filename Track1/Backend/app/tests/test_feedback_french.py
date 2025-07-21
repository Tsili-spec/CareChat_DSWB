import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_post_feedback_french_text():
    # Create a dummy patient first
    patient_data = {
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "1234567890",
        "email": "testuser@example.com",
        "preferred_language": "fr"
    }
    patient_resp = client.post("/api/patient/", json=patient_data)
    assert patient_resp.status_code == 200
    patient_id = patient_resp.json()["patient_id"]

    # Post feedback with French text
    feedback_data = {
        "patient_id": patient_id,
        "rating": 4,
        "feedback_text": "Le service était très lent et le personnel était impoli.",
        "language": "fr"
    }
    response = client.post("/api/feedback/", data=feedback_data)
    assert response.status_code == 200
    resp_json = response.json()
    print("Translated text:", resp_json["translated_text"])
    assert resp_json["rating"] == 4
    assert resp_json["sentiment"] in ["positive", "negative", "neutral"]
    assert resp_json["patient_id"] == patient_id
    assert resp_json["feedback_text"] == "Le service était très lent et le personnel était impoli."
    assert resp_json["language"] == "fr"
    assert resp_json["translated_text"] is not None and resp_json["translated_text"] != ""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_endpoint_valid():
    payload = {
        "conversation_id": "test123",
        "messages": [
            {"role": "user", "content": "Hello, I need to book an appointment for a haircut."}
        ],
        "language": "en"
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == "test123"
    assert "response" in data
    assert isinstance(data["response"], str)

def test_chat_endpoint_empty_messages():
    payload = {
        "conversation_id": "test123",
        "messages": [],
        "language": "en"
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Messages list is empty."

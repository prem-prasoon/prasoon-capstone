from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_rejects_missing_question():
    response = client.post("/ask", json={})
    assert response.status_code == 422
    assert "question" in response.text
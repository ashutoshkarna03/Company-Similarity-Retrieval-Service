from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_retrieve_similar_companies():
    response = client.get("/retrieve_similar_companies/1009")
    assert response.status_code == 200

def test_invalid_company_id():
    response = client.get("/retrieve_similar_companies/999999")
    assert response.status_code == 404

import pytest
from sqlalchemy import text
from fastapi import status

def test_retrieve_similar_companies_success(client, db_session):
    # Insert test data
    db_session.execute(text("""
        INSERT INTO companies (company_id, name, embedding) 
        VALUES (1001, 'Test Corp', '[0.1, 0.1]')
    """))
    db_session.commit()
    
    response = client.get("/api/retrieve_similar_companies/1001")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["company_id"] == 1001

def test_retrieve_similar_companies_not_found(client):
    response = client.get("/api/retrieve_similar_companies/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Company ID not found"

def test_response_model_structure(client, db_session):
    # Insert test data
    db_session.execute(text("""
        INSERT INTO companies (company_id, name, embedding) 
        VALUES (1001, 'Test Corp', '[0.1, 0.1]')
    """))
    db_session.commit()
    
    response = client.get("/api/retrieve_similar_companies/1001")
    data = response.json()
    assert "company_id" in data
    assert "similar_companies" in data
    assert isinstance(data["similar_companies"], list)

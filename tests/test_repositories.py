import pytest
from sqlalchemy import text  # Import text
from app.repositories.company import get_embedding_by_company_id, get_similar_companies


# tests/test_repositories.py
def test_get_embedding_by_company_id(client, db_session):
    # Insert test data with a 384-dimensional vector
    db_session.execute(text("""
        INSERT INTO companies (company_id, name, embedding)
        VALUES (1001, 'Test Corp', :embedding::vector(384))
    """), {
        "embedding": [0.1] * 384
    })
    db_session.commit()
    
    # Test valid company_id
    embedding = get_embedding_by_company_id(1001)
    assert len(embedding) == 384  # Verify dimension
    assert embedding == [0.1] * 384


def test_get_similar_companies(client, db_session):
    # Insert test data with proper CAST syntax
    db_session.execute(text("""
        INSERT INTO companies (company_id, name, embedding) 
        VALUES 
            (1001, 'Test Corp', CAST(:embedding1 AS vector(384))),
            (1002, 'Similar Corp', CAST(:embedding2 AS vector(384))),
            (1003, 'Different Corp', CAST(:embedding3 AS vector(384)))
    """), {
        "embedding1": [0.1] * 384,  # 384-dimensional vector
        "embedding2": [0.1] * 384,
        "embedding3": [0.9] * 384
    })
    db_session.commit()

    # Define a target embedding
    target_embedding = [0.1] * 384

    # Call the repository function to get similar companies
    results = get_similar_companies(target_embedding, 1001, limit=2)

    # Verify results
    assert len(results) == 2
    assert results[0][0] == 1002  # Most similar (company_id=1002)
    assert results[1][0] == 1003  # Less similar (company_id=1003)


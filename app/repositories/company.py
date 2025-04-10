from sqlalchemy import text
from app.database import SessionLocal


def get_embedding_by_company_id(company_id: int):
    """
    Retrieve the embedding for a given company_id from the database.
    """
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT embedding FROM companies 
            WHERE company_id = :company_id
        """), {"company_id": company_id}).fetchone()
        return result[0] if result else None
    finally:
        db.close()


def get_similar_companies(target_embedding, company_id: int, limit: int = 5):
    """
    Retrieve the most similar companies based on the target embedding.
    """
    db = SessionLocal()
    try:
        # Validate embedding dimensions
        if len(target_embedding) != 384:
            raise ValueError("Embedding must have 384 dimensions")
        results = db.execute(text("""
            SELECT company_id, 
                   1 - (embedding <=> :target_embedding) as similarity
            FROM companies
            WHERE company_id != :company_id
            ORDER BY similarity DESC
            LIMIT :limit
        """), {
            "target_embedding": target_embedding,
            "company_id": company_id,
            "limit": limit,
        }).fetchall()
        return results
    finally:
        db.close()

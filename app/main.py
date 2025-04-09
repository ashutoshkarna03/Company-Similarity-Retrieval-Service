# app/main.py
from fastapi import FastAPI, HTTPException
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from app.database import SessionLocal

app = FastAPI()
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.get("/retrieve_similar_companies/{company_id}")
def retrieve_similar_companies(company_id: int):
    db = SessionLocal()
    
    # Get target embedding
    target = db.execute(text("""
        SELECT embedding FROM companies 
        WHERE company_id = :company_id
    """), {"company_id": company_id}).fetchone()
    
    if not target:
        raise HTTPException(status_code=404, detail="Company ID not found")
    
    # Find similar companies using pgvector
    results = db.execute(text("""
        SELECT company_id, 
               1 - (embedding <=> :target_embedding) as similarity
        FROM companies
        WHERE company_id != :company_id
        ORDER BY similarity DESC
        LIMIT 5
    """), {
        "target_embedding": target[0],
        "company_id": company_id
    }).fetchall()

    return {
        "company_id": company_id,
        "similar_companies": [
            {"id": r[0], "similarity": float(r[1])} 
            for r in results
        ]
    }

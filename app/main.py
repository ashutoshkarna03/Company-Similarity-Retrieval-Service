from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from app.database import SessionLocal
from app.models.company import SimilarCompany, SimilarCompaniesResponse


app = FastAPI()


@app.get("/retrieve_similar_companies/{company_id}", response_model=SimilarCompaniesResponse)
def retrieve_similar_companies(company_id: int):
    db = SessionLocal()
    try:
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

        # Construct response using Pydantic model
        return SimilarCompaniesResponse(
            company_id=company_id,
            similar_companies=[
                SimilarCompany(id=r[0], similarity=float(r[1]))
                for r in results
            ]
        )
    finally:
        db.close()  # Ensure the session is closed

# app/routers/company.py
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.database import SessionLocal
from app.models.company import SimilarCompany, SimilarCompaniesResponse
from fastapi_redis_cache import cache
from app.repositories.company import get_embedding_by_company_id, get_similar_companies


router = APIRouter()


@router.get("/retrieve_similar_companies/{company_id}", response_model=SimilarCompaniesResponse)
@cache(expire=3600)  # Cache results for 1 hour (3600 seconds)
def retrieve_similar_companies(company_id: int):
    # Get target embedding from PostgreSQL
    target_embedding = get_embedding_by_company_id(company_id)
    
    if not target_embedding:
        raise HTTPException(status_code=404, detail="Company ID not found")
    
    # Find similar companies using pgvector in PostgreSQL
    results = get_similar_companies(target_embedding, company_id)

    # Construct response using Pydantic model
    return SimilarCompaniesResponse(
        company_id=company_id,
        similar_companies=[
            SimilarCompany(id=r[0], similarity=float(r[1]))
            for r in results
        ]
    )

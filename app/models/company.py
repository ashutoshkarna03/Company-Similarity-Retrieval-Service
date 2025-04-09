from pydantic import BaseModel
from typing import List


# Pydantic models for request and response
class SimilarCompany(BaseModel):
    id: int
    similarity: float


class SimilarCompaniesResponse(BaseModel):
    company_id: int
    similar_companies: List[SimilarCompany]
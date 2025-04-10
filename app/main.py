# app/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi_redis_cache import FastApiRedisCache, cache

from app.routers.company import router as company_router

app = FastAPI()


# Initialize Redis cache during startup
@app.on_event("startup")
def startup():
    redis_cache = FastApiRedisCache()
    redis_cache.init(
        host_url=os.environ.get("REDIS_URL", "redis://127.0.0.1:6379"),
        prefix="company-similarity-cache",
        response_header="X-Cache",
        ignore_arg_types=[]
    )


# Include the router for company-related APIs
app.include_router(company_router, prefix="/api", tags=["Company APIs"])


@app.get("/")
def root():
    return {"message": "Welcome to the Company Similarity API"}

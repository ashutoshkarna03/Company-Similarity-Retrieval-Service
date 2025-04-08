from fastapi import FastAPI, HTTPException
from app.data_loader import load_datasets
from app.similarity import generate_embeddings, compute_similarity, get_top_similar

app = FastAPI()

# Load data and generate embeddings at startup
data = load_datasets()
descriptions = data['description'].apply(str).tolist()
company_ids = data['company_id'].tolist()
embeddings = generate_embeddings(descriptions)


@app.get("/health")
def ping():
    return True


@app.get("/retrieve_similar_companies/{company_id}")
def retrieve_similar_companies(company_id: int):
    # TODO: handle exception
    if company_id not in company_ids:
        raise HTTPException(status_code=404, detail="Company ID not found")

    target_index = company_ids.index(company_id)
    target_embedding = embeddings[target_index]

    similarities = compute_similarity(target_embedding, embeddings)
    top_similar_companies = get_top_similar(similarities, company_ids)

    return {
        "company_id": company_id,
        "similar_companies": [
            {"id": comp[0], "similarity": round(float(comp[1]), 4)}
            for comp in top_similar_companies if comp[0] != company_id  # Exclude self-match
        ]
    }

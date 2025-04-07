from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(descriptions):
    """Generate embeddings for a list of company descriptions."""
    return model.encode(descriptions, show_progress_bar=True)

def compute_similarity(target_embedding, all_embeddings):
    """Compute cosine similarity between target embedding and all other embeddings."""
    similarities = cosine_similarity([target_embedding], all_embeddings)[0]
    return similarities

def get_top_similar(similarities, company_ids, top_n=5):
    """Retrieve top N similar companies based on similarity scores."""
    ranked_indices = similarities.argsort()[::-1][:top_n]
    return [(company_ids[i], similarities[i]) for i in ranked_indices]

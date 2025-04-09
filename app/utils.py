import numpy as np
import pandas as pd


def preprocess_text(text):
    """Clean and preprocess text data."""
    if pd.isna(text):
        return ""
    return text.lower().strip()


def save_embeddings(embeddings, file_path):
    """Save embeddings to a file."""
    np.save(file_path, embeddings)


def load_embeddings(file_path):
    """Load embeddings from a file."""
    return np.load(file_path)

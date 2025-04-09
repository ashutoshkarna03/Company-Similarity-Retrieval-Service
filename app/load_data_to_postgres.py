# load_data_to_postgres.py
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm  # For progress bar

# Configure logging (optional)
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DATABASE_URL = "postgresql://user:password@localhost:5432/company_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Load and merge data
def load_and_merge_data():
    logging.info("Loading CSV files...")
    companies = pd.read_csv("data/companies.csv")
    industries = pd.read_csv("data/company_industries.csv")
    specialities = pd.read_csv("data/company_specialities.csv")

    logging.info("Merging CSV files...")
    merged_data = companies.merge(industries, on="company_id", how="left")
    merged_data = merged_data.merge(specialities, on="company_id", how="left")
    # for test, only taking first 100 data, will remove later to take all
    merged_data = merged_data[:100]
    return merged_data


# Generate embeddings
def generate_embeddings(merged_data):
    logging.info("Initializing SentenceTransformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    logging.info("Generating embeddings for company descriptions...")
    descriptions = merged_data['description'].fillna('').tolist()
    embeddings = [model.encode(description) for description in tqdm(descriptions, desc="Generating embeddings")]
    return embeddings


def create_company_table():
    # Create table and extension in PostgreSQL
    logging.info("Creating table and pgvector extension in PostgreSQL...")
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS companies (
                company_id INT PRIMARY KEY,
                name TEXT,
                description TEXT,
                industry TEXT,
                speciality TEXT,
                embedding vector(384)
            )
        """))
        conn.commit()


def insert_data_to_db(merged_data, embeddings):
    # Insert data into PostgreSQL
    logging.info("Inserting data into PostgreSQL...")
    with engine.begin() as conn:
        for idx, row in tqdm(merged_data.iterrows(), total=len(merged_data), desc="Inserting data"):
            savepoint = conn.begin_nested()  # Create a savepoint for each row
            try:
                # Check for existing company_id to avoid duplicates
                existing = conn.execute(
                    text("SELECT 1 FROM companies WHERE company_id = :id"), 
                    {"id": row['company_id']}
                ).scalar()
                if existing:
                    logging.warning(f"Skipping duplicate company_id {row['company_id']}")
                    continue

                # Validate industry/speciality length (e.g., 100 characters)
                if len(row['industry']) > 100:
                    raise ValueError(f"Industry '{row['industry']}' exceeds 100 characters")
                if len(row['speciality']) > 100:
                    raise ValueError(f"Speciality '{row['speciality']}' exceeds 100 characters")

                # Insert data
                conn.execute(text("""
                    INSERT INTO companies 
                    (company_id, name, description, industry, speciality, embedding)
                    VALUES (:id, :name, :desc, :industry, :speciality, :embedding)
                """), {
                    "id": row['company_id'],
                    "name": row['name'],
                    "desc": row['description'],
                    "industry": row['industry'],
                    "speciality": row['speciality'],
                    "embedding": embeddings[idx].tolist()
                })
                savepoint.commit()  # Commit the savepoint
                logging.info(f"Inserted company_id {row['company_id']} successfully.")
            except Exception as e:
                savepoint.rollback()  # Rollback only this insert
                logging.error(f"Failed to insert company_id {row['company_id']}: {e}")


def main():
    merged_data = load_and_merge_data()
    embeddings = generate_embeddings(merged_data)
    create_company_table()
    insert_data_to_db(merged_data, embeddings)


if __name__ == '__main__':
    main()
import pandas as pd

def load_datasets():
    companies = pd.read_csv('data/companies.csv')
    industries = pd.read_csv('data/company_industries.csv')
    specialities = pd.read_csv('data/company_specialities.csv')

    # Merge datasets on company_id
    merged_data = companies.merge(industries, on='company_id', how='left')
    merged_data = merged_data.merge(specialities, on='company_id', how='left')

    return merged_data

def load_ground_truth():
    import json
    with open('data/ground_truth.json', 'r') as f:
        ground_truth = [json.loads(line) for line in f]
    return ground_truth

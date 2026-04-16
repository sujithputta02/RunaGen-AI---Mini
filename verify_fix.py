
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Load model
model_path = Path("models/career_predictor.pkl")
if not model_path.exists():
    print("Error: Model not found at models/career_predictor.pkl")
    exit(1)

# Using joblib load
data = joblib.load(model_path)
best_model = data['model']
le = data['label_encoder']
tfidf = data['tfidf_vectorizer']
feature_cols = data['feature_cols']

def predict_role_local(skills_list):
    skills_str = ' '.join([s.lower() for s in skills_list])
    
    # 1. TF-IDF
    X_tfidf = tfidf.transform([skills_str]).toarray()
    
    # 2. Meta-features
    data_keywords = ['data', 'sql', 'analysis', 'statistics', 'ml', 'pandas', 'tableau']
    dev_keywords = ['software', 'developer', 'web', 'javascript', 'frontend', 'backend', 'api']
    
    data_count = sum(1 for k in data_keywords if k in skills_str.lower())
    dev_count = sum(1 for k in dev_keywords if k in skills_str.lower())
    
    meta = {
        'skill_count': len(skills_list),
        'data_focus': data_count / (len(skills_list) + 1),
        'dev_focus': dev_count / (len(skills_list) + 1),
        'has_python': int('python' in skills_str.lower()),
        'has_sql': int('sql' in skills_str.lower() or 'mysql' in skills_str.lower() or 'postgresql' in skills_str.lower()),
        'skill_diversity': 5 
    }
    
    X_meta = np.array([[meta[col] for col in feature_cols]])
    X_combined = np.hstack([X_tfidf, X_meta])
    
    # Predict
    probs = best_model.predict_proba(X_combined)[0]
    top_indices = np.argsort(probs)[-3:][::-1]
    
    print("\n--------------------------------------------------")
    print(f"Test Skills: {skills_list}")
    for i, idx in enumerate(top_indices, 1):
        role = le.inverse_transform([idx])[0]
        prob = probs[idx]
        print(f"  {i}. {role}: {prob:.2%}")

# Test Cases
print("VERIFYING MODEL PERFORMANCE ON SPECIFIC PROBLEM ROLES")

print("\nCASE 1: Data Analyst (User reported: wrongly predicted as Backend)")
predict_role_local(["SQL", "Python", "Tableau", "Excel", "Data Analysis", "Statistics"])

print("\nCASE 2: Full Stack Developer (User reported: issues with gaps)")
predict_role_local(["React", "Node.js", "Express", "MongoDB", "Redux", "Javascript", "HTML", "CSS", "REST API"])

print("\nCASE 3: Backend Developer")
predict_role_local(["Python", "Django", "FastAPI", "SQL", "PostgreSQL", "Docker", "Redis", "API"])

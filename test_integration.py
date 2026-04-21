#!/usr/bin/env python3
"""
Integration Test Suite for RunaGen AI v2
Tests all components: ETL, Models, API, and Web Interface
"""
import sys
import os
sys.path.insert(0, 'src')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials/bigquery-key.json'
os.environ['GCP_PROJECT_ID'] = 'runagen-ai'

import json
from pathlib import Path
from datetime import datetime

# Test results
results = {
    "timestamp": datetime.now().isoformat(),
    "tests": {},
    "summary": {}
}

def test_models_exist():
    """Test 1: Check if trained models exist"""
    print("\n" + "="*70)
    print("TEST 1: Model Files Existence")
    print("="*70)
    
    models = {
        "career_predictor_90pct.pkl": "Career Model (91.42%)",
        "career_scaler_90pct.pkl": "Career Scaler",
        "career_encoder_90pct.pkl": "Career Encoder",
        "salary_predictor_90pct.pkl": "Salary Model",
        "salary_scaler_90pct.pkl": "Salary Scaler"
    }
    
    all_exist = True
    for model_file, description in models.items():
        path = Path(f"models/{model_file}")
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {description}: {model_file}")
        if not exists:
            all_exist = False
    
    results["tests"]["models_exist"] = all_exist
    return all_exist

def test_model_loading():
    """Test 2: Load and test models"""
    print("\n" + "="*70)
    print("TEST 2: Model Loading & Prediction")
    print("="*70)
    
    try:
        from api.main_v2_90pct import AdvancedCareerPredictor, AdvancedSalaryPredictor
        import numpy as np
        
        # Test career model
        print("\n  Loading Career Model...")
        career_model = AdvancedCareerPredictor()
        career_loaded = career_model.load()
        print(f"    {'✓' if career_loaded else '✗'} Career model loaded")
        
        # Test salary model
        print("  Loading Salary Model...")
        salary_model = AdvancedSalaryPredictor()
        salary_loaded = salary_model.load()
        print(f"    {'✓' if salary_loaded else '✗'} Salary model loaded")
        
        if career_loaded and salary_loaded:
            # Test predictions
            print("\n  Testing Predictions...")
            test_features = np.random.randn(1, 42).astype(np.float32)
            
            career_result = career_model.predict(test_features)
            print(f"    ✓ Career prediction: {career_result.get('primary_career')}")
            
            salary_result = salary_model.predict(test_features)
            if 'error' not in salary_result:
                print(f"    ✓ Salary prediction: ₹{salary_result.get('predicted_salary_inr', 0):,.0f}")
            
            results["tests"]["model_loading"] = True
            return True
        else:
            results["tests"]["model_loading"] = False
            return False
            
    except Exception as e:
        print(f"    ✗ Error: {e}")
        results["tests"]["model_loading"] = False
        return False

def test_feature_engineering():
    """Test 3: Feature engineering"""
    print("\n" + "="*70)
    print("TEST 3: Feature Engineering")
    print("="*70)
    
    try:
        from api.main_v2_90pct import engineer_features_for_prediction
        
        resume = "Senior Data Scientist with Python, ML, SQL skills"
        skills = ['Python', 'Machine Learning', 'SQL']
        
        features = engineer_features_for_prediction(resume, skills, 5)
        
        print(f"  ✓ Generated {len(features)} features (expected 42)")
        print(f"  ✓ Feature dtype: {features.dtype}")
        print(f"  ✓ Feature range: [{features.min():.2f}, {features.max():.2f}]")
        
        results["tests"]["feature_engineering"] = len(features) == 42
        return len(features) == 42
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"]["feature_engineering"] = False
        return False

def test_skill_extraction():
    """Test 4: Skill extraction"""
    print("\n" + "="*70)
    print("TEST 4: Skill Extraction")
    print("="*70)
    
    try:
        from ml.model_1_skill_extraction import SkillExtractor
        
        extractor = SkillExtractor(use_ollama=False)
        resume = "Expert in Python, Java, SQL, AWS, Docker, Kubernetes"
        
        skills = extractor.extract_skills(resume)
        
        print(f"  ✓ Extracted {len(skills)} skills")
        print(f"  ✓ Sample skills: {skills[:5]}")
        
        results["tests"]["skill_extraction"] = len(skills) > 0
        return len(skills) > 0
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"]["skill_extraction"] = False
        return False

def test_bigquery_connection():
    """Test 5: BigQuery connection"""
    print("\n" + "="*70)
    print("TEST 5: BigQuery Connection")
    print("="*70)
    
    try:
        from google.cloud import bigquery
        from google.oauth2 import service_account
        
        credentials_path = 'credentials/bigquery-key.json'
        if not Path(credentials_path).exists():
            print(f"  ✗ Credentials not found: {credentials_path}")
            results["tests"]["bigquery_connection"] = False
            return False
        
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = bigquery.Client(credentials=credentials, project='runagen-ai')
        
        # Test query
        query = "SELECT COUNT(*) as count FROM `runagen-ai.runagen_silver_silver.jobs_cleaned` LIMIT 1"
        result = client.query(query).result()
        
        for row in result:
            count = row['count']
            print(f"  ✓ BigQuery connected")
            print(f"  ✓ Jobs in Silver layer: {count:,}")
        
        results["tests"]["bigquery_connection"] = True
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"]["bigquery_connection"] = False
        return False

def test_api_endpoints():
    """Test 6: API endpoints"""
    print("\n" + "="*70)
    print("TEST 6: API Endpoints")
    print("="*70)
    
    try:
        from api.main_v2_90pct import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        print("  Testing /health endpoint...")
        response = client.get("/health")
        print(f"    ✓ Status: {response.status_code}")
        print(f"    ✓ Response: {response.json()}")
        
        results["tests"]["api_endpoints"] = response.status_code == 200
        return response.status_code == 200
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"]["api_endpoints"] = False
        return False

def test_end_to_end():
    """Test 7: End-to-end analysis"""
    print("\n" + "="*70)
    print("TEST 7: End-to-End Resume Analysis")
    print("="*70)
    
    try:
        from api.main_v2_90pct import (
            AdvancedCareerPredictor,
            AdvancedSalaryPredictor,
            engineer_features_for_prediction,
            analyze_skill_gap,
            generate_recommendations
        )
        from ml.model_1_skill_extraction import SkillExtractor
        
        resume = """
        Senior Data Scientist with 5 years experience
        Skills: Python, Machine Learning, SQL, TensorFlow, AWS
        """
        
        # Extract skills
        extractor = SkillExtractor(use_ollama=False)
        skills = extractor.extract_skills(resume)
        print(f"  ✓ Extracted {len(skills)} skills")
        
        # Engineer features
        features = engineer_features_for_prediction(resume, skills, 5)
        print(f"  ✓ Engineered {len(features)} features")
        
        # Predict career
        career_model = AdvancedCareerPredictor()
        career_model.load()
        career_result = career_model.predict(features)
        print(f"  ✓ Career: {career_result.get('primary_career')}")
        
        # Predict salary
        salary_model = AdvancedSalaryPredictor()
        salary_model.load()
        salary_result = salary_model.predict(features)
        print(f"  ✓ Salary: ₹{salary_result.get('predicted_salary_inr', 0):,.0f}")
        
        # Skill gap
        gap = analyze_skill_gap(career_result.get('primary_career', 'Software Engineer'), skills)
        print(f"  ✓ Skill coverage: {gap['coverage_percentage']:.1f}%")
        
        # Recommendations
        recs = generate_recommendations(career_result.get('primary_career', 'Software Engineer'), skills, gap['missing_skills'])
        print(f"  ✓ Generated {len(recs)} recommendations")
        
        results["tests"]["end_to_end"] = True
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["tests"]["end_to_end"] = False
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 RunaGen AI v2 - Integration Test Suite")
    print("="*70)
    
    tests = [
        ("Models Exist", test_models_exist),
        ("Model Loading", test_model_loading),
        ("Feature Engineering", test_feature_engineering),
        ("Skill Extraction", test_skill_extraction),
        ("BigQuery Connection", test_bigquery_connection),
        ("API Endpoints", test_api_endpoints),
        ("End-to-End Analysis", test_end_to_end),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    print(f"  ✓ Passed: {passed}/{len(tests)}")
    print(f"  ✗ Failed: {failed}/{len(tests)}")
    
    results["summary"] = {
        "total_tests": len(tests),
        "passed": passed,
        "failed": failed,
        "success_rate": f"{(passed/len(tests)*100):.1f}%"
    }
    
    if failed == 0:
        print("\n✅ All tests passed! System is ready for deployment.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review.")
    
    print("="*70 + "\n")
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
Test API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_skill_extraction():
    """Test skill extraction"""
    print("Testing skill extraction...")
    data = {
        "resume_text": """
        Senior Data Engineer with 5 years of experience in Python, SQL, and AWS.
        Master's degree in Computer Science from Stanford University.
        Expertise in building ETL pipelines using Apache Spark, Airflow, and Docker.
        """
    }
    response = requests.post(f"{BASE_URL}/api/extract-skills", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_career_prediction():
    """Test career prediction"""
    print("Testing career prediction...")
    data = {
        "current_skills": ["Python", "SQL", "AWS", "Docker"],
        "experience_years": 5
    }
    response = requests.post(f"{BASE_URL}/api/predict-career", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_skill_gap():
    """Test skill gap analysis"""
    print("Testing skill gap analysis...")
    data = {
        "current_skills": ["Python", "SQL"],
        "target_role": "Data Scientist"
    }
    response = requests.post(f"{BASE_URL}/api/analyze-skill-gaps", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_salary_prediction():
    """Test salary prediction"""
    print("Testing salary prediction...")
    data = {
        "role": "Data Engineer",
        "skills": ["Python", "SQL", "AWS", "Docker", "Spark"],
        "experience_years": 5,
        "location": "United States"
    }
    response = requests.post(f"{BASE_URL}/api/predict-salary", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("="*60)
    print("RUNAGEN AI - API TESTING")
    print("="*60)
    print()
    
    try:
        test_root()
        test_health()
        test_skill_extraction()
        test_career_prediction()
        test_skill_gap()
        test_salary_prediction()
        
        print("="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("Make sure the server is running: python3 src/api/main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

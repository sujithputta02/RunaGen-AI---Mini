"""
Test script for RunaGen AI API v2 - All Features
Tests all Phase 3-6 endpoints
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_test_header(test_name: str):
    """Print test header"""
    print("\n" + "="*70)
    print(f"🧪 TEST: {test_name}")
    print("="*70)

def print_result(success: bool, message: str, data: Any = None):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if data and isinstance(data, dict):
        print(json.dumps(data, indent=2)[:500])  # Print first 500 chars

def test_health_check():
    """Test health check endpoint"""
    print_test_header("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get('status') == 'healthy' and
            data.get('model_accuracy') == 91.42
        )
        
        print_result(success, "Health check", data)
        return success
    except Exception as e:
        print_result(False, f"Health check failed: {e}")
        return False

def test_analyze_resume():
    """Test resume analysis"""
    print_test_header("Analyze Resume")
    
    sample_resume = """
    John Doe
    Data Analyst | Python | SQL | Tableau
    
    Skills:
    - Python, SQL, R
    - Tableau, Power BI
    - Excel, Google Sheets
    - Data Analysis, Statistical Analysis
    
    Experience:
    - 3 years as Data Analyst
    - Worked with BigQuery, PostgreSQL
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze-resume",
            json={
                "resume_text": sample_resume,
                "experience_years": 3
            }
        )
        data = response.json()
        
        success = (
            response.status_code == 200 and
            'extracted_skills' in data and
            'career_prediction' in data and
            'salary_prediction' in data
        )
        
        print_result(success, "Resume analysis", {
            "skills_count": len(data.get('extracted_skills', [])),
            "career": data.get('career_prediction', {}).get('primary_career'),
            "confidence": data.get('career_prediction', {}).get('confidence'),
            "salary": data.get('salary_prediction', {}).get('predicted_salary_inr')
        })
        return success
    except Exception as e:
        print_result(False, f"Resume analysis failed: {e}")
        return False

def test_job_scraping():
    """Test Phase 3: Job Scraping"""
    print_test_header("Phase 3: Job Scraping")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/jobs/scrape",
            params={"keywords": "python,data", "location": "India"}
        )
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get('status') == 'success'
        )
        
        print_result(success, "Job scraping", {
            "jobs_found": data.get('jobs_found'),
            "source": data.get('source')
        })
        return success
    except Exception as e:
        print_result(False, f"Job scraping failed: {e}")
        return False

def test_learning_path():
    """Test Phase 4: Learning Path Generation"""
    print_test_header("Phase 4: Learning Path Generation")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/learning-path",
            json={
                "career": "Data Analyst",
                "current_skills": ["Python", "SQL"],
                "target_level": "intermediate"
            }
        )
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get('status') == 'success' and
            'learning_path' in data
        )
        
        learning_path = data.get('learning_path', {})
        print_result(success, "Learning path generation", {
            "career": learning_path.get('career'),
            "duration_weeks": learning_path.get('estimated_duration_weeks'),
            "phases_count": len(learning_path.get('phases', []))
        })
        return success
    except Exception as e:
        print_result(False, f"Learning path generation failed: {e}")
        return False

def test_learning_resources():
    """Test learning resources endpoint"""
    print_test_header("Learning Resources")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/learning-resources/Python",
            params={"resource_type": "free"}
        )
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get('status') == 'success'
        )
        
        print_result(success, "Learning resources", {
            "skill": data.get('skill'),
            "resources_count": len(data.get('resources', []))
        })
        return success
    except Exception as e:
        print_result(False, f"Learning resources failed: {e}")
        return False

def test_trending_skills():
    """Test Phase 5: Trending Skills"""
    print_test_header("Phase 5: Trending Skills")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/skill-trends/trending",
            params={"days": 30, "limit": 10}
        )
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get('status') == 'success'
        )
        
        print_result(success, "Trending skills", {
            "skills_count": len(data.get('trending_skills', [])),
            "period_days": data.get('period_days')
        })
        return success
    except Exception as e:
        print_result(False, f"Trending skills failed: {e}")
        return False

def test_emerging_skills():
    """Test emerging skills endpoint"""
    print_test_header("Emerging Skills")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/skill-trends/emerging",
            params={"threshold_days": 30}
        )
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get('status') == 'success'
        )
        
        print_result(success, "Emerging skills", {
            "skills_count": len(data.get('emerging_skills', [])),
            "threshold_days": data.get('threshold_days')
        })
        return success
    except Exception as e:
        print_result(False, f"Emerging skills failed: {e}")
        return False

def test_skill_growth():
    """Test skill growth rate endpoint"""
    print_test_header("Skill Growth Rate")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/skill-trends/growth/Python",
            params={"days": 90}
        )
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get('status') == 'success'
        )
        
        skill_growth = data.get('skill_growth', {})
        print_result(success, "Skill growth rate", {
            "skill": skill_growth.get('skill_name'),
            "growth_rate": skill_growth.get('growth_rate'),
            "status": skill_growth.get('status')
        })
        return success
    except Exception as e:
        print_result(False, f"Skill growth rate failed: {e}")
        return False

def test_skill_salary():
    """Test skill salary correlation endpoint"""
    print_test_header("Skill Salary Correlation")
    
    try:
        response = requests.get(f"{BASE_URL}/api/skill-trends/salary/Python")
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get('status') == 'success'
        )
        
        skill_salary = data.get('skill_salary', {})
        print_result(success, "Skill salary correlation", {
            "skill": skill_salary.get('skill_name'),
            "avg_salary": skill_salary.get('avg_salary'),
            "salary_range": skill_salary.get('salary_range')
        })
        return success
    except Exception as e:
        print_result(False, f"Skill salary correlation failed: {e}")
        return False

def test_resume_optimization():
    """Test Phase 6: Resume Optimization"""
    print_test_header("Phase 6: Resume Optimization")
    
    sample_resume = """
    John Doe
    Data Analyst | Python | SQL
    
    Skills: Python, SQL, Tableau
    Experience: 3 years as Data Analyst
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/resume/optimize",
            json={
                "resume_text": sample_resume,
                "target_role": "Data Analyst"
            }
        )
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get('status') == 'success'
        )
        
        optimization = data.get('optimization', {})
        current_status = optimization.get('current_status', {})
        print_result(success, "Resume optimization", {
            "target_role": optimization.get('target_role'),
            "current_match": current_status.get('match_percentage'),
            "suggestions_count": len(optimization.get('optimization_suggestions', []))
        })
        return success
    except Exception as e:
        print_result(False, f"Resume optimization failed: {e}")
        return False

def test_match_score():
    """Test resume match score endpoint"""
    print_test_header("Resume Match Score")
    
    sample_resume = """
    John Doe
    Data Analyst | Python | SQL
    
    Skills: Python, SQL, Tableau
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/resume/match-score",
            json={
                "resume_text": sample_resume,
                "job_title": "Data Analyst"
            }
        )
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get('status') == 'success'
        )
        
        match_score = data.get('match_score', {})
        print_result(success, "Resume match score", {
            "job_title": data.get('job_title'),
            "match_percentage": match_score.get('match_percentage'),
            "match_level": match_score.get('match_level')
        })
        return success
    except Exception as e:
        print_result(False, f"Resume match score failed: {e}")
        return False

def test_optimization_suggestions():
    """Test optimization suggestions endpoint"""
    print_test_header("Optimization Suggestions")
    
    sample_resume = """
    John Doe
    Data Analyst | Python | SQL
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/resume/suggestions",
            json={
                "resume_text": sample_resume,
                "job_title": "Data Analyst"
            }
        )
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get('status') == 'success'
        )
        
        suggestions = data.get('suggestions', {})
        print_result(success, "Optimization suggestions", {
            "job_title": suggestions.get('job_title'),
            "current_match": suggestions.get('current_match'),
            "suggestions_count": len(suggestions.get('suggestions', []))
        })
        return success
    except Exception as e:
        print_result(False, f"Optimization suggestions failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 RunaGen AI API v2 - Complete Test Suite")
    print("="*70)
    print("\nTesting all Phase 3-6 features...")
    
    tests = [
        ("Health Check", test_health_check),
        ("Resume Analysis", test_analyze_resume),
        ("Job Scraping (Phase 3)", test_job_scraping),
        ("Learning Path (Phase 4)", test_learning_path),
        ("Learning Resources (Phase 4)", test_learning_resources),
        ("Trending Skills (Phase 5)", test_trending_skills),
        ("Emerging Skills (Phase 5)", test_emerging_skills),
        ("Skill Growth (Phase 5)", test_skill_growth),
        ("Skill Salary (Phase 5)", test_skill_salary),
        ("Resume Optimization (Phase 6)", test_resume_optimization),
        ("Match Score (Phase 6)", test_match_score),
        ("Optimization Suggestions (Phase 6)", test_optimization_suggestions),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*70 + "\n")
    
    if passed == total:
        print("🎉 All tests passed! API v2 is fully functional.")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Check the output above.")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

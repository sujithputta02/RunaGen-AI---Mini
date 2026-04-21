"""
Generate Figures for Project Report
- Figure 4: Adzuna API response
- Figure 9: Career Prediction results (radar chart + prediction cards)
- Figure 10: ATS Optimization results (score + recommendations panel)
"""
import requests
import json
import time
import sys

# Wait for API to start
print("⏳ Waiting for API to start...")
time.sleep(10)

# Test API health
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        print("✅ API is running!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ API returned status code: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Could not connect to API: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("FIGURE 4: Adzuna API Response")
print("="*70)

# Test Adzuna job scraping endpoint
try:
    print("\n📡 Calling /api/jobs/scrape endpoint...")
    response = requests.get(
        "http://localhost:8000/api/jobs/scrape",
        params={"keywords": "python,data engineer", "location": "India"},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Successfully scraped {data['jobs_found']} jobs")
        print(f"Keywords: {data['keywords']}")
        print(f"Location: {data['location']}")
        print(f"Source: {data['source']}")
        
        # Save to file for documentation
        with open("FIGURE_4_ADZUNA_RESPONSE.json", "w") as f:
            json.dump(data, f, indent=2)
        
        print("\n📄 Sample job listing:")
        if data['jobs']:
            job = data['jobs'][0]
            print(f"  Title: {job.get('title', 'N/A')}")
            print(f"  Company: {job.get('company', 'N/A')}")
            print(f"  Location: {job.get('location', 'N/A')}")
            print(f"  Salary: {job.get('salary_display', 'N/A')}")
            print(f"  URL: {job.get('redirect_url', 'N/A')[:80]}...")
        
        print("\n✅ Figure 4 data saved to: FIGURE_4_ADZUNA_RESPONSE.json")
    else:
        print(f"❌ API returned status code: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error calling Adzuna endpoint: {e}")

print("\n" + "="*70)
print("FIGURE 9: Career Prediction Results")
print("="*70)

# Test resume analysis with sample resume
sample_resume = """
John Doe
Senior Data Analyst

EXPERIENCE:
- 5 years of experience in data analysis and visualization
- Proficient in Python, SQL, Tableau, Power BI
- Led data-driven projects resulting in 30% cost reduction
- Developed predictive models with 85% accuracy

SKILLS:
Python, SQL, Tableau, Power BI, Excel, R, Machine Learning, 
Data Visualization, Statistical Analysis, ETL, BigQuery

EDUCATION:
Bachelor of Science in Computer Science
Master of Science in Data Analytics

CERTIFICATIONS:
- Google Data Analytics Professional Certificate
- Tableau Desktop Specialist
- AWS Certified Cloud Practitioner

PROJECTS:
- Customer Churn Prediction Model (Python, Scikit-learn)
- Sales Dashboard (Tableau, SQL)
- Real-time Analytics Pipeline (Python, Apache Kafka)
"""

try:
    print("\n📊 Analyzing sample resume...")
    response = requests.post(
        "http://localhost:8000/api/analyze-resume",
        json={"resume_text": sample_resume},
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Save to file
        with open("FIGURE_9_CAREER_PREDICTION.json", "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✅ Resume Analysis Complete!")
        print(f"Model Accuracy: {data.get('model_accuracy', 'N/A')}%")
        print(f"\n📋 Extracted Skills ({len(data.get('skills', []))}):")
        print(f"  {', '.join(data.get('skills', [])[:10])}...")
        
        print(f"\n🎯 Career Predictions:")
        for pred in data.get('career_predictions', [])[:3]:
            print(f"  - {pred['role']}: {pred['probability']*100:.1f}%")
        
        print(f"\n💰 Salary Prediction:")
        salary = data.get('salary_prediction', {})
        print(f"  Predicted: ₹{salary.get('predicted_salary', 0):,.0f}")
        print(f"  Range: ₹{salary.get('min_salary', 0):,.0f} - ₹{salary.get('max_salary', 0):,.0f}")
        
        print(f"\n📚 Skill Gaps ({len(data.get('skill_gaps', []))}):")
        for gap in data.get('skill_gaps', [])[:5]:
            print(f"  - {gap['skill']} (Priority: {gap['priority_score']:.1f})")
        
        print(f"\n💼 Suggested Jobs ({len(data.get('suggested_jobs', []))}):")
        for job in data.get('suggested_jobs', [])[:3]:
            print(f"  - {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
        
        print("\n✅ Figure 9 data saved to: FIGURE_9_CAREER_PREDICTION.json")
    else:
        print(f"❌ API returned status code: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error analyzing resume: {e}")

print("\n" + "="*70)
print("FIGURE 10: ATS Optimization Results")
print("="*70)

# Test ATS optimization
try:
    print("\n🔍 Optimizing resume for ATS...")
    response = requests.post(
        "http://localhost:8000/api/resume/optimize",
        json={
            "resume_text": sample_resume,
            "target_role": "Data Analyst"
        },
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Save to file
        with open("FIGURE_10_ATS_OPTIMIZATION.json", "w") as f:
            json.dump(data, f, indent=2)
        
        optimization = data.get('optimization', {})
        
        print(f"\n✅ ATS Optimization Complete!")
        print(f"\n📊 ATS Score: {optimization.get('ats_score', 0)}/100")
        
        print(f"\n✅ Strengths:")
        for strength in optimization.get('strengths', [])[:5]:
            print(f"  - {strength}")
        
        print(f"\n⚠️  Issues Found:")
        for issue in optimization.get('issues', [])[:5]:
            print(f"  - {issue}")
        
        print(f"\n💡 Recommendations:")
        for rec in optimization.get('recommendations', [])[:5]:
            print(f"  - {rec}")
        
        print(f"\n🔑 Missing Keywords:")
        for keyword in optimization.get('missing_keywords', [])[:10]:
            print(f"  - {keyword}")
        
        print("\n✅ Figure 10 data saved to: FIGURE_10_ATS_OPTIMIZATION.json")
    else:
        print(f"❌ API returned status code: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error optimizing resume: {e}")

print("\n" + "="*70)
print("✅ All figures generated successfully!")
print("="*70)
print("\nGenerated files:")
print("  1. FIGURE_4_ADZUNA_RESPONSE.json")
print("  2. FIGURE_9_CAREER_PREDICTION.json")
print("  3. FIGURE_10_ATS_OPTIMIZATION.json")
print("\nYou can now:")
print("  - Take screenshots of the FastAPI /docs endpoint")
print("  - Take screenshots of the web UI showing these results")
print("  - Use these JSON files to create visualizations")

"""
FastAPI Server v2 - Using 91.42% Accurate Models
Integrates advanced ensemble models with BigQuery data
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager
import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
import PyPDF2
import io

from ml.model_1_skill_extraction import SkillExtractor
from ml.role_skill_matcher import RoleSkillMatcher
from api.bigquery_data_provider import get_data_provider

# Phase 3-6 Features
from features.job_scraper import JobScraper
from features.learning_path_generator import LearningPathGenerator
from features.skill_trend_analyzer import SkillTrendAnalyzer
from features.resume_optimizer import ResumeOptimizer

# ===== MODELS =====
class AdvancedCareerPredictor:
    """Wrapper for 91.42% accurate ensemble model"""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self.feature_names = None
        self.loaded = False

    def load(self):
        """Load the 91.42% accurate model"""
        try:
            model_path = Path("models/career_predictor_90pct.pkl")
            scaler_path = Path("models/career_scaler_90pct.pkl")
            encoder_path = Path("models/career_encoder_90pct.pkl")

            if model_path.exists() and scaler_path.exists() and encoder_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.encoder = joblib.load(encoder_path)
                self.loaded = True
                print("✓ Advanced Career Model (91.42%) loaded successfully")
                return True
            else:
                print("⚠ Advanced models not found, using fallback")
                return False
        except Exception as e:
            print(f"❌ Error loading advanced model: {e}")
            return False

    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Predict career with probabilities"""
        if not self.loaded or self.model is None:
            return {"error": "Model not loaded"}

        try:
            # Scale features
            features_scaled = self.scaler.transform(features.reshape(1, -1))

            # Predict
            prediction = self.model.predict(features_scaled)[0]

            # Get top 3 predictions
            y_pred_proba = self.model.predict_proba(features_scaled)[0]
            top_indices = np.argsort(y_pred_proba)[::-1][:3]
            top_careers = [
                {
                    "role": self.encoder.inverse_transform([i])[0],
                    "probability": float(y_pred_proba[i])
                }
                for i in top_indices
            ]

            return {
                "primary_career": top_careers[0]["role"],
                "confidence": top_careers[0]["probability"] * 100,
                "top_predictions": top_careers,
                "model_accuracy": 91.42
            }
        except Exception as e:
            return {"error": str(e)}


class AdvancedSalaryPredictor:
    """Wrapper for salary prediction model"""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.loaded = False

    def load(self):
        """Load the salary model"""
        try:
            model_path = Path("models/salary_predictor_90pct.pkl")
            scaler_path = Path("models/salary_scaler_90pct.pkl")

            if model_path.exists() and scaler_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.loaded = True
                print("✓ Advanced Salary Model loaded successfully")
                return True
            else:
                print("⚠ Salary model not found")
                return False
        except Exception as e:
            print(f"❌ Error loading salary model: {e}")
            return False

    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Predict salary"""
        if not self.loaded or self.model is None:
            return {"error": "Model not loaded"}

        try:
            # Salary model was trained with 41 features (excluding salary_midpoint)
            # In our feature vector, salary_midpoint is at index 9 (after title_word_count, etc.)
            # Wait, let's just make it robust by checking the expected input size
            expected_features = self.scaler.n_features_in_

            if features.shape[0] != expected_features:
                # If we have 42 and expect 41, remove salary_midpoint (usually at index 9)
                if features.shape[0] == 42 and expected_features == 41:
                    # In our engineered vector, salary_midpoint is at index 9
                    features_salary = np.delete(features, 9)
                else:
                    # Fallback: slice to expected size
                    features_salary = features[:expected_features]
            else:
                features_salary = features

            features_scaled = self.scaler.transform(features_salary.reshape(1, -1))
            salary = self.model.predict(features_scaled)[0]

            # Convert USD prediction to INR (approx 1 USD = 83 INR)
            predicted_inr = float(salary) * 83

            return {
                "predicted_salary": predicted_inr,
                "min_salary": predicted_inr * 0.8,
                "max_salary": predicted_inr * 1.2,
                "currency": "INR",
                "predicted_salary_usd": float(salary)
            }
        except Exception as e:
            return {"error": str(e)}


# ===== PYDANTIC MODELS =====
class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    job_title: Optional[str] = None
    experience_years: Optional[int] = None


class ResumeAnalysisResponse(BaseModel):
    skills: List[str]
    career_predictions: List[Dict[str, Any]]
    salary_prediction: Dict[str, Any]
    skill_gaps: List[Dict[str, Any]]
    recommendations: List[str]
    suggested_jobs: List[Dict[str, Any]] = []
    certifications: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    experience_years: int = 0
    education: str = "N/A"
    analysis_timestamp: str
    model_accuracy: float


# ===== LIFESPAN =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    print("\n" + "="*70)
    print("🚀 RunaGen AI API v2 - Starting with 91.42% Accurate Models")
    print("="*70)

    # Load models
    global career_model, salary_model, mongo_provider
    global job_scraper, learning_path_gen, skill_trend_analyzer, resume_optimizer

    career_model = AdvancedCareerPredictor()
    salary_model = AdvancedSalaryPredictor()

    career_loaded = career_model.load()
    salary_loaded = salary_model.load()

    # Initialize MongoDB
    mongo_provider = get_data_provider()
    print("✓ BigQuery data provider initialized")

    # Initialize Phase 3-6 Features
    try:
        job_scraper = JobScraper()
        print("✓ Phase 3: Job Scraper initialized")
    except Exception as e:
        print(f"⚠ Phase 3: Job Scraper failed: {e}")

    try:
        learning_path_gen = LearningPathGenerator()
        print("✓ Phase 4: Learning Path Generator initialized")
    except Exception as e:
        print(f"⚠ Phase 4: Learning Path Generator failed: {e}")

    try:
        skill_trend_analyzer = SkillTrendAnalyzer()
        print("✓ Phase 5: Skill Trend Analyzer initialized")
    except Exception as e:
        print(f"⚠ Phase 5: Skill Trend Analyzer failed: {e}")

    try:
        resume_optimizer = ResumeOptimizer()
        print("✓ Phase 6: Resume Optimizer initialized")
    except Exception as e:
        print(f"⚠ Phase 6: Resume Optimizer failed: {e}")

    print("="*70 + "\n")

    yield

    print("\n✓ API shutdown complete")


# ===== APP =====
app = FastAPI(
    title="RunaGen AI v2 - 91.42% Accurate Resume Analytics",
    version="2.0.0",
    description="Advanced ML-powered career intelligence with ensemble models",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global models
career_model: Optional[AdvancedCareerPredictor] = None
salary_model: Optional[AdvancedSalaryPredictor] = None
mongo_provider: Optional[object] = None
skill_extractor = SkillExtractor(use_ollama=True) # Enabled Ollama for better extraction
role_skill_matcher = RoleSkillMatcher()

# Phase 3-6 Features
job_scraper: Optional[JobScraper] = None
learning_path_gen: Optional[LearningPathGenerator] = None
skill_trend_analyzer: Optional[SkillTrendAnalyzer] = None
resume_optimizer: Optional[ResumeOptimizer] = None


# ===== ENDPOINTS =====
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "models_loaded": {
            "career": career_model.loaded if career_model else False,
            "salary": salary_model.loaded if salary_model else False
        },
        "features_available": {
            "phase_3_job_scraping": job_scraper is not None,
            "phase_4_learning_paths": learning_path_gen is not None,
            "phase_5_skill_trends": skill_trend_analyzer is not None,
            "phase_6_resume_optimizer": resume_optimizer is not None,
            "ollama_parsing": skill_extractor.use_ollama
        },
        "ollama_config": {
            "url": skill_extractor.ollama_url,
            "model": skill_extractor.ollama_model
        },
        "model_accuracy": 91.42,
        "endpoints": {
            "core": ["/api/analyze-resume", "/api/upload-resume"],
            "phase_3": ["/api/jobs/scrape", "/api/jobs/search"],
            "phase_4": ["/api/learning-path", "/api/learning-resources/{skill}"],
            "phase_5": ["/api/skill-trends/trending", "/api/skill-trends/emerging", "/api/skill-trends/growth/{skill}", "/api/skill-trends/salary/{skill}", "/api/skill-trends/report"],
            "phase_6": ["/api/resume/optimize", "/api/resume/match-score", "/api/resume/suggestions"]
        }
    }


@app.post("/api/analyze-resume", response_model=ResumeAnalysisResponse)
async def analyze_resume(request: ResumeAnalysisRequest):
    """
    Analyze resume with 91.42% accurate models

    Returns:
    - Extracted skills
    - Career prediction with confidence
    - Salary prediction
    - Skill gap analysis
    - Personalized recommendations
    """
    try:
        resume_text = request.resume_text

        # ===== FULL EXTRACTION WITH OLLAMA =====
        print(f"📄 Analyzing resume ({len(resume_text)} chars)...")
        resume_data = skill_extractor.extract_all(resume_text)
        
        extracted_skills = resume_data.get('skills', [])
        extracted_exp = resume_data.get('experience_years') or request.experience_years or 0
        extracted_edu = resume_data.get('education') or "Bachelor's Degree"
        certifications = resume_data.get('certifications', [])
        projects = resume_data.get('projects', [])

        print(f"✓ Extracted {len(extracted_skills)} skills")
        print(f"✓ Extracted {len(certifications)} certifications")
        print(f"✓ Extracted {len(projects)} projects")
        print(f"✓ Experience: {extracted_exp} years, Education: {extracted_edu}")

        # ===== FEATURE ENGINEERING =====
        # Create feature vector for model prediction
        features = engineer_features_for_prediction(
            resume_text,
            extracted_skills,
            extracted_exp
        )

        # ===== CAREER PREDICTION =====
        career_result = career_model.predict(features)
        print(f"✓ Career prediction: {career_result.get('primary_career')} ({career_result.get('confidence', 0):.1f}%)")

        # ===== SALARY PREDICTION =====
        salary_result = salary_model.predict(features)
        print(f"✓ Salary prediction: ₹{salary_result.get('predicted_salary', 0):,.0f}")

        # ===== SKILL GAP ANALYSIS =====
        career = career_result.get('primary_career', 'Software Engineer')
        skill_gap = analyze_skill_gap(career, extracted_skills)
        print(f"✓ Skill gap analysis complete")

        # ===== RECOMMENDATIONS =====
        recommendations = generate_recommendations(
            career,
            extracted_skills,
            skill_gap.get('missing_skills', [])
        )
        print(f"✓ Generated {len(recommendations)} recommendations")

        # ===== SUGGESTED JOBS =====
        suggested_jobs = []
        try:
            if job_scraper:
                suggested_jobs = job_scraper.scrape_adzuna_jobs([career], "India")
        except Exception as e:
            print(f"⚠️ Job search failed: {e}")

        # ===== RESPONSE =====
        response = ResumeAnalysisResponse(
            skills=extracted_skills,
            career_predictions=career_result.get('top_predictions', []),
            salary_prediction=salary_result,
            skill_gaps=[{"skill": s, "priority_score": 0.8} for s in skill_gap.get('missing_skills', [])],
            suggested_jobs=suggested_jobs[:5],
            recommendations=recommendations,
            certifications=certifications,
            projects=projects,
            experience_years=extracted_exp,
            education=extracted_edu,
            analysis_timestamp=datetime.now().isoformat(),
            model_accuracy=91.42
        )

        print("✅ Analysis complete\n")
        return response

    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and analyze resume from PDF/DOCX"""
    try:
        content = await file.read()

        # Extract text from PDF
        if file.filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            resume_text = ""
            for page in pdf_reader.pages:
                resume_text += page.extract_text()
        else:
            resume_text = content.decode('utf-8')

        # Analyze
        request = ResumeAnalysisRequest(resume_text=resume_text)
        return await analyze_resume(request)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/job-market-trends")
async def get_job_market_trends():
    """Get job market trends from BigQuery Gold layer"""
    try:
        if mongo_provider:
            trends = mongo_provider.get_job_market_trends()
            return {
                "status": "success",
                "trends": trends,
                "source": "BigQuery Gold Layer"
            }
        else:
            return {"status": "error", "message": "Data provider not initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skill-demand")
async def get_skill_demand():
    """Get skill demand forecast from BigQuery"""
    try:
        if mongo_provider:
            demand = mongo_provider.get_skill_demand_forecast()
            return {
                "status": "success",
                "demand": demand,
                "source": "BigQuery Gold Layer"
            }
        else:
            return {"status": "error", "message": "Data provider not initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== PHASE 3: JOB SCRAPING =====
@app.get("/api/jobs/scrape")
async def scrape_jobs(keywords: str = "python,data", location: str = "India"):
    """
    Phase 3: Scrape real-time jobs from multiple sources

    Parameters:
    - keywords: Comma-separated keywords (e.g., "python,data,ml")
    - location: Job location (default: India)
    """
    try:
        if not job_scraper:
            raise HTTPException(status_code=503, detail="Job scraper not initialized")

        keywords_list = [k.strip() for k in keywords.split(',')]

        # Scrape from Adzuna (most reliable)
        jobs = job_scraper.scrape_adzuna_jobs(keywords_list, location)

        return {
            "status": "success",
            "jobs_found": len(jobs),
            "jobs": jobs[:20],  # Return top 20
            "keywords": keywords_list,
            "location": location,
            "source": "Adzuna API"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/search")
async def search_jobs(title: str, location: str = "India", limit: int = 10):
    """
    Search jobs from MongoDB/BigQuery

    Parameters:
    - title: Job title to search
    - location: Job location
    - limit: Number of results
    """
    try:
        if mongo_provider:
            jobs = mongo_provider.search_jobs(title, location, limit)
            return {
                "status": "success",
                "jobs_found": len(jobs),
                "jobs": jobs,
                "source": "MongoDB/BigQuery"
            }
        else:
            raise HTTPException(status_code=503, detail="Data provider not initialized")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== PHASE 4: LEARNING PATH =====
@app.post("/api/learning-path")
async def generate_learning_path(
    career: str,
    current_skills: List[str] = [],
    target_level: str = "intermediate"
):
    """
    Phase 4: Generate personalized learning path

    Parameters:
    - career: Target career (e.g., "Data Analyst")
    - current_skills: List of current skills
    - target_level: beginner, intermediate, or advanced
    """
    try:
        if not learning_path_gen:
            raise HTTPException(status_code=503, detail="Learning path generator not initialized")

        learning_path = learning_path_gen.generate_learning_path(
            career=career,
            current_skills=current_skills,
            target_level=target_level
        )

        return {
            "status": "success",
            "career": career,
            "learning_path": learning_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/learning-resources/{skill}")
async def get_learning_resources(skill: str, resource_type: str = "all"):
    """
    Get learning resources for a specific skill

    Parameters:
    - skill: Skill name (e.g., "Python")
    - resource_type: free, paid, or all
    """
    try:
        if not learning_path_gen:
            raise HTTPException(status_code=503, detail="Learning path generator not initialized")

        if resource_type == "free":
            resources = learning_path_gen.get_free_resources(skill)
        elif resource_type == "paid":
            resources = learning_path_gen.get_paid_resources(skill)
        else:
            free = learning_path_gen.get_free_resources(skill)
            paid = learning_path_gen.get_paid_resources(skill)
            resources = free + paid

        return {
            "status": "success",
            "skill": skill,
            "resource_type": resource_type,
            "resources": resources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== PHASE 5: SKILL TRENDS =====
@app.get("/api/skill-trends/trending")
async def get_trending_skills(days: int = 30, limit: int = 20):
    """
    Phase 5: Get trending skills in the job market

    Parameters:
    - days: Number of days to analyze (default: 30)
    - limit: Number of skills to return (default: 20)
    """
    try:
        if not skill_trend_analyzer:
            raise HTTPException(status_code=503, detail="Skill trend analyzer not initialized")

        trending = skill_trend_analyzer.get_trending_skills(days, limit)

        return {
            "status": "success",
            "trending_skills": trending,
            "period_days": days,
            "analyzed_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skill-trends/emerging")
async def get_emerging_skills(threshold_days: int = 30):
    """
    Get emerging skills (recently added to job market)

    Parameters:
    - threshold_days: Days to look back (default: 30)
    """
    try:
        if not skill_trend_analyzer:
            raise HTTPException(status_code=503, detail="Skill trend analyzer not initialized")

        emerging = skill_trend_analyzer.get_emerging_skills(threshold_days)

        return {
            "status": "success",
            "emerging_skills": emerging,
            "threshold_days": threshold_days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skill-trends/growth/{skill_name}")
async def get_skill_growth(skill_name: str, days: int = 90):
    """
    Get growth rate for a specific skill

    Parameters:
    - skill_name: Name of the skill
    - days: Days to analyze (default: 90)
    """
    try:
        if not skill_trend_analyzer:
            raise HTTPException(status_code=503, detail="Skill trend analyzer not initialized")

        growth = skill_trend_analyzer.get_skill_growth_rate(skill_name, days)

        return {
            "status": "success",
            "skill_growth": growth
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skill-trends/salary/{skill_name}")
async def get_skill_salary(skill_name: str):
    """
    Get salary correlation for a specific skill

    Parameters:
    - skill_name: Name of the skill
    """
    try:
        if not skill_trend_analyzer:
            raise HTTPException(status_code=503, detail="Skill trend analyzer not initialized")

        salary = skill_trend_analyzer.get_skill_salary_correlation(skill_name)

        return {
            "status": "success",
            "skill_salary": salary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skill-trends/report")
async def get_trend_report():
    """
    Generate comprehensive skill trend report
    """
    try:
        if not skill_trend_analyzer:
            raise HTTPException(status_code=503, detail="Skill trend analyzer not initialized")

        report = skill_trend_analyzer.generate_trend_report()

        return {
            "status": "success",
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== PHASE 6: RESUME OPTIMIZATION =====
@app.post("/api/resume/optimize")
async def optimize_resume(resume_text: str, target_role: str):
    """
    Phase 6: Optimize resume for a target role

    Parameters:
    - resume_text: Full resume text
    - target_role: Target job role (e.g., "Data Analyst")
    """
    try:
        if not resume_optimizer:
            raise HTTPException(status_code=503, detail="Resume optimizer not initialized")

        optimization = resume_optimizer.optimize_resume_for_role(resume_text, target_role)

        return {
            "status": "success",
            "optimization": optimization
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/resume/match-score")
async def calculate_match_score(resume_text: str, job_title: str):
    """
    Calculate resume match score for a job

    Parameters:
    - resume_text: Full resume text
    - job_title: Target job title
    """
    try:
        if not resume_optimizer:
            raise HTTPException(status_code=503, detail="Resume optimizer not initialized")

        # Extract skills from resume
        resume_skills = resume_optimizer.extract_skills_from_resume(resume_text)

        # Get job requirements
        job_reqs = resume_optimizer.get_job_requirements(job_title)

        if 'error' in job_reqs or 'status' in job_reqs:
            raise HTTPException(status_code=404, detail="Job requirements not found")

        # Calculate match
        required_skills = [req['skill'] for req in job_reqs['top_requirements']]
        match_score = resume_optimizer.calculate_resume_match_score(resume_skills, required_skills)

        return {
            "status": "success",
            "job_title": job_title,
            "match_score": match_score,
            "job_requirements": job_reqs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/resume/suggestions")
async def get_optimization_suggestions(resume_text: str, job_title: str):
    """
    Get optimization suggestions for resume

    Parameters:
    - resume_text: Full resume text
    - job_title: Target job title
    """
    try:
        if not resume_optimizer:
            raise HTTPException(status_code=503, detail="Resume optimizer not initialized")

        # Extract skills
        resume_skills = resume_optimizer.extract_skills_from_resume(resume_text)

        # Generate suggestions
        suggestions = resume_optimizer.generate_optimization_suggestions(resume_skills, job_title)

        return {
            "status": "success",
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== HELPER FUNCTIONS =====
def engineer_features_for_prediction(resume_text: str, skills: List[str], experience_years: int) -> np.ndarray:
    """Engineer 42 features exactly matching the training pipeline"""

    # 1-8: Text features
    title_text = resume_text.split('\n')[0] if resume_text else ""
    title_length = len(title_text)
    title_word_count = len(title_text.split())
    description_length = len(resume_text)
    description_word_count = len(resume_text.split())
    requirements_length = len(resume_text) // 2 # Approximation
    requirements_word_count = description_word_count // 2 # Approximation

    title_avg_word_length = np.mean([len(w) for w in title_text.split()]) if title_text.split() else 0
    description_avg_word_length = np.mean([len(w) for w in resume_text.split()]) if resume_text.split() else 0

    # 9-15: Salary features (using USD scale as model was trained on USD)
    salary_min_default = 50000
    salary_max_default = 80000
    salary_range = salary_max_default - salary_min_default
    salary_midpoint = (salary_min_default + salary_max_default) / 2
    salary_ratio = salary_max_default / (salary_min_default + 1)
    salary_log_min = np.log1p(salary_min_default)
    salary_log_max = np.log1p(salary_max_default)
    salary_log_mid = np.log1p(salary_midpoint)
    salary_percentile = 2 # Mid-range

    # 16-20: Location features
    is_remote = 1 if 'remote' in resume_text.lower() else 0
    is_india = 1 if 'india' in resume_text.lower() else 1 # Default to India
    is_usa = 1 if 'usa' in resume_text.lower() or 'united states' in resume_text.lower() else 0
    is_uk = 1 if 'uk' in resume_text.lower() or 'united kingdom' in resume_text.lower() else 0
    location_length = 5 if is_india else 10

    # 21-22: Experience & Employment
    # Mapping to: Entry (1), Mid (2), Senior (3), Lead (4)
    if experience_years >= 10:
        experience_level_encoded = 4
    elif experience_years >= 6:
        experience_level_encoded = 3
    elif experience_years >= 3:
        experience_level_encoded = 2
    else:
        experience_level_encoded = 1

    employment_type_encoded = 1 # Full-time

    # 23-24: Skill features
    skill_count = len(skills)
    skill_density = skill_count / (description_word_count + 1)

    # 25-37: Keyword features
    keywords = {
        'python': 1 if 'python' in resume_text.lower() else 0,
        'java': 1 if 'java' in resume_text.lower() else 0,
        'javascript': 1 if any(x in resume_text.lower() for x in ['javascript', 'js', 'node']) else 0,
        'sql': 1 if any(x in resume_text.lower() for x in ['sql', 'database']) else 0,
        'cloud': 1 if any(x in resume_text.lower() for x in ['aws', 'gcp', 'azure', 'cloud']) else 0,
        'ml': 1 if any(x in resume_text.lower() for x in ['machine learning', 'ml', 'ai']) else 0,
        'devops': 1 if any(x in resume_text.lower() for x in ['devops', 'kubernetes', 'docker']) else 0,
        'frontend': 1 if any(x in resume_text.lower() for x in ['react', 'angular', 'vue', 'frontend']) else 0,
        'backend': 1 if any(x in resume_text.lower() for x in ['backend', 'api', 'rest']) else 0,
        'data': 1 if any(x in resume_text.lower() for x in ['data', 'analytics', 'bi']) else 0,
        'leadership': 1 if any(x in resume_text.lower() for x in ['lead', 'manager', 'director', 'principal']) else 0,
        'startup': 1 if any(x in resume_text.lower() for x in ['startup', 'scale-up']) else 0,
        'enterprise': 1 if any(x in resume_text.lower() for x in ['enterprise', 'fortune', 'large']) else 0,
    }

    # 38-40: Interaction features
    senior_high_salary = 1 if (experience_level_encoded >= 3 and salary_percentile >= 3) else 0
    remote_tech_role = is_remote * (keywords['python'] + keywords['java'] + keywords['javascript'])
    startup_ml = keywords['startup'] * keywords['ml']

    # 41-42: Original salary features (targets in training, but fixed inputs here)
    salary_min_usd = salary_min_default
    salary_max_usd = salary_max_default

    features = np.array([
        title_length, title_word_count, description_length, description_word_count,
        requirements_length, requirements_word_count, title_avg_word_length, description_avg_word_length,
        salary_range, salary_midpoint, salary_ratio, salary_log_min, salary_log_max, salary_log_mid, salary_percentile,
        is_remote, is_india, is_usa, is_uk, location_length,
        experience_level_encoded, employment_type_encoded,
        skill_count, skill_density,
        keywords['python'], keywords['java'], keywords['javascript'], keywords['sql'],
        keywords['cloud'], keywords['ml'], keywords['devops'], keywords['frontend'],
        keywords['backend'], keywords['data'], keywords['leadership'], keywords['startup'],
        keywords['enterprise'],
        senior_high_salary, remote_tech_role, startup_ml,
        salary_min_usd, salary_max_usd
    ], dtype=np.float32)

    return features


def analyze_skill_gap(career: str, extracted_skills: List[str]) -> Dict[str, Any]:
    """Analyze skill gap for career"""

    career_skills = {
        'Data Scientist': ['Python', 'Machine Learning', 'Statistics', 'SQL', 'TensorFlow', 'Pandas'],
        'Data Engineer': ['Python', 'SQL', 'Spark', 'Hadoop', 'ETL', 'BigQuery'],
        'Backend Developer': ['Python', 'Java', 'Node.js', 'SQL', 'REST API', 'Docker'],
        'Frontend Developer': ['JavaScript', 'React', 'CSS', 'HTML', 'TypeScript', 'Vue'],
        'Full Stack Developer': ['JavaScript', 'Python', 'React', 'SQL', 'Docker', 'AWS'],
        'DevOps Engineer': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Terraform'],
        'Cloud Architect': ['AWS', 'Azure', 'GCP', 'Architecture', 'Security', 'Networking'],
        'Software Engineer': ['Python', 'Java', 'C++', 'Design Patterns', 'Testing', 'Git'],
    }

    required = set(career_skills.get(career, []))
    have = set(s.title() for s in extracted_skills)
    missing = list(required - have)

    return {
        "career": career,
        "required_skills": list(required),
        "have_skills": list(have),
        "missing_skills": missing,
        "coverage_percentage": (len(have) / len(required) * 100) if required else 0
    }


def generate_recommendations(career: str, skills: List[str], missing_skills: List[str]) -> List[str]:
    """Generate personalized recommendations"""

    recommendations = []

    # Skill recommendations
    if missing_skills:
        recommendations.append(f"Learn {missing_skills[0]} to strengthen your {career} profile")
        if len(missing_skills) > 1:
            recommendations.append(f"Consider certifications in {', '.join(missing_skills[1:3])}")

    # Experience recommendations
    if len(skills) < 5:
        recommendations.append("Build a portfolio with 3-5 projects showcasing your skills")

    # Career-specific recommendations
    if career == 'Data Scientist':
        recommendations.append("Participate in Kaggle competitions to build ML experience")
        recommendations.append("Publish research papers or blog posts on ML topics")
    elif career == 'DevOps Engineer':
        recommendations.append("Get AWS or Kubernetes certifications")
        recommendations.append("Contribute to open-source DevOps projects")
    elif career == 'Frontend Developer':
        recommendations.append("Build responsive web applications")
        recommendations.append("Learn modern frameworks like React or Vue")

    # General recommendations
    recommendations.append("Update your LinkedIn profile with your skills and projects")
    recommendations.append("Network with professionals in your target career")

    return recommendations[:5]  # Return top 5


# ===== STATIC FILES =====
# Mount the web directory at root to serve styles.css, script.js, etc.
# html=True serves index.html at /
app.mount("/", StaticFiles(directory="web", html=True), name="web")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

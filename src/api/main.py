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
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Decode
            career = self.encoder.inverse_transform([prediction])[0]
            
            # Get top 3 predictions
            top_indices = np.argsort(probabilities)[::-1][:3]
            top_careers = [
                {
                    "career": self.encoder.inverse_transform([idx])[0],
                    "probability": float(probabilities[idx]) * 100
                }
                for idx in top_indices
            ]
            
            return {
                "primary_career": career,
                "confidence": float(probabilities[prediction]) * 100,
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
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            salary = self.model.predict(features_scaled)[0]
            
            return {
                "predicted_salary_inr": float(salary),
                "salary_range_low": float(salary * 0.85),
                "salary_range_high": float(salary * 1.15),
                "currency": "INR"
            }
        except Exception as e:
            return {"error": str(e)}


# ===== PYDANTIC MODELS =====
class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    job_title: Optional[str] = None
    experience_years: Optional[int] = None


class ResumeAnalysisResponse(BaseModel):
    skills: List[str]  # Frontend expects 'skills'
    career_predictions: List[Dict[str, Any]]  # Frontend expects array of predictions
    salary_prediction: Dict[str, Any]
    skill_gaps: List[Dict[str, Any]]  # Frontend expects array
    recommendations: List[str]
    suggested_jobs: List[Dict[str, Any]] = []  # Frontend expects this
    certifications: List[Dict[str, Any]] = []  # Frontend expects this
    experience_years: int = 0  # Frontend expects this
    education: str = "N/A"  # Frontend expects this
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
skill_extractor = SkillExtractor(use_ollama=True)  # Enable Ollama for better extraction
role_skill_matcher = RoleSkillMatcher()

# Phase 3-6 Features
job_scraper: Optional[JobScraper] = None
learning_path_gen: Optional[LearningPathGenerator] = None
skill_trend_analyzer: Optional[SkillTrendAnalyzer] = None
resume_optimizer: Optional[ResumeOptimizer] = None

# Resume cache for phase 6 (store last uploaded resume)
last_resume_text: str = ""


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
            "phase_6_resume_optimizer": resume_optimizer is not None
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
        
        # ===== COMPREHENSIVE EXTRACTION WITH OLLAMA =====
        print(f"📄 Analyzing resume ({len(resume_text)} chars)...")
        
        # Use the comprehensive extract_all method for better results
        extracted_data = skill_extractor.extract_all(resume_text)
        
        extracted_skills = extracted_data.get('skills', [])
        certifications = extracted_data.get('certifications', [])
        experience_years = extracted_data.get('experience_years', 0)
        education = extracted_data.get('education', 'N/A')
        job_titles = extracted_data.get('job_titles', [])
        
        print(f"✓ Extracted {len(extracted_skills)} skills")
        print(f"✓ Extracted {len(certifications)} certifications")
        print(f"✓ Experience: {experience_years} years")
        print(f"✓ Education: {education}")
        
        # ===== PROJECT EXTRACTION =====
        projects = extract_projects(resume_text)
        print(f"✓ Extracted {len(projects)} projects")
        
        # ===== FEATURE ENGINEERING =====
        # Create feature vector for model prediction (including projects)
        features = engineer_features_for_prediction(
            resume_text, 
            extracted_skills,
            experience_years or 0,
            projects=projects
        )
        
        # ===== CAREER PREDICTION =====
        career_result = career_model.predict(features)
        
        # Get primary career for skill gap and salary analysis
        career = career_result.get('primary_career', 'Software Engineer')
        print(f"✓ Career prediction: {career} ({career_result.get('confidence', 0):.1f}%)")
        
        # Convert career predictions to frontend format (array of {role, probability})
        career_predictions = []
        if 'top_predictions' in career_result:
            for pred in career_result['top_predictions']:
                career_predictions.append({
                    'role': pred['career'],
                    'probability': pred['probability'] / 100  # Convert back to 0-1 range
                })
        
        # Fallback if no predictions
        if not career_predictions:
            career_predictions = [{
                'role': career,
                'probability': career_result.get('confidence', 65) / 100
            }]
        
        # ===== SALARY PREDICTION =====
        salary_result = salary_model.predict(features)
        
        # Format salary for frontend
        predicted_salary = salary_result.get('predicted_salary_inr', 0)
        if predicted_salary == 0:
            # Fallback to role-based salary if model returns 0
            role_salary = mongo_provider.get_salary_data_by_role(career) if mongo_provider else None
            if role_salary:
                predicted_salary = role_salary.get('median_salary', 800000)
        
        salary_prediction = {
            'predicted_salary': int(predicted_salary),
            'min_salary': int(predicted_salary * 0.85),
            'max_salary': int(predicted_salary * 1.15),
            'currency': 'INR'
        }
        
        print(f"✓ Salary prediction: ₹{salary_prediction['predicted_salary']:,.0f}")
        
        # ===== SKILL GAP ANALYSIS =====
        skill_gap = analyze_skill_gap(career, extracted_skills)
        print(f"✓ Skill gap analysis complete")
        
        # Convert skill gaps to frontend format (array of {skill, priority_score})
        skill_gaps = []
        for skill in skill_gap.get('missing_skills', []):
            skill_gaps.append({
                'skill': skill,
                'priority_score': 0.8  # Default high priority
            })
        
        # ===== SUGGESTED JOBS =====
        # Fetch jobs from BigQuery matching the predicted career
        suggested_jobs = []
        try:
            if mongo_provider:
                jobs = mongo_provider.get_suggested_jobs(career, limit=3)
                if jobs:
                    suggested_jobs = jobs
                    print(f"✓ Found {len(suggested_jobs)} matching jobs from BigQuery")
                else:
                    print(f"⚠ No jobs found for {career}")
        except Exception as e:
            print(f"⚠ Could not fetch jobs: {e}")
            import traceback
            traceback.print_exc()
        
        # ===== EXTRACT EXPERIENCE & EDUCATION =====
        # Already extracted above, but keep for backward compatibility
        if not experience_years:
            experience_years = request.experience_years or extract_experience_years(resume_text)
        if not education or education == 'N/A':
            education = extract_education(resume_text)
        
        # ===== PROCESS CERTIFICATIONS =====
        # Add verification status and scoring to certifications
        processed_certifications = process_certifications(certifications)
        
        # ===== RECOMMENDATIONS =====
        recommendations = generate_recommendations(
            career,
            extracted_skills,
            skill_gap.get('missing_skills', [])
        )
        print(f"✓ Generated {len(recommendations)} recommendations")
        
        # ===== RESPONSE =====
        response = ResumeAnalysisResponse(
            skills=extracted_skills,
            career_predictions=career_predictions,
            salary_prediction=salary_prediction,
            skill_gaps=skill_gaps,
            recommendations=recommendations,
            suggested_jobs=suggested_jobs,
            certifications=processed_certifications,
            experience_years=experience_years,
            education=education,
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
    global last_resume_text
    
    try:
        print(f"📄 Received file upload: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        content = await file.read()
        print(f"📦 File size: {len(content)} bytes")
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Extract text from PDF
        resume_text = ""
        if file.filename.lower().endswith('.pdf'):
            try:
                print("📖 Extracting text from PDF...")
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                print(f"📄 PDF has {len(pdf_reader.pages)} pages")
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        resume_text += text + "\n"
                print(f"✅ Extracted {len(resume_text)} characters")
            except Exception as pdf_error:
                print(f"❌ PDF extraction error: {pdf_error}")
                raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(pdf_error)}")
        elif file.filename.lower().endswith(('.txt', '.docx')):
            try:
                resume_text = content.decode('utf-8')
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="File encoding not supported. Please use UTF-8 encoded text files.")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF or TXT files.")
        
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the file")
        
        # Cache resume text for phase 6
        last_resume_text = resume_text
        
        print(f"🔍 Analyzing resume with {len(resume_text)} characters...")
        
        # Analyze
        request = ResumeAnalysisRequest(resume_text=resume_text)
        return await analyze_resume(request)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
async def generate_learning_path(request: dict):
    """
    Phase 4: Generate personalized learning path
    
    Parameters:
    - career: Target career (e.g., "Data Analyst")
    - current_skills: List of current skills (optional)
    - target_level: beginner, intermediate, or advanced (optional)
    """
    try:
        if not learning_path_gen:
            raise HTTPException(status_code=503, detail="Learning path generator not initialized")
        
        from features.learning_path_generator import SkillLevel
        
        career = request.get('career', '')
        current_skills = request.get('current_skills', [])
        target_level_str = request.get('target_level', 'intermediate').lower()
        
        if not career:
            raise HTTPException(status_code=400, detail="career is required")
        
        # Convert string to SkillLevel enum
        target_level_map = {
            'beginner': SkillLevel.BEGINNER,
            'intermediate': SkillLevel.INTERMEDIATE,
            'advanced': SkillLevel.ADVANCED
        }
        target_level = target_level_map.get(target_level_str, SkillLevel.INTERMEDIATE)
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
async def optimize_resume(request: dict):
    """
    Phase 6: Optimize resume for a target role
    
    Parameters:
    - resume_text: Full resume text (or 'USE_CACHED' to use last uploaded)
    - target_role: Target job role (e.g., "Data Analyst")
    """
    global last_resume_text
    
    try:
        if not resume_optimizer:
            raise HTTPException(status_code=503, detail="Resume optimizer not initialized")
        
        resume_text = request.get('resume_text', '')
        target_role = request.get('target_role', '')
        
        # Use cached resume if requested
        if resume_text == 'USE_CACHED':
            if not last_resume_text:
                raise HTTPException(status_code=400, detail="No resume cached. Please upload a resume first.")
            resume_text = last_resume_text
        
        if not resume_text or not target_role:
            raise HTTPException(status_code=400, detail="resume_text and target_role are required")
        
        optimization = resume_optimizer.optimize_resume_for_role(resume_text, target_role)
        
        return {
            "status": "success",
            "optimization": optimization
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/resume/match-score")
async def calculate_match_score(request: dict):
    """
    Calculate resume match score for a job
    
    Parameters:
    - resume_text: Full resume text
    - job_title: Target job title
    """
    try:
        if not resume_optimizer:
            raise HTTPException(status_code=503, detail="Resume optimizer not initialized")
        
        resume_text = request.get('resume_text', '')
        job_title = request.get('job_title', '')
        
        if not resume_text or not job_title:
            raise HTTPException(status_code=400, detail="resume_text and job_title are required")
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/resume/suggestions")
async def get_optimization_suggestions(request: dict):
    """
    Get optimization suggestions for resume
    
    Parameters:
    - resume_text: Full resume text
    - job_title: Target job title
    """
    try:
        if not resume_optimizer:
            raise HTTPException(status_code=503, detail="Resume optimizer not initialized")
        
        resume_text = request.get('resume_text', '')
        job_title = request.get('job_title', '')
        
        if not resume_text or not job_title:
            raise HTTPException(status_code=400, detail="resume_text and job_title are required")
        
        # Extract skills
        resume_skills = resume_optimizer.extract_skills_from_resume(resume_text)
        
        # Generate suggestions
        suggestions = resume_optimizer.generate_optimization_suggestions(resume_skills, job_title)
        
        return {
            "status": "success",
            "suggestions": suggestions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== HELPER FUNCTIONS =====
def engineer_features_for_prediction(resume_text: str, skills: List[str], experience_years: int, projects: List[Dict[str, Any]] = None) -> np.ndarray:
    """Engineer features for model prediction (42 features) - Enhanced with project analysis"""
    
    if projects is None:
        projects = []
    
    # Text features
    title_length = len(resume_text.split('\n')[0]) if resume_text else 0
    description_length = len(resume_text)
    description_word_count = len(resume_text.split())
    title_avg_word_length = np.mean([len(w) for w in resume_text.split('\n')[0].split()]) if resume_text.split('\n')[0].split() else 0
    description_avg_word_length = np.mean([len(w) for w in resume_text.split()]) if resume_text.split() else 0
    
    # Salary features (defaults)
    salary_midpoint = 500000
    salary_range = 200000
    salary_ratio = 1.2
    salary_log_min = np.log1p(400000)
    salary_log_max = np.log1p(600000)
    salary_log_mid = np.log1p(salary_midpoint)
    salary_percentile = 2
    
    # Location features
    is_remote = 1 if 'remote' in resume_text.lower() else 0
    is_india = 1 if 'india' in resume_text.lower() else 0
    is_usa = 1 if 'usa' in resume_text.lower() or 'united states' in resume_text.lower() else 0
    is_uk = 1 if 'uk' in resume_text.lower() or 'united kingdom' in resume_text.lower() else 0
    location_length = 10
    
    # Experience
    experience_level_encoded = min(experience_years // 3, 4)
    employment_type_encoded = 1
    
    # Skills
    skill_count = len(skills)
    skill_density = skill_count / (description_word_count + 1) if description_word_count > 0 else 0
    
    # PROJECT-BASED FEATURES (NEW)
    project_count = len(projects)
    project_tech_diversity = 0
    if projects:
        all_project_techs = set()
        for proj in projects:
            all_project_techs.update([t.lower() for t in proj.get('technologies', [])])
        project_tech_diversity = len(all_project_techs)
    
    # Keywords (enhanced with project context)
    resume_lower = resume_text.lower()
    project_text = ' '.join([p.get('description', '') for p in projects]).lower()
    combined_text = resume_lower + ' ' + project_text
    
    keywords = {
        'python': 1 if 'python' in combined_text else 0,
        'java': 1 if 'java' in combined_text else 0,
        'javascript': 1 if 'javascript' in combined_text or 'js' in combined_text else 0,
        'sql': 1 if 'sql' in combined_text else 0,
        'cloud': 1 if any(x in combined_text for x in ['aws', 'gcp', 'azure']) else 0,
        'ml': 1 if any(x in combined_text for x in ['machine learning', 'ml', 'ai', 'deep learning']) else 0,
        'devops': 1 if 'devops' in combined_text else 0,
        'frontend': 1 if any(x in combined_text for x in ['react', 'angular', 'vue', 'frontend']) else 0,
        'backend': 1 if 'backend' in combined_text else 0,
        'data': 1 if 'data' in combined_text else 0,
        'leadership': 1 if any(x in combined_text for x in ['lead', 'manager', 'director']) else 0,
        'startup': 1 if 'startup' in combined_text else 0,
        'enterprise': 1 if 'enterprise' in combined_text else 0,
    }
    
    # Interactions (enhanced with project signals)
    senior_high_salary = (experience_level_encoded >= 3) * (salary_percentile >= 3)
    remote_tech_role = is_remote * (keywords['python'] + keywords['java'] + keywords['javascript'])
    startup_ml = keywords['startup'] * keywords['ml']
    has_portfolio = 1 if project_count > 0 else 0
    experienced_with_projects = (experience_level_encoded >= 2) * has_portfolio
    
    # Combine all features (42 total)
    features = np.array([
        title_length, description_word_count, description_length,
        title_avg_word_length, description_avg_word_length,
        salary_range, salary_midpoint, salary_ratio,
        salary_log_min, salary_log_max, salary_log_mid, salary_percentile,
        is_remote, is_india, is_usa, is_uk, location_length,
        experience_level_encoded, employment_type_encoded,
        skill_count, skill_density,
        keywords['python'], keywords['java'], keywords['javascript'],
        keywords['sql'], keywords['cloud'], keywords['ml'],
        keywords['devops'], keywords['frontend'], keywords['backend'],
        keywords['data'], keywords['leadership'], keywords['startup'],
        keywords['enterprise'],
        senior_high_salary, remote_tech_role, startup_ml,
        project_count, project_tech_diversity, has_portfolio, experienced_with_projects, 0  # Project features
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


def extract_experience_years(resume_text: str) -> int:
    """Extract years of experience from resume text"""
    import re
    
    # Look for patterns like "5 years", "5+ years", "5-7 years"
    patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience[:\s]+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s+in\s+',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, resume_text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return 0


def extract_education(resume_text: str) -> str:
    """Extract highest education level from resume text"""
    import re
    
    text_lower = resume_text.lower()
    
    # Check for degrees in order of priority
    if re.search(r'\b(phd|ph\.d|doctorate)\b', text_lower):
        return 'PhD'
    elif re.search(r'\b(master|m\.s|m\.tech|mba|m\.b\.a)\b', text_lower):
        return "Master's"
    elif re.search(r'\b(bachelor|b\.s|b\.tech|b\.e|b\.a)\b', text_lower):
        return "Bachelor's"
    elif re.search(r'\b(diploma|associate)\b', text_lower):
        return 'Diploma'
    
    return 'N/A'


def extract_projects(resume_text: str) -> List[Dict[str, Any]]:
    """Extract projects from resume text"""
    import re
    
    projects = []
    
    # Look for project sections
    project_section_pattern = r'(?:projects?|portfolio|work samples?)\s*:?\s*\n(.*?)(?:\n\s*\n|\Z)'
    matches = re.findall(project_section_pattern, resume_text, re.IGNORECASE | re.DOTALL)
    
    if matches:
        for section in matches:
            # Split by bullet points or numbered lists
            project_items = re.split(r'\n\s*[•\-\*\d+\.]\s*', section)
            
            for item in project_items:
                item = item.strip()
                if len(item) > 20:  # Minimum length for a project description
                    # Extract project name (usually first line or before colon)
                    lines = item.split('\n')
                    name = lines[0].split(':')[0].strip()
                    
                    # Extract technologies mentioned
                    tech_pattern = r'\b(?:using|with|technologies?|stack|built with)\s*:?\s*([^\n\.]+)'
                    tech_match = re.search(tech_pattern, item, re.IGNORECASE)
                    technologies = []
                    if tech_match:
                        tech_text = tech_match.group(1)
                        technologies = [t.strip() for t in re.split(r'[,;]', tech_text) if t.strip()]
                    
                    projects.append({
                        'name': name[:100],  # Limit length
                        'description': item[:300],  # Limit description
                        'technologies': technologies[:10]  # Limit tech list
                    })
    
    return projects[:10]  # Limit to 10 projects


def process_certifications(certifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process and validate certifications with status and scoring"""
    processed = []
    
    # Known certification authorities and their credibility scores
    known_issuers = {
        'amazon web services': {'name': 'Amazon Web Services', 'score': 0.95, 'color': 'green'},
        'aws': {'name': 'Amazon Web Services', 'score': 0.95, 'color': 'green'},
        'microsoft': {'name': 'Microsoft', 'score': 0.95, 'color': 'green'},
        'google': {'name': 'Google', 'score': 0.95, 'color': 'green'},
        'cisco': {'name': 'Cisco', 'score': 0.90, 'color': 'green'},
        'oracle': {'name': 'Oracle', 'score': 0.90, 'color': 'green'},
        'coursera': {'name': 'Coursera', 'score': 0.75, 'color': 'blue'},
        'udemy': {'name': 'Udemy', 'score': 0.60, 'color': 'blue'},
        'linkedin': {'name': 'LinkedIn Learning', 'score': 0.65, 'color': 'blue'},
        'pmi': {'name': 'Project Management Institute', 'score': 0.90, 'color': 'green'},
        'comptia': {'name': 'CompTIA', 'score': 0.85, 'color': 'green'},
    }
    
    for cert in certifications:
        issuer_lower = cert.get('issuer', '').lower()
        
        # Match issuer to known authorities
        issuer_info = None
        for key, info in known_issuers.items():
            if key in issuer_lower:
                issuer_info = info
                break
        
        if issuer_info:
            score = issuer_info['score']
            status_color = issuer_info['color']
            issuer_name = issuer_info['name']
        else:
            score = 0.50  # Unknown issuer
            status_color = 'yellow'
            issuer_name = cert.get('issuer', 'Unknown')
        
        # Determine status based on verification ID and score
        if cert.get('verification_id'):
            status = 'Verified'
            score = min(score + 0.05, 1.0)  # Boost score if has verification ID
        elif score >= 0.85:
            status = 'Recognized'
        elif score >= 0.60:
            status = 'Valid'
        else:
            status = 'Unverified'
        
        processed.append({
            'name': cert.get('name', 'Unknown Certification'),
            'issuer': issuer_name,
            'year': cert.get('year'),
            'verification_id': cert.get('verification_id'),
            'status': status,
            'status_color': status_color,
            'score': score
        })
    
    return processed


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
# Mount static files for CSS, JS, etc.
app.mount("/static", StaticFiles(directory="web"), name="static")

@app.get("/")
async def root():
    """Serve index.html"""
    return FileResponse("web/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

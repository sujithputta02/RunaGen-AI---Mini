"""
FastAPI Server v2 - Using 91.42% Accurate Models
Integrates advanced ensemble models with BigQuery data
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
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
import re
import base64
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
from utils.mongodb_client import MongoDBClient

# Phase 3-6 Features
from features.job_scraper import JobScraper
from features.learning_path_generator import LearningPathGenerator
from features.skill_trend_analyzer import SkillTrendAnalyzer
from features.resume_optimizer import ResumeOptimizer
from features.linkedin_verifier import get_linkedin_verifier

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
    filename: Optional[str] = "unknown"
    guest_id: Optional[str] = "guest_default"
    pdf_base64: Optional[str] = None


class ResumeAnalysisResponse(BaseModel):
    skills: List[str]  # Frontend expects 'skills'
    career_predictions: List[Dict[str, Any]]  # Frontend expects array of predictions
    salary_prediction: Dict[str, Any]
    skill_gaps: List[Dict[str, Any]]  # Frontend expects array
    recommendations: List[str]
    suggested_jobs: List[Dict[str, Any]] = []  # Frontend expects this
    certifications: List[Dict[str, Any]] = []  # Frontend expects this
    projects: List[Dict[str, Any]] = []  # Frontend expects this
    experience_years: int = 0  # Frontend expects this
    education: str = "N/A"  # Frontend expects this
    social_links: Dict[str, Optional[str]] = {}  # LinkedIn, GitHub, Portfolio
    linkedin_verified_count: int = 0  # Number of LinkedIn-verified certs
    analysis_timestamp: str
    model_accuracy: float


# ===== LIFESPAN =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events - Lightweight startup"""
    print("\n" + "="*70)
    print("🚀 RunaGen AI API v2 - Starting (Lightweight Mode)")
    print("="*70)
    
    # Load models
    global career_model, salary_model, mongo_provider, mongodb_client
    global job_scraper, learning_path_gen, skill_trend_analyzer, resume_optimizer
    
    # Initialize models (lazy load)
    career_model = AdvancedCareerPredictor()
    salary_model = AdvancedSalaryPredictor()
    
    # Try to load models, but don't block startup
    try:
        career_model.load()
    except Exception as e:
        print(f"⚠ Career model load deferred: {e}")
    
    try:
        salary_model.load()
    except Exception as e:
        print(f"⚠ Salary model load deferred: {e}")
    
    # Initialize MongoDB (with timeout)
    try:
        mongo_provider = get_data_provider()
        print("✓ BigQuery data provider initialized")
    except Exception as e:
        print(f"⚠ BigQuery provider failed: {e}")
        mongo_provider = None
    
    # Initialize MongoDB Client for storage
    try:
        mongodb_client = MongoDBClient()
        if mongodb_client.connect():
            print("✓ MongoDB storage client initialized")
        else:
            print("⚠ MongoDB storage client failed to connect")
    except Exception as e:
        print(f"⚠ MongoDB client failed: {e}")
        mongodb_client = None
    
    # Initialize Phase 3-6 Features
    try:
        job_scraper = JobScraper()
        print("✓ Job scraper initialized")
    except Exception as e:
        print(f"❌ Job scraper failed: {e}")
        job_scraper = None
    
    try:
        learning_path_gen = LearningPathGenerator()
        print("✓ Learning path generator initialized")
    except Exception as e:
        print(f"❌ Learning path generator failed: {e}")
        print(f"   Error details: {str(e)}")
        learning_path_gen = None
    
    try:
        skill_trend_analyzer = SkillTrendAnalyzer()
        print("✓ Skill trend analyzer initialized")
    except Exception as e:
        print(f"❌ Skill trend analyzer failed: {e}")
        print(f"   Error details: {str(e)}")
        skill_trend_analyzer = None
    
    try:
        resume_optimizer = ResumeOptimizer()
        print("✓ Resume optimizer initialized")
    except Exception as e:
        print(f"❌ Resume optimizer failed: {e}")
        print(f"   Error details: {str(e)}")
        resume_optimizer = None
    
    print("✓ API ready (features will load on first use)")
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
mongodb_client: Optional[MongoDBClient] = None

# Initialize skill extractor with environment-aware settings
import os
_is_cloud = os.getenv("ENVIRONMENT", "local").lower() == "cloud"
_ollama_url = os.getenv("OLLAMA_URL", "").strip()
_use_ollama = _ollama_url != ""  # Use Ollama if URL is configured (both local and cloud)
skill_extractor = SkillExtractor(use_ollama=_use_ollama, use_gemini=False)  # Disable Gemini, use Ollama only
role_skill_matcher = RoleSkillMatcher()

# Phase 3-6 Features
job_scraper: Optional[JobScraper] = None
learning_path_gen: Optional[LearningPathGenerator] = None
skill_trend_analyzer: Optional[SkillTrendAnalyzer] = None
resume_optimizer: Optional[ResumeOptimizer] = None

# Resume cache for phase 6 (store last uploaded resume)
last_resume_text: str = ""
last_extracted_skills: List[str] = []
last_predicted_career: str = ""


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
        projects = extracted_data.get('projects', [])
        
        # Cache for later use (e.g., learning path)
        global last_extracted_skills
        last_extracted_skills = extracted_skills
        
        # ===== VALIDATE EXPERIENCE YEARS =====
        # If LLM returned suspicious experience, use strict heuristic instead
        if experience_years > 0:
            # Double-check with strict heuristic
            strict_experience = extract_experience_years(resume_text)
            if strict_experience == 0:
                # Heuristic says no experience, so override LLM
                experience_years = 0
                print(f"⚠ LLM returned {extracted_data.get('experience_years', 0)} years, but strict heuristic found 0. Using 0.")
        
        print(f"✓ Extracted {len(extracted_skills)} skills")
        print(f"✓ Extracted {len(certifications)} certifications")
        print(f"✓ Extracted {len(projects)} projects")
        print(f"✓ Experience: {experience_years} years")
        print(f"✓ Education: {education}")
        
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
        
        # Cache for later use
        global last_predicted_career
        last_predicted_career = career
        
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
        # Fetch real jobs from Adzuna API matching the predicted career
        suggested_jobs = []
        try:
            if job_scraper:
                print(f"🔍 Fetching real jobs from Adzuna for: {career}")
                adzuna_jobs = job_scraper.scrape_adzuna_jobs([career], "India", limit=5)
                
                if adzuna_jobs:
                    # Format Adzuna jobs properly - ensure complete JSON without truncation
                    formatted_jobs = []
                    for job in adzuna_jobs:
                        if isinstance(job, dict):
                            # Ensure all fields are properly converted to strings/ints
                            formatted_job = {
                                'title': str(job.get('title', 'Position')).strip() if job.get('title') else 'Position',
                                'company': str(job.get('company', 'Company')).strip() if job.get('company') else 'Company',
                                'location': str(job.get('location', 'India')).strip() if job.get('location') else 'India',
                                'salary_min': int(job.get('salary_min', 0)) if job.get('salary_min') and str(job.get('salary_min')).replace('.','').isdigit() else 0,
                                'salary_max': int(job.get('salary_max', 0)) if job.get('salary_max') and str(job.get('salary_max')).replace('.','').isdigit() else 0,
                                'currency': str(job.get('currency', 'INR')).strip() if job.get('currency') else 'INR',
                                'description': str(job.get('description', ''))[:200].strip() if job.get('description') else '',
                                'url': str(job.get('url', '#')).strip() if job.get('url') else '#'
                            }
                            
                            # CROSS-REFERENCE: If salary is 0, check BigQuery for this company's historical salary
                            if formatted_job['salary_min'] == 0 and mongo_provider and hasattr(mongo_provider, 'get_company_salary'):
                                company_sal = mongo_provider.get_company_salary(formatted_job['company'], career)
                                if company_sal:
                                    formatted_job['salary_min'] = company_sal['min']
                                    formatted_job['salary_max'] = company_sal['max']
                                    formatted_job['is_actual_bigquery'] = True
                                    print(f"📊 Filled actual BigQuery salary for {formatted_job['company']}: {company_sal['min']}")
                        else:
                            formatted_job = {
                                'title': str(getattr(job, 'title', 'Position')).strip(),
                                'company': str(getattr(job, 'company', 'Company')).strip(),
                                'location': str(getattr(job, 'location', 'India')).strip(),
                                'salary_min': int(getattr(job, 'salary_min', 0)) if getattr(job, 'salary_min', 0) else 0,
                                'salary_max': int(getattr(job, 'salary_max', 0)) if getattr(job, 'salary_max', 0) else 0,
                                'currency': str(getattr(job, 'currency', 'INR')).strip(),
                                'description': str(getattr(job, 'description', ''))[:200].strip(),
                                'url': str(getattr(job, 'url', '#')).strip()
                            }
                        formatted_jobs.append(formatted_job)
                    
                    suggested_jobs = formatted_jobs
                    print(f"✅ Found {len(suggested_jobs)} real jobs from Adzuna")
                else:
                    print(f"⚠️ No jobs found from Adzuna for {career}")
            else:
                print(f"⚠️ Job scraper not initialized")
        except Exception as e:
            print(f"❌ Could not fetch jobs from Adzuna: {e}")
            import traceback
            traceback.print_exc()
        
        # ===== EXTRACT EXPERIENCE & EDUCATION =====
        # Already extracted above, but keep for backward compatibility
        if experience_years is None or experience_years < 0:
            experience_years = request.experience_years or extract_experience_years(resume_text)
        if not education or education == 'N/A':
            education = extract_education(resume_text)
        
        # ===== PROCESS CERTIFICATIONS WITH LINKEDIN VERIFICATION =====
        # Extract social links and verify certifications
        print("🔍 Starting LinkedIn verification...")
        try:
            linkedin_verifier = get_linkedin_verifier()
            verification_result = linkedin_verifier.get_verification_summary(resume_text, certifications)
            
            print(f"✓ Social Links: LinkedIn={verification_result['linkedin_available']}, "
                  f"GitHub={verification_result['github_available']}, "
                  f"Portfolio={verification_result['portfolio_available']}")
            print(f"✓ LinkedIn Certifications Found: {verification_result['linkedin_certifications_found']}")
        except Exception as e:
            print(f"⚠️ LinkedIn verification failed: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to empty verification result
            verification_result = {
                'verified_certifications': certifications,
                'social_links': {'linkedin': None, 'github': None, 'portfolio': None},
                'linkedin_certifications_found': 0,
                'verification_notes': [],
                'profile_recommendations': [],
                'linkedin_available': False,
                'github_available': False,
                'portfolio_available': False
            }
        
        # Process certifications with traditional scoring
        processed_certifications = process_certifications(verification_result['verified_certifications'])
        
        # Add LinkedIn verification status to each certification
        for cert in processed_certifications:
            # Check if this cert was verified via LinkedIn
            matching_verified = next(
                (v for v in verification_result['verified_certifications'] 
                 if v.get('name', '').lower() == cert.get('name', '').lower()),
                None
            )
            if matching_verified:
                cert['linkedin_verified'] = matching_verified.get('linkedin_verified', False)
                cert['verification_source'] = matching_verified.get('verification_source', 'Resume Only')
        
        # Log verification results
        print(f"✓ Social Links: LinkedIn={verification_result['linkedin_available']}, "
              f"GitHub={verification_result['github_available']}, "
              f"Portfolio={verification_result['portfolio_available']}")
        print(f"✓ LinkedIn Certifications Found: {verification_result['linkedin_certifications_found']}")
        
        # ===== RECOMMENDATIONS (Enhanced with profile recommendations) =====
        recommendations = generate_recommendations(
            career,
            extracted_skills,
            skill_gap.get('missing_skills', [])
        )
        
        # Add profile recommendations from LinkedIn verifier
        recommendations.extend(verification_result['profile_recommendations'])
        print(f"✓ Generated {len(recommendations)} recommendations")
        
        # ===== RESPONSE =====
        linkedin_verified_count = sum(1 for cert in processed_certifications if cert.get('linkedin_verified', False))
        
        response = ResumeAnalysisResponse(
            skills=extracted_skills,
            career_predictions=career_predictions,
            salary_prediction=salary_prediction,
            skill_gaps=skill_gaps,
            recommendations=recommendations,
            suggested_jobs=suggested_jobs,
            certifications=processed_certifications,
            projects=projects,
            experience_years=experience_years,
            education=education,
            social_links=verification_result['social_links'],
            linkedin_verified_count=linkedin_verified_count,
            analysis_timestamp=datetime.now().isoformat(),
            model_accuracy=91.42
        )
        
        print(f"✅ Analysis complete")
        
        # ===== STORE COMPREHENSIVE RESUME RECORD IN MONGODB =====
        try:
            if mongodb_client:
                # Convert the full response to a dictionary for storage
                response_data = response.model_dump()
                
                resume_record = {
                    "timestamp": response.analysis_timestamp,
                    "guest_id": request.guest_id or "guest_default",
                    "filename": request.filename or "unknown",
                    "resume_text": request.resume_text, # Store full text for future phases
                    "resume_pdf_base64": getattr(request, 'pdf_base64', None), # Store PDF for viewer
                    "resume_text_preview": (request.resume_text[:500] + "...") if request.resume_text else "",
                    "extracted_data": {
                        "skills": extracted_skills,
                        "experience_years": experience_years,
                        "education": education,
                        "certifications": processed_certifications,
                        "projects": projects
                    },
                    "analysis_results": {
                        "career_predictions": career_predictions,
                        "salary_prediction": salary_prediction,
                        "suggested_jobs": suggested_jobs, # Persist jobs in history
                        "skill_gaps": skill_gaps,
                        "recommendations": recommendations,
                        "linkedin_verification": {
                            "social_links": verification_result['social_links'],
                            "verified_count": linkedin_verified_count
                        }
                    },
                    # Store the complete raw response for future-proofing
                    "full_response": response_data,
                    "model_accuracy": 91.42,
                    "environment": os.getenv("ENVIRONMENT", "local")
                }
                
                # Store in 'resumes' collection
                mongodb_client.db["resumes"].insert_one(resume_record)
                print(f"💾 Full resume analysis record stored for guest {request.guest_id}")
        except Exception as store_error:
            print(f"⚠️ Failed to store comprehensive resume record: {store_error}")
            
        print(f"   - Skills: {len(extracted_skills)}")
        print(f"   - Career: {career}")
        print(f"   - Salary: ₹{salary_prediction['predicted_salary']:,.0f}")
        print(f"   - Suggested Jobs: {len(suggested_jobs)}")
        print(f"   - Certifications: {len(processed_certifications)}")
        print(f"   - Projects: {len(projects)}")
        print("")
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    guest_id: str = Form("guest_default")
):
    """Upload and analyze resume from PDF/DOCX"""
    global last_resume_text
    
    try:
        print(f"📄 Received file upload: {file.filename} | Guest ID: {guest_id}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        content = await file.read()
        print(f"📦 File size: {len(content)} bytes")
        
        # Store PDF as Base64 for history retrieval
        pdf_base64 = base64.b64encode(content).decode('utf-8') if file.filename.lower().endswith('.pdf') else None
        
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
        request = ResumeAnalysisRequest(
            resume_text=resume_text,
            filename=file.filename,
            guest_id=guest_id,
            pdf_base64=pdf_base64
        )
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
    global learning_path_gen
    
    try:
        if not learning_path_gen:
            try:
                from features.learning_path_generator import LearningPathGenerator, SkillLevel
                learning_path_gen = LearningPathGenerator()
                print("✓ LearningPathGenerator initialized successfully")
            except Exception as init_error:
                print(f"❌ Failed to initialize LearningPathGenerator: {init_error}")
                import traceback
                traceback.print_exc()
                raise HTTPException(
                    status_code=503,
                    detail=f"Learning path generator not available: {str(init_error)}"
                )
        
        from features.learning_path_generator import SkillLevel
        
        career = request.get('career', last_predicted_career or '')
        current_skills = request.get('current_skills', [])
        
        # If no skills provided (or empty list), use cached skills from last resume upload
        if (not current_skills or len(current_skills) == 0) and last_extracted_skills:
            current_skills = last_extracted_skills
            print(f"ℹ Using {len(current_skills)} cached skills from last resume upload")
        
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
        
        # ===== STORE LEARNING PATH IN MONGODB =====
        try:
            if mongodb_client:
                lp_record = {
                    "timestamp": datetime.now().isoformat(),
                    "guest_id": request.get('guest_id', 'guest_default'),
                    "career": career,
                    "target_level": target_level_str,
                    "current_skills": current_skills,
                    "learning_path": learning_path,
                    "environment": os.getenv("ENVIRONMENT", "local")
                }
                mongodb_client.db["learning_paths"].insert_one(lp_record)
                print(f"💾 Learning path stored in MongoDB (Collection: learning_paths)")
        except Exception as store_error:
            print(f"⚠️ Failed to store learning path record: {store_error}")
            
        return {
            "status": "success",
            "career": career,
            "learning_path": learning_path
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in generate_learning_path: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating learning path: {str(e)}")


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
async def get_trending_skills(days: int = 30, limit: int = 20, role: str = None):
    """
    Phase 5: Get trending skills in the job market
    
    Parameters:
    - days: Number of days to analyze (default: 30)
    - limit: Number of skills to return (default: 20)
    """
    try:
        # Initialize if not already done
        global skill_trend_analyzer
        if not skill_trend_analyzer:
            try:
                skill_trend_analyzer = SkillTrendAnalyzer()
                print("✓ SkillTrendAnalyzer initialized successfully")
            except Exception as init_error:
                print(f"❌ Failed to initialize SkillTrendAnalyzer: {init_error}")
                import traceback
                traceback.print_exc()
                raise HTTPException(
                    status_code=503, 
                    detail=f"Skill trend analyzer not available: {str(init_error)}"
                )
        
        trending = skill_trend_analyzer.get_trending_skills(days, limit, role)
        
        if not trending:
            raise HTTPException(
                status_code=404,
                detail="No trending skills data found. Please ensure BigQuery has job data."
            )
        
        return {
            "status": "success",
            "trending_skills": trending,
            "period_days": days,
            "analyzed_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_trending_skills: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error analyzing trending skills: {str(e)}")


@app.get("/api/skill-trends/emerging")
async def get_emerging_skills(threshold_days: int = 30, role: str = None):
    """
    Get emerging skills (recently added to job market)
    
    Parameters:
    - threshold_days: Days to look back (default: 30)
    """
    try:
        # Initialize if not already done
        global skill_trend_analyzer
        if not skill_trend_analyzer:
            try:
                skill_trend_analyzer = SkillTrendAnalyzer()
                print("✓ SkillTrendAnalyzer initialized successfully")
            except Exception as init_error:
                print(f"❌ Failed to initialize SkillTrendAnalyzer: {init_error}")
                import traceback
                traceback.print_exc()
                raise HTTPException(
                    status_code=503,
                    detail=f"Skill trend analyzer not available: {str(init_error)}"
                )
        
        emerging = skill_trend_analyzer.get_emerging_skills(threshold_days, role)
        
        if not emerging:
            raise HTTPException(
                status_code=404,
                detail="No emerging skills data found. Please ensure BigQuery has recent job data."
            )
        
        return {
            "status": "success",
            "emerging_skills": emerging,
            "threshold_days": threshold_days
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_emerging_skills: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error analyzing emerging skills: {str(e)}")


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


@app.get("/api/skill-trends/role/{role}")
async def get_role_based_trends(role: str, days: int = 30):
    """
    Get comprehensive skill trends for a specific role with graph data
    
    Parameters:
    - role: Job role (e.g., "Data Analyst", "Software Engineer")
    - days: Number of days to analyze (default: 30)
    
    Returns:
    - Skill demand for the role
    - Available job postings
    - Graph data for visualization (skill demand, timeline, salary trends)
    """
    global skill_trend_analyzer
    
    try:
        # Initialize if not already done
        if not skill_trend_analyzer:
            try:
                skill_trend_analyzer = SkillTrendAnalyzer()
                print("✓ SkillTrendAnalyzer initialized successfully")
            except Exception as init_error:
                print(f"❌ Failed to initialize SkillTrendAnalyzer: {init_error}")
                import traceback
                traceback.print_exc()
                raise HTTPException(
                    status_code=503,
                    detail=f"Skill trend analyzer not available: {str(init_error)}"
                )
        
        # Get role-based trends with graph data
        trends = skill_trend_analyzer.get_role_based_trends(role, days)
        
        if 'error' in trends:
            raise HTTPException(status_code=500, detail=trends['error'])
        
        if not trends.get('available_jobs'):
            logger.warning(f"No jobs found for role: {role}")
        
        return {
            "status": "success",
            "role": role,
            "analysis_period_days": days,
            "trends": trends
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_role_based_trends: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error analyzing role trends: {str(e)}")


# ===== PHASE 6: RESUME OPTIMIZATION =====
@app.post("/api/resume/optimize")
async def optimize_resume(request: dict):
    """
    Phase 6: Optimize resume for a target role
    
    Parameters:
    - resume_text: Full resume text (or 'USE_CACHED' to use last uploaded)
    - target_role: Target job role (e.g., "Data Analyst")
    """
    global last_resume_text, resume_optimizer
    
    try:
        # Initialize if not already done
        if not resume_optimizer:
            try:
                resume_optimizer = ResumeOptimizer()
                print("✓ ResumeOptimizer initialized successfully")
            except Exception as init_error:
                print(f"❌ Failed to initialize ResumeOptimizer: {init_error}")
                import traceback
                traceback.print_exc()
                raise HTTPException(
                    status_code=503,
                    detail=f"Resume optimizer not available: {str(init_error)}"
                )
        
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
        
        # ===== STORE OPTIMIZATION IN MONGODB =====
        try:
            if mongodb_client:
                opt_record = {
                    "timestamp": datetime.now().isoformat(),
                    "guest_id": request.get('guest_id', 'guest_default'),
                    "target_role": target_role,
                    "filename": getattr(request, 'filename', 'cached' if request.get('resume_text') == 'USE_CACHED' else 'direct_text'),
                    "optimization_results": optimization,
                    "environment": os.getenv("ENVIRONMENT", "local")
                }
                mongodb_client.db["optimizations"].insert_one(opt_record)
                print(f"💾 Resume optimization stored in MongoDB (Collection: optimizations)")
        except Exception as store_error:
            print(f"⚠️ Failed to store optimization record: {store_error}")
            
        if 'error' in optimization:
            raise HTTPException(status_code=500, detail=optimization['error'])
        
        return {
            "status": "success",
            "optimization": optimization
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in optimize_resume: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error optimizing resume: {str(e)}")


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
    """Extract years of experience from resume text - ULTRA STRICT"""
    import re
    from datetime import datetime
    
    # First check: Is there a work experience section?
    has_work_section = bool(re.search(
        r'(?:work\s+experience|professional\s+experience|employment|career|experience)',
        resume_text,
        re.IGNORECASE
    ))
    
    if not has_work_section:
        return 0
    
    # Look for explicit experience mentions
    patterns = [
        r'total\s+(?:professional\s+)?experience[:\s]+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience',
        r'experience[:\s]+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s+in\s+(?:industry|field|software|development)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, resume_text, re.IGNORECASE)
        if match:
            years = int(match.group(1))
            # Only return if it's a reasonable number (1-60 years)
            if 1 <= years <= 60:
                return years
    
    # Fallback: Try to calculate from work history dates
    # Look for date ranges like "Jan 2020 - Present" or "2020-2023"
    # But be strict - only count if we have clear employment dates
    date_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)?\s*(\d{4})\s*[-–]\s*(?:Present|Current|Now|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)?\s*(\d{4})?'
    
    matches = re.findall(date_pattern, resume_text, re.IGNORECASE)
    
    # Only calculate if we have multiple date ranges (indicating real work history)
    if len(matches) >= 2:
        years_list = []
        current_year = datetime.now().year
        for match in matches:
            start_year = int(match[0])
            end_year = int(match[1]) if match[1] else current_year
            
            # Validate years are reasonable
            if 1990 <= start_year <= current_year and 1990 <= end_year <= current_year:
                if start_year < end_year:
                    years_list.append(end_year - start_year)
        
        if years_list:
            total_years = sum(years_list)
            # Return average if multiple roles, but cap at reasonable max
            avg_years = total_years // len(years_list)
            return min(avg_years, 60)
    
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
    
    # BLACKLIST: Exact certification names that are NOT real certifications
    # These are hackathons, competitions, and courses (NOT professional certifications)
    blacklist_exact = [
        'nasa space apps challenge',
        'google gen ai exchange hackathon',
        'microsoft imagine cup',
        'kaggle 5-day ai agents intensive course',
        'kaggle intensive course',
    ]
    
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
        'kaggle': {'name': 'Kaggle', 'score': 0.70, 'color': 'blue'},
    }
    
    for cert in certifications:
        cert_name = cert.get('name', '').lower().strip()
        
        # FILTER: Skip if certification name is in the exact blacklist
        if cert_name in blacklist_exact:
            continue  # Skip this certification
        
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



# ===== SILENCE CHROME DEVTOOLS 404s =====
@app.get("/.well-known/appspecific/com.chrome.devtools.json")
async def silence_devtools():
    return {"status": "ignored"}


# ===== HISTORY ENDPOINTS =====
@app.get("/api/history/{guest_id}")
async def get_user_history(guest_id: str):
    """Retrieve analysis history for a specific guest ID"""
    try:
        if not mongodb_client:
            raise HTTPException(status_code=503, detail="Storage not available")
        
        # Get resume history
        resumes = list(mongodb_client.db["resumes"].find(
            {"guest_id": guest_id},
            {"full_response": 0, "resume_text_preview": 0, "_id": 1}
        ).sort("timestamp", -1))
        
        # Convert ObjectId to string
        for r in resumes:
            r["id"] = str(r["_id"])
            del r["_id"]
            
        return {
            "status": "success",
            "guest_id": guest_id,
            "count": len(resumes),
            "history": resumes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/record/{record_id}")
async def get_history_record(record_id: str):
    """Retrieve full details of a specific history record and activate it in session"""
    global last_resume_text, last_extracted_skills, last_predicted_career
    try:
        if not mongodb_client:
            raise HTTPException(status_code=503, detail="Storage not available")
        
        from bson import ObjectId
        record = mongodb_client.db["resumes"].find_one({"_id": ObjectId(record_id)})
        
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # ACTIVATE this record in global cache so other phases (Optimize, etc) work
        last_resume_text = record.get("resume_text", "")
        last_extracted_skills = record.get("extracted_data", {}).get("skills", [])
        last_predicted_career = record.get("analysis_results", {}).get("career_predictions", [{}])[0].get("role", "")
        
        print(f"🔄 Activated history record {record_id} for guest {record.get('guest_id')}")
        
        # Convert ObjectId to string
        record["id"] = str(record["_id"])
        del record["_id"]
        
        return {
            "status": "success",
            "record": record
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== STATIC FILES MOUNT (MUST BE LAST) =====
# Mount web directory for frontend - this must be after all API routes
try:
    web_dir = Path(__file__).parent.parent.parent / "web"
    if web_dir.exists():
        app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="static")
        print(f"✓ Static files mounted from {web_dir}")
    else:
        print(f"⚠ Web directory not found at {web_dir}")
except Exception as e:
    print(f"⚠ Failed to mount static files: {e}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

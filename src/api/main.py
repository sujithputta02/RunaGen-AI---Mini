"""
FastAPI Server for Resume Analytics
Exposes ML models as REST endpoints
"""
from fastapi import FastAPI, UploadFile, File, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.responses import FileResponse # type: ignore
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
from contextlib import asynccontextmanager
import sys
import os
import asyncio
import pandas as pd # type: ignore
import numpy as np # type: ignore
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ml.model_1_skill_extraction import SkillExtractor # type: ignore
from ml.model_2_career_prediction import CareerPredictor # type: ignore
from ml.model_3_skill_gap import SkillGapAnalyzer # type: ignore
from ml.model_4_salary_prediction import SalaryPredictor # type: ignore
from ml.recommendation_generator import RecommendationGenerator # type: ignore
from ml.role_skill_matcher import RoleSkillMatcher # type: ignore
from ml.certificate_validator import CertificateValidator # type: ignore
from api.mongodb_data_provider import get_data_provider # type: ignore
import PyPDF2 # type: ignore
import io

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the FastAPI application"""
    # Load models on startup
    load_trained_models()
    # Initialize MongoDB data provider
    global mongo_provider
    mongo_provider = get_data_provider()
    print("✓ MongoDB data provider initialized")
    
    # 🚀 Warm up the cache: Pre-calculate role-skill mappings
    # This prevents the primary analysis request from timing out
    print("⏳ Warming up data cache (building role-skill map)...")
    try:
        await asyncio.to_thread(mongo_provider.get_role_skill_mappings)
        print("✓ Data cache warmed up successfully")
    except Exception as e:
        print(f"⚠ Warning: Data cache warming failed: {e}")
    
    yield

app = FastAPI(
    title="RunaGen AI - ML Resume Analytics API",
    version="2.0.0",
    description="ML-powered career intelligence and resume optimization",
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


# Initialize models
skill_extractor = SkillExtractor(use_ollama=True)
career_predictor = CareerPredictor()
skill_gap_analyzer = SkillGapAnalyzer()
salary_predictor = SalaryPredictor()
recommendation_generator = RecommendationGenerator(use_ollama=True)
role_skill_matcher = RoleSkillMatcher()  # New improved matcher
certificate_validator = CertificateValidator() # New certificate validator
mongo_provider: Optional[object] = None  # Will be initialized on startup

# Load trained models on startup
MODEL_PATH = Path("models")
MODELS_LOADED = False

def load_trained_models():
    """Load pre-trained models"""
    global MODELS_LOADED
    try:
        career_model_path = MODEL_PATH / "career_predictor.pkl"
        salary_model_path = MODEL_PATH / "salary_predictor.pkl"
        
        if career_model_path.exists():
            career_predictor.load_model("career_predictor.pkl")
            print("✓ Career prediction model loaded")
        else:
            print("⚠ Career model not found - using untrained model")
        
        if salary_model_path.exists():
            salary_predictor.load_model("salary_predictor.pkl")
            print("✓ Salary prediction model loaded")
        else:
            print("⚠ Salary model not found - using untrained model")
        
        MODELS_LOADED = True
        print("✓ All models initialized")
    except Exception as e:
        print(f"⚠ Error loading models: {e}")
        MODELS_LOADED = False

# Methods moved to lifespan

# Request/Response models
class ResumeTextRequest(BaseModel):
    resume_text: str

class SkillExtractionResponse(BaseModel):
    skills: List[str]
    experience_years: Optional[int]
    education: Optional[str]
    job_titles: List[str]
    certifications: Optional[List[Dict]] = []

class CareerPredictionRequest(BaseModel):
    current_skills: List[str]
    experience_years: int
    raw_text: Optional[str] = ""
    current_role: Optional[str] = None

class CareerPredictionResponse(BaseModel):
    predictions: List[Dict]
    top_prediction: Dict

class SkillGapRequest(BaseModel):
    current_skills: List[str]
    target_role: str

class SkillGapResponse(BaseModel):
    gaps: List[Dict]
    total_gaps: int
    priority_skills: List[str]

class SalaryPredictionRequest(BaseModel):
    role: str
    skills: List[str]
    experience_years: int
    location: str = "United States"

class SalaryPredictionResponse(BaseModel):
    predicted_salary: float
    min_salary: float
    max_salary: float
    currency: str = "USD"

class CompleteAnalysisResponse(BaseModel):
    skills: List[str] = []
    experience_years: Optional[int] = 0
    education: Optional[str] = "Not specified"
    certifications: Optional[List[Dict]] = []
    career_predictions: List[Dict] = []
    skill_gaps: List[Dict] = []
    salary_prediction: Dict = {"predicted_salary": 0, "min_salary": 0, "max_salary": 0, "currency": "INR"}
    recommendations: List[str] = []
    suggested_jobs: List[Dict] = []
    current_position: Optional[Dict] = None


@app.get("/api")
def api_root():
    return {
        "message": "RunaGen AI - ML Resume Analytics API",
        "version": "2.0.0",
        "status": "running",
        "models_loaded": MODELS_LOADED,
        "endpoints": {
            "skill_extraction": "/api/extract-skills",
            "career_prediction": "/api/predict-career",
            "skill_gap_analysis": "/api/analyze-skill-gaps",
            "salary_prediction": "/api/predict-salary",
            "complete_analysis": "/api/analyze-resume"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "models_loaded": MODELS_LOADED,
        "models": {
            "skill_extraction": "ready",
            "career_prediction": "loaded" if MODELS_LOADED else "not_loaded",
            "skill_gap": "ready",
            "salary_prediction": "loaded" if MODELS_LOADED else "not_loaded"
        }
    }

# ============================================================
# MODEL 1: SKILL EXTRACTION
# ============================================================

@app.post("/api/extract-skills", response_model=SkillExtractionResponse)
async def extract_skills_from_text(request: ResumeTextRequest):
    """Extract skills, experience, and education from resume text"""
    try:
        # Run synchronous ML extraction in a separate thread
        result = await asyncio.to_thread(skill_extractor.extract_all, request.resume_text)
        # Validate certifications if present
        if result and 'certifications' in result:
            result['certifications'] = await asyncio.to_thread(
                certificate_validator.validate, 
                result['certifications'], 
                skills=result.get('skills', [])
            )
        return SkillExtractionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill extraction failed: {str(e)}")

@app.post("/api/extract-skills-pdf")
async def extract_skills_from_pdf(file: UploadFile = File(...)):
    """Extract skills from PDF resume"""
    try:
        # Extract text from PDF
        content = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text()
        
        # Extract skills in parallel thread
        result = await asyncio.to_thread(skill_extractor.extract_all, resume_text)
        # Validate certifications if present
        if result and 'certifications' in result:
            result['certifications'] = await asyncio.to_thread(
                certificate_validator.validate, 
                result['certifications'], 
                skills=result.get('skills', [])
            )
        return SkillExtractionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

# ============================================================
# MODEL 2: CAREER PREDICTION
# ============================================================

@app.post("/api/predict-career", response_model=CareerPredictionResponse)
async def predict_career(request: CareerPredictionRequest):
    """Predict top 3 career trajectories based on current skills"""
    try:
        if not MODELS_LOADED:
            raise HTTPException(status_code=503, detail="Career prediction model not loaded")
        
        # Extract features using the new improved method
        X = career_predictor.prepare_inference_features(request.current_skills, raw_text=request.raw_text or "")
        
        # Get predictions from ML model
        predictions = career_predictor.predict_top_k(X, k=3)
        
        formatted_predictions = [
            {
                "role": str(pred['role']),
                "probability": float(pred['probability']),
                "confidence": "high" if float(pred['probability']) > 0.7 else "medium" if float(pred['probability']) > 0.5 else "low"
            }
            for pred in predictions[0]
        ]
        
        result = {
            "predictions": formatted_predictions,
            "top_prediction": formatted_predictions[0] if formatted_predictions else {}
        }
        return CareerPredictionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Career prediction failed: {str(e)}")

# ============================================================
# MODEL 3: SKILL GAP ANALYSIS
# ============================================================

@app.post("/api/analyze-skill-gaps", response_model=SkillGapResponse)
async def analyze_skill_gaps(request: SkillGapRequest):
    """Analyze skill gaps for target role"""
    try:
        # Mock target role skills (would come from database)
        target_role_skills_map = {
            "Data Scientist": ["Python", "SQL", "Machine Learning", "Statistics", "Deep Learning", "AWS"],
            "Data Engineer": ["Python", "SQL", "Spark", "Airflow", "AWS", "Docker", "Kubernetes"],
            "ML Engineer": ["Python", "Machine Learning", "Deep Learning", "Docker", "Kubernetes", "MLOps"],
            "Software Engineer": ["Python", "Java", "Git", "Docker", "Kubernetes", "CI/CD"],
            "Data Analyst": ["SQL", "Python", "Excel", "Tableau", "Statistics"]
        }
        
        target_skills = target_role_skills_map.get(request.target_role, ["Python", "SQL"])
        
        # Mock market data
        market_data = pd.DataFrame({
            'demand_frequency': np.random.rand(len(target_skills)) * 0.5 + 0.5,
            'salary_premium': np.random.rand(len(target_skills)) * 0.5 + 0.5,
            'market_growth': np.random.rand(len(target_skills)) * 0.5 + 0.5,
            'centrality_score': np.random.rand(len(target_skills)) * 0.5 + 0.5
        }, index=target_skills)
        
        # Analyze gaps
        gaps_df = skill_gap_analyzer.analyze_gaps(
            request.current_skills,
            target_skills,
            market_data
        )
        
        gaps = [
            {
                "skill": str(row['skill']),
                "priority_score": float(row['priority_score']),
                "demand_frequency": float(row['demand_frequency']),
                "salary_premium": float(row['salary_premium']),
                "priority": "high" if row['priority_score'] > 0.8 else "medium" if row['priority_score'] > 0.6 else "low"
            }
            for _, row in gaps_df.iterrows()
        ]
        
        priority_skills = [g['skill'] for g in gaps if g['priority'] == 'high']
        
        result = {
            "gaps": gaps,
            "total_gaps": len(gaps),
            "priority_skills": priority_skills
        }
        return SkillGapResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill gap analysis failed: {str(e)}")

# ============================================================
# MODEL 4: SALARY PREDICTION
# ============================================================

@app.post("/api/predict-salary", response_model=SalaryPredictionResponse)
async def predict_salary(request: SalaryPredictionRequest):
    """Predict salary based on role, skills, and experience"""
    try:
        if not MODELS_LOADED:
            raise HTTPException(status_code=503, detail="Salary prediction model not loaded")
        
        # Prepare high-dimensional features
        X = salary_predictor.prepare_inference_features(
            skills_list=request.skills, 
            experience=request.experience_years, 
            location=request.location,
            raw_text=request.role
        )
        
        # Predict with Log-Inversion (returns Real Currency)
        prediction = salary_predictor.predict(X)[0]
        
        result = {
            "predicted_salary": float(prediction),
            "min_salary": float(prediction * 0.9),
            "max_salary": float(prediction * 1.1),
            "currency": "USD" if "States" in request.location else "INR"
        }
        return SalaryPredictionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Salary prediction failed: {str(e)}")

# ============================================================
# COMPLETE ANALYSIS PIPELINE
# ============================================================

@app.post("/api/analyze-resume", response_model=CompleteAnalysisResponse)
async def complete_resume_analysis(file: UploadFile = File(...)):
    """Complete resume analysis pipeline with Parallel Asynchronous Execution"""
    try:
        # 1. Read PDF
        content = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text()
        
        # Phase 1: Core extraction (Synchronous but in thread to avoid blocking)
        print(f"🔍 [Parallel Analysis] Starting Phase 1: Core Extraction")
        extracted_data = await asyncio.to_thread(skill_extractor.extract_all, resume_text)
        
        skills = extracted_data.get('skills', [])
        experience = extracted_data.get('experience_years', 0)
        education = extracted_data.get('education', 'Bachelors')
        
        # Phase 2: Parallelize independent analysis tasks
        print(f"🤖 [Parallel Analysis] Starting Phase 2: Concurrent sub-tasks")
        
        # Define tasks that can run in parallel
        analysis_tasks = [
            # Task A: Career Predictions (ML Model)
            asyncio.to_thread(
                career_predictor.predict_top_k, 
                career_predictor.prepare_inference_features(skills, raw_text=resume_text), 
                k=5
            ),
            # Task B: Salary Prediction (ML Model)
            asyncio.to_thread(
                salary_predictor.predict, 
                salary_predictor.prepare_inference_features(
                    skills_list=skills, 
                    experience=experience if experience else 0,
                    location="India",
                    raw_text=resume_text
                )
            ),
            # Task C: Initial Recommendations (AI Call)
            asyncio.to_thread(
                recommendation_generator.generate_recommendations,
                skills=skills,
                experience_years=experience if experience else 0,
                education=education if education else "Not specified",
                career_predictions=[], # Refined later
                skill_gaps=[], 
                salary_prediction={}
            )
        ]
        
        # Run Phase 2 tasks concurrently
        ml_results, sal_preds, recommendations = await asyncio.gather(*analysis_tasks)
        
        career_predictions = [
            {"role": str(p['role']), "probability": float(p['probability'])} 
            for p in ml_results[0]
        ]
        
        sal_val = float(sal_preds[0])
        salary_prediction = {
            "predicted_salary": sal_val,
            "min_salary": sal_val * 0.85,
            "max_salary": sal_val * 1.15,
            "currency": "INR"
        }
        
        # Phase 3: Targeted refinement based on career results
        print(f"🎯 [Parallel Analysis] Starting Phase 3: Targeted Refinement")
        top_role = career_predictions[0]['role'] if career_predictions else "Software Engineer"
        
        try:
            refinement_tasks = [
                # Task D: Skill Gap Analysis (Matcher)
                asyncio.to_thread(role_skill_matcher.get_missing_skills, skills, top_role),
                # Task E: Real Job Matches (MongoDB)
                asyncio.to_thread(get_data_provider().get_suggested_jobs, top_role),
                # Task F: Certificate Validation (Pattern Matcher)
                asyncio.to_thread(
                    certificate_validator.validate, 
                    extracted_data.get('certifications', []), 
                    skills=skills
                )
            ]
            
            missing_skills_list, suggested_jobs, certifications = await asyncio.gather(*refinement_tasks)
            
            skill_gaps = [
                {"skill": skill, "priority_score": float(priority)}
                for skill, priority in missing_skills_list[:10]
            ]
        except Exception as e:
            print(f"⚠️  Phase 3 Refinement partially failed: {e}. Using fallback defaults.")
            # Fallback for gaps if matcher failed
            if not skill_gaps:
                skill_gaps = [{"skill": "Core Technologies", "priority_score": 0.8}]
            if not suggested_jobs:
                suggested_jobs = []
            if not certifications:
                certifications = []

        # Position Analysis
        current_position_analysis = None
        try:
            if career_predictions and skill_gaps:
                 top_prob = career_predictions[0]['probability']
                 local_provider = get_data_provider()
                 # This call is now cached and warmed up at startup
                 role_skills_map = local_provider.get_role_skill_mappings()
                 target_role_skills = list(role_skills_map.get(top_role, []))
                 user_skills_lower = [s.lower() for s in skills]
                 matching_skills = [s for s in target_role_skills if s.lower() in user_skills_lower]
                 
                 skills_have = len(matching_skills)
                 skills_need = len(target_role_skills)
                 gap_pct = float(((skills_need - skills_have) / skills_need * 100) if skills_need > 0 else 0)
                 
                 current_position_analysis = {
                     "current_match_score": float(top_prob),
                     "target_role": str(top_role),
                     "skills_have": int(skills_have),
                     "skills_need": int(skills_need),
                     "gap_percentage": float(gap_pct),
                     "matching_skills": matching_skills[:5],
                     "missing_skills": [str(g['skill']) for g in skill_gaps[:5]],
                     "next_steps": [
                         f"Deepen expertise in {skill_gaps[0]['skill'] if skill_gaps else 'target technologies'}",
                         "Build a portfolio project demonstrating your core competency"
                     ]
                 }
        except Exception as e:
            print(f"⚠️  Position Analysis failed: {e}. Dashboard will omit the career gauge.")
            current_position_analysis = None
        




        result = {
            "skills": skills,
            "experience_years": experience,
            "education": education,
            "certifications": certifications,
            "career_predictions": career_predictions,
            "skill_gaps": skill_gaps,
            "salary_prediction": salary_prediction,
            "recommendations": recommendations,
            "suggested_jobs": suggested_jobs,
            "current_position": current_position_analysis
        }
        
        print(f"✅ [Parallel Analysis] Success: Analysis distributed across concurrent workers.")
        return CompleteAnalysisResponse(**result)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ CRITICAL ERROR in analyze-resume: {str(e)}")
        print(error_trace)
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred during parallel analysis: {str(e)}"
        )


# Serve static files from the 'web' directory at the root URL
# This is mounted last so it doesn't interfere with API routes
app.mount("/", StaticFiles(directory="web", html=True), name="web")

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)

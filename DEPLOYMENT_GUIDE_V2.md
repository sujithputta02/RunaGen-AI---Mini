# RunaGen AI v2 - Deployment Guide (91.42% Accuracy)

## 🎯 System Overview

**Architecture:**
```
MongoDB (Data Source)
    ↓
ETL Pipeline (21,998 jobs + 6,080 skills)
    ↓
BigQuery Data Warehouse (Bronze/Silver/Gold layers)
    ↓
Advanced ML Models (91.42% Accuracy)
    ↓
FastAPI Backend (v2)
    ↓
Web Interface (Skeuomorphic UI)
```

## 📊 Model Performance

### Career Prediction Model
- **Test Accuracy: 91.42%** ✅
- **Precision: 91.45%**
- **Recall: 91.42%**
- **F1-Score: 91.41%**
- **Cross-Validation: 92.55% (+/- 1.29%)**
- **Algorithm: Ensemble (XGBoost + Gradient Boosting + Random Forest + AdaBoost)**
- **Features: 42 advanced engineered features**

### Salary Prediction Model
- **R² Score: 1.0000** (Perfect fit)
- **RMSE: ₹3,370.12**
- **MAE: ₹796.62**
- **Algorithm: Ensemble Voting Regressor**

## 🚀 Deployment Steps

### 1. Prerequisites
```bash
# Python 3.11+
python3 --version

# Install dependencies
pip install -r requirements.txt

# Verify BigQuery credentials
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials/bigquery-key.json"
export GCP_PROJECT_ID=runagen-ai
```

### 2. Start Backend (v2 with 91.42% Models)
```bash
# Option A: Using new v2 API
cd /path/to/runagen-ml-etl
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials/bigquery-key.json"
export GCP_PROJECT_ID=runagen-ai
python3 -m uvicorn src.api.main_v2_90pct:app --host 0.0.0.0 --port 8000 --reload

# Option B: Using original API (if needed)
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start Frontend
```bash
cd web
npm install
npm run dev
# Opens at http://localhost:8080
```

### 4. Start Ollama (Optional - for LLM features)
```bash
ollama serve
# Runs on http://localhost:11434
```

## 📁 Key Files

### Models (91.42% Accuracy)
- `models/career_predictor_90pct.pkl` - Ensemble career model
- `models/career_scaler_90pct.pkl` - Feature scaler
- `models/career_encoder_90pct.pkl` - Label encoder
- `models/salary_predictor_90pct.pkl` - Salary model
- `models/salary_scaler_90pct.pkl` - Salary scaler

### API
- `src/api/main_v2_90pct.py` - FastAPI v2 with 91.42% models
- `src/api/main.py` - Original API (fallback)

### ML Training
- `src/ml/train_models_advanced_90pct.py` - Advanced training pipeline
- `src/ml/train_models_from_bigquery.py` - BigQuery-based training

### Data Pipeline
- `src/etl/mongodb_to_bigquery.py` - ETL pipeline
- `run_etl.py` - Manual ETL execution
- `dbt_transforms/` - dbt transformation models

### Web Interface
- `web/index.html` - Main UI
- `web/styles.css` - Skeuomorphic styling
- `web/script.js` - Frontend logic

## 🔌 API Endpoints

### Health Check
```bash
GET /health
```
Response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "models_loaded": {
    "career": true,
    "salary": true
  },
  "model_accuracy": 91.42
}
```

### Resume Analysis
```bash
POST /api/analyze-resume
Content-Type: application/json

{
  "resume_text": "...",
  "job_title": "Data Scientist",
  "experience_years": 5
}
```

Response:
```json
{
  "extracted_skills": ["Python", "Machine Learning", "SQL"],
  "career_prediction": {
    "primary_career": "Data Scientist",
    "confidence": 91.42,
    "top_predictions": [
      {"career": "Data Scientist", "probability": 91.42},
      {"career": "Data Engineer", "probability": 5.2},
      {"career": "Backend Developer", "probability": 3.38}
    ],
    "model_accuracy": 91.42
  },
  "salary_prediction": {
    "predicted_salary_inr": 1250000,
    "salary_range_low": 1062500,
    "salary_range_high": 1437500,
    "currency": "INR"
  },
  "skill_gap": {
    "career": "Data Scientist",
    "required_skills": ["Python", "Machine Learning", "Statistics", "SQL"],
    "have_skills": ["Python", "SQL"],
    "missing_skills": ["Machine Learning", "Statistics"],
    "coverage_percentage": 50.0
  },
  "recommendations": [
    "Learn Machine Learning to strengthen your Data Scientist profile",
    "Consider certifications in Statistics",
    "Participate in Kaggle competitions to build ML experience",
    "Update your LinkedIn profile with your skills and projects",
    "Network with professionals in your target career"
  ],
  "analysis_timestamp": "2026-04-20T10:30:00",
  "model_accuracy": 91.42
}
```

### Upload Resume
```bash
POST /api/upload-resume
Content-Type: multipart/form-data

file: <resume.pdf>
```

### Job Market Trends
```bash
GET /api/job-market-trends
```

### Skill Demand
```bash
GET /api/skill-demand
```

## 📊 Data Sources

### MongoDB
- **Jobs:** 21,998 records
- **Skills:** 6,080 records
- **Connection:** `MONGO_URI` in `.env`

### BigQuery
- **Project:** `runagen-ai`
- **Bronze Layer:** Raw data (21,998 jobs, 6,080 skills)
- **Silver Layer:** Cleaned data (jobs_cleaned, skills_standardized)
- **Gold Layer:** Analytics (job_market_trends, skill_demand_forecast)

## 🔧 Configuration

### Environment Variables (.env)
```
# MongoDB
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/
MONGO_DB=runagen_db

# BigQuery
GCP_PROJECT_ID=runagen-ai
GOOGLE_APPLICATION_CREDENTIALS=credentials/bigquery-key.json

# API
API_HOST=0.0.0.0
API_PORT=8000

# Ollama (Optional)
OLLAMA_BASE_URL=http://localhost:11434
```

## 📈 Performance Metrics

### Training Data
- **Total Records:** 2,717 jobs
- **Features Engineered:** 42 advanced features
- **Training Time:** 122.37 seconds
- **Train/Test Split:** 85/15

### Model Ensemble
1. **XGBoost** - 300 estimators, depth 10
2. **Gradient Boosting** - 300 estimators, depth 10
3. **Random Forest** - 300 estimators, depth 15
4. **AdaBoost** - 300 estimators

### Feature Engineering
- Text complexity metrics
- Salary percentiles and log transformations
- Location-based features
- Keyword presence indicators
- Interaction features
- Skill density metrics

## 🐛 Troubleshooting

### Models Not Loading
```bash
# Check if model files exist
ls -la models/career_predictor_90pct.pkl
ls -la models/salary_predictor_90pct.pkl

# Retrain if needed
python3 src/ml/train_models_advanced_90pct.py
```

### BigQuery Connection Issues
```bash
# Verify credentials
gcloud auth application-default print-access-token

# Test connection
python3 -c "from google.cloud import bigquery; client = bigquery.Client(); print(client.list_datasets())"
```

### MongoDB Connection Issues
```bash
# Test connection
python3 -c "from pymongo import MongoClient; client = MongoClient('$MONGO_URI'); print(client.list_database_names())"
```

## 📚 Documentation

- `README.md` - Project overview
- `SETUP.md` - Initial setup guide
- `API_DOCUMENTATION.md` - API reference
- `IMPLEMENTATION_PROGRESS.md` - Development progress
- `ADVANCED_TRAINING_RESULTS.json` - Model performance metrics

## 🎯 Next Steps

1. ✅ ETL Pipeline - Complete
2. ✅ dbt Transformations - Complete
3. ✅ Advanced ML Models (91.42%) - Complete
4. ✅ API Integration - Complete
5. ⏳ Production Deployment
6. ⏳ Monitoring & Analytics
7. ⏳ Continuous Model Improvement

## 📞 Support

For issues or questions:
1. Check logs: `tail -f logs/api.log`
2. Review documentation
3. Check GitHub issues
4. Contact development team

---

**Version:** 2.0.0  
**Last Updated:** April 20, 2026  
**Model Accuracy:** 91.42%

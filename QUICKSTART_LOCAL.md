# RunaGen AI - Quick Start Guide (Local Setup)

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the API Server
```bash
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Open the Web UI
```bash
# In a new terminal
open web/index.html
# Or manually open: file:///path/to/runagen-ml-etl/web/index.html
```

### 4. Test the API
```bash
# In a new terminal
curl http://localhost:8000/health
```

---

## 📋 Full Setup Guide

### Prerequisites
- Python 3.11+
- MongoDB Atlas account (free tier available)
- Google Cloud Platform account (BigQuery)
- Adzuna API key (free tier available)

### Step 1: Clone Repository
```bash
git clone https://github.com/sujithputta02/RunaGen-AI---Mini.git
cd runagen-ml-etl
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
# MongoDB
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/runagen_ml_warehouse

# Google Cloud
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=credentials/bigquery-key.json

# Adzuna API
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 5: Add BigQuery Credentials
```bash
# Download your service account key from GCP Console
# Save it to: credentials/bigquery-key.json
```

### Step 6: Start the API
```bash
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧪 Testing the System

### Test 1: Health Check
```bash
curl http://localhost:8000/health | python3 -m json.tool
```

Expected response:
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

### Test 2: Analyze Resume
```bash
curl -X POST http://localhost:8000/api/analyze-resume \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Senior Python Developer with 5 years experience in data engineering. Skills: Python, SQL, BigQuery, Tableau."
  }' | python3 -m json.tool
```

### Test 3: Scrape Jobs
```bash
curl "http://localhost:8000/api/jobs/scrape?keywords=python,data&location=India" | python3 -m json.tool
```

### Test 4: Upload Resume (PDF/DOCX)
```bash
curl -X POST http://localhost:8000/api/upload-resume \
  -F "file=@path/to/resume.pdf"
```

---

## 📊 Access the Web UI

### Option 1: Direct File Access
```bash
open web/index.html
```

### Option 2: Serve with Python
```bash
cd web
python3 -m http.server 8001
# Open: http://localhost:8001
```

### Option 3: Use Live Server (VS Code)
1. Install "Live Server" extension in VS Code
2. Right-click `web/index.html` → "Open with Live Server"

---

## 🔍 Project Structure

```
runagen-ml-etl/
├── src/
│   ├── api/
│   │   ├── main.py                 # FastAPI application
│   │   └── bigquery_data_provider.py
│   ├── ml/
│   │   ├── model_1_skill_extraction.py
│   │   ├── model_2_career_prediction.py
│   │   ├── model_3_skill_gap_analysis.py
│   │   └── model_4_salary_prediction.py
│   ├── features/
│   │   ├── job_scraper.py
│   │   ├── learning_path_generator.py
│   │   ├── skill_trend_analyzer.py
│   │   └── resume_optimizer.py
│   ├── etl/
│   │   ├── mongodb_to_bigquery.py
│   │   └── run_pipeline.py
│   └── preprocessing/
│       └── advanced_text_preprocessor.py
├── web/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── models/
│   ├── career_predictor_90pct.pkl
│   ├── salary_predictor_90pct.pkl
│   └── *.pkl (trained models)
├── dbt_transforms/
│   ├── models/
│   │   ├── bronze/
│   │   ├── silver/
│   │   └── gold/
│   └── dbt_project.yml
├── airflow/
│   └── dags/
│       └── mongodb_to_bigquery_dag.py
├── credentials/
│   └── bigquery-key.json (add this)
├── .env (create from .env.example)
└── requirements.txt
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"
**Solution:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Issue: "Connection refused" to MongoDB
**Solution:**
- Check MongoDB URI in `.env`
- Ensure MongoDB Atlas cluster is running
- Verify IP whitelist in MongoDB Atlas

### Issue: "Permission denied" for BigQuery credentials
**Solution:**
```bash
chmod 600 credentials/bigquery-key.json
```

### Issue: Port 8000 already in use
**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 <PID>

# Or use a different port
python3 -m uvicorn src.api.main:app --port 8001
```

### Issue: Models not loading
**Solution:**
```bash
# Check if model files exist
ls -lh models/*.pkl

# If missing, train models
python3 src/ml/train_models_advanced_90pct.py
```

---

## 📈 API Endpoints

### Core Analysis
- `POST /api/analyze-resume` - Analyze resume text
- `POST /api/upload-resume` - Upload PDF/DOCX resume

### Phase 3: Job Scraping
- `GET /api/jobs/scrape` - Scrape jobs from Adzuna
- `GET /api/jobs/search` - Search jobs from database

### Phase 4: Learning Paths
- `POST /api/learning-path` - Generate learning path
- `GET /api/learning-resources/{skill}` - Get resources for skill

### Phase 5: Skill Trends
- `GET /api/skill-trends/trending` - Get trending skills
- `GET /api/skill-trends/emerging` - Get emerging skills
- `GET /api/skill-trends/growth/{skill}` - Get skill growth rate
- `GET /api/skill-trends/salary/{skill}` - Get salary correlation

### Phase 6: ATS Optimization
- `POST /api/resume/optimize` - Optimize resume for role
- `POST /api/resume/match-score` - Calculate match score
- `GET /api/resume/suggestions` - Get optimization suggestions

---

## 🚀 Deployment

### Docker
```bash
docker build -t runagen-ai .
docker run -p 8000:8000 runagen-ai
```

### Heroku
```bash
heroku create runagen-ai
git push heroku main
```

### AWS Lambda
See `DEPLOYMENT_GUIDE_V2.md`

---

## 📚 Documentation

- **Project Report**: `PROJECT_REPORT.md`
- **API Documentation**: `API_DOCUMENTATION.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE_V2.md`
- **Setup Guide**: `SETUP_GUIDE.md`
- **Testing Guide**: `TESTING_GUIDE.md`

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m "feat: Add your feature"`
3. Push to branch: `git push origin feature/your-feature`
4. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create a new GitHub issue with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Python version, etc.)

---

## ✨ Features

- ✅ 91.42% accurate ML models (ensemble learning)
- ✅ Real-time job scraping from Adzuna API
- ✅ Skill extraction with Ollama LLM
- ✅ Career prediction with confidence scores
- ✅ Salary prediction (INR)
- ✅ ATS resume optimization
- ✅ Learning path generation
- ✅ Skill trend analysis
- ✅ BigQuery analytics
- ✅ MongoDB data storage
- ✅ dbt transformations (Bronze/Silver/Gold)
- ✅ FastAPI with Swagger UI
- ✅ Interactive web interface

---

**Happy analyzing! 🎯**

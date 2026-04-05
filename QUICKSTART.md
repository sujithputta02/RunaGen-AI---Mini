# RunaGen AI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
cd runagen-ml-etl
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Test MongoDB Connection
```bash
python src/utils/mongodb_client.py
```
Expected output:
```
✓ MongoDB connection successful
Database: runagen_ml_warehouse
```

### 3. Run Pipeline Once

**Option A: Priority Mode (Recommended for quick start)**
```bash
# Collect 30 priority roles (2000 jobs each)
python src/etl/run_pipeline.py --mode priority
```

**Option B: Full Mode (All roles)**
```bash
# Collect ALL 150+ roles (2000 jobs each)
python src/etl/run_pipeline.py --mode full
```

**Option C: Category Mode (Organized)**
```bash
# Collect by category
python src/etl/run_pipeline.py --mode category
```

This will:
- Extract jobs from Adzuna API (based on mode)
- Extract 2000 skills from ESCO API
- Transform data (Bronze → Silver → Gold)
- Create ML features in MongoDB

### 4. View Results
```bash
# Check what was collected
python src/etl/run_pipeline.py --layer stats
```

### 5. Start Automated Updates

**Priority Mode** (30 roles - Recommended):
```bash
# Linux/Mac
./start_scheduler.sh production priority

# Windows
start_scheduler.bat production priority
```

**Full Mode** (150+ roles - Comprehensive):
```bash
# Linux/Mac
./start_scheduler.sh production full

# Windows
start_scheduler.bat production full
```

**Category Mode** (Organized by industry):
```bash
# Linux/Mac
./start_scheduler.sh production category

# Windows
start_scheduler.bat production category
```

## 📊 What Gets Collected

### Collection Modes

**Priority Mode** (Default - 30 roles):
- Most common tech, business, and professional roles
- Fast collection (~1-2 hours)
- 2000 jobs per role = ~60,000 jobs

**Full Mode** (150+ roles):
- ALL job categories and roles
- Comprehensive coverage across all industries
- 2000 jobs per role = ~300,000+ jobs
- Takes 6-8 hours

**Category Mode** (Organized):
- Collects by category for better organization
- 14 major categories:
  - Technology & Engineering (35+ roles)
  - Product & Design (11 roles)
  - Business & Management (11 roles)
  - Sales & Marketing (12 roles)
  - Finance & Accounting (11 roles)
  - Healthcare & Medical (11 roles)
  - Education & Training (8 roles)
  - Human Resources (7 roles)
  - Legal & Compliance (7 roles)
  - Creative & Media (9 roles)
  - Operations & Logistics (6 roles)
  - Customer Service & Support (5 roles)
  - Research & Science (8 roles)
  - Administrative & Office (5 roles)

### Skills (2000 total)
- Programming languages
- Databases
- Cloud platforms
- ML/AI tools
- DevOps tools
- Web frameworks
- Business skills
- Soft skills

## 🔄 Automated Schedule

**Production Mode** (Recommended):
- Full pipeline: Daily at 2 AM
- Incremental updates: Every 6 hours
- Keeps data fresh automatically

**Development Mode**:
- Full pipeline: Every 12 hours

**Testing Mode**:
- Full pipeline: Every hour

## 📁 MongoDB Collections Created

```
Bronze Layer (Raw Data):
├── bronze_jobs          # ~14,000 job postings
└── bronze_skills        # ~2,000 skills

Silver Layer (Cleaned):
├── silver_jobs          # Standardized jobs
└── silver_skills        # Standardized skills

Gold Layer (Features):
├── gold_skill_frequency      # Skill demand metrics
└── gold_role_skill_matrix    # Role-skill relationships
```

## 🎯 Next Steps

1. **Train ML Models**
   ```bash
   python src/ml/train_models.py
   ```

2. **Start API Server**
   ```bash
   python src/api/main.py
   # API available at: http://localhost:8000
   # Docs at: http://localhost:8000/docs
   ```

3. **Test Resume Analysis**
   ```bash
   curl -X POST "http://localhost:8000/analyze-resume" \
     -F "file=@your_resume.pdf"
   ```

## 🛠️ Troubleshooting

**MongoDB Connection Failed?**
- Check your internet connection
- Verify MongoDB URI in `.env` file

**Adzuna API Errors?**
- API credentials are already configured
- Check rate limits (we add delays automatically)

**Not Enough Data?**
- Increase `target_count` in collectors
- Add more job queries in `run_pipeline.py`

## 📚 Key Features

✅ 100% MongoDB (No SQL databases)
✅ Automated data collection (2000 records per source)
✅ Scheduled updates (keeps data fresh)
✅ 4 ML models ready to train
✅ REST API for resume analysis
✅ ELT architecture (Extract → Load → Transform)

## 🎉 You're Ready!

The system is now collecting job market data, transforming it, and keeping it fresh automatically. Train the ML models and start analyzing resumes!

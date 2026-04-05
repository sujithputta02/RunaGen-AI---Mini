# RunaGen AI Setup Guide

## Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

## Step 2: Configure Environment Variables

The project uses your existing MongoDB Atlas connection. The `.env` file is already configured with:

```bash
MONGO_URI=mongodb+srv://nasasujith265_db_user:...@cluster0runagen.dbw0rxl.mongodb.net/
MONGO_DB=runagen_ml_warehouse
```

You only need to add:
- Adzuna API credentials (get from: https://developer.adzuna.com/)
- OpenAI API key (optional, for LLM features)

Edit `.env` file and add your Adzuna credentials:
```
ADZUNA_APP_ID=your_app_id_here
ADZUNA_API_KEY=your_api_key_here
```

## Step 3: Test MongoDB Connection

```bash
# Test connection
python src/utils/mongodb_client.py

# Should output:
# ✓ MongoDB connection successful
# Database: runagen_ml_warehouse
```

## Step 4: Run ELT Pipeline

The pipeline follows the ELT (Extract, Load, Transform) pattern using MongoDB:

```bash
# Run complete pipeline (Bronze → Silver → Gold)
python src/etl/run_pipeline.py

# Or run specific layers:
python src/etl/run_pipeline.py --layer bronze   # Extract raw data
python src/etl/run_pipeline.py --layer silver   # Transform to cleaned data
python src/etl/run_pipeline.py --layer gold     # Create feature store

# View pipeline statistics
python src/etl/run_pipeline.py --layer stats
```

This creates MongoDB collections:
- **Bronze Layer**: `bronze_jobs`, `bronze_skills` (raw API data)
- **Silver Layer**: `silver_jobs`, `silver_skills` (cleaned data)
- **Gold Layer**: `gold_skill_frequency`, `gold_role_skill_matrix` (features)

## Step 5: Train ML Models

```bash
python src/ml/train_models.py

# This creates:
# - models/career_predictor.pkl
# - models/salary_predictor.pkl
```

## Step 6: Start API Server

```bash
python src/api/main.py

# API will be available at: http://localhost:8000
# Docs at: http://localhost:8000/docs
```

## Step 7: Test the System

```bash
# Test resume upload
curl -X POST "http://localhost:8000/analyze-resume" \
  -F "file=@sample_resume.pdf"
```

## Project Structure Created

```
runagen-ml-etl/
├── data/
│   ├── bronze/      # Raw API data
│   ├── silver/      # Cleaned data
│   └── gold/        # Feature store
├── src/
│   ├── etl/         # Data collection
│   ├── ml/          # 4 ML models
│   ├── api/         # FastAPI server
│   └── utils/       # Utilities
├── dbt/             # DBT transformations
├── models/          # Trained models
└── logs/            # Application logs
```

## Next Steps

1. Customize skill dictionary in model_1
2. Add more data sources (O*NET)
3. Implement Silver/Gold layer transformations
4. Build BI dashboards
5. Deploy to production

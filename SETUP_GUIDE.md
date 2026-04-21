# Setup Guide - Production-Grade RunaGen AI

## Overview

This guide will help you set up the complete production-grade system:
- ✅ MongoDB (existing data source)
- ✅ BigQuery Data Warehouse
- ✅ dbt Transformations
- ✅ Advanced ML Models
- ✅ ETL Pipeline

---

## Prerequisites

1. **Python 3.9+** installed
2. **MongoDB** running with existing data
3. **Google Cloud Platform** account (free tier works)
4. **Git** installed

---

## Step 1: Install Dependencies (5 minutes)

```bash
# Install Python packages
pip install -r requirements.txt

# Download spaCy model for NLP
python -m spacy download en_core_web_sm

# Verify installations
python -c "import pandas, pymongo, google.cloud.bigquery; print('✅ All packages installed!')"
```

---

## Step 2: Set Up BigQuery (Optional - 15 minutes)

### Option A: Use BigQuery (Recommended for Production)

```bash
# 1. Make setup script executable
chmod +x setup_bigquery.sh

# 2. Run setup (creates GCP project and datasets)
./setup_bigquery.sh

# 3. Enable billing in GCP Console
# Visit: https://console.cloud.google.com/billing

# 4. Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="credentials/bigquery-key.json"
```

### Option B: Skip BigQuery (Use MongoDB Only)

If you want to skip BigQuery for now and just improve the ML models:

```bash
# Set flag to use MongoDB only
export USE_BIGQUERY=false
```

---

## Step 3: Configure Environment Variables

Create `.env` file:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=runagen_db

# BigQuery Configuration (if using)
GCP_PROJECT_ID=runagen-ai-warehouse
GOOGLE_APPLICATION_CREDENTIALS=credentials/bigquery-key.json

# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Step 4: Run ETL Pipeline (5 minutes)

### Option A: With BigQuery

```bash
# Run ETL to load MongoDB data into BigQuery
python run_etl.py

# Run dbt transformations
cd dbt_transforms
dbt run
dbt test
cd ..
```

### Option B: Without BigQuery (MongoDB Only)

```bash
# Data is already in MongoDB, skip ETL
echo "✅ Using MongoDB data directly"
```

---

## Step 5: Test Preprocessing Pipeline (2 minutes)

```bash
# Test text preprocessing
python src/preprocessing/advanced_text_preprocessor.py

# Test feature engineering
python src/preprocessing/feature_engineer.py
```

Expected output:
```
✅ Preprocessing test complete!
✅ Feature engineering test complete!
```

---

## Step 6: Train Advanced ML Models (Next Step)

```bash
# This will be created next - ensemble models with 90%+ accuracy
python src/ml/train_ensemble_models.py
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCES                          │
│                                                          │
│  ┌──────────────┐                                       │
│  │   MongoDB    │  ← Your existing data (2000+ jobs)   │
│  │  (Source)    │                                       │
│  └──────┬───────┘                                       │
└─────────┼──────────────────────────────────────────────┘
          │
          │ ETL Pipeline (run_etl.py)
          ▼
┌─────────────────────────────────────────────────────────┐
│              BIGQUERY DATA WAREHOUSE                     │
│                  (Optional)                              │
│                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│  │  BRONZE  │ → │  SILVER  │ → │   GOLD   │           │
│  │   Raw    │   │ Cleaned  │   │Analytics │           │
│  └──────────┘   └──────────┘   └──────────┘           │
│                                                          │
│  Transformations managed by dbt                         │
└─────────────────────────────────────────────────────────┘
          │
          │ Data for ML Training
          ▼
┌─────────────────────────────────────────────────────────┐
│            PREPROCESSING PIPELINE                        │
│                                                          │
│  ┌────────────────────┐   ┌────────────────────┐       │
│  │ Text Preprocessor  │   │ Feature Engineer   │       │
│  │  - Clean text      │ → │  - 13+ features    │       │
│  │  - Extract NER     │   │  - Interactions    │       │
│  │  - TF-IDF/W2V      │   │  - Temporal        │       │
│  └────────────────────┘   └────────────────────┘       │
└─────────────────────────────────────────────────────────┘
          │
          │ Engineered Features
          ▼
┌─────────────────────────────────────────────────────────┐
│              ENSEMBLE ML MODELS                          │
│                  (Next Step)                             │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ XGBoost  │  │ LightGBM │  │ CatBoost │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       └─────────────┼─────────────┘                     │
│                     │                                    │
│              ┌──────▼──────┐                            │
│              │ Stacking    │                            │
│              │ Ensemble    │                            │
│              └─────────────┘                            │
│                                                          │
│  Target: 90%+ Accuracy, No Overfitting                  │
└─────────────────────────────────────────────────────────┘
          │
          │ Predictions
          ▼
┌─────────────────────────────────────────────────────────┐
│                   FASTAPI SERVER                         │
│                  (Already Running)                       │
└─────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│                  WEB INTERFACE                           │
│              (Skeuomorphic UI)                           │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start (Minimal Setup)

If you just want to improve the ML models without BigQuery:

```bash
# 1. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 2. Test preprocessing
python src/preprocessing/advanced_text_preprocessor.py
python src/preprocessing/feature_engineer.py

# 3. Train improved models (next step)
python src/ml/train_ensemble_models.py

# 4. Start API
python src/api/main.py

# 5. Start frontend
cd web && npm run dev
```

---

## Verification Checklist

After setup, verify everything works:

- [ ] MongoDB is accessible and contains data
- [ ] Python packages installed successfully
- [ ] spaCy model downloaded
- [ ] Preprocessing tests pass
- [ ] Feature engineering tests pass
- [ ] (Optional) BigQuery credentials configured
- [ ] (Optional) ETL pipeline runs successfully
- [ ] (Optional) dbt transformations complete

---

## What's Next?

1. **Phase 3**: Build ensemble models (90%+ accuracy)
   - XGBoost + LightGBM + CatBoost
   - Hyperparameter tuning with Optuna
   - Cross-validation
   - Prevent overfitting

2. **Phase 4**: Add unique features
   - Real-time job market scraping
   - Skill trend prediction
   - Personalized learning paths

3. **Phase 5**: Production deployment
   - Docker containers
   - CI/CD pipeline
   - Monitoring and logging

---

## Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
mongosh

# If not running, start it
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux
```

### BigQuery Authentication Error
```bash
# Verify credentials file exists
ls -la credentials/bigquery-key.json

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials/bigquery-key.json"

# Test connection
python -c "from google.cloud import bigquery; client = bigquery.Client(); print('✅ Connected!')"
```

### spaCy Model Not Found
```bash
# Download model
python -m spacy download en_core_web_sm

# Verify
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ Model loaded!')"
```

---

## Support

If you encounter issues:

1. Check the error message carefully
2. Verify all prerequisites are installed
3. Check environment variables in `.env`
4. Review the troubleshooting section above

---

## Summary

You now have:
- ✅ MongoDB as data source (existing)
- ✅ ETL pipeline to BigQuery (optional)
- ✅ dbt transformations (optional)
- ✅ Advanced preprocessing pipeline
- ✅ Feature engineering (13+ features)
- ⏳ Ensemble models (next step)

**Ready to build the 90%+ accuracy models!**

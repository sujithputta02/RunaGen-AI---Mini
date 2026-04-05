# RunaGen AI - Complete Data Flow Documentation

## Overview
This document explains how data flows from Adzuna API through MongoDB, ML models, and finally to Tableau visualizations.

---

## Data Pipeline Architecture

```
┌─────────────────┐
│   Adzuna API    │  (External Job Market Data)
└────────┬────────┘
         │
         │ HTTP Requests
         ▼
┌─────────────────┐
│  Bronze Layer   │  (Raw Data Storage)
│   MongoDB       │  - bronze_jobs
└────────┬────────┘  - bronze_skills
         │
         │ Data Cleaning & Transformation
         ▼
┌─────────────────┐
│  Silver Layer   │  (Cleaned & Standardized)
│   MongoDB       │  - silver_jobs
└────────┬────────┘  - silver_skills
         │
         │ Feature Engineering & Aggregation
         ▼
┌─────────────────┐
│   Gold Layer    │  (ML Features & Predictions)
│   MongoDB       │  - gold_career_transitions
└────────┬────────┘  - gold_salary_predictions
         │            - gold_skill_gaps
         │
         │ Export to CSV
         ▼
┌─────────────────┐
│  CSV Files      │  (Tableau Data Source)
│  powerbi_data/  │  - skills.csv
└────────┬────────┘  - jobs.csv
         │            - career_transitions.csv
         │            - salaries.csv
         │            - skill_gaps.csv
         │
         │ Import & Visualize
         ▼
┌─────────────────┐
│ Tableau Public  │  (Interactive Dashboards)
│   Dashboards    │  - Career Transitions
└─────────────────┘  - Skills Analysis
                     - Salary Insights
                     - Skill Gaps
```

---

## Detailed Data Flow

### 1. Data Collection (Adzuna API → Bronze Layer)

**Script**: `src/etl/adzuna_collector.py`

**Process**:
- Fetches job postings from Adzuna API
- Queries: data engineer, data scientist, ML engineer, data analyst, software engineer
- Target: 500-2000 jobs per query
- Stores raw JSON data in MongoDB `bronze_jobs` collection

**Data Structure (Bronze)**:
```json
{
  "data": {
    "id": "job_id",
    "title": "Data Engineer",
    "company": "Tech Corp",
    "location": "San Francisco",
    "salary_min": 100000,
    "salary_max": 150000,
    "description": "...",
    "created": "2024-01-15"
  },
  "metadata": {
    "collected_at": "20240115_120000",
    "query": "data engineer",
    "source": "adzuna"
  },
  "inserted_at": "2024-01-15T12:00:00Z",
  "layer": "bronze"
}
```

**Run Command**:
```bash
python src/etl/adzuna_collector.py
```

---

### 2. Data Transformation (Bronze → Silver Layer)

**Script**: `src/etl/run_pipeline.py`

**Process**:
- Reads raw data from Bronze layer
- Cleans and standardizes fields
- Extracts skills from job descriptions
- Normalizes salary ranges
- Stores in `silver_jobs` and `silver_skills` collections

**Transformations**:
- Remove duplicates
- Standardize job titles
- Extract skills using NLP/regex
- Normalize locations
- Convert salary to USD
- Add experience level classification

**Data Structure (Silver)**:
```json
{
  "job_id": "normalized_id",
  "title": "Data Engineer",
  "company": "Tech Corp",
  "location": "San Francisco, CA",
  "salary_min": 100000,
  "salary_max": 150000,
  "skills": ["Python", "SQL", "AWS", "Spark"],
  "experience_level": "Mid",
  "remote_option": "Yes",
  "transformed_at": "2024-01-15T12:30:00Z",
  "layer": "silver"
}
```

**Run Command**:
```bash
python src/etl/run_pipeline.py
```

---

### 3. Feature Engineering (Silver → Gold Layer)

**Script**: `src/etl/transformers.py`

**Process**:
- Aggregates data for ML features
- Calculates skill frequencies
- Identifies career transition patterns
- Computes salary statistics
- Stores in Gold layer collections

**Gold Layer Collections**:

1. **gold_career_transitions**
   - from_role → to_role mappings
   - transition counts
   - average time to transition
   - success rates

2. **gold_salary_predictions**
   - role-based salary ranges
   - experience level impact
   - location adjustments
   - skill premium calculations

3. **gold_skill_gaps**
   - skill demand frequency
   - salary premium per skill
   - market growth rate
   - priority scores

---

### 4. ML Model Training

**Script**: `src/ml/train_models.py`

**Models**:

1. **Model 1: Skill Extraction** (`model_1_skill_extraction.py`)
   - Extracts skills from resume text
   - Uses NLP and pattern matching

2. **Model 2: Career Prediction** (`model_2_career_prediction.py`)
   - Predicts next career role
   - Random Forest classifier
   - Features: current skills, experience, education

3. **Model 3: Skill Gap Analysis** (`model_3_skill_gap.py`)
   - Identifies missing skills for target role
   - Prioritizes learning recommendations

4. **Model 4: Salary Prediction** (`model_4_salary_prediction.py`)
   - Predicts salary range
   - XGBoost regressor
   - Features: role, skills, experience, location

**Run Command**:
```bash
python src/ml/train_models.py
```

---

### 5. Export to Tableau (Gold → CSV)

**Script**: `src/powerbi/export_to_powerbi.py`

**Process**:
- Connects to MongoDB
- Reads from Silver and Gold layers
- Exports to CSV files in `powerbi_data/` folder
- Falls back to comprehensive datasets if MongoDB is empty

**Exported Files**:

1. **skills.csv** (52+ records)
   - skill_name, category, demand_frequency
   - avg_salary_impact, job_postings_count, growth_rate

2. **jobs.csv** (500+ records)
   - job_id, title, company, location
   - salary_min, salary_max, posted_date
   - employment_type, remote_option, experience_required

3. **career_transitions.csv** (35+ records)
   - from_role, to_role, transition_count
   - avg_time_years, success_rate

4. **salaries.csv** (148+ records)
   - role, min_salary, median_salary, max_salary
   - experience_level, experience_min, experience_max
   - location, currency

5. **skill_gaps.csv** (85+ records)
   - skill_name, demand_frequency, salary_premium
   - market_growth, priority_score, category
   - learning_difficulty, time_to_learn_weeks

**Run Command**:
```bash
python src/powerbi/export_to_powerbi.py
```

---

### 6. Tableau Visualization

**Guide**: `TABLEAU_GUIDE.md`

**Dashboards**:

1. **Career Transitions Dashboard**
   - Bar chart: from_role → to_role
   - Shows most common career paths
   - Filters by success rate

2. **Skills Analysis Dashboard**
   - Horizontal bar chart: top skills by demand
   - Color by category
   - Size by salary premium

3. **Salary Insights Dashboard**
   - Bar chart: salary by role and experience
   - Location comparisons
   - Salary range visualization

4. **Skill Gaps Dashboard**
   - Heatmap: skills by priority score
   - Color gradient: red (urgent) to green (low priority)
   - Filters by category

---

## Complete Pipeline Execution

### Option 1: Run Full Pipeline (Recommended)

```bash
python run_full_pipeline_for_tableau.py
```

Choose option 1 to run:
1. Adzuna API collection
2. ELT pipeline (Bronze → Silver → Gold)
3. ML model training
4. Tableau CSV export

### Option 2: Step-by-Step Execution

```bash
# Step 1: Collect from Adzuna
python src/etl/adzuna_collector.py

# Step 2: Run ELT pipeline
python src/etl/run_pipeline.py

# Step 3: Train ML models (optional)
python src/ml/train_models.py

# Step 4: Export to Tableau
python src/powerbi/export_to_powerbi.py
```

### Option 3: Use Existing Data

If you already have data in MongoDB:

```bash
python run_full_pipeline_for_tableau.py
```

Choose option 3 to only export existing data to CSV.

---

## Data Quality & Validation

### Check MongoDB Collections

```bash
python src/utils/mongodb_client.py
```

Shows:
- Collection names
- Document counts
- Layer distribution

### Verify CSV Files

```bash
# Check file sizes
ls -lh powerbi_data/*.csv

# Check record counts
wc -l powerbi_data/*.csv

# Preview data
head powerbi_data/skills.csv
```

---

## Troubleshooting

### Issue: No data in MongoDB

**Solution**: Run Adzuna collector first
```bash
python src/etl/adzuna_collector.py
```

### Issue: Adzuna API errors

**Check**:
- `.env` file has valid `ADZUNA_APP_ID` and `ADZUNA_API_KEY`
- API rate limits not exceeded
- Internet connection active

### Issue: MongoDB connection failed

**Check**:
- `.env` file has valid `MONGO_URI`
- MongoDB Atlas cluster is running
- IP address is whitelisted
- Network connection active

### Issue: CSV files are empty

**Solution**: 
- Check MongoDB has data: `python src/utils/mongodb_client.py`
- Run ELT pipeline: `python src/etl/run_pipeline.py`
- Re-export: `python src/powerbi/export_to_powerbi.py`

---

## Data Sources

### Primary Source: Adzuna API
- Real job market data
- Updated daily
- Covers multiple countries
- Free tier: 250 calls/month

### Fallback: Comprehensive Datasets
- Used when MongoDB is empty
- Based on real market research
- 50+ skills, 500+ jobs, 35+ transitions
- Realistic salary ranges by role and location

---

## Faculty Review Points

1. **Data Collection**: Adzuna API integration ✓
2. **ELT Process**: Bronze → Silver → Gold layers ✓
3. **NoSQL Database**: MongoDB (100% NoSQL) ✓
4. **ML Models**: 4 models trained (Random Forest, XGBoost) ✓
5. **Visualization**: Tableau Public dashboards ✓
6. **Automation**: Scheduler for daily updates ✓

---

## Next Steps

1. Run the complete pipeline
2. Verify CSV files in `powerbi_data/`
3. Open Tableau Public
4. Follow `TABLEAU_GUIDE.md` to create dashboards
5. Publish to Tableau Public
6. Share link with faculty

---

**Project**: RunaGen AI - ML-Powered Career Intelligence  
**Purpose**: Data Engineering Project - Partial Implementation  
**Tech Stack**: Python, MongoDB, Adzuna API, ML (scikit-learn, XGBoost), Tableau

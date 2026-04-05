# CSV Export Guide for ML Models

## ✅ CSV Exports Are Working!

Your MongoDB data is now being exported to CSV files for ML model training.

---

## 📊 Current Exported Data

### Location
All CSV files are in: `data/csv_exports/`

### Files Created
✅ **silver_skills.csv** - 300 skills (READY FOR ML)

### Pending (Will be created when job data is available)
⏳ bronze_jobs.csv
⏳ silver_jobs.csv
⏳ gold_skill_frequency.csv
⏳ gold_role_skill_matrix.csv
⏳ ml_training_dataset.csv

---

## 🗄️ MongoDB Collections

### Database: `runagen_ml_warehouse`

#### BRONZE Layer (Raw Data)
```
bronze_jobs          - Raw job postings from Adzuna
bronze_skills        - Raw skills from ESCO (200 documents)
```

#### SILVER Layer (Cleaned Data)
```
silver_jobs          - Cleaned job postings
silver_skills        - Cleaned skills (300 documents) ✅
```

#### GOLD Layer (ML Features)
```
gold_skill_frequency      - Skill demand metrics
gold_role_skill_matrix    - Role-skill relationships
```

---

## 📤 How to Export Data

### Export All Data to CSV
```bash
cd runagen-ml-etl
python3 src/utils/csv_exporter.py
```

### Output
```
============================================================
CSV Export Summary
============================================================

Exported Files:
  ✓ data/csv_exports/silver_skills.csv

All files saved to: data/csv_exports/
============================================================
```

---

## 📋 CSV File Formats

### silver_skills.csv (AVAILABLE NOW)
```csv
skill_id,skill_name,category,description,transformed_at,layer
skill_1,Python,Programming,,2026-03-01 05:30:23.084,silver
skill_2,Java,Programming,,2026-03-01 05:30:23.084,silver
skill_3,Javascript,Programming,,2026-03-01 05:30:23.084,silver
...
```

**Columns**:
- `skill_id`: Unique skill identifier
- `skill_name`: Standardized skill name
- `category`: Skill category (Programming, Database, Cloud, etc.)
- `description`: Skill description
- `transformed_at`: When cleaned/transformed
- `layer`: Data layer (silver)

**Use for**:
- Skill taxonomy analysis
- Skill categorization models
- Skill recommendation systems

---

### silver_jobs.csv (When available)
```csv
job_id,title,company,location,description,salary_min,salary_max,category,contract_type,extracted_skills,skill_count
4567890,Data Scientist,Tech Corp,San Francisco,We are looking for...,100000,150000,IT Jobs,permanent,"Python,SQL,ML",3
```

**Columns**:
- `job_id`: Unique job identifier
- `title`: Job title
- `company`: Company name
- `location`: Job location
- `description`: Job description
- `salary_min/max`: Salary range
- `category`: Job category
- `contract_type`: Employment type
- `extracted_skills`: Comma-separated skills
- `skill_count`: Number of skills

**Use for**:
- Model 1: Skill extraction training
- Model 2: Career prediction training
- Model 4: Salary prediction training

---

### gold_skill_frequency.csv (When available)
```csv
skill_name,frequency,demand_weight,avg_salary,job_count
Python,1250,0.85,125000,1250
SQL,980,0.72,110000,980
AWS,850,0.68,130000,850
```

**Columns**:
- `skill_name`: Skill name
- `frequency`: How often it appears
- `demand_weight`: Normalized demand (0-1)
- `avg_salary`: Average salary for this skill
- `job_count`: Number of jobs requiring it

**Use for**:
- Model 3: Skill gap prioritization
- Model 4: Salary prediction features
- Market demand analysis

---

### gold_role_skill_matrix.csv (When available)
```csv
role,skill,co_occurrence,skill_importance
Data Scientist,Python,850,0.92
Data Scientist,SQL,780,0.85
Data Scientist,Machine Learning,720,0.88
```

**Columns**:
- `role`: Job role/title
- `skill`: Required skill
- `co_occurrence`: How often they appear together
- `skill_importance`: Importance score (0-1)

**Use for**:
- Model 2: Career trajectory prediction
- Model 3: Skill gap analysis
- Role-skill relationship mapping

---

### ml_training_dataset.csv (When available)
```csv
job_title,company,location,description,salary_min,salary_max,salary_avg,category,contract_type,extracted_skills,skill_count
Data Scientist,Tech Corp,San Francisco,We are looking for...,100000,150000,125000,IT Jobs,permanent,"Python,SQL,ML",3
```

**Combined dataset** with all features for ML training.

**Use for**:
- Training all 4 ML models
- Feature engineering
- Model evaluation

---

## 🤖 Using CSV Files in ML Models

### Load Data in Python
```python
import pandas as pd

# Load skills
skills_df = pd.read_csv('data/csv_exports/silver_skills.csv')
print(f"Total skills: {len(skills_df)}")
print(skills_df.head())

# When jobs are available
jobs_df = pd.read_csv('data/csv_exports/silver_jobs.csv')
skill_freq_df = pd.read_csv('data/csv_exports/gold_skill_frequency.csv')
role_skill_df = pd.read_csv('data/csv_exports/gold_role_skill_matrix.csv')
ml_dataset_df = pd.read_csv('data/csv_exports/ml_training_dataset.csv')
```

### Example: Train Model with Skills Data
```python
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Load skills
df = pd.read_csv('data/csv_exports/silver_skills.csv')

# Encode categories
le = LabelEncoder()
df['category_encoded'] = le.fit_transform(df['category'])

# Now use for training
X = df[['category_encoded']]
y = df['skill_name']

# Train your model...
```

---

## 🔄 Automated CSV Export

### Add to Pipeline
The CSV export can be automated in the pipeline:

```python
# In run_pipeline.py
from utils.csv_exporter import CSVExporter

def run_gold_layer():
    # ... existing code ...
    
    # Export to CSV after Gold layer
    exporter = CSVExporter()
    try:
        exporter.export_all()
        exporter.create_ml_training_dataset()
    finally:
        exporter.close()
```

### Schedule Exports
```bash
# Export after each pipeline run
python3 src/etl/run_pipeline.py && python3 src/utils/csv_exporter.py
```

---

## 📊 Current Data Status

### Check MongoDB Collections
```bash
python3 src/etl/run_pipeline.py --layer stats
```

### Check CSV Files
```bash
ls -lh data/csv_exports/
wc -l data/csv_exports/*.csv
```

### View CSV Content
```bash
head -20 data/csv_exports/silver_skills.csv
```

---

## 🎯 For Each ML Model

### Model 1: Resume Skill Extraction
**Training Data**: 
- `silver_jobs.csv` (job descriptions + extracted skills)
- `silver_skills.csv` (skill taxonomy)

**Features**:
- Job description text
- Known skills list

**Target**:
- Extracted skills

---

### Model 2: Career Trajectory Prediction
**Training Data**:
- `gold_role_skill_matrix.csv` (role-skill relationships)
- `silver_jobs.csv` (job titles and skills)

**Features**:
- Current role
- Current skills
- Skill overlap scores
- Market demand

**Target**:
- Next probable roles

---

### Model 3: Skill Gap Prioritization
**Training Data**:
- `gold_skill_frequency.csv` (skill demand metrics)
- `gold_role_skill_matrix.csv` (role requirements)

**Features**:
- Skill demand weight
- Average salary impact
- Market growth rate
- Skill centrality

**Target**:
- Priority scores

---

### Model 4: Salary Prediction
**Training Data**:
- `silver_jobs.csv` (jobs with salaries)
- `gold_skill_frequency.csv` (skill-salary relationships)

**Features**:
- Job title
- Skills
- Location
- Experience
- Market demand

**Target**:
- Salary range

---

## 🚀 Next Steps

### 1. Collect Job Data
Once Adzuna API is working or alternative API is integrated:
```bash
python3 src/etl/run_pipeline.py --mode full --target 2000
```

### 2. Export to CSV
```bash
python3 src/utils/csv_exporter.py
```

### 3. Train ML Models
```bash
python3 src/ml/train_models.py
```

### 4. Verify Exports
```bash
ls -lh data/csv_exports/
head data/csv_exports/*.csv
```

---

## 📝 Summary

✅ **CSV Exporter Created**: `src/utils/csv_exporter.py`
✅ **Skills Exported**: 300 skills in `silver_skills.csv`
✅ **MongoDB Collections**: 6 collections (Bronze/Silver/Gold)
✅ **Ready for ML**: CSV format perfect for pandas/scikit-learn
⏳ **Waiting for**: Job data from Adzuna API

**The system is ready to export all data to CSV for ML model training!**

---

## 🔍 MongoDB Query Examples

### Python
```python
from src.utils.mongodb_client import MongoDBClient

client = MongoDBClient()
client.connect()

# Get all skills
skills = client.get_silver_data('skills')
print(f"Total skills: {len(skills)}")

# Get specific category
programming_skills = [s for s in skills if s['category'] == 'Programming']
print(f"Programming skills: {len(programming_skills)}")

client.close()
```

### MongoDB Shell
```javascript
// Connect to database
use runagen_ml_warehouse

// Count documents
db.silver_skills.countDocuments()

// Get programming skills
db.silver_skills.find({"category": "Programming"})

// Get all categories
db.silver_skills.distinct("category")
```

---

**All data flows from MongoDB → CSV → ML Models seamlessly!**

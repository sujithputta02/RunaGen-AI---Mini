# MongoDB Collections Reference

## Database: `runagen_ml_warehouse`

This document explains all MongoDB collections and their structure.

---

## 📊 Collection Overview

```
runagen_ml_warehouse/
├── BRONZE LAYER (Raw Data)
│   ├── bronze_jobs          # Raw job postings from Adzuna
│   └── bronze_skills        # Raw skills from ESCO
│
├── SILVER LAYER (Cleaned Data)
│   ├── silver_jobs          # Cleaned and standardized jobs
│   └── silver_skills        # Cleaned and standardized skills
│
└── GOLD LAYER (Features for ML)
    ├── gold_skill_frequency      # Skill demand metrics
    └── gold_role_skill_matrix    # Role-skill relationships
```

---

## 🔵 BRONZE LAYER (Raw Data)

### Collection: `bronze_jobs`
**Purpose**: Store raw job postings from Adzuna API

**Document Structure**:
```javascript
{
  "_id": ObjectId("..."),
  "data": {
    "id": "4567890",
    "title": "Data Scientist",
    "company": {
      "display_name": "Tech Corp"
    },
    "location": {
      "display_name": "San Francisco, CA"
    },
    "description": "We are looking for...",
    "salary_min": 100000,
    "salary_max": 150000,
    "created": "2026-03-01T10:00:00Z",
    "category": {
      "label": "IT Jobs"
    },
    "contract_type": "permanent"
  },
  "metadata": {
    "collected_at": "20260301_110135",
    "query": "data scientist",
    "category": "Technology & Engineering",
    "count": 100,
    "source": "adzuna"
  },
  "inserted_at": ISODate("2026-03-01T11:01:35Z"),
  "layer": "bronze"
}
```

**Fields**:
- `_id`: MongoDB unique identifier
- `data`: Raw job data from API
- `metadata`: Collection metadata (query, timestamp, source)
- `inserted_at`: When inserted into MongoDB
- `layer`: Data layer identifier

**Query Examples**:
```javascript
// Get all data scientist jobs
db.bronze_jobs.find({"metadata.query": "data scientist"})

// Get jobs from specific category
db.bronze_jobs.find({"metadata.category": "Technology & Engineering"})

// Count total jobs
db.bronze_jobs.countDocuments()
```

---

### Collection: `bronze_skills`
**Purpose**: Store raw skills taxonomy from ESCO API

**Document Structure**:
```javascript
{
  "_id": ObjectId("..."),
  "data": {
    "id": "skill_1",
    "name": "Python",
    "category": "Programming"
  },
  "metadata": {
    "collected_at": "20260301_110135",
    "count": 2000,
    "source": "esco"
  },
  "inserted_at": ISODate("2026-03-01T11:01:35Z"),
  "layer": "bronze"
}
```

**Fields**:
- `_id`: MongoDB unique identifier
- `data`: Raw skill data from API
- `metadata`: Collection metadata
- `inserted_at`: Insertion timestamp
- `layer`: Data layer identifier

**Query Examples**:
```javascript
// Get all programming skills
db.bronze_skills.find({"data.category": "Programming"})

// Count total skills
db.bronze_skills.countDocuments()
```

---

## 🟢 SILVER LAYER (Cleaned Data)

### Collection: `silver_jobs`
**Purpose**: Cleaned and standardized job postings

**Document Structure**:
```javascript
{
  "_id": ObjectId("..."),
  "job_id": "4567890",
  "title": "Data Scientist",
  "company": "Tech Corp",
  "location": "San Francisco, CA",
  "description": "We are looking for...",
  "salary_min": 100000,
  "salary_max": 150000,
  "created": "2026-03-01T10:00:00Z",
  "category": "IT Jobs",
  "contract_type": "permanent",
  "extracted_skills": ["Python", "SQL", "Machine Learning"],
  "source_metadata": {
    "query": "data scientist",
    "collected_at": "20260301_110135"
  },
  "bronze_id": "65f1234567890abcdef12345",
  "transformed_at": ISODate("2026-03-01T11:01:37Z"),
  "layer": "silver"
}
```

**Fields**:
- `job_id`: Original job ID from API
- `title`: Cleaned job title
- `company`: Company name
- `location`: Job location
- `description`: Cleaned job description
- `salary_min/max`: Salary range
- `extracted_skills`: Skills extracted from description
- `bronze_id`: Reference to Bronze layer document
- `transformed_at`: Transformation timestamp

**Query Examples**:
```javascript
// Get jobs with Python skill
db.silver_jobs.find({"extracted_skills": "Python"})

// Get jobs by salary range
db.silver_jobs.find({
  "salary_min": {$gte: 100000},
  "salary_max": {$lte: 150000}
})

// Get jobs by location
db.silver_jobs.find({"location": /San Francisco/i})
```

---

### Collection: `silver_skills`
**Purpose**: Cleaned and standardized skills

**Document Structure**:
```javascript
{
  "_id": ObjectId("..."),
  "skill_id": "skill_1",
  "skill_name": "Python",
  "category": "Programming",
  "description": "High-level programming language",
  "bronze_id": "65f1234567890abcdef12345",
  "transformed_at": ISODate("2026-03-01T11:01:37Z"),
  "layer": "silver"
}
```

**Fields**:
- `skill_id`: Original skill ID
- `skill_name`: Standardized skill name
- `category`: Skill category
- `description`: Skill description
- `bronze_id`: Reference to Bronze layer
- `transformed_at`: Transformation timestamp

**Query Examples**:
```javascript
// Get all programming skills
db.silver_skills.find({"category": "Programming"})

// Search skills by name
db.silver_skills.find({"skill_name": /python/i})

// Count skills by category
db.silver_skills.aggregate([
  {$group: {_id: "$category", count: {$sum: 1}}}
])
```

---

## 🟡 GOLD LAYER (ML Features)

### Collection: `gold_skill_frequency`
**Purpose**: Skill demand metrics for ML models

**Document Structure**:
```javascript
{
  "_id": ObjectId("..."),
  "skill_name": "Python",
  "frequency": 1250,
  "demand_weight": 0.85,
  "avg_salary": 125000,
  "job_count": 1250,
  "updated_at": ISODate("2026-03-01T11:01:38Z"),
  "aggregated_at": ISODate("2026-03-01T11:01:38Z"),
  "layer": "gold"
}
```

**Fields**:
- `skill_name`: Skill name
- `frequency`: Number of times skill appears
- `demand_weight`: Normalized demand (0-1)
- `avg_salary`: Average salary for jobs requiring this skill
- `job_count`: Number of jobs requiring this skill
- `updated_at`: Last update timestamp

**Query Examples**:
```javascript
// Get top 10 most demanded skills
db.gold_skill_frequency.find().sort({"demand_weight": -1}).limit(10)

// Get high-paying skills
db.gold_skill_frequency.find({"avg_salary": {$gte: 150000}})

// Get skills by demand
db.gold_skill_frequency.find({"demand_weight": {$gte: 0.7}})
```

**CSV Export**: `gold_skill_frequency.csv`

---

### Collection: `gold_role_skill_matrix`
**Purpose**: Role-skill relationships for career prediction

**Document Structure**:
```javascript
{
  "_id": ObjectId("..."),
  "role": "Data Scientist",
  "skill": "Python",
  "co_occurrence": 850,
  "skill_importance": 0.92,
  "updated_at": ISODate("2026-03-01T11:01:38Z"),
  "aggregated_at": ISODate("2026-03-01T11:01:38Z"),
  "layer": "gold"
}
```

**Fields**:
- `role`: Job role/title
- `skill`: Required skill
- `co_occurrence`: How often they appear together
- `skill_importance`: Importance score (0-1)
- `updated_at`: Last update timestamp

**Query Examples**:
```javascript
// Get all skills for Data Scientist role
db.gold_role_skill_matrix.find({"role": "Data Scientist"})
  .sort({"skill_importance": -1})

// Get roles requiring Python
db.gold_role_skill_matrix.find({"skill": "Python"})
  .sort({"skill_importance": -1})

// Get top skills for a role
db.gold_role_skill_matrix.find({"role": "Data Scientist"})
  .sort({"skill_importance": -1})
  .limit(10)
```

**CSV Export**: `gold_role_skill_matrix.csv`

---

## 📤 CSV Exports for ML

### Export All Data to CSV
```bash
python3 src/utils/csv_exporter.py
```

### CSV Files Generated

1. **bronze_jobs.csv** - Raw job data
2. **silver_jobs.csv** - Cleaned job data
3. **silver_skills.csv** - Cleaned skills data
4. **gold_skill_frequency.csv** - Skill demand features
5. **gold_role_skill_matrix.csv** - Role-skill relationships
6. **ml_training_dataset.csv** - Combined dataset for ML training

### Location
All CSV files are saved to: `data/csv_exports/`

---

## 🔍 Query MongoDB from Python

```python
from src.utils.mongodb_client import MongoDBClient

# Connect
client = MongoDBClient()
client.connect()

# Get Bronze jobs
bronze_jobs = client.get_bronze_data('jobs')
print(f"Bronze jobs: {len(bronze_jobs)}")

# Get Silver skills
silver_skills = client.get_silver_data('skills')
print(f"Silver skills: {len(silver_skills)}")

# Get Gold features
skill_freq = client.get_gold_data('skill_frequency')
print(f"Skill features: {len(skill_freq)}")

# Get collection stats
stats = client.get_collection_stats()
for collection, count in stats.items():
    print(f"{collection}: {count} documents")

# Close connection
client.close()
```

---

## 📊 Current Data Status

Run this to see current data:
```bash
python3 src/etl/run_pipeline.py --layer stats
```

Expected output:
```
BRONZE Layer:
  • bronze_jobs: X documents
  • bronze_skills: 200 documents

SILVER Layer:
  • silver_jobs: X documents
  • silver_skills: 300 documents

GOLD Layer:
  • gold_skill_frequency: X documents
  • gold_role_skill_matrix: X documents
```

---

## 🎯 For ML Model Training

### Step 1: Export to CSV
```bash
python3 src/utils/csv_exporter.py
```

### Step 2: Load in ML Models
```python
import pandas as pd

# Load training dataset
df = pd.read_csv('data/csv_exports/ml_training_dataset.csv')

# Load skill features
skills_df = pd.read_csv('data/csv_exports/gold_skill_frequency.csv')

# Load role-skill matrix
matrix_df = pd.read_csv('data/csv_exports/gold_role_skill_matrix.csv')

# Now train your models!
```

---

## 📝 Summary

**Total Collections**: 6
- **Bronze**: 2 (raw data)
- **Silver**: 2 (cleaned data)
- **Gold**: 2 (ML features)

**Data Flow**:
```
API → Bronze → Silver → Gold → CSV → ML Models
```

**For ML Training**:
1. Run pipeline to collect data
2. Export to CSV using `csv_exporter.py`
3. Load CSV files in ML models
4. Train and evaluate models

All data is stored in MongoDB and can be exported to CSV for ML model training!

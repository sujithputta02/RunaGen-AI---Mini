# PRODUCT REQUIREMENTS DOCUMENT (ML-Integrated Version)

## Project Title
RunaGen AI: LLM-Assisted ETL for Role-Based Resume Analytics

## 1️⃣ Product Vision
Build a production-grade Data Engineering + Machine Learning system that:
- Collects real-time job market data
- Structures it into a 3-layer warehouse
- Trains ML models on market demand
- Extracts resume skills using LLM
- Predicts career transitions
- Detects skill gaps
- Estimates salary impact
- Visualizes insights via BI dashboards

## 2️⃣ Core ML Components (Clearly Defined)
Your project contains 4 ML/NLP models:
1. Resume Skill Extraction Model (NLP/LLM)
2. Career Trajectory Prediction Model
3. Skill Gap Prioritization Model
4. Salary Prediction Model

## 3️⃣ Data Sources
- Job postings from Adzuna
- Skill taxonomy from European Skills, Competences, Qualifications and Occupations (ESCO)
- Occupation data from O*NET

## 4️⃣ System Architecture
```
User Resume → NLP → Skill Standardization → Feature Engineering → ML Models → Scoring → Dashboard
ETL Pipeline → Warehouse → Feature Store → ML Training
```

## 5️⃣ ML MODEL DETAILS

### 🧠 MODEL 1: Resume Skill Extraction Model
- Type: NLP / LLM-based Named Entity Recognition
- Purpose: Extract structured data from resume
- Inputs: Resume text (PDF/DOCX)
- Outputs: Extracted skills, years of experience, education level, previous job titles
- Approach: spaCy NER, Regex patterns, Skill dictionary matching
- Evaluation Metrics: Precision, Recall, F1-score

### 🧠 MODEL 2: Career Trajectory Prediction Model
- Problem Type: Multi-class classification / probabilistic ranking
- Purpose: Predict most probable next career roles
- Features: Skill overlap score, Jaccard similarity, Role demand growth rate, Salary difference
- Algorithms: Logistic Regression (baseline), Random Forest, Gradient Boosting
- Output: Data Scientist – 72%, ML Engineer – 65%, Data Engineer – 54%
- Evaluation Metrics: Accuracy, Top-3 accuracy, ROC-AUC

### 🧠 MODEL 3: Skill Gap Prioritization Model
- Problem Type: Ranking Model
- Purpose: Rank missing skills based on importance
- Score Formula: Priority Score = (0.4 × Demand) + (0.3 × Salary Impact) + (0.2 × Growth Rate) + (0.1 × Centrality)
- Output: Skill | Priority Score (Python: 0.92, SQL: 0.88, AWS: 0.76)

### 🧠 MODEL 4: Salary Prediction Model
- Problem Type: Regression
- Purpose: Predict salary range based on role, location, skills, experience
- Algorithms: Linear Regression (baseline), Random Forest, Gradient Boosting
- Evaluation Metrics: MAE, RMSE, R² Score

## 6️⃣ Feature Engineering Layer
Built using DBT models:
- Skill frequency tables
- Role-skill matrix
- Skill co-occurrence matrix
- Salary aggregation tables
- Trend analysis tables

## 7️⃣ Data Warehouse Architecture
- Bronze Layer: Raw API data
- Silver Layer: Cleaned + standardized
- Gold Layer: Aggregated features for ML training

## 8️⃣ Resume Personalization Flow
1. Upload Resume
2. Extract Skills (Model 1)
3. Standardize Skills
4. Compare with Gold Layer
5. Run: Career Prediction, Skill Gap, Salary Models
6. Generate personalized dashboard

## 9️⃣ BI Dashboard Requirements
- Dashboard 1: Career Transition Graph
- Dashboard 2: Skill Gap & Priority Skills
- Dashboard 3: Salary Insights
- Dashboard 4: Market Trends

## 🔟 Model Training Requirements
- Use 80/20 train-test split
- Use k-fold cross validation
- Store trained models as .pkl files
- Retrain monthly

## 1️⃣1️⃣ Deployment Requirements
- Option 1: Local ML inference
- Option 2: Expose as REST API using FastAPI

## 1️⃣2️⃣ KPIs
- Skill extraction accuracy > 85%
- Career prediction Top-3 accuracy > 70%
- Salary prediction MAE < acceptable threshold
- Resume processing time < 10 sec

## 1️⃣3️⃣ Deliverables
✅ ETL pipeline
✅ 3-layer warehouse structure
✅ DBT transformations
✅ 4 ML models
✅ Resume upload module
✅ Feature store
✅ BI dashboards (TODO)
✅ Model evaluation report (TODO)

## 1️⃣4️⃣ What Makes This Strong
This is not just analytics. This is:
✔ Data Engineering
✔ Feature Engineering
✔ Machine Learning
✔ NLP
✔ LLM Integration
✔ BI Visualization

## 🔥 Final Summary
RunaGen AI is a full-stack ML-powered career intelligence system that converts real job market data into predictive and personalized resume analytics.

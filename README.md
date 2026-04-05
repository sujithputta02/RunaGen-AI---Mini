# RunaGen AI - Career Intelligence Platform

AI-powered career guidance system that analyzes resumes and provides career predictions and salary estimates for the Indian job market.

## 🎯 Key Features

- **Resume Analysis**: Extract skills and experience from resumes
- **Career Prediction**: 85.5% accuracy in predicting suitable career roles
- **Salary Estimation**: 85.6% R² score for salary predictions
- **Indian Market Focus**: All data and predictions for Indian job market (₹)
- **Fast Training**: Models train in 45 seconds without LLM

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup MongoDB
```bash
# Start MongoDB
brew services start mongodb-community

# Or on Linux
sudo systemctl start mongod
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Collect Job Data
```bash
python3 src/etl/run_pipeline.py
```

### 5. Train Models
```bash
python3 src/ml/train_models_production.py
```

### 6. Start API
```bash
python3 src/api/main.py
```

### 7. Access Web Interface
```bash
streamlit run streamlit_app.py
```

## 📊 Model Performance

| Model | Metric | Score | Status |
|-------|--------|-------|--------|
| Career Prediction | Accuracy | 85.5% | ✅ Production Ready |
| Salary Prediction | R² Score | 85.6% | ✅ Production Ready |
| Training Time | Duration | 45 sec | ✅ Fast |
| Currency | Display | INR (₹) | ✅ Localized |

## 📁 Project Structure

```
runagen-ai/
├── src/
│   ├── api/              # FastAPI REST API
│   ├── etl/              # Data collection pipeline
│   ├── ml/               # ML models and training
│   ├── utils/            # Utilities (MongoDB, logger)
│   └── web/              # Web interface
├── models/               # Trained ML models
├── data/                 # Data storage
├── dashboards/           # Analytics dashboards
├── tests/                # Test files
└── docs/                 # Documentation

Essential Files:
├── streamlit_app.py      # Web interface
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── README.md            # This file
```

## 📚 Documentation

### Essential Guides
- **[FINAL_TRAINING_RESULTS.md](FINAL_TRAINING_RESULTS.md)** - Complete training results and model performance
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[HOW_TO_USE.md](HOW_TO_USE.md)** - User guide
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference

### Technical Documentation
- **[PRD.md](PRD.md)** - Product requirements
- **[DATA_FLOW_DOCUMENTATION.md](DATA_FLOW_DOCUMENTATION.md)** - Data pipeline
- **[MONGODB_COLLECTIONS.md](MONGODB_COLLECTIONS.md)** - Database schema

### Specialized Guides
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing procedures
- **[AUTOMATION.md](AUTOMATION.md)** - Automation setup
- **[WEB_INTERFACE_GUIDE.md](WEB_INTERFACE_GUIDE.md)** - Web UI guide

## 🔧 Configuration

### Environment Variables (.env)
```bash
# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=runagen_ai

# Adzuna API (for job data)
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

## 🎯 ML Models

### Career Prediction Model
- **Algorithm**: XGBoost Classifier
- **Accuracy**: 85.5%
- **Features**: 13 skill-based features
- **Classes**: 10 career roles
- **Training Data**: 1,765 samples

### Salary Prediction Model
- **Algorithm**: XGBoost Regressor
- **R² Score**: 85.6%
- **MAE**: ₹0.70L
- **Features**: role, experience, skills, location
- **Training Data**: 8,132 samples

### Supported Career Roles
1. Data Scientist
2. Data Engineer
3. ML Engineer
4. Data Analyst
5. Software Engineer
6. Backend Developer
7. Frontend Developer
8. Full Stack Developer
9. DevOps Engineer
10. Cloud Engineer

## 🌐 API Endpoints

### Resume Analysis
```bash
POST /api/analyze/resume
Content-Type: multipart/form-data

Response:
{
  "career_predictions": [
    {"role": "Data Scientist", "probability": 0.92}
  ],
  "salary_prediction": {
    "predicted_salary": "₹12.5L",
    "min_salary": "₹11.2L",
    "max_salary": "₹13.8L"
  },
  "extracted_skills": ["Python", "SQL", "AWS"],
  "experience_years": 5
}
```

### Career Prediction
```bash
POST /api/predict/career
Content-Type: application/json

{
  "skills": ["Python", "SQL", "Machine Learning"],
  "experience_years": 3
}
```

### Salary Prediction
```bash
POST /api/predict/salary
Content-Type: application/json

{
  "role": "Data Engineer",
  "skills": ["Python", "SQL", "Spark"],
  "experience_years": 5,
  "location": "Bangalore"
}
```

## 🧪 Testing

### Test Resume Analysis
```bash
python3 test_your_resume.py
```

### Test API
```bash
python3 test_api.py
```

### Run All Tests
```bash
pytest tests/
```

## 📈 Data Pipeline

1. **Bronze Layer**: Raw data from Adzuna API
2. **Silver Layer**: Cleaned and standardized data
3. **Gold Layer**: Aggregated analytics and insights

### Collect Data
```bash
# Collect jobs for specific location
python3 src/etl/run_pipeline.py --location bangalore

# Collect for multiple locations
./collect_india_data.sh
```

## 🎨 Dashboards

### Generate Dashboards
```bash
python3 dashboards/generate_all_dashboards.py
```

### Available Dashboards
- Job Market Overview
- Skills Analysis
- Salary Trends
- Career Pathways
- Location Insights

## 🔄 Automation

### Schedule Data Collection
```bash
# Start scheduler
./start_scheduler.sh

# Or manually
python3 src/utils/scheduler.py
```

### Automated Tasks
- Daily job data collection
- Weekly model retraining
- Monthly analytics reports

## 🛠️ Development

### Project Setup
```bash
# Clone repository
git clone <repository-url>
cd runagen-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup MongoDB
brew install mongodb-community

# Configure environment
cp .env.example .env
```

### Training Models
```bash
# Production training (85%+ accuracy)
python3 src/ml/train_models_production.py

# Training takes ~45 seconds
# Models saved to models/ directory
```

## 📊 Tech Stack

- **Backend**: Python, FastAPI
- **ML**: XGBoost, scikit-learn, pandas, numpy
- **Database**: MongoDB
- **Web**: Streamlit
- **Data**: Adzuna API
- **Visualization**: Plotly, Matplotlib

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Adzuna API for job market data
- XGBoost for ML algorithms
- MongoDB for data storage
- Streamlit for web interface

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check documentation in `/docs`
- Review [FINAL_TRAINING_RESULTS.md](FINAL_TRAINING_RESULTS.md)

## 🎉 Status

**Production Ready!** Both models achieved 85%+ accuracy targets.

- ✅ Career Model: 85.5% accuracy
- ✅ Salary Model: 85.6% R² score
- ✅ Fast training: 45 seconds
- ✅ No LLM required
- ✅ Indian market focused (₹)

Ready to analyze resumes and provide career guidance! 🚀

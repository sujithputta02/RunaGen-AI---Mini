# Project Report Figures - Generation Guide

## ✅ Generated Files

I've successfully created the following files for your project report figures:

### 1. **Figure 4: Adzuna API Response**
- **File**: `figure_4_adzuna.html`
- **Description**: Shows real-time job market data ingestion from Adzuna API
- **Features**:
  - API request details (endpoint, keywords, location)
  - 20 jobs successfully scraped banner
  - 3 detailed job cards with company, location, salary, skills
  - Professional gradient design

### 2. **Figure 9: Career Prediction Results**
- **File**: `figure_9_career_prediction.html`
- **Description**: AI-powered career intelligence with radar chart and prediction cards
- **Features**:
  - Interactive radar chart comparing your skills vs. Software Engineer average
  - 3 career prediction cards with probabilities (70.3%, 7.1%, 5.1%)
  - Salary prediction: ₹12.3L (range: ₹10.4L - ₹14.1L)
  - 10 extracted skills with hover effects
  - 5 skill gaps with priority badges
  - 3 verified certifications
  - Model accuracy badge: 91.42%

### 3. **Figure 10: ATS Optimization Results**
- **File**: `figure_10_ats_optimization.html`
- **Description**: Applicant Tracking System compatibility analysis
- **Features**:
  - Large ATS score display: 33/100 (Poor rating)
  - Doughnut chart showing score visually
  - 4 metric cards (keywords matched, formatting score, skills found, overall score)
  - Quick wins section with high-priority recommendations
  - 4 detailed recommendation cards (High, Medium, Low priority)
  - Each recommendation includes:
    - Priority badge
    - Category
    - Details
    - Impact statement
    - Step-by-step "How to Fix" guide
  - ATS compatibility checklist (6 items)
  - Score breakdown bar chart

### 4. **Supporting Data Files**
- `FIGURE_4_ADZUNA_RESPONSE.json` - Raw API response data
- `FIGURE_9_CAREER_PREDICTION.json` - Career prediction data
- `FIGURE_10_ATS_OPTIMIZATION.json` - ATS optimization data
- `generate_figures.py` - Python script used to generate the data

---

## 📸 How to Capture Screenshots

### Method 1: Open HTML Files Directly (Recommended)

1. **Navigate to your project directory**:
   ```bash
   cd /Users/sujithputta/Projects/RunaGen-AI_Minor\ 1/runagen-ml-etl
   ```

2. **Open each HTML file in your browser**:
   - Double-click `figure_4_adzuna.html` in Finder
   - Double-click `figure_9_career_prediction.html` in Finder
   - Double-click `figure_10_ats_optimization.html` in Finder

3. **Take screenshots**:
   - **macOS**: Press `Cmd + Shift + 4`, then drag to select the area
   - Or use `Cmd + Shift + 3` for full screen
   - Screenshots will be saved to your Desktop

4. **Recommended screenshot settings**:
   - Use full browser window (maximize for best quality)
   - Zoom to 100% (Cmd + 0)
   - Hide browser toolbars for cleaner look (Cmd + Shift + F for fullscreen)

### Method 2: Using FastAPI /docs Endpoint

Your API is running at `http://localhost:8000`. You can also capture screenshots from:

1. **Open Swagger UI**:
   ```
   http://localhost:8000/docs
   ```

2. **Test endpoints and capture responses**:
   - `/api/jobs/scrape` - For Figure 4
   - `/api/analyze-resume` - For Figure 9
   - `/api/resume/optimize` - For Figure 10

3. **Take screenshots of**:
   - The endpoint interface
   - Request parameters
   - Response JSON (expand all sections)

### Method 3: Using Your Web UI

If you have the web UI running:

1. **Start the web server**:
   ```bash
   open web/index.html
   ```

2. **Upload a sample resume** and capture:
   - Career prediction results page
   - ATS optimization results page

---

## 🎨 Screenshot Tips for Best Quality

1. **Resolution**: Use at least 1920x1080 display resolution
2. **Browser**: Chrome or Safari (best rendering)
3. **Zoom**: Keep at 100% (Cmd + 0)
4. **Clean up**: Close unnecessary tabs and bookmarks bar
5. **Lighting**: Use light mode for better contrast in print
6. **Crop**: Crop to remove unnecessary whitespace
7. **Format**: Save as PNG for best quality (not JPG)

---

## 📊 What Each Figure Shows

### Figure 4: Adzuna API Response
**Purpose**: Demonstrate real-time job data ingestion capability

**Key Elements to Highlight**:
- API endpoint and parameters
- Number of jobs scraped (20)
- Job details: title, company, location, salary, skills
- Data source attribution (Adzuna API)

**Caption Suggestion**:
> "Figure 4 — Adzuna API response showing successful ingestion of 20 job listings with detailed metadata including title, company, location, salary range, and required skills. The system processes this data through the Bronze layer of the medallion architecture."

---

### Figure 9: Career Prediction Results
**Purpose**: Showcase ML model accuracy and comprehensive resume analysis

**Key Elements to Highlight**:
- Radar chart comparing candidate skills vs. role requirements
- Top 3 career predictions with confidence scores
- Salary prediction with range
- Extracted skills (10 technical skills)
- Skill gaps with priorities
- Verified certifications
- Model accuracy: 91.42%

**Caption Suggestion**:
> "Figure 9 — Career Prediction results from the ensemble ML model (91.42% accuracy) showing: (a) Skills radar chart comparing candidate profile against Software Engineer requirements, (b) Top 3 career predictions with confidence scores (Software Engineer: 70.3%, Data Scientist: 7.1%, Full Stack Developer: 5.1%), (c) Salary prediction of ₹12.3L with range, (d) 10 extracted skills, (e) 5 prioritized skill gaps, and (f) 3 verified certifications."

---

### Figure 10: ATS Optimization Results
**Purpose**: Demonstrate ATS compatibility analysis and actionable recommendations

**Key Elements to Highlight**:
- Overall ATS score: 33/100 (Poor)
- Score breakdown: Keyword Match (0), Formatting (80)
- 4 prioritized recommendations (High, Medium, Low)
- Step-by-step "How to Fix" guides
- ATS compatibility checklist
- Impact statements (e.g., "Improves ATS ranking by 25-35%")

**Caption Suggestion**:
> "Figure 10 — ATS Optimization results showing: (a) Overall ATS compatibility score of 33/100 with 'Poor' rating, (b) Score breakdown across keyword matching (0%), formatting (80%), and overall compatibility (33%), (c) Prioritized recommendations with HIGH priority on keyword density improvement, (d) Detailed 'How to Fix' guides for each issue, (e) ATS compatibility checklist showing 4/6 criteria met, and (f) Impact statements quantifying potential improvements (25-35% ranking boost)."

---

## 🔧 Troubleshooting

### If HTML files don't display correctly:
1. Make sure you have internet connection (for Chart.js CDN)
2. Try a different browser (Chrome recommended)
3. Check browser console for errors (F12)

### If charts don't render:
1. Wait a few seconds for Chart.js to load
2. Refresh the page (Cmd + R)
3. Check internet connection

### If you need to regenerate data:
```bash
python3 generate_figures.py
```

---

## 📝 Next Steps

1. ✅ Open each HTML file in your browser
2. ✅ Take high-quality screenshots
3. ✅ Save screenshots with descriptive names:
   - `figure_4_adzuna_api_response.png`
   - `figure_9_career_prediction_results.png`
   - `figure_10_ats_optimization_results.png`
4. ✅ Insert screenshots into your PROJECT_REPORT.md
5. ✅ Add captions using the suggestions above
6. ✅ Reference figures in the text (e.g., "As shown in Figure 4...")

---

## 🎯 Summary

All three figures are ready to be captured! The HTML files are fully styled, interactive, and production-ready. Simply open them in your browser and take screenshots.

**Files Created**:
- ✅ `figure_4_adzuna.html` - Adzuna API Response
- ✅ `figure_9_career_prediction.html` - Career Prediction Results  
- ✅ `figure_10_ats_optimization.html` - ATS Optimization Results
- ✅ `generate_figures.py` - Data generation script
- ✅ `FIGURE_4_ADZUNA_RESPONSE.json` - API response data
- ✅ `FIGURE_9_CAREER_PREDICTION.json` - Career prediction data
- ✅ `FIGURE_10_ATS_OPTIMIZATION.json` - ATS optimization data

**API Status**: ✅ Running at http://localhost:8000

Good luck with your project report! 🚀

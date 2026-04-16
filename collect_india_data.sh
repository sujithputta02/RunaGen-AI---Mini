#!/bin/bash

# Collect Indian Job Market Data from Adzuna API
# This script fetches real job data from India and processes it

echo "=========================================="
echo "RunaGen AI - India Data Collection"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with:"
    echo "  ADZUNA_APP_ID=your_app_id"
    echo "  ADZUNA_API_KEY=your_api_key"
    echo "  MONGO_URI=your_mongodb_uri"
    exit 1
fi

echo "✓ .env file found"
echo ""

# Step 1: Collect from Adzuna India API
echo "Step 1: Collecting jobs from Adzuna India API..."
echo "Country: India (in)"
echo "Queries: data engineer, data scientist, ml engineer, data analyst"
echo ""
python3 src/etl/adzuna_collector.py

if [ $? -eq 0 ]; then
    echo "✓ Data collection completed"
else
    echo "❌ Data collection failed"
    echo "Check your Adzuna API credentials in .env file"
    exit 1
fi

echo ""
echo "Step 2: Running ELT Pipeline (Bronze → Silver → Gold)..."
python3 src/etl/run_pipeline.py

if [ $? -eq 0 ]; then
    echo "✓ ELT Pipeline completed"
else
    echo "⚠️  ELT Pipeline had issues, continuing..."
fi

echo ""
echo "Step 3: Exporting to CSV for Tableau..."
python3 src/powerbi/export_to_powerbi.py

if [ $? -eq 0 ]; then
    echo "✓ CSV export completed"
else
    echo "❌ CSV export failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Indian Data Collection Complete!"
echo "=========================================="
echo ""
echo "CSV files created in: powerbi_data/"
echo ""
echo "Files:"
echo "  - skills.csv (from Indian job market)"
echo "  - jobs.csv (Indian companies & cities)"
echo "  - salaries.csv (INR currency)"
echo "  - career_transitions.csv"
echo "  - skill_gaps.csv"
echo ""
echo "Next steps:"
echo "1. Check powerbi_data/ folder"
echo "2. Open Tableau Public"
echo "3. Follow TABLEAU_GUIDE.md"
echo "4. Create dashboards with Indian data"
echo ""

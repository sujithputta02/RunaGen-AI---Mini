@echo off
REM Collect Indian Job Market Data from Adzuna API

echo ==========================================
echo RunaGen AI - India Data Collection
echo ==========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found
    echo Please create .env file with:
    echo   ADZUNA_APP_ID=your_app_id
    echo   ADZUNA_API_KEY=your_api_key
    echo   MONGO_URI=your_mongodb_uri
    pause
    exit /b 1
)

echo [OK] .env file found
echo.

REM Step 1: Collect from Adzuna India API
echo Step 1: Collecting jobs from Adzuna India API...
echo Country: India (in)
echo Queries: data engineer, data scientist, ml engineer, data analyst
echo.
python src/etl/adzuna_collector.py

if %errorlevel% neq 0 (
    echo [ERROR] Data collection failed
    echo Check your Adzuna API credentials in .env file
    pause
    exit /b 1
)

echo [OK] Data collection completed
echo.

REM Step 2: Run ELT Pipeline
echo Step 2: Running ELT Pipeline (Bronze - Silver - Gold)...
python src/etl/run_pipeline.py

if %errorlevel% neq 0 (
    echo [WARNING] ELT Pipeline had issues, continuing...
)

echo [OK] ELT Pipeline completed
echo.

REM Step 3: Export to CSV
echo Step 3: Exporting to CSV for Tableau...
python src/powerbi/export_to_powerbi.py

if %errorlevel% neq 0 (
    echo [ERROR] CSV export failed
    pause
    exit /b 1
)

echo [OK] CSV export completed
echo.

echo ==========================================
echo SUCCESS! Indian Data Collection Complete!
echo ==========================================
echo.
echo CSV files created in: powerbi_data\
echo.
echo Files:
echo   - skills.csv (from Indian job market)
echo   - jobs.csv (Indian companies and cities)
echo   - salaries.csv (INR currency)
echo   - career_transitions.csv
echo   - skill_gaps.csv
echo.
echo Next steps:
echo 1. Check powerbi_data\ folder
echo 2. Open Tableau Public
echo 3. Follow TABLEAU_GUIDE.md
echo 4. Create dashboards with Indian data
echo.
pause

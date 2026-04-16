@echo off
REM Start RunaGen AI Web Application

echo Starting RunaGen AI Web Application
echo ======================================
echo.

cd /d "%~dp0"

REM Check if models exist
if not exist "models\career_predictor.pkl" (
    echo Warning: ML models not found. Training models first...
    python src\ml\train_models.py
    echo.
)

REM Start API server
echo Starting API server...
start /B python src\api\main.py

REM Wait for API to start
timeout /t 3 /nobreak > nul

echo.
echo ======================================
echo RunaGen AI is ready!
echo.
echo Web Interface: Opening in browser...
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ======================================
echo.

REM Open web interface
start web\index.html

pause

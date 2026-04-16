@echo off
REM Start FastAPI server

echo Starting RunaGen AI API Server...
echo ==================================
echo.

cd /d "%~dp0"

REM Check if models exist
if not exist "models\career_predictor.pkl" (
    echo Warning: ML models not found. Training models first...
    python src\ml\train_models.py
    echo.
)

echo Starting API server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python src\api\main.py
pause

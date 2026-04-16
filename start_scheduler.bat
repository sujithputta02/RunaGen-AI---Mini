@echo off
REM Start the automated pipeline scheduler (Windows)

echo Starting RunaGen AI Automated Pipeline Scheduler
echo ==================================================

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Set mode (production, development, or testing)
set MODE=%1
if "%MODE%"=="" set MODE=production

REM Set collection mode (priority, full, or category)
set COLLECTION=%2
if "%COLLECTION%"=="" set COLLECTION=priority

echo Scheduler Mode: %MODE%
echo Collection Mode: %COLLECTION%
echo.

REM Start scheduler
python src\scheduler\automated_pipeline.py --mode %MODE% --collection %COLLECTION%

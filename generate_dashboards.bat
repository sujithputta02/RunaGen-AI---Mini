@echo off
REM Generate BI Dashboards

echo Generating RunaGen AI BI Dashboards...
echo ======================================
echo.

cd /d "%~dp0"

REM Generate dashboards
python src\dashboards\dashboard_generator.py

echo.
echo ======================================
echo Dashboards generated successfully!
echo.
echo Opening dashboards in browser...
start dashboards\html\index.html

pause

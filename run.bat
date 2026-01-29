@echo off
echo ========================================
echo  BUDGET ANALYSIS PRO - STARTUP LAUNCHER
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher from: https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo 📦 Checking required packages...
python -c "import flask, pandas, werkzeug" >nul 2>&1
if errorlevel 1 (
    echo 📥 Installing required packages...
    pip install flask pandas werkzeug openpyxl
)

REM Create required directories
if not exist "uploads" mkdir uploads
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css

REM Start the application
echo.
echo 🚀 Starting Budget Analysis Pro...
echo 🌐 Open your browser to: http://localhost:5000
echo ⏳ Please wait...
echo.
echo ========================================
echo.

python budget_analysis_startup.py

pause
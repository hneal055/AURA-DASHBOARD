@echo off
REM Budget Analysis App Startup Script
REM Simple and robust version

echo.
echo ========================================
echo  Starting Budget Analysis App
echo ========================================
echo.

REM Go to project folder
cd /d "%~dp0"
echo Current folder: %CD%
echo.

REM Check if main app file exists
if not exist "web_app_COMPLETE_WITH_COMPARISON.py" (
    echo ERROR: Cannot find web_app_COMPLETE_WITH_COMPARISON.py
    echo Make sure this batch file is in the project folder
    echo.
    pause
    exit /b 1
)

REM Check if venv exists, if not create it
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Done!
    echo.
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    pause
    exit /b 1
)
echo.

REM Start Flask
echo Starting Flask server...
echo.
echo Your app will be at: http://localhost:8080
echo.
echo Press Ctrl+C to stop
echo.

python web_app_COMPLETE_WITH_COMPARISON.py

pause

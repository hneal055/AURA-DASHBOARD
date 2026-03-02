@echo off
REM ============================================================================
REM Budget Analysis App - Enhanced Startup Script
REM Includes Unicode support and better error handling
REM ============================================================================

REM Fix Unicode/Emoji display (prevents encoding errors)
chcp 65001 >nul 2>&1

cls
echo.
echo ================================================================================
echo                    BUDGET ANALYSIS APP - STARTING
echo ================================================================================
echo.

REM Save current directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [1/5] Checking project folder...
echo       Location: %CD%
echo.

REM Check if we're in the right directory
if not exist "web_app_COMPLETE_WITH_COMPARISON.py" (
    echo [ERROR] Cannot find web_app_COMPLETE_WITH_COMPARISON.py
    echo         Make sure you're in the correct folder!
    echo.
    pause
    exit /b 1
)
echo       [OK] Found Flask app file
echo.

echo [2/5] Checking virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please create it first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo       [OK] Virtual environment found
echo.

echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo       [OK] Virtual environment activated
echo.

echo [4/5] Checking Python packages...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [WARNING] Flask not installed. Installing now...
    pip install Flask==3.0.3 pandas openpyxl reportlab
    echo.
)
echo       [OK] Python packages ready
echo.

echo [5/5] Starting Flask server...
echo.
echo ================================================================================
echo.
echo   Your app will be available at:
echo.
echo      http://localhost:8080
echo      http://127.0.0.1:8080
echo.
echo   Press Ctrl+C to stop the server
echo.
echo ================================================================================
echo.

REM Start the Flask application
python web_app_COMPLETE_WITH_COMPARISON.py

REM If app exits with error
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo [ERROR] Flask app stopped with an error
    echo ================================================================================
    echo.
    echo Common issues:
    echo   - Port 8080 already in use
    echo   - Missing Python packages
    echo   - Syntax error in Flask app
    echo.
    echo Try these fixes:
    echo   1. Close other apps using port 8080
    echo   2. pip install Flask pandas openpyxl reportlab
    echo   3. Check the error message above
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Server stopped normally
echo ================================================================================
pause

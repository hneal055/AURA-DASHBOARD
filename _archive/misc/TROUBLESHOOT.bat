@echo off
REM ============================================================================
REM Budget Analysis App - Troubleshooting & Diagnostics
REM ============================================================================

chcp 65001 >nul 2>&1
cls

echo.
echo ================================================================================
echo                    TROUBLESHOOTING & DIAGNOSTICS
echo ================================================================================
echo.

cd /d "%~dp0"

echo [Checking System...]
echo.

echo 1. Python Installation:
echo    -------------------
python --version 2>nul
if errorlevel 1 (
    echo    [ERROR] Python not found in PATH
    echo    Install Python from: https://www.python.org/downloads/
) else (
    echo    [OK] Python is installed
)
echo.

echo 2. Project Location:
echo    ----------------
echo    Current folder: %CD%
echo.

echo 3. Required Files:
echo    --------------
if exist "web_app_COMPLETE_WITH_COMPARISON.py" (
    echo    [OK] web_app_COMPLETE_WITH_COMPARISON.py
) else (
    echo    [MISSING] web_app_COMPLETE_WITH_COMPARISON.py
)

if exist "START_APP.bat" (
    echo    [OK] START_APP.bat
) else (
    echo    [MISSING] START_APP.bat
)

if exist "budget_comparison.py" (
    echo    [OK] budget_comparison.py
) else (
    echo    [MISSING] budget_comparison.py
)
echo.

echo 4. Virtual Environment:
echo    -------------------
if exist "venv\Scripts\activate.bat" (
    echo    [OK] Virtual environment exists
    
    echo.
    echo    Activating to check packages...
    call venv\Scripts\activate.bat
    
    echo.
    echo    Checking Flask:
    python -c "import flask; print('    [OK] Flask version:', flask.__version__)" 2>nul || echo    [MISSING] Flask not installed
    
    echo.
    echo    Checking pandas:
    python -c "import pandas; print('    [OK] pandas version:', pandas.__version__)" 2>nul || echo    [MISSING] pandas not installed
    
    echo.
    echo    Checking openpyxl:
    python -c "import openpyxl; print('    [OK] openpyxl installed')" 2>nul || echo    [MISSING] openpyxl not installed
    
    echo.
    echo    Checking reportlab:
    python -c "import reportlab; print('    [OK] reportlab installed')" 2>nul || echo    [MISSING] reportlab not installed
    
) else (
    echo    [MISSING] Virtual environment not found
    echo.
    echo    Create it with:
    echo      python -m venv venv
)
echo.

echo 5. Port 8080 Availability:
echo    ----------------------
netstat -ano | findstr :8080 >nul
if errorlevel 1 (
    echo    [OK] Port 8080 is available
) else (
    echo    [WARNING] Port 8080 is in use
    echo.
    echo    Processes using port 8080:
    netstat -ano | findstr :8080
    echo.
    echo    Kill the process with:
    echo      taskkill /PID [PID_NUMBER] /F
)
echo.

echo.
echo ================================================================================
echo                         RECOMMENDED ACTIONS
echo ================================================================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [!] Create virtual environment:
    echo     python -m venv venv
    echo.
)

if not exist "web_app_COMPLETE_WITH_COMPARISON.py" (
    echo [!] Download the missing Flask app file
    echo.
)

echo [!] Install/Update all packages:
echo     venv\Scripts\activate
echo     pip install Flask==3.0.3 pandas openpyxl reportlab python-dotenv requests
echo.

echo [!] If port 8080 is in use:
echo     - Close other applications
echo     - Or kill the process using the port
echo.

echo ================================================================================
echo.
pause

@echo off
REM Production Budget Parser - Windows Startup Script
REM Copyright (c) 2024. All rights reserved.

REM Always run from the directory containing this script
cd /d "%~dp0"

echo ================================================================
echo   [92m[1mProduction Budget Parser - Starting Server[0m
echo ================================================================
echo.

REM Check for required .env values
if not exist ".env" (
    echo [91mERROR: .env file not found![0m
    echo Create a .env file with:
    echo   SECRET_KEY=your-secret-key
    echo   ANTHROPIC_API_KEY=your-anthropic-key
    echo   BUDGET_API_KEY=your-api-key
    echo.
    pause
    exit /b 1
)

REM Use local venv if it exists, otherwise fall back to system Python
if exist "venv\Scripts\python.exe" (
    set PYTHON=venv\Scripts\python.exe
    set PIP=venv\Scripts\pip.exe
    echo [96mUsing local venv Python[0m
) else (
    set PYTHON=python
    set PIP=pip
    echo [93mNo venv found — using system Python[0m
)

REM Install / verify dependencies
echo [96mChecking dependencies...[0m
%PIP% show flask-sqlalchemy >nul 2>&1
if errorlevel 1 (
    echo [91mMissing dependencies! Installing...[0m
    %PIP% install -r requirements.txt
    if errorlevel 1 (
        echo [91mFailed to install dependencies. Check requirements.txt[0m
        pause
        exit /b 1
    )
)

echo.
echo [92mStarting Flask server...[0m
echo.
echo Server will be available at:
echo   * Local:   http://localhost:8080
echo   * Network: http://%COMPUTERNAME%:8080
echo.
echo AI Insights API ^(requires X-API-Key header^):
echo   POST http://localhost:8080/api/ai-insights/^<file_id^>
echo   Header: X-API-Key: ^<BUDGET_API_KEY from .env^>
echo.
echo Press CTRL+C to stop the server
echo ================================================================
echo.

%PYTHON% web_app.py

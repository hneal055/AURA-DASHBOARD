@echo off
REM Contract Review Tool - Windows Startup Script
REM Copyright (c) 2024. All rights reserved.

REM Always run from the directory containing this script
cd /d "%~dp0"

echo ================================================================
echo   [92m[1mContract Review Tool - Starting Server[0m
echo ================================================================
echo.

REM Check if API key is set
if "%ANTHROPIC_API_KEY%"=="" (
    echo [93mWARNING: ANTHROPIC_API_KEY environment variable not set![0m
    echo.
    echo To use the AI analysis feature, you need to set your API key:
    echo   set ANTHROPIC_API_KEY=your-api-key-here
    echo.
    echo Or add it permanently to Windows Environment Variables:
    echo   1. Search for "Environment Variables" in Windows
    echo   2. Click "Edit the system environment variables"
    echo   3. Click "Environment Variables" button
    echo   4. Add ANTHROPIC_API_KEY under "User variables"
    echo.
    echo You can still access the interface, but analysis won't work.
    echo.
    set /p continue="Continue anyway? (Y/N): "
    if /i not "%continue%"=="Y" (
        echo Exiting...
        exit /b 1
    )
)

REM Use local venv if it exists, otherwise fall back to system Python
if exist "venv\Scripts\python.exe" (
    set PYTHON=venv\Scripts\python.exe
    set PIP=venv\Scripts\pip.exe
) else (
    set PYTHON=python
    set PIP=pip
)

echo [96mChecking dependencies...[0m
%PIP% show flask-sqlalchemy >nul 2>&1
if errorlevel 1 (
    echo [91mMissing dependencies! Installing...[0m
    %PIP% install -r requirements.txt
)

echo.
echo [92mStarting Flask server...[0m
echo.
echo Server will be available at:
echo   * Local:   http://localhost:5001
echo   * Network: http://%COMPUTERNAME%:5001
echo.
echo Login required — default password set in .env ^(APP_PASSWORD^)
echo Analysis history available at: http://localhost:5001/history
echo.
echo Press CTRL+C to stop the server
echo ================================================================
echo.

%PYTHON% app.py
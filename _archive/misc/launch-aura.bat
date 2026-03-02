@echo off
chcp 65001 >nul
title Aura Analytics Dashboard Launcher

echo ===========================================
echo    🚀 Aura Analytics Dashboard Launcher   
echo ===========================================
echo.

echo [AURA] Initializing Aura Analytics Dashboard...
echo.

:: Check for Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Node.js is installed
    node --version
) else (
    echo [WARNING] Node.js not installed (needed for Phase 2)
)

:: Check for Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Python is installed
    python --version
) else (
    echo [WARNING] Python not available for local server
)

echo.
echo [AURA] Starting Aura Dashboard on http://localhost:8080
echo [AURA] Press Ctrl+C to stop the server
echo.

:: Try to start server with available tools
where npx >nul 2>&1
if %errorlevel% equ 0 (
    echo [AURA] Using npx http-server...
    npx http-server -p 8080 -a localhost -o
    goto :end
)

where node >nul 2>&1
if %errorlevel% equ 0 (
    echo [AURA] Using Node.js http-server...
    npx http-server -p 8080 -a localhost -o
    goto :end
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    echo [AURA] Using Python HTTP server...
    python -m http.server 8080 --bind localhost
    goto :end
)

echo [ERROR] No server tool found. Please install:
echo   - Node.js ^(recommended^): https://nodejs.org
echo   - Python: https://python.org
echo.
echo [WARNING] You can also open index.html directly in your browser
pause

:end
echo.
echo [AURA] Thank you for using Aura Analytics!
pause
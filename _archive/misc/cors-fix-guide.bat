@echo off
echo Stopping servers...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im uvicorn.exe >nul 2>&1
timeout /t 2 >nul

echo Opening app.py in VS Code for CORS fix...
code "C:\Users\hneal\SCRIPT_PARSER_PROJECT\aura-api-simple\app.py"

echo.
echo ==========================================
echo   MANUAL STEP REQUIRED:
echo ==========================================
echo.
echo 1. Add this import at the TOP of app.py:
echo    from fastapi.middleware.cors import CORSMiddleware
echo.
echo 2. Add this code AFTER app = FastAPI():
echo.
echo    # CORS configuration
echo    origins = [
echo        "http://localhost:3000",
echo        "http://127.0.0.1:3000",
echo    ]
echo.
echo    app.add_middleware(
echo        CORSMiddleware,
echo        allow_origins=origins,
echo        allow_credentials=True,
echo        allow_methods=["*"],
echo        allow_headers=["*"],
echo    )
echo.
echo 3. Save the file in VS Code (Ctrl+S)
echo 4. Then press any key to continue...
pause >nul

echo Starting backend with CORS...
start "AURA Backend" cmd /k "cd /d C:\Users\hneal\SCRIPT_PARSER_PROJECT\aura-api-simple && venv\Scripts\activate && uvicorn app:app --reload --port 8000"

echo.
echo ? Backend starting with CORS support!
echo ?? Test at: http://localhost:3000
echo.
pause

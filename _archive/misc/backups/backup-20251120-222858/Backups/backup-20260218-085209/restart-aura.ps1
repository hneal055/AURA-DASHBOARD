echo "Stopping AURA Parser Pro servers..."
taskkill /f /im python.exe 2>$null
timeout /t 2

echo "Starting Backend API..."
cd aura-api-simple
venv\Scripts\activate
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn app:app --reload --port 8000"

echo "Starting Frontend Dashboard..."
cd ..\aura-frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m http.server 3000"

echo "AURA Parser Pro restarted!"
echo "Backend: http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"

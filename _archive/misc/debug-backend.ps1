# Backend Debugging Script
Write-Host "🐛 Debugging Backend Issues" -ForegroundColor Green

# Check container status
Write-Host "`n📦 Container Status:" -ForegroundColor Yellow
docker ps -a --filter "name=aura-backend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check logs
Write-Host "`n📝 Full Logs:" -ForegroundColor Yellow
docker logs aura-backend

# Check if Python dependencies are installed
Write-Host "`n🐍 Checking Python in container..." -ForegroundColor Yellow
docker exec aura-backend python --version
docker exec aura-backend pip list | findstr -i "flask\|gunicorn\|psycopg2"

# Check if application files are present
Write-Host "`n📁 Checking application files..." -ForegroundColor Yellow
docker exec aura-backend ls -la /app/

# Try to run the app manually in the container
Write-Host "`n🔧 Testing manual startup..." -ForegroundColor Yellow
docker exec -it aura-backend python run.py
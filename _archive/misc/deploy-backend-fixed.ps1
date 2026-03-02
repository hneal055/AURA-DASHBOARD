# Quick Fix for Backend Deployment
Write-Host "🔧 Fixing Backend Deployment" -ForegroundColor Green

# Stop and remove existing backend
docker stop aura-backend 2>&1 | Out-Null
docker rm aura-backend 2>&1 | Out-Null

# Check if we have the fixed Dockerfile
if (-not (Test-Path "Dockerfile.api")) {
    Write-Host "❌ Dockerfile.api not found" -ForegroundColor Red
    exit 1
}

# Rebuild with fixed Dockerfile
Write-Host "🔨 Rebuilding backend image..." -ForegroundColor Yellow
docker build -t aura-backend:latest -f Dockerfile.api .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed, trying alternative approach..." -ForegroundColor Red
    
    # Try the simple Dockerfile
    if (Test-Path "Dockerfile.api-simple") {
        Write-Host "Trying simple Dockerfile..." -ForegroundColor Yellow
        docker build -t aura-backend:latest -f Dockerfile.api-simple .
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ All build attempts failed" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Image rebuilt successfully" -ForegroundColor Green

# Start the backend with simpler configuration
Write-Host "🚀 Starting backend container..." -ForegroundColor Yellow
docker run -d `
    --name aura-backend `
    -p 5000:5000 `
    -e DB_HOST=aura-postgres `
    -e DB_NAME=aura_dashboard `
    -e DB_USER=aura_admin `
    -e DB_PASSWORD=AuraDB2024! `
    -e JWT_SECRET_KEY=aura-jwt-super-secret-2024 `
    -e SECRET_KEY=aura-flask-secret-2024 `
    -e FLASK_CONFIG=development `
    --link aura-postgres:postgres `
    aura-backend:latest

Write-Host "✅ Backend container started" -ForegroundColor Green

# Check status with detailed logs
Write-Host "`n📋 Checking container status..." -ForegroundColor Cyan
docker ps -a --filter "name=aura-backend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n📝 Checking logs..." -ForegroundColor Cyan
docker logs aura-backend

Write-Host "`n🎉 Fixed deployment complete!" -ForegroundColor Green
Write-Host "Run .\backend-status.ps1 to check if it's working" -ForegroundColor White
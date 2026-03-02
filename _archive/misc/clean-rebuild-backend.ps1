# Complete Clean Rebuild of Backend
Write-Host "🧹 Complete Backend Clean Rebuild" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan

# Stop and remove all backend containers
Write-Host "🛑 Stopping and removing backend containers..." -ForegroundColor Yellow
docker stop aura-backend 2>&1 | Out-Null
docker rm aura-backend 2>&1 | Out-Null

# Remove all backend images
Write-Host "🗑️ Removing backend images..." -ForegroundColor Yellow
docker images --filter "reference=aura-backend*" --format "table {{.ID}}\t{{.Repository}}\t{{.Tag}}" | ForEach-Object {
    if ($_ -match "^(?<ImageID>[a-f0-9]+)\s+aura-backend") {
        docker rmi $matches.ImageID -f 2>&1 | Out-Null
    }
}

# Clean up any dangling images
Write-Host "🧽 Cleaning up dangling images..." -ForegroundColor Yellow
docker image prune -f 2>&1 | Out-Null

# Verify the fixed models.py is in place
Write-Host "🔍 Verifying fixed models.py..." -ForegroundColor Yellow
if (Test-Path "backend/app/models.py") {
    $content = Get-Content "backend/app/models.py" -Raw
    if ($content -match 'query = """SELECT id, username, email, password_hash, role, first_name, last_name,') {
        Write-Host "✅ models.py is fixed" -ForegroundColor Green
    } else {
        Write-Host "❌ models.py still has issues" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ models.py not found" -ForegroundColor Red
    exit 1
}

# Create a fresh Dockerfile without cache issues
Write-Host "🐳 Creating fresh Dockerfile..." -ForegroundColor Yellow
$freshDockerfile = @'
FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies
RUN apk update && apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    linux-headers \
    curl \
    libpq

# Copy requirements first
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Simple startup command
CMD ["python", "run.py"]
'@

$freshDockerfile | Out-File -FilePath "Dockerfile.fresh" -Encoding UTF8
Write-Host "✅ Created fresh Dockerfile" -ForegroundColor Green

# Build with no cache
Write-Host "🔨 Building fresh backend image (no cache)..." -ForegroundColor Yellow
docker build --no-cache -t aura-backend-fresh -f Dockerfile.fresh .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Fresh image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Fresh build failed" -ForegroundColor Red
    Write-Host "Trying alternative approach..." -ForegroundColor Yellow
    
    # Alternative: Use docker-compose
    if (Test-Path "docker-compose.full.yml") {
        Write-Host "🔄 Trying docker-compose..." -ForegroundColor Yellow
        docker-compose -f docker-compose.full.yml build --no-cache backend
    } else {
        exit 1
    }
}

# Start the fresh backend
Write-Host "🚀 Starting fresh backend..." -ForegroundColor Yellow
docker run -d `
    --name aura-backend `
    -p 5000:5000 `
    -e DB_HOST=aura-postgres `
    -e DB_PORT=5432 `
    -e DB_NAME=aura_dashboard `
    -e DB_USER=aura_admin `
    -e DB_PASSWORD=AuraDB2024! `
    -e JWT_SECRET_KEY=aura-jwt-super-secret-2024 `
    -e SECRET_KEY=aura-flask-secret-2024 `
    -e FLASK_CONFIG=development `
    --link aura-postgres:postgres `
    aura-backend-fresh

Write-Host "✅ Fresh backend started" -ForegroundColor Green

# Monitor startup
Write-Host "`n📊 Monitoring backend startup..." -ForegroundColor Cyan

$maxWait = 30
$waited = 0
$isHealthy = $false

while ($waited -lt $maxWait -and -not $isHealthy) {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 2
        if ($health.status -eq "healthy") {
            $isHealthy = $true
            Write-Host "✅ Backend is healthy!" -ForegroundColor Green
            break
        }
    } catch {
        # Not ready yet
    }
    
    Write-Host "⏳ Waiting... ($waited/$maxWait seconds)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
    $waited += 2
    
    # Show logs every 10 seconds
    if ($waited % 10 -eq 0) {
        Write-Host "`n📝 Recent logs:" -ForegroundColor Yellow
        docker logs aura-backend --tail 5
    }
}

if (-not $isHealthy) {
    Write-Host "❌ Backend didn't become healthy within $maxWait seconds" -ForegroundColor Red
    Write-Host "`n📋 Full logs:" -ForegroundColor Yellow
    docker logs aura-backend
} else {
    Write-Host "`n🎉 Backend is fully operational!" -ForegroundColor Green
    Write-Host "🔗 API: http://localhost:5000" -ForegroundColor White
    Write-Host "🔐 Health: http://localhost:5000/health" -ForegroundColor White
}
# Fix Docker Build Context
Write-Host "🔧 Fixing Docker Build Context" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan

# Stop and remove any existing backend
docker stop aura-backend 2>&1 | Out-Null
docker rm aura-backend 2>&1 | Out-Null

# Check what files we have
Write-Host "📁 Checking backend files..." -ForegroundColor Yellow
if (Test-Path "backend") {
    Get-ChildItem -Path "backend" -Recurse -Name | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "❌ Backend directory not found" -ForegroundColor Red
    exit 1
}

# Create a corrected Dockerfile with proper context
Write-Host "🐳 Creating corrected Dockerfile..." -ForegroundColor Yellow
$correctedDockerfile = @'
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

# Copy backend files
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire backend directory
COPY backend/ .

# Create a startup script that shows what files are available
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'echo "=== AURA Backend Starting ==="' >> /app/start.sh && \
    echo 'echo "Current directory: $(pwd)"' >> /app/start.sh && \
    echo 'echo "Files in /app:"' >> /app/start.sh && \
    echo 'ls -la' >> /app/start.sh && \
    echo 'echo "=== Starting Application ==="' >> /app/start.sh && \
    echo 'python run.py' >> /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE 5000

CMD ["/app/start.sh"]
'@

$correctedDockerfile | Out-File -FilePath "Dockerfile.corrected" -Encoding UTF8
Write-Host "✅ Created corrected Dockerfile" -ForegroundColor Green

# Build with the corrected Dockerfile
Write-Host "🔨 Building corrected backend image..." -ForegroundColor Yellow
docker build -t aura-backend-corrected -f Dockerfile.corrected .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Image built successfully" -ForegroundColor Green

# Start the backend
Write-Host "🚀 Starting corrected backend..." -ForegroundColor Yellow
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
    aura-backend-corrected

Write-Host "✅ Backend container started" -ForegroundColor Green

# Check the logs to see what happened
Write-Host "`n📝 Checking startup logs..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
docker logs aura-backend

Write-Host "`n🎉 Corrected deployment complete!" -ForegroundColor Green
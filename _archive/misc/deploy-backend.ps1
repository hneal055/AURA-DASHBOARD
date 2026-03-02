# Phase 3.2 - Backend API Deployment (Fixed for Windows)
Write-Host "🚀 Deploying AURA Backend API" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan

function Write-Status {
    param($Message, $Color = "White")
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Gray
    Write-Host $Message -ForegroundColor $Color
}

# Check if database is running
Write-Status "Checking database status..."
$dbStatus = docker ps -q -f "name=aura-postgres"
if (-not $dbStatus) {
    Write-Status "❌ Database container is not running" "Red"
    Write-Host "💡 Run: .\setup-database.ps1" -ForegroundColor Yellow
    exit 1
}
Write-Status "✅ Database is running" "Green"

# Check if backend directory exists
if (-not (Test-Path "backend")) {
    Write-Status "❌ Backend directory not found" "Red"
    Write-Host "💡 Run: .\setup-backend.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Create simplified requirements without psycopg2 build issues
Write-Status "Creating Windows-compatible requirements..." "Yellow"
$simpleRequirements = @"
Flask==2.3.3
Flask-JWT-Extended==4.5.3
Flask-CORS==4.0.0
Flask-Bcrypt==1.0.1
psycopg2-binary==2.9.7
python-dotenv==1.0.0
gunicorn==21.2.0
pyjwt==2.8.0
requests==2.31.0
"@

$simpleRequirements | Out-File -FilePath "backend/requirements-simple.txt" -Encoding UTF8
Write-Status "✅ Created simplified requirements" "Green"

# Build backend Docker image directly (skip local Python install)
Write-Status "Building backend Docker image..." "Yellow"

# Stop existing backend container if running
$existingBackend = docker ps -a -q -f "name=aura-backend"
if ($existingBackend) {
    Write-Status "Stopping existing backend container..." "Yellow"
    docker stop aura-backend 2>&1 | Out-Null
    docker rm aura-backend 2>&1 | Out-Null
}

# Build the Docker image - this will handle dependencies in Linux container
docker build -t aura-backend:latest -f Dockerfile.api .

if ($LASTEXITCODE -eq 0) {
    Write-Status "✅ Backend Docker image built successfully" "Green"
} else {
    Write-Status "❌ Failed to build backend image" "Red"
    Write-Host "Trying alternative build approach..." -ForegroundColor Yellow
    
    # Try building with no cache
    docker build --no-cache -t aura-backend:latest -f Dockerfile.api .
    
    if ($LASTEXITCODE -ne 0) {
        Write-Status "❌ Build failed even with no cache" "Red"
        exit 1
    }
}

# Run backend container
Write-Status "Starting backend container..." "Yellow"
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
    -e FLASK_CONFIG=production `
    --link aura-postgres:postgres `
    aura-backend:latest

if ($LASTEXITCODE -eq 0) {
    Write-Status "✅ Backend container started successfully" "Green"
} else {
    Write-Status "❌ Failed to start backend container" "Red"
    exit 1
}

# Wait for backend to be ready with better polling
Write-Status "Waiting for backend to be ready..." "Yellow"
$maxAttempts = 12
$attempt = 0
$isHealthy = $false

while ($attempt -lt $maxAttempts -and -not $isHealthy) {
    $attempt++
    Write-Host "   Attempt $attempt/$maxAttempts..." -NoNewline -ForegroundColor Gray
    
    try {
        $healthResponse = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get -TimeoutSec 5
        if ($healthResponse.status -eq "healthy") {
            Write-Host " ✅ Healthy!" -ForegroundColor Green
            $isHealthy = $true
            break
        }
    } catch {
        Write-Host " ❌ Not ready yet" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}

if (-not $isHealthy) {
    Write-Status "❌ Backend failed to become healthy within $($maxAttempts * 5) seconds" "Red"
    Write-Host "`n🔍 Checking backend logs..." -ForegroundColor Yellow
    docker logs aura-backend --tail 20
    Write-Host "`n💡 Troubleshooting steps:" -ForegroundColor Cyan
    Write-Host "   1. Check if port 5000 is available" -ForegroundColor White
    Write-Host "   2. Verify database connection" -ForegroundColor White
    Write-Host "   3. Check Docker resource allocation" -ForegroundColor White
    exit 1
}

# Test authentication endpoint
Write-Status "Testing authentication system..." "Yellow"
$loginData = @{
    username = "admin"
    password = "AuraDemo2024!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/v1/auth/login" -Method Post -Body $loginData -ContentType "application/json" -TimeoutSec 10
    
    if ($loginResponse.status -eq "success") {
        Write-Status "✅ Authentication test successful" "Green"
        Write-Host "   User: $($loginResponse.user.username)" -ForegroundColor Gray
        Write-Host "   Role: $($loginResponse.user.role)" -ForegroundColor Gray
        Write-Host "   Token: $($loginResponse.access_token.substring(0, 50))..." -ForegroundColor Gray
    } else {
        Write-Status "❌ Authentication test failed" "Red"
        Write-Host "   Response: $($loginResponse | ConvertTo-Json -Compress)" -ForegroundColor Red
    }
} catch {
    Write-Status "❌ Authentication test failed: $($_.Exception.Message)" "Red"
    Write-Host "🔍 Checking backend logs for details..." -ForegroundColor Yellow
    docker logs aura-backend --tail 10
}

Write-Host "`n🎉 Backend API Deployment Complete!" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "📊 Backend API: http://localhost:5000" -ForegroundColor White
Write-Host "🔐 Health Check: http://localhost:5000/health" -ForegroundColor White
Write-Host "🔑 Login Endpoint: http://localhost:5000/api/v1/auth/login" -ForegroundColor White
Write-Host "📈 System Metrics: http://localhost:5000/api/v1/system/health" -ForegroundColor White
Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Run .\test-backend.ps1 to run comprehensive tests" -ForegroundColor White
Write-Host "   2. Check .\backend-status.ps1 for quick status" -ForegroundColor White
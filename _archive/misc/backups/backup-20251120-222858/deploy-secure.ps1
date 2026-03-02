
Write-Host "🚀 Deploying AURA Dashboard (Secure Version)..." -ForegroundColor Cyan

# Check if SSL certificates exist
if (-not (Test-Path "ssl\cert.pem") -or -not (Test-Path "ssl\key.pem")) {
    Write-Host "SSL certificates not found. Generating..." -ForegroundColor Yellow
    .\add-ssl.ps1
}

Write-Host "Building secure Docker image..." -ForegroundColor White
docker build -t aura-dashboard-secure -f Dockerfile.secure .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "Stopping and removing old container..." -ForegroundColor White
docker stop aura-dashboard-secure 2>$null
docker rm aura-dashboard-secure 2>$null

Write-Host "Starting secure container..." -ForegroundColor White
docker run -d -p 80:80 -p 443:443 --name aura-dashboard-secure aura-dashboard-secure

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ AURA Dashboard (Secure) started successfully" -ForegroundColor Green
    Write-Host "📍 Access: https://localhost" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to start container" -ForegroundColor Red
}
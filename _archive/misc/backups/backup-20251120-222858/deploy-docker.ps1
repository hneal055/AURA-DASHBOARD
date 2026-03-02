# AURA Enterprise Dashboard - Docker Deployment Script
# Version: 2.3.1
# Description: Deploys AURA Enterprise Dashboard using Docker

Write-Host "🚀 AURA Enterprise Dashboard - Docker Deployment" -ForegroundColor Green
Write-Host "=" * 60
Write-Host "AI-Powered Screenplay Analysis Platform" -ForegroundColor Cyan
Write-Host "Enterprise Grade • Production Ready • Containerized" -ForegroundColor Cyan
Write-Host "=" * 60

# Function to display status messages
function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = @{
        "SUCCESS" = "Green"
        "ERROR" = "Red" 
        "WARNING" = "Yellow"
        "INFO" = "Cyan"
    }
    
    Write-Host "[$timestamp] " -NoNewline -ForegroundColor White
    Write-Host "$Message" -ForegroundColor $color[$Type]
}

# Check if Docker is running
Write-Status "Checking Docker installation..." "INFO"
try {
    $dockerVersion = docker --version
    Write-Status "Docker: $dockerVersion" "SUCCESS"
} catch {
    Write-Status "Docker is not running or not installed" "ERROR"
    Write-Host "   Please ensure Docker Desktop is running" -ForegroundColor Yellow
    Write-Host "   Download from: https://docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check for required files
Write-Status "Verifying required deployment files..." "INFO"

$requiredFiles = @(
    @{Name="Dockerfile"; Description="Container definition"},
    @{Name="index.html"; Description="AURA dashboard application"}
)

$optionalFiles = @(
    @{Name="nginx.conf"; Description="Nginx configuration"},
    @{Name="docker-compose.yml"; Description="Container orchestration"}
)

$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (Test-Path $file.Name) {
        Write-Status "$($file.Name) - $($file.Description)" "SUCCESS"
    } else {
        $missingFiles += $file.Name
        Write-Status "$($file.Name) - $($file.Description) - MISSING" "ERROR"
    }
}

foreach ($file in $optionalFiles) {
    if (Test-Path $file.Name) {
        Write-Status "$($file.Name) - $($file.Description)" "SUCCESS"
    } else {
        Write-Status "$($file.Name) - $($file.Description) - Optional" "WARNING"
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Status "Missing required files: $($missingFiles -join ', ')" "ERROR"
    Write-Host "   Please ensure all required files are present before deploying" -ForegroundColor Yellow
    exit 1
}

# Clean up previous builds and containers
Write-Status "Cleaning up previous builds and containers..." "INFO"

Write-Status "Stopping existing AURA containers..." "INFO"
docker stop aura-dashboard 2>$null
docker rm aura-dashboard 2>$null

Write-Status "Removing unused Docker data..." "INFO"
docker system prune -f 2>$null

# Build the Docker image
Write-Status "Building Docker image: aura-dashboard..." "INFO"
docker build -t aura-dashboard .

if ($LASTEXITCODE -ne 0) {
    Write-Status "Docker build failed - check errors above" "ERROR"
    Write-Host "   Common issues:" -ForegroundColor Yellow
    Write-Host "   - Missing files in build context" -ForegroundColor Yellow
    Write-Host "   - Docker Desktop not running" -ForegroundColor Yellow
    Write-Host "   - Network connectivity issues" -ForegroundColor Yellow
    exit 1
}

# Run the container
Write-Status "Starting AURA Dashboard container..." "INFO"
docker run -d `
  --name aura-dashboard `
  -p 8080:80 `
  --restart unless-stopped `
  aura-dashboard

if ($LASTEXITCODE -eq 0) {
    Write-Status "AURA Dashboard container started successfully" "SUCCESS"
} else {
    Write-Status "Failed to start container" "ERROR"
    exit 1
}

# Wait for container to initialize
Write-Status "Waiting for container to initialize..." "INFO"
Start-Sleep -Seconds 5

# Display deployment summary
Write-Host "`n" + "=" * 60 -ForegroundColor Green
Write-Host "🎉 AURA ENTERPRISE DASHBOARD DEPLOYED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

Write-Host "`n📍 ACCESS URLs:" -ForegroundColor Yellow
Write-Host "   Main Dashboard:  http://localhost:8080" -ForegroundColor Cyan
Write-Host "   Health Check:    http://localhost:8080/health" -ForegroundColor Cyan

Write-Host "`n📊 CONTAINER STATUS:" -ForegroundColor Yellow
docker ps --filter "name=aura-dashboard" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n🔧 MANAGEMENT COMMANDS:" -ForegroundColor Yellow
Write-Host "   View Logs:       docker logs aura-dashboard" -ForegroundColor White
Write-Host "   Stop Container:  docker stop aura-dashboard" -ForegroundColor White
Write-Host "   Start Container: docker start aura-dashboard" -ForegroundColor White
Write-Host "   Remove Container: docker rm -f aura-dashboard" -ForegroundColor White

Write-Host "`n📈 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "   1. Open http://localhost:8080 in your browser" -ForegroundColor White
Write-Host "   2. Verify all dashboard features are working" -ForegroundColor White
Write-Host "   3. Consider deploying to cloud (AWS, Azure, GCP)" -ForegroundColor White

# Test health endpoint
Write-Host "`n🏥 PERFORMING HEALTH CHECK..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 10
    Write-Status "Health check: $($health.Content.Trim())" "SUCCESS"
} catch {
    Write-Status "Health check: $($_.Exception.Message)" "WARNING"
    Write-Host "   The container might need more time to start..." -ForegroundColor Yellow
    Write-Host "   Try accessing http://localhost:8080 in 30 seconds" -ForegroundColor Yellow
}

Write-Host "`n" + "=" * 60 -ForegroundColor Green
Write-Host "✅ DEPLOYMENT COMPLETED - AURA Enterprise Dashboard is now running!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

# Optional: Open browser automatically
$openBrowser = Read-Host "`n🌐 Open dashboard in browser now? (Y/N)"
if ($openBrowser -eq 'Y' -or $openBrowser -eq 'y') {
    Start-Process "http://localhost:8080"
    Write-Status "Browser opened with AURA Dashboard" "SUCCESS"
}

Write-Host "`nThank you for using AURA Enterprise Platform! 🚀" -ForegroundColor Cyan
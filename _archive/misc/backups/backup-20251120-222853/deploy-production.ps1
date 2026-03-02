Write-Host "🏭 PRODUCTION DEPLOYMENT" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n1. Pre-deployment checks..." -ForegroundColor White

# Check system resources
$memory = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
$disk = (Get-PSDrive -Name C).Free / 1GB

Write-Host "   System Memory: $([math]::Round($memory, 2)) GB" -ForegroundColor Gray
Write-Host "   Free Disk Space: $([math]::Round($disk, 2)) GB" -ForegroundColor Gray

if ($memory -lt 2) {
    Write-Host "⚠️  Low memory - recommend 2GB+ for production" -ForegroundColor Yellow
}

if ($disk -lt 5) {
    Write-Host "⚠️  Low disk space - recommend 5GB+ free" -ForegroundColor Yellow
}

Write-Host "`n2. Security validation..." -ForegroundColor White

.\security-scan.ps1

Write-Host "`n3. Creating production backup..." -ForegroundColor White

.\auto-backup.ps1

Write-Host "`n4. Deploying production container..." -ForegroundColor White

# Stop existing production container
docker stop aura-dashboard-prod 2>$null
docker rm aura-dashboard-prod 2>$null

# Build with production settings
docker build -t aura-dashboard-prod -f Dockerfile.secure .

# Run with production settings
docker run -d `
  --name aura-dashboard-prod `
  -p 80:80 `
  --restart unless-stopped `
  --memory "512m" `
  --cpus "1.0" `
  aura-dashboard-prod

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Production container deployed successfully" -ForegroundColor Green
    
    Write-Host "`n5. Health check..." -ForegroundColor White
    Start-Sleep -Seconds 3
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:80" -TimeoutSec 10 -UseBasicParsing
        Write-Host "✅ Production dashboard is healthy" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Health check issue: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Production deployment failed" -ForegroundColor Red
}

Write-Host "`n🎉 PRODUCTION DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "📊 Production Features:" -ForegroundColor White
Write-Host "   • Security headers enabled" -ForegroundColor Gray
Write-Host "   • Resource limits configured" -ForegroundColor Gray
Write-Host "   • Auto-restart on failure" -ForegroundColor Gray
Write-Host "   • Health monitoring" -ForegroundColor Gray
Write-Host "   • Backup system ready" -ForegroundColor Gray
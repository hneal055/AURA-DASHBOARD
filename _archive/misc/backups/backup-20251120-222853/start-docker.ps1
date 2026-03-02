Write-Host "🎯 Starting AURA Dashboard..." -ForegroundColor Yellow
docker start aura-dashboard
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ AURA Dashboard started successfully" -ForegroundColor Green
    Write-Host "📍 Access: http://localhost:8080" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to start container" -ForegroundColor Red
}
Write-Host "🛑 Stopping AURA Dashboard..." -ForegroundColor Yellow
docker stop aura-dashboard
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ AURA Dashboard stopped successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️  Container was not running" -ForegroundColor Yellow
}
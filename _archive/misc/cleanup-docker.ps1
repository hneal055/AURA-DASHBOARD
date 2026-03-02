Write-Host "🧹 Cleaning up AURA Dashboard..." -ForegroundColor Yellow

Write-Host "Stopping container..." -ForegroundColor White
docker stop aura-dashboard 2>$null

Write-Host "Removing container..." -ForegroundColor White
docker rm aura-dashboard 2>$null

Write-Host "Removing image..." -ForegroundColor White
docker rmi aura-dashboard 2>$null

Write-Host "Cleaning system..." -ForegroundColor White
docker system prune -f

Write-Host "✅ Cleanup completed successfully" -ForegroundColor Green
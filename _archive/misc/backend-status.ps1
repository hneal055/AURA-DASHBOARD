# Quick Backend Status Check
Write-Host "🔍 AURA Backend Status Check" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Cyan

# Check container status
Write-Host "`n📦 Container Status:" -ForegroundColor Yellow
docker ps -a --filter "name=aura-backend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check health
try {
    Write-Host "`n🏥 Health Check:" -ForegroundColor Yellow
    $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 5
    Write-Host "✅ $($health.status) - $($health.service)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not responding: $($_.Exception.Message)" -ForegroundColor Red
}

# Check recent logs
Write-Host "`n📝 Recent Logs:" -ForegroundColor Yellow
docker logs aura-backend --tail 5 2>&1

# Test database connection through backend
try {
    Write-Host "`n🗄️ Database Connection Test:" -ForegroundColor Yellow
    $loginTest = @{username = "admin"; password = "AuraDemo2024!"} | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/v1/auth/login" -Method Post -Body $loginTest -ContentType "application/json" -TimeoutSec 5
    
    if ($response.status -eq "success") {
        Write-Host "✅ Database connection working" -ForegroundColor Green
        Write-Host "   Logged in as: $($response.user.username)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Database connection test failed" -ForegroundColor Red
}
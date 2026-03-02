# Quick Manual Backend Test
Write-Host "🔧 Quick Manual Backend Test" -ForegroundColor Green

# Check if backend is running
$status = docker ps -q -f "name=aura-backend"
if (-not $status) {
    Write-Host "❌ Backend not running" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Backend container running" -ForegroundColor Green

# Show recent logs
Write-Host "`n📝 Recent logs:" -ForegroundColor Cyan
docker logs aura-backend --tail 10

# Quick health check
try {
    Write-Host "`n🏥 Health check..." -ForegroundColor Yellow
    $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 3
    Write-Host "✅ $($health.status) - $($health.service)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Quick login test
try {
    Write-Host "`n🔐 Login test..." -ForegroundColor Yellow
    $loginData = @{
        username = "admin"
        password = "AuraDemo2024!"
    } | ConvertTo-Json
    
    $login = Invoke-RestMethod -Uri "http://localhost:5000/api/v1/auth/login" -Method Post -Body $loginData -ContentType "application/json" -TimeoutSec 5
    
    if ($login.status -eq "success") {
        Write-Host "✅ Login successful" -ForegroundColor Green
        Write-Host "   User: $($login.user.username)" -ForegroundColor Gray
        Write-Host "   Token: $($login.access_token.substring(0, 30))..." -ForegroundColor Gray
    } else {
        Write-Host "❌ Login failed: $($login.message)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Login test failed: $($_.Exception.Message)" -ForegroundColor Red
}
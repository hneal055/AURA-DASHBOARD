# Test Fixed Backend
Write-Host "🧪 Testing Fixed Backend" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Cyan

# Check if backend is running
$containerStatus = docker ps -q -f "name=aura-backend"
if (-not $containerStatus) {
    Write-Host "❌ Backend container is not running" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Backend container is running" -ForegroundColor Green

# Test endpoints
$baseUrl = "http://localhost:5000"

Write-Host "`n🔬 Testing endpoints..." -ForegroundColor Yellow

# Test 1: Health endpoint
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
    Write-Host "✅ Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: System health (public)
try {
    $system = Invoke-RestMethod -Uri "$baseUrl/api/v1/system/health" -TimeoutSec 5
    Write-Host "✅ System Health: $($system.status)" -ForegroundColor Green
    Write-Host "   CPU: $($system.data.cpu_usage)%" -ForegroundColor Gray
    Write-Host "   Memory: $($system.data.memory_usage)%" -ForegroundColor Gray
} catch {
    Write-Host "❌ System health failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Login
try {
    $loginData = @{
        username = "admin"
        password = "AuraDemo2024!"
    } | ConvertTo-Json
    
    $login = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $loginData -ContentType "application/json" -TimeoutSec 5
    
    if ($login.status -eq "success") {
        Write-Host "✅ Login successful" -ForegroundColor Green
        Write-Host "   User: $($login.user.username)" -ForegroundColor Gray
        Write-Host "   Role: $($login.user.role)" -ForegroundColor Gray
        
        # Test 4: Protected endpoint with token
        $token = $login.access_token
        $headers = @{Authorization = "Bearer $token"}
        
        $profile = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/me" -Headers $headers -TimeoutSec 5
        Write-Host "✅ Protected endpoint access: $($profile.status)" -ForegroundColor Green
        
        # Test 5: Dashboard stats
        $stats = Invoke-RestMethod -Uri "$baseUrl/api/v1/dashboard/stats" -Headers $headers -TimeoutSec 5
        Write-Host "✅ Dashboard stats: $($stats.status)" -ForegroundColor Green
        Write-Host "   Users: $($stats.data.user_count)" -ForegroundColor Gray
        Write-Host "   Metrics: $($stats.data.metrics_count)" -ForegroundColor Gray
        
    } else {
        Write-Host "❌ Login failed: $($login.message)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Login test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Backend testing complete!" -ForegroundColor Green
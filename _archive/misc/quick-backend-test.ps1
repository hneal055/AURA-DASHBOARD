# Quick Backend Test (No Dependencies Required)
Write-Host "🧪 Quick Backend Test" -ForegroundColor Green

$baseUrl = "http://localhost:5000"

# Test 1: Health endpoint
try {
    Write-Host "`n1. Testing health endpoint..." -NoNewline
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
    Write-Host " ✅ $($health.status)" -ForegroundColor Green
} catch {
    Write-Host " ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Login endpoint
try {
    Write-Host "2. Testing login endpoint..." -NoNewline
    $loginData = @{username = "admin"; password = "AuraDemo2024!"} | ConvertTo-Json
    $login = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $loginData -ContentType "application/json" -TimeoutSec 5
    
    if ($login.status -eq "success") {
        Write-Host " ✅ Logged in as $($login.user.username)" -ForegroundColor Green
        $token = $login.access_token
        
        # Test 3: Protected endpoint with token
        Write-Host "3. Testing protected endpoint..." -NoNewline
        $headers = @{Authorization = "Bearer $token"}
        $profile = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/me" -Headers $headers -TimeoutSec 5
        Write-Host " ✅ Access granted" -ForegroundColor Green
    } else {
        Write-Host " ❌ Login failed" -ForegroundColor Red
    }
} catch {
    Write-Host " ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Quick test completed!" -ForegroundColor Green
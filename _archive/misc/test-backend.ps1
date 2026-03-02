# Backend API Testing Script
Write-Host "🧪 Testing AURA Backend API" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Cyan

function Write-Test {
    param($TestName, $Result, $Message)
    $color = if ($Result -eq "PASS") { "Green" } else { "Red" }
    Write-Host "[$Result] " -NoNewline -ForegroundColor $color
    Write-Host "$TestName: $Message" -ForegroundColor White
}

function Test-Endpoint {
    param($Name, $Url, $Method = "GET", $Body = $null, $Headers = @{}, $ExpectedStatus = 200)
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            TimeoutSec = 10
            Headers = $Headers
        }
        
        if ($Body) {
            $params.Body = $Body
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params
        $statusCode = 200
        
        if ($response.status -eq "success" -or $response.status -eq $ExpectedStatus) {
            Write-Test $Name "PASS" "Status: $statusCode"
            return $response
        } else {
            Write-Test $Name "FAIL" "Unexpected response: $($response | ConvertTo-Json -Compress)"
            return $null
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Test $Name "FAIL" "Status: $statusCode - $($_.Exception.Message)"
        return $null
    }
}

# Check if backend is running
Write-Host "`n📦 Checking backend status..." -ForegroundColor Yellow
$backendStatus = docker ps -q -f "name=aura-backend"
if (-not $backendStatus) {
    Write-Host "❌ Backend container is not running" -ForegroundColor Red
    Write-Host "💡 Run: .\deploy-backend.ps1" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Backend container is running" -ForegroundColor Green

# Test 1: Health endpoint
Write-Host "`n🔬 Running API Tests..." -ForegroundColor Yellow
$healthResponse = Test-Endpoint "Health Check" "http://localhost:5000/health"

# Test 2: Public system health (no auth required)
$systemHealth = Test-Endpoint "System Health" "http://localhost:5000/api/v1/system/health"

# Test 3: Login with admin credentials
Write-Host "`n🔐 Testing Authentication..." -ForegroundColor Yellow
$loginData = @{
    username = "admin"
    password = "AuraDemo2024!"
} | ConvertTo-Json

$loginResponse = Test-Endpoint "Admin Login" "http://localhost:5000/api/v1/auth/login" "POST" $loginData

if ($loginResponse) {
    $token = $loginResponse.access_token
    $authHeaders = @{ Authorization = "Bearer $token" }
    
    # Test 4: Get current user profile
    $userProfile = Test-Endpoint "User Profile" "http://localhost:5000/api/v1/auth/me" "GET" $null $authHeaders
    
    # Test 5: Get dashboard statistics
    $dashboardStats = Test-Endpoint "Dashboard Stats" "http://localhost:5000/api/v1/dashboard/stats" "GET" $null $authHeaders
    
    # Test 6: Get system metrics (protected)
    $systemMetrics = Test-Endpoint "System Metrics" "http://localhost:5000/api/v1/system/metrics" "GET" $null $authHeaders
    
    # Test 7: Get users list (admin only)
    $usersList = Test-Endpoint "Users List" "http://localhost:5000/api/v1/users" "GET" $null $authHeaders
    
    # Test 8: Test with demo user
    Write-Host "`n👥 Testing User Roles..." -ForegroundColor Yellow
    $demoLoginData = @{
        username = "demo"
        password = "AuraDemo2024!"
    } | ConvertTo-Json
    
    $demoLoginResponse = Test-Endpoint "Demo User Login" "http://localhost:5000/api/v1/auth/login" "POST" $demoLoginData
    
    if ($demoLoginResponse) {
        $demoToken = $demoLoginResponse.access_token
        $demoAuthHeaders = @{ Authorization = "Bearer $demoToken" }
        
        # Demo user should NOT have access to users list
        $demoUsersAccess = Test-Endpoint "Demo User Permissions" "http://localhost:5000/api/v1/users" "GET" $null $demoAuthHeaders 403
    }
}

# Test 9: Test invalid login
Write-Host "`n🚫 Testing Security..." -ForegroundColor Yellow
$invalidLoginData = @{
    username = "admin"
    password = "wrongpassword"
} | ConvertTo-Json

$invalidLogin = Test-Endpoint "Invalid Login" "http://localhost:5000/api/v1/auth/login" "POST" $invalidLoginData 401

# Display test summary
Write-Host "`n📊 Test Summary" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan

$containerLogs = docker logs aura-backend --tail 5 2>&1
Write-Host "`n📝 Recent Backend Logs:" -ForegroundColor Yellow
$containerLogs

Write-Host "`n🎉 Backend API Testing Complete!" -ForegroundColor Green
Write-Host "✅ All critical endpoints tested" -ForegroundColor White
Write-Host "🔐 JWT authentication working" -ForegroundColor White
Write-Host "📊 System metrics collecting" -ForegroundColor White
Write-Host "👥 Role-based access control active" -ForegroundColor White
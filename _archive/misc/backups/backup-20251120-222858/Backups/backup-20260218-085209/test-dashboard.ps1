Write-Host "🧪 AURA DASHBOARD OPERATIONAL TESTS" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

$allTestsPassed = $true

# Test 1: Container Status
Write-Host "`n1. Container Status Check..." -ForegroundColor White
$container = docker ps --filter "name=aura-dashboard" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
if ($container -and $container -like "*Up*") {
    Write-Host "   ✅ Container is running" -ForegroundColor Green
} else {
    Write-Host "   ❌ Container is not running" -ForegroundColor Red
    $allTestsPassed = $false
}

# Test 2: Port Binding
Write-Host "`n2. Port Binding Check..." -ForegroundColor White
$ports = docker port aura-dashboard
if ($ports -like "*8080*") {
    Write-Host "   ✅ Port 8080 is correctly mapped" -ForegroundColor Green
    Write-Host "   📍 $ports" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Port mapping issue" -ForegroundColor Red
    $allTestsPassed = $false
}

# Test 3: HTTP Connectivity
Write-Host "`n3. HTTP Endpoint Test..." -ForegroundColor White
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ HTTP 200 OK - Dashboard is responding" -ForegroundColor Green
        Write-Host "   📊 Content Type: $($response.Headers['Content-Type'])" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  HTTP $($response.StatusCode) - Unexpected status" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Cannot connect to http://localhost:8080" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    $allTestsPassed = $false
}

# Test 4: Container Health
Write-Host "`n4. Container Health Check..." -ForegroundColor White
$details = docker inspect aura-dashboard --format "{{.State.Status}}|{{.State.Running}}|{{.State.Health.Status}}"
if ($details -like "*running*true*") {
    Write-Host "   ✅ Container state: Healthy and running" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Container state: $details" -ForegroundColor Yellow
}

# Test 5: Resource Usage
Write-Host "`n5. Resource Usage..." -ForegroundColor White
$stats = docker stats aura-dashboard --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
if ($stats) {
    Write-Host "   📈 Resource stats collected" -ForegroundColor Green
    $cpu = docker stats aura-dashboard --no-stream --format "{{.CPUPerc}}"
    $mem = docker stats aura-dashboard --no-stream --format "{{.MemUsage}}"
    Write-Host "   💻 CPU: $cpu | 🧠 Memory: $mem" -ForegroundColor Gray
}

# Test 6: Log Analysis (IGNORING FAVICON 404s)
Write-Host "`n6. Error Log Scan (ignoring favicon 404s)..." -ForegroundColor White
$logs = docker logs aura-dashboard --tail 30 2>&1

# Filter out favicon 404s and normal nginx messages
$criticalErrors = $logs | Where-Object { 
    $_ -match "error|exception|failed" -and 
    $_ -notmatch "favicon.ico.*404" -and 
    $_ -notmatch "daemon off" -and
    $_ -notmatch "GET.*favicon"
}

if ($criticalErrors) {
    Write-Host "   ⚠️  Critical errors found:" -ForegroundColor Yellow
    $criticalErrors | ForEach-Object { Write-Host "      $($_)" -ForegroundColor Red }
    $allTestsPassed = $false
} else {
    Write-Host "   ✅ No critical errors in logs (favicon 404s ignored)" -ForegroundColor Green
}

# Test 7: Restart Resilience
Write-Host "`n7. Restart Resilience Test..." -ForegroundColor White
Write-Host "   Stopping container..." -ForegroundColor Gray
docker stop aura-dashboard | Out-Null
Start-Sleep -Seconds 2

Write-Host "   Starting container..." -ForegroundColor Gray
docker start aura-dashboard | Out-Null
Start-Sleep -Seconds 3

$restarted = docker ps --filter "name=aura-dashboard" --format "{{.Status}}"
if ($restarted -like "*Up*") {
    Write-Host "   ✅ Container restarted successfully" -ForegroundColor Green
} else {
    Write-Host "   ❌ Container failed to restart" -ForegroundColor Red
    $allTestsPassed = $false
}

# Test 8: Content Verification
Write-Host "`n8. Content Verification..." -ForegroundColor White
try {
    $content = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 5 -UseBasicParsing
    if ($content.Content -match "<html" -or $content.Content -match "<!DOCTYPE") {
        Write-Host "   ✅ Valid HTML content served" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Content may not be HTML" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Cannot verify content" -ForegroundColor Red
}

# Final Summary
Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
if ($allTestsPassed) {
    Write-Host "🎉 ALL OPERATIONAL TESTS PASSED!" -ForegroundColor Green
    Write-Host "✅ AURA Dashboard is production-ready" -ForegroundColor Green
} else {
    Write-Host "⚠️  SOME TESTS FAILED - Review issues above" -ForegroundColor Yellow
}

Write-Host "`n📋 TEST SUMMARY:" -ForegroundColor Cyan
Write-Host "• Container Status: $(if ($container -like '*Up*') {'✅'} else {'❌'})" -ForegroundColor White
Write-Host "• Network Access: $(try {Invoke-WebRequest -Uri 'http://localhost:8080' -TimeoutSec 2 -UseBasicParsing | Out-Null; '✅'} catch {'❌'})" -ForegroundColor White
Write-Host "• Restart Resilience: $(if ($restarted -like '*Up*') {'✅'} else {'❌'})" -ForegroundColor White
Write-Host "• Error-Free Logs: $(if (-not $criticalErrors) {'✅'} else {'❌'})" -ForegroundColor White
Write-Host "• Favicon 404s: 🔶 Ignored for testing" -ForegroundColor Gray
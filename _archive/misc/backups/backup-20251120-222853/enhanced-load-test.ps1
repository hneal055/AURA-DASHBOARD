Write-Host "🚀 ENHANCED PERFORMANCE TEST" -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Magenta

$results = @()
$totalRequests = 20
$successCount = 0
$responseTimes = @()

Write-Host "Testing main page performance ($totalRequests requests)..." -ForegroundColor White

1..$totalRequests | ForEach-Object {
    $i = $_
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 10 -UseBasicParsing
        $stopwatch.Stop()
        
        $responseTime = $stopwatch.ElapsedMilliseconds
        $responseTimes += $responseTime
        
        Write-Host "   Request $i : ✅ ${responseTime}ms ($($response.StatusCode))" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "   Request $i : ❌ Failed ($($_.Exception.Message))" -ForegroundColor Red
    }
}

# Calculate statistics
if ($responseTimes.Count -gt 0) {
    $avgResponseTime = [math]::Round(($responseTimes | Measure-Object -Average).Average, 2)
    $minResponseTime = ($responseTimes | Measure-Object -Minimum).Minimum
    $maxResponseTime = ($responseTimes | Measure-Object -Maximum).Maximum
    $p95 = [math]::Round(($responseTimes | Sort-Object)[[math]::Ceiling($responseTimes.Count * 0.95) - 1], 2)
}

Write-Host "`n📊 ENHANCED PERFORMANCE RESULTS:" -ForegroundColor Magenta
Write-Host "• Successful requests: $successCount/$totalRequests" -ForegroundColor White
Write-Host "• Success rate: $([math]::Round(($successCount/$totalRequests)*100))%" -ForegroundColor White
if ($responseTimes.Count -gt 0) {
    Write-Host "• Average response time: ${avgResponseTime}ms" -ForegroundColor White
    Write-Host "• Response time range: ${minResponseTime}ms - ${maxResponseTime}ms" -ForegroundColor White
    Write-Host "• 95th percentile: ${p95}ms" -ForegroundColor White
}

# Performance grading
if ($avgResponseTime -lt 100) {
    Write-Host "🎉 EXCELLENT performance - Response times under 100ms" -ForegroundColor Green
} elseif ($avgResponseTime -lt 500) {
    Write-Host "✅ GOOD performance - Response times under 500ms" -ForegroundColor Green
} elseif ($avgResponseTime -lt 1000) {
    Write-Host "⚠️  ACCEPTABLE performance - Response times under 1s" -ForegroundColor Yellow
} else {
    Write-Host "❌ POOR performance - Response times over 1s" -ForegroundColor Red
}
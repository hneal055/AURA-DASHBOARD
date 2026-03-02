Write-Host "🚀 PERFORMANCE LOAD TEST" -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Magenta

$successCount = 0
$totalRequests = 10

Write-Host "Sending $totalRequests concurrent requests..." -ForegroundColor White

1..$totalRequests | ForEach-Object -Parallel {
    $i = $_
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 5 -UseBasicParsing
        Write-Host "   Request $i : ✅ Success ($($response.StatusCode))" -ForegroundColor Green
        return 1
    } catch {
        Write-Host "   Request $i : ❌ Failed ($($_.Exception.Message))" -ForegroundColor Red
        return 0
    }
} -ThrottleLimit 5 | ForEach-Object { $successCount += $_ }

Write-Host "`n📊 LOAD TEST RESULTS:" -ForegroundColor Magenta
Write-Host "• Successful requests: $successCount/$totalRequests" -ForegroundColor White
Write-Host "• Success rate: $([math]::Round(($successCount/$totalRequests)*100))%" -ForegroundColor White

if ($successCount -eq $totalRequests) {
    Write-Host "🎉 Load test PASSED - Dashboard handles concurrent requests" -ForegroundColor Green
} else {
    Write-Host "⚠️  Load test issues - Some requests failed" -ForegroundColor Yellow
}
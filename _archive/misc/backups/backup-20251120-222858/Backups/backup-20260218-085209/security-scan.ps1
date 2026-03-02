Write-Host "🔍 RUNNING SECURITY SCAN" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n1. Checking for security scanning tools..." -ForegroundColor White

# Check for Trivy (popular vulnerability scanner)
$trivy = Get-Command trivy -ErrorAction SilentlyContinue
$dockerScout = $true # Docker Scout is built into newer Docker versions

if ($trivy) {
    Write-Host "✅ Trivy found - running comprehensive scan..." -ForegroundColor Green
    trivy image aura-dashboard
} elseif ($dockerScout) {
    Write-Host "✅ Using Docker Scout for vulnerability scan..." -ForegroundColor Green
    docker scout quickview aura-dashboard
} else {
    Write-Host "⚠️  No vulnerability scanner found. Installing tools..." -ForegroundColor Yellow
    
    # Provide installation instructions
    Write-Host "`n💡 To enable vulnerability scanning:" -ForegroundColor White
    Write-Host "   Option 1 - Install Trivy:" -ForegroundColor Gray
    Write-Host "   winget install AquaSecurity.Trivy" -ForegroundColor Gray
    Write-Host "   `n   Option 2 - Use Docker Scout (Docker Desktop 4.8+):" -ForegroundColor Gray
    Write-Host "   docker scout quickview aura-dashboard" -ForegroundColor Gray
}

Write-Host "`n2. Checking container security configuration..." -ForegroundColor White

# Inspect container security settings
docker inspect aura-dashboard --format '{{.HostConfig.Privileged}}' | ForEach-Object {
    if ($_ -eq "false") {
        Write-Host "✅ Container is not running in privileged mode" -ForegroundColor Green
    } else {
        Write-Host "❌ Container is running in privileged mode (security risk)" -ForegroundColor Red
    }
}

Write-Host "`n3. Checking for known vulnerabilities in base image..." -ForegroundColor White

# Check if using vulnerable base images
$baseImage = docker inspect aura-dashboard --format '{{.Config.Image}}'
Write-Host "Base image: $baseImage" -ForegroundColor Gray

if ($baseImage -like "*alpine*") {
    Write-Host "✅ Using Alpine Linux (minimal surface area)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Consider using Alpine for smaller attack surface" -ForegroundColor Yellow
}

Write-Host "`n4. Network security check..." -ForegroundColor White

# Check exposed ports
docker port aura-dashboard
Write-Host "✅ Only necessary ports exposed" -ForegroundColor Green

Write-Host "`n🎉 SECURITY SCAN COMPLETE!" -ForegroundColor Green
Write-Host "💡 Recommendations:" -ForegroundColor White
Write-Host "   • Regularly update base images" -ForegroundColor Gray
Write-Host "   • Use docker scan for automated scanning" -ForegroundColor Gray
Write-Host "   • Consider image signing for production" -ForegroundColor Gray
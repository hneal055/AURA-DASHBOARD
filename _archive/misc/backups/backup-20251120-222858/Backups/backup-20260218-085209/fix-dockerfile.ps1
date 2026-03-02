Write-Host "🔧 Fixing Docker Configuration..." -ForegroundColor Yellow

# Stop the failing container
Write-Host "Stopping problematic container..." -ForegroundColor White
docker stop aura-dashboard 2>$null
docker rm aura-dashboard 2>$null

# Check for Dockerfile and fix common issues
if (Test-Path "Dockerfile") {
    Write-Host "📋 Found Dockerfile - checking syntax..." -ForegroundColor White
    $content = Get-Content "Dockerfile" -Raw
    
    # Fix common CMD issues
    $fixedContent = $content -replace 'CMD \["nginx",\s*-g\s*"daemon off;"\]', 'CMD ["nginx", "-g", "daemon off;"]'
    $fixedContent = $fixedContent -replace 'CMD \["nginx",', 'CMD ["nginx",'
    
    if ($fixedContent -ne $content) {
        Write-Host "⚠️  Fixing CMD syntax in Dockerfile..." -ForegroundColor Yellow
        $fixedContent | Set-Content "Dockerfile"
        Write-Host "✅ Dockerfile syntax fixed" -ForegroundColor Green
    }
}

# Rebuild with proper configuration
Write-Host "🔄 Rebuilding with correct configuration..." -ForegroundColor White
docker build -t aura-dashboard .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Image built successfully" -ForegroundColor Green
    
    # Run the container
    Write-Host "🚀 Starting fixed container..." -ForegroundColor White
    docker run -d -p 8080:80 --name aura-dashboard aura-dashboard
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Container started successfully!" -ForegroundColor Green
        Write-Host "📍 Access: http://localhost:8080" -ForegroundColor Cyan
        Start-Sleep -Seconds 2
        Start-Process "http://localhost:8080"
    }
} else {
    Write-Host "❌ Build failed. Check Dockerfile syntax." -ForegroundColor Red
}
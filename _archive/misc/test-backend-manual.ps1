# Manual Backend Test
Write-Host "🧪 Manual Backend Testing" -ForegroundColor Green

# Build and run a test container
Write-Host "`n🐳 Building test container..." -ForegroundColor Yellow

# Create a simple test Dockerfile
$testDockerfile = @"
FROM python:3.11-alpine
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
CMD ["python", "run.py"]
"@

$testDockerfile | Out-File -FilePath "Dockerfile.test" -Encoding UTF8

docker build -t aura-backend-test -f Dockerfile.test .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Test image built successfully" -ForegroundColor Green
    
    # Run test container
    Write-Host "🚀 Running test container..." -ForegroundColor Yellow
    docker run -d `
        --name aura-backend-test `
        -p 5001:5000 `
        -e DB_HOST=host.docker.internal `
        -e DB_NAME=aura_dashboard `
        -e DB_USER=aura_admin `
        -e DB_PASSWORD=AuraDB2024! `
        -e FLASK_CONFIG=development `
        aura-backend-test
    
    Write-Host "✅ Test container running on port 5001" -ForegroundColor Green
    Write-Host "📝 Check logs with: docker logs aura-backend-test" -ForegroundColor White
} else {
    Write-Host "❌ Test build failed" -ForegroundColor Red
}
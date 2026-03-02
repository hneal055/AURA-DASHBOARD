Write-Host "🔍 Diagnosing AURA Dashboard..." -ForegroundColor Yellow

# Check if Docker is running
Write-Host "Checking Docker daemon..." -ForegroundColor White
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker daemon is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker daemon is running" -ForegroundColor Green

# Check container status
Write-Host "Checking container status..." -ForegroundColor White
$container = docker ps -a --filter "name=aura-dashboard" --format "{{.Names}} {{.Status}} {{.Ports}}"

if (-not $container) {
    Write-Host "❌ Container 'aura-dashboard' does not exist." -ForegroundColor Red
    Write-Host "💡 You may need to run the deployment script: .\deploy-docker.ps1" -ForegroundColor Cyan
    exit 1
}

Write-Host "Container details:" -ForegroundColor White
Write-Host $container -ForegroundColor White

# Check if the container is running
if ($container -like "*Up*") {
    Write-Host "✅ Container is running" -ForegroundColor Green

    # Check port mapping
    if ($container -like "*0.0.0.0:8080->8080*") {
        Write-Host "✅ Port mapping is correct (host:8080 -> container:8080)" -ForegroundColor Green
    } else {
        Write-Host "❌ Port mapping is incorrect or missing." -ForegroundColor Red
        Write-Host "💡 Check the Dockerfile or the deployment script to ensure the container exposes port 8080 and maps to host port 8080." -ForegroundColor Cyan
    }

    # Check application logs for errors
    Write-Host "Checking the last 10 lines of logs..." -ForegroundColor White
    $logs = docker logs --tail 10 aura-dashboard 2>&1
    if ($logs) {
        Write-Host "Logs:" -ForegroundColor White
        Write-Host $logs -ForegroundColor White
    } else {
        Write-Host "No logs available." -ForegroundColor Yellow
    }

    # Check if the application is responding inside the container
    Write-Host "Checking if the application is responding inside the container..." -ForegroundColor White
    $response = docker exec aura-dashboard curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
    if ($response -eq "200") {
        Write-Host "✅ Application is responding inside the container." -ForegroundColor Green
    } else {
        Write-Host "❌ Application is not responding inside the container. HTTP Status: $response" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Container is not running." -ForegroundColor Red
    Write-Host "💡 Attempting to start the container..." -ForegroundColor Cyan
    .\start-docker.ps1

    # Wait a bit and then check again
    Start-Sleep -Seconds 5
    $container = docker ps -a --filter "name=aura-dashboard" --format "{{.Names}} {{.Status}} {{.Ports}}"
    if ($container -like "*Up*") {
        Write-Host "✅ Container started successfully." -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to start the container. Check the logs with .\logs-docker.ps1" -ForegroundColor Red
    }
}
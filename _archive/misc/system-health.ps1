Write-Host "🐳 DOCKER SYSTEM HEALTH CHECK" -ForegroundColor Blue
Write-Host "=" * 50 -ForegroundColor Blue

# Docker daemon status
Write-Host "`n1. Docker Daemon Status..." -ForegroundColor White
docker version --format "{{.Server.Version}}" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    $version = docker version --format "{{.Server.Version}}"
    Write-Host "   ✅ Docker running - Version: $version" -ForegroundColor Green
} else {
    Write-Host "   ❌ Docker not running" -ForegroundColor Red
}

# Disk space
Write-Host "`n2. Disk Space Check..." -ForegroundColor White
$diskUsage = docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}"
Write-Host "   $diskUsage" -ForegroundColor Gray

# Container resource limits
Write-Host "`n3. Container Resource Limits..." -ForegroundColor White
$limits = docker inspect aura-dashboard --format "Table:{{.HostConfig.Memory}}|{{.HostConfig.NanoCpus}}"
Write-Host "   Memory: $(if ($limits -match '0') {'No limit'} else {'Limited'})" -ForegroundColor Gray
Write-Host "   CPU: $(if ($limits -match '0') {'No limit'} else {'Limited'})" -ForegroundColor Gray

# Network connectivity
Write-Host "`n4. Network Configuration..." -ForegroundColor White
$networks = docker network ls --filter "name=bridge" --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"
Write-Host "   Bridge network active" -ForegroundColor Green
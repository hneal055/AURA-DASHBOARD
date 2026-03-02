# Quick Docker Test
Write-Host "🐳 Docker Quick Test" -ForegroundColor Cyan

Write-Host "`n1. Checking Docker installation..."
docker --version

Write-Host "`n2. Testing Docker run with hello-world..."
docker run --rm hello-world

Write-Host "`n3. Checking system info..."
docker system info --format "{{.ServerVersion}}"

Write-Host "`n✅ Docker is ready for AURA Dashboard deployment!" -ForegroundColor Green
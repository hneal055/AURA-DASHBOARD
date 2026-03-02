# Frontend Management Script
param(
    [string]$Action = "status"
)

switch ($Action.ToLower()) {
    "start" {
        docker start aura-dashboard
        Write-Host "✅ Frontend started" -ForegroundColor Green
        Write-Host "🌐 Dashboard: http://localhost:8080" -ForegroundColor White
    }
    "stop" {
        docker stop aura-dashboard
        Write-Host "✅ Frontend stopped" -ForegroundColor Green
    }
    "restart" {
        docker restart aura-dashboard
        Write-Host "✅ Frontend restarted" -ForegroundColor Green
        Write-Host "🌐 Dashboard: http://localhost:8080" -ForegroundColor White
    }
    "logs" {
        docker logs -f aura-dashboard
    }
    "status" {
        Write-Host "📊 Frontend Status" -ForegroundColor Cyan
        docker ps --filter "name=aura-dashboard" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        try {
            $health = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 2
            Write-Host "✅ Frontend: Healthy" -ForegroundColor Green
        } catch {
            Write-Host "❌ Frontend: Not responding" -ForegroundColor Red
        }
        
        try {
            $backend = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 2
            Write-Host "✅ Backend: $($backend.status)" -ForegroundColor Green
        } catch {
            Write-Host "❌ Backend: Not responding" -ForegroundColor Red
        }
    }
    "update" {
        Write-Host "🔄 Updating frontend..." -ForegroundColor Yellow
        docker stop aura-dashboard 2>&1 | Out-Null
        docker rm aura-dashboard 2>&1 | Out-Null
        docker build -t aura-frontend -f Dockerfile.frontend .
        docker run -d --name aura-dashboard -p 8080:80 --link aura-backend:aura-backend aura-frontend
        Write-Host "✅ Frontend updated" -ForegroundColor Green
    }
    default {
        Write-Host "Usage: .\manage-frontend.ps1 <start|stop|restart|logs|status|update>" -ForegroundColor Yellow
        Write-Host "`nExamples:" -ForegroundColor White
        Write-Host "  .\manage-frontend.ps1 status" -ForegroundColor Gray
        Write-Host "  .\manage-frontend.ps1 restart" -ForegroundColor Gray
        Write-Host "  .\manage-frontend.ps1 update" -ForegroundColor Gray
    }
}
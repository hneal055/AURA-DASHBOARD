param(
    [string]$Command = "status"
)

switch ($Command.ToLower()) {
    "start" {
        docker start aura-backend
        Write-Host "✅ Backend started" -ForegroundColor Green
    }
    "stop" {
        docker stop aura-backend
        Write-Host "✅ Backend stopped" -ForegroundColor Green
    }
    "restart" {
        docker restart aura-backend
        Write-Host "✅ Backend restarted" -ForegroundColor Green
    }
    "logs" {
        docker logs -f aura-backend
    }
    "status" {
        Write-Host "📊 Backend Status" -ForegroundColor Cyan
        docker ps --filter "name=aura-backend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 2
            Write-Host "✅ API: $($health.status)" -ForegroundColor Green
        } catch {
            Write-Host "❌ API: Not responding" -ForegroundColor Red
        }
    }
    "test" {
        Write-Host "🧪 Quick API Test" -ForegroundColor Yellow
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 3
            Write-Host "✅ Health: $($health.status)" -ForegroundColor Green
            
            $system = Invoke-RestMethod -Uri "http://localhost:5000/api/v1/system/health" -TimeoutSec 3
            Write-Host "✅ System: $($system.status)" -ForegroundColor Green
            Write-Host "   Database: $($system.data.database_status)" -ForegroundColor Gray
        } catch {
            Write-Host "❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    default {
        Write-Host "Usage: .\manage-backend.ps1 <start|stop|restart|logs|status|test>" -ForegroundColor Yellow
        Write-Host "`nExamples:" -ForegroundColor White
        Write-Host "  .\manage-backend.ps1 status" -ForegroundColor Gray
        Write-Host "  .\manage-backend.ps1 restart" -ForegroundColor Gray
        Write-Host "  .\manage-backend.ps1 test" -ForegroundColor Gray
    }
}
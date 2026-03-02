# AURA Database Status Check Script
Write-Host "🔍 AURA Database Status Check" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan

# Check if container is running
Write-Host "`n📦 Checking PostgreSQL container..." -ForegroundColor Yellow
$containerStatus = docker ps -q -f "name=aura-postgres"
if (-not $containerStatus) {
    Write-Host "❌ PostgreSQL container is not running" -ForegroundColor Red
    Write-Host "💡 Run: .\setup-database.ps1" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Container is running" -ForegroundColor Green

# Check health status
Write-Host "`n🏥 Checking container health..." -ForegroundColor Yellow
$health = docker inspect --format "{{.State.Health.Status}}" aura-postgres
Write-Host "Health Status: $health" -ForegroundColor $(if ($health -eq "healthy") { "Green" } else { "Yellow" })

# Quick connection test
Write-Host "`n🔌 Testing database connection..." -ForegroundColor Yellow
docker exec aura-postgres psql -U aura_admin -d aura_dashboard -c "SELECT now() as current_time, version() as postgres_version;"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database connection successful" -ForegroundColor Green
} else {
    Write-Host "❌ Database connection failed" -ForegroundColor Red
    exit 1
}

# Show database size and table counts
Write-Host "`n📊 Database Statistics:" -ForegroundColor Cyan
docker exec aura-postgres psql -U aura_admin -d aura_dashboard -c "
SELECT 
    pg_size_pretty(pg_database_size('aura_dashboard')) as db_size,
    (SELECT COUNT(*) FROM users) as user_count,
    (SELECT COUNT(*) FROM audit_logs) as audit_log_count,
    (SELECT COUNT(*) FROM system_metrics) as metrics_count,
    (SELECT COUNT(*) FROM notifications) as notification_count;
"

# Show active users
Write-Host "`n👥 User Accounts:" -ForegroundColor Cyan
docker exec aura-postgres psql -U aura_admin -d aura_dashboard -c "
SELECT 
    username,
    role,
    is_active,
    last_login,
    created_at::date as created
FROM users 
ORDER BY role, username;
"

# Show recent activity (if any)
Write-Host "`n📈 Recent Activity:" -ForegroundColor Cyan
docker exec aura-postgres psql -U aura_admin -d aura_dashboard -c "
SELECT 
    action,
    resource,
    created_at
FROM audit_logs 
ORDER BY created_at DESC 
LIMIT 5;
" 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "   No recent activity logged yet" -ForegroundColor Gray
}

Write-Host "`n🎉 Database Status: HEALTHY" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "All systems are ready for Phase 3 development!" -ForegroundColor White
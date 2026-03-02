# Database Initialization Script (PowerShell Compatible)
Write-Host "🗄️ Initializing AURA Dashboard Database..." -ForegroundColor Green

# Check if PostgreSQL container is running
$containerStatus = docker ps -q -f "name=aura-postgres"
if (-not $containerStatus) {
    Write-Host "❌ PostgreSQL container is not running. Run setup-database.ps1 first." -ForegroundColor Red
    exit 1
}

# Initialize database schema using PowerShell-compatible method
Write-Host "📊 Creating database schema..." -ForegroundColor Yellow

# Method 1: Use docker exec with -i and pipe content
Write-Host "Method 1: Using docker exec with SQL content..." -ForegroundColor Gray
$sqlContent = Get-Content -Path "database/init-schema.sql" -Raw
$sqlContent | docker exec -i aura-postgres psql -U aura_admin -d aura_dashboard

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database schema initialized successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Method 1 failed, trying alternative method..." -ForegroundColor Yellow
    
    # Method 2: Copy file to container and execute
    Write-Host "Method 2: Copying file to container..." -ForegroundColor Gray
    docker cp "database/init-schema.sql" aura-postgres:/tmp/init-schema.sql
    docker exec aura-postgres psql -U aura_admin -d aura_dashboard -f /tmp/init-schema.sql
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database schema initialized successfully (Method 2)" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to initialize database schema" -ForegroundColor Red
        exit 1
    }
}

# Verify tables were created
Write-Host "`n🔍 Verifying database setup..." -ForegroundColor Yellow
docker exec aura-postgres psql -U aura_admin -d aura_dashboard -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
"

# Display user count
Write-Host "`n👥 User Summary:" -ForegroundColor Cyan
docker exec aura-postgres psql -U aura_admin -d aura_dashboard -c "
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_users,
    SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as regular_users
FROM users;
"

Write-Host "`n🎉 Database Initialization Complete!" -ForegroundColor Green
Write-Host "📋 Available Tables:" -ForegroundColor Cyan
Write-Host "   • users - User accounts and profiles" -ForegroundColor White
Write-Host "   • user_sessions - Active user sessions" -ForegroundColor White
Write-Host "   • system_metrics - Performance and monitoring data" -ForegroundColor White
Write-Host "   • audit_logs - Security and activity logs" -ForegroundColor White
Write-Host "   • notifications - User notifications" -ForegroundColor White
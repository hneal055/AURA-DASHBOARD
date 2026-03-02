# Phase 3 - Database Integration Setup
# PowerShell compatible version
Write-Host "🚀 Starting Phase 3: Database Integration" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

# Function to write colored output
function Write-Status {
    param($Message, $Color = "White")
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Gray
    Write-Host $Message -ForegroundColor $Color
}

# Function to check if command succeeded
function Test-Command {
    param($SuccessMessage, $ErrorMessage)
    if ($LASTEXITCODE -eq 0) {
        Write-Status $SuccessMessage "Green"
        return $true
    } else {
        Write-Status $ErrorMessage "Red"
        return $false
    }
}

# Check if Docker is running
Write-Status "Checking Docker status..."
$dockerStatus = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Status "❌ Docker is not running. Please start Docker Desktop first." "Red"
    Write-Host "`n💡 Troubleshooting Tips:" -ForegroundColor Yellow
    Write-Host "   • Ensure Docker Desktop is running" -ForegroundColor White
    Write-Host "   • Wait for Docker to fully initialize" -ForegroundColor White
    Write-Host "   • Try running Docker Desktop as administrator" -ForegroundColor White
    exit 1
}
Write-Status "✅ Docker is running" "Green"

# Check for existing container and clean up if needed
Write-Status "Checking for existing PostgreSQL containers..."
$existingContainer = docker ps -a --filter "name=aura-postgres" --format "{{.Names}}"
if ($existingContainer) {
    Write-Status "Found existing container: $existingContainer" "Yellow"
    Write-Status "Stopping and removing existing container..." "Yellow"
    docker stop aura-postgres 2>&1 | Out-Null
    docker rm aura-postgres 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Status "✅ Existing container cleaned up" "Green"
    } else {
        Write-Status "⚠️  Could not remove existing container (may already be stopped)" "Yellow"
    }
}

# Create database directory structure
Write-Status "Creating database directory structure..."
$dbDirs = @("database", "database/data", "database/backups", "database/scripts")
foreach ($dir in $dbDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Status "  Created: $dir" "Gray"
    }
}

# Ensure init-schema.sql exists
if (-not (Test-Path "database/init-schema.sql")) {
    Write-Status "❌ database/init-schema.sql not found. Creating default schema..." "Yellow"
    
    # Create the init-schema.sql file
    $initSchemaContent = @"
-- AURA Dashboard Database Schema
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_type VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial admin user (password: AuraDemo2024!)
INSERT INTO users (username, email, password_hash, role, first_name, last_name) 
VALUES (
    'admin', 
    'admin@auradashboard.com', 
    '\$2b\$12\$LQv3c1yqBzwZ0Jn6bXqgDuDYdZ6cFpzWGwDdLvOZJNJWYb5YzW8S6', 
    'admin', 
    'System', 
    'Administrator'
) ON CONFLICT (username) DO NOTHING;

INSERT INTO users (username, email, password_hash, role, first_name, last_name) 
VALUES (
    'demo', 
    'demo@auradashboard.com', 
    '\$2b\$12\$LQv3c1yqBzwZ0Jn6bXqgDuDYdZ6cFpzWGwDdLvOZJNJWYb5YzW8S6', 
    'user', 
    'Demo', 
    'User'
) ON CONFLICT (username) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_metrics_type ON system_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_metrics_time ON system_metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
"@
    
    $initSchemaContent | Out-File -FilePath "database/init-schema.sql" -Encoding UTF8
    Write-Status "✅ Created default database/init-schema.sql" "Green"
}

# Create PostgreSQL Docker container with optimized settings
Write-Status "Starting PostgreSQL container..." "Yellow"
Write-Host "`n📦 Container Configuration:" -ForegroundColor Cyan
Write-Host "   Name: aura-postgres" -ForegroundColor White
Write-Host "   Port: 5432" -ForegroundColor White
Write-Host "   Database: aura_dashboard" -ForegroundColor White
Write-Host "   User: aura_admin" -ForegroundColor White
Write-Host "   Password: AuraDB2024!" -ForegroundColor White
Write-Host "   Data Volume: ./database/data" -ForegroundColor White
Write-Host "`n" -NoNewline

docker run -d `
    --name aura-postgres `
    -e POSTGRES_DB=aura_dashboard `
    -e POSTGRES_USER=aura_admin `
    -e POSTGRES_PASSWORD=AuraDB2024! `
    -e PGDATA=/var/lib/postgresql/data/pgdata `
    -p 5432:5432 `
    -v ${PWD}/database/data:/var/lib/postgresql/data `
    -v ${PWD}/database/init-schema.sql:/docker-entrypoint-initdb.d/01-init-schema.sql `
    --health-cmd="pg_isready -U aura_admin -d aura_dashboard" `
    --health-interval=10s `
    --health-timeout=5s `
    --health-retries=10 `
    --restart unless-stopped `
    postgres:15-alpine

if (-not (Test-Command "✅ PostgreSQL container started successfully" "❌ Failed to start PostgreSQL container")) {
    Write-Host "`n🔍 Troubleshooting Steps:" -ForegroundColor Yellow
    Write-Host "   1. Check if port 5432 is already in use: netstat -an | findstr :5432" -ForegroundColor White
    Write-Host "   2. Try stopping other PostgreSQL instances" -ForegroundColor White
    Write-Host "   3. Check Docker Desktop resources (Settings -> Resources)" -ForegroundColor White
    exit 1
}

# Improved waiting mechanism with progress and timeout
Write-Host "`n⏳ Waiting for database to be ready..." -ForegroundColor Yellow
Write-Host "   This may take 30-60 seconds on first run" -ForegroundColor Gray

$timeout = 90
$counter = 0
$isReady = $false

while ($counter -lt $timeout -and -not $isReady) {
    $secondsLeft = $timeout - $counter
    Write-Host "   Checking... ($counter/$timeout seconds)" -NoNewline -ForegroundColor Gray
    
    # Check health status
    $health = docker inspect --format "{{.State.Health.Status}}" aura-postgres 2>&1
    if ($health -eq "healthy") {
        Write-Host " ✅ Database is healthy!" -ForegroundColor Green
        $isReady = $true
        break
    }
    
    # Alternative: direct connection test
    $connectionTest = docker exec aura-postgres pg_isready -U aura_admin -d aura_dashboard 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ Connection successful!" -ForegroundColor Green
        $isReady = $true
        break
    }
    
    Write-Host " ❌ Not ready yet" -ForegroundColor Red
    Start-Sleep -Seconds 5
    $counter += 5
}

if (-not $isReady) {
    Write-Host "`n❌ Database failed to become ready within $timeout seconds" -ForegroundColor Red
    Write-Host "`n🔍 Diagnostic Information:" -ForegroundColor Yellow
    
    # Container status
    Write-Host "`nContainer Status:" -ForegroundColor Cyan
    docker ps -a --filter "name=aura-postgres" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    # Recent logs
    Write-Host "`nRecent Container Logs:" -ForegroundColor Cyan
    docker logs aura-postgres --tail 20
    
    Write-Host "`n💡 Troubleshooting Steps:" -ForegroundColor Yellow
    Write-Host "   1. Wait longer - first-time setup can take time" -ForegroundColor White
    Write-Host "   2. Check Docker Desktop resources (memory/CPU)" -ForegroundColor White
    Write-Host "   3. Try: docker restart aura-postgres" -ForegroundColor White
    Write-Host "   4. Check for port conflicts" -ForegroundColor White
    
    exit 1
}

# Final verification and display database information
Write-Host "`n🔍 Final database verification..." -ForegroundColor Yellow

# Test basic connection
docker exec aura-postgres psql -U aura_admin -d aura_dashboard -c "SELECT version();" 2>&1 | Out-Null
if (-not (Test-Command "✅ Database connection successful" "❌ Database connection failed")) {
    exit 1
}

# Display database information
Write-Host "`n📊 Database Information:" -ForegroundColor Cyan
docker exec aura-postgres psql -U aura_admin -d aura_dashboard -c "
SELECT 
    version() as postgres_version,
    current_database() as current_db,
    current_user as current_user;
"

# Check if schema was initialized by counting tables
Write-Host "`n📋 Checking database schema..." -ForegroundColor Yellow
$tableCount = docker exec aura-postgres psql -U aura_admin -d aura_dashboard -t -c "
SELECT COUNT(*) 
FROM information_schema.tables 
WHERE table_schema = 'public';
"

# Clean up the table count output
$tableCount = $tableCount.Trim()

if ([string]::IsNullOrWhiteSpace($tableCount) -or [int]$tableCount -eq 0) {
    Write-Status "Database schema not initialized. Manual initialization required." "Yellow"
    Write-Host "`n💡 Manual Initialization Steps:" -ForegroundColor Cyan
    Write-Host "   1. Wait a bit longer for auto-initialization" -ForegroundColor White
    Write-Host "   2. Or run: .\init-database.ps1" -ForegroundColor White
    Write-Host "   3. Or restart container: docker restart aura-postgres" -ForegroundColor White
} else {
    Write-Status "✅ Database schema initialized ($tableCount tables found)" "Green"
    
    # Show tables
    Write-Host "`n📋 Database Tables:" -ForegroundColor Cyan
    docker exec aura-postgres psql -U aura_admin -d aura_dashboard -c "
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
    "
}

# Show user information (if available)
Write-Host "`n👥 User Accounts:" -ForegroundColor Cyan
docker exec aura-postgres psql -U aura_admin -d aura_dashboard -c "
SELECT 
    username,
    role,
    is_active,
    created_at::date as created
FROM users 
ORDER BY role, username;
" 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "   Users table not initialized yet" -ForegroundColor Yellow
}

Write-Host "`n🎉 Phase 3 Database Setup Complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "📊 PostgreSQL is now running and ready!" -ForegroundColor White
Write-Host "`n🔗 Connection Details:" -ForegroundColor Cyan
Write-Host "   Host: localhost:5432" -ForegroundColor White
Write-Host "   Database: aura_dashboard" -ForegroundColor White
Write-Host "   Username: aura_admin" -ForegroundColor White
Write-Host "   Password: AuraDB2024!" -ForegroundColor White
Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Run .\check-database.ps1 to verify everything is working" -ForegroundColor White
Write-Host "   2. Run .\init-database.ps1 if schema needs manual initialization" -ForegroundColor White
Write-Host "   3. Proceed with backend API development" -ForegroundColor White
Write-Host "`n" -NoNewline
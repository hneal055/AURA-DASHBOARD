# Run Backend in Development Mode
Write-Host "🚀 Running Backend in Development Mode" -ForegroundColor Green

# Stop and remove existing backend containers
docker stop aura-backend 2>&1 | Out-Null
docker rm aura-backend 2>&1 | Out-Null

# Build the development image
Write-Host "🔨 Building development image..." -ForegroundColor Yellow
docker build -t aura-backend-dev -f Dockerfile.api-dev .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

# Run the container in the foreground
Write-Host "🚀 Starting backend in development mode..." -ForegroundColor Yellow
docker run --name aura-backend-dev `
    -p 5000:5000 `
    -e DB_HOST=aura-postgres `
    -e DB_NAME=aura_dashboard `
    -e DB_USER=aura_admin `
    -e DB_PASSWORD=AuraDB2024! `
    -e JWT_SECRET_KEY=aura-jwt-super-secret-2024 `
    -e SECRET_KEY=aura-flask-secret-2024 `
    -e FLASK_CONFIG=development `
    --link aura-postgres:postgres `
    aura-backend-dev
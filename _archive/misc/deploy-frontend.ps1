# Build the frontend image
docker build -t aura-frontend -f Dockerfile.frontend .

# Create network if not exists
$networkExists = docker network ls --filter "name=aura-network" --format "table {{.Name}}" | Select-String "aura-network"
if (-not $networkExists) {
    docker network create aura-network
}

# Connect existing containers to the network (if not already connected)
docker network connect aura-network aura-postgres 2>&1 | Out-Null
docker network connect aura-network aura-backend 2>&1 | Out-Null

# Stop and remove existing frontend container if exists
docker stop aura-frontend 2>&1 | Out-Null
docker rm aura-frontend 2>&1 | Out-Null

# Run the frontend container
docker run -d --name aura-frontend -p 8080:80 --network aura-network aura-frontend

Write-Host "Frontend deployed at http://localhost:8080" -ForegroundColor Green
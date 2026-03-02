#!/bin/bash

# AURA Dashboard Deployment Script
echo "🚀 Deploying AURA Dashboard..."

# Stop and remove existing container
docker-compose down

# Build and start new container
docker-compose up -d --build

# Wait for container to be healthy
echo "⏳ Waiting for container to be healthy..."
for i in {1..30}; do
    if [ "$(docker inspect -f '{{.State.Health.Status}}' aura-dashboard)" == "healthy" ]; then
        echo "✅ AURA Dashboard is healthy and running!"
        break
    fi
    sleep 2
done

# Show container status
echo ""
echo "📊 Deployment Status:"
docker-compose ps

echo ""
echo "🌐 AURA Dashboard is now running at: http://localhost:8080"
echo "📋 Container logs: docker logs aura-dashboard"
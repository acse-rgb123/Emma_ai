#!/bin/bash

# Restart Emma Incident Response System

echo "Restarting Emma Incident Response System..."
echo "=========================================="

# Stop existing containers
docker-compose down

# Rebuild and start
docker-compose up -d --build

# Wait for services
echo "Waiting for services to start..."
sleep 10

# Check status
docker-compose ps

echo ""
echo "System restarted. Access at:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"

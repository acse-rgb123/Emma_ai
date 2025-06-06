#!/bin/bash

# Emma Incident Response System Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Emma Incident Response System${NC}"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Stop any existing containers
echo -e "${YELLOW}Stopping any existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Build and start the application
echo -e "${YELLOW}Building and starting the application...${NC}"
docker-compose up -d --build

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Services are running${NC}"
    
    # Test backend health
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
    else
        echo -e "${RED}✗ Backend health check failed${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}Deployment successful!${NC}"
    echo ""
    echo "Access the application at:"
    echo "  - Frontend: ${GREEN}http://localhost:3000${NC}"
    echo "  - Backend API: ${GREEN}http://localhost:8000${NC}"
    echo "  - API Docs: ${GREEN}http://localhost:8000/docs${NC}"
else
    echo -e "${RED}✗ Services failed to start${NC}"
    exit 1
fi

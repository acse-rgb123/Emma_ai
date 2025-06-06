#!/bin/bash

# Emma Incident Response System - Local Run Script (No Docker)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Emma Incident Response System - Local Development${NC}"
echo "================================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
if ! command_exists python3; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check Node.js
if ! command_exists node; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Please install Node.js 14 or higher"
    exit 1
fi

# Check npm
if ! command_exists npm; then
    echo -e "${RED}Error: npm is not installed${NC}"
    echo "Please install npm"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

# Function to run backend
run_backend() {
    echo -e "${YELLOW}Starting backend server...${NC}"
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    echo "Installing backend dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Run the backend
    echo -e "${GREEN}Backend starting on http://localhost:8000${NC}"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
}

# Function to run frontend
run_frontend() {
    echo -e "${YELLOW}Starting frontend server...${NC}"
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    # Set the API URL for local development
    export REACT_APP_API_URL=http://localhost:8000
    
    # Run the frontend
    echo -e "${GREEN}Frontend starting on http://localhost:3000${NC}"
    npm start &
    FRONTEND_PID=$!
    cd ..
}

# Function to stop servers
stop_servers() {
    echo -e "\n${YELLOW}Stopping servers...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    # Kill any remaining processes on the ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}Servers stopped${NC}"
}

# Set up trap to stop servers on exit
trap stop_servers EXIT INT TERM

# Start servers
run_backend
sleep 5  # Give backend time to start

run_frontend
sleep 5  # Give frontend time to start

# Show status
echo ""
echo -e "${GREEN}✓ System is running!${NC}"
echo ""
echo "Access the application at:"
echo "  - Frontend: ${GREEN}http://localhost:3000${NC}"
echo "  - Backend API: ${GREEN}http://localhost:8000${NC}"
echo "  - API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for user to stop
wait

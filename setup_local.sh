#!/bin/bash

# Emma Incident Response System - Robust Local Setup Script
# Handles Python version compatibility automatically

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Emma Incident Response System - Local Setup${NC}"
echo "==========================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
echo "Detected OS: $OS"

# Function to find suitable Python version
find_python() {
    # Check for Python versions in order of preference
    for version in "3.12" "3.11" "3.10" "3.9"; do
        if command_exists "python$version"; then
            echo "python$version"
            return 0
        fi
    done
    
    # Check default python3
    if command_exists python3; then
        # Get version
        PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
        PY_MAJOR=$(echo $PY_VERSION | cut -d. -f1)
        PY_MINOR=$(echo $PY_VERSION | cut -d. -f2)
        
        if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -le 12 ] && [ "$PY_MINOR" -ge 9 ]; then
            echo "python3"
            return 0
        fi
    fi
    
    # No suitable Python found
    return 1
}

# Check for Python
echo -e "${YELLOW}Checking Python installation...${NC}"
PYTHON_CMD=$(find_python)

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: No suitable Python version found (3.9-3.12 required)${NC}"
    echo ""
    echo "Python 3.13+ has compatibility issues with some dependencies."
    echo ""
    echo "Please install Python 3.12 or earlier:"
    
    if [ "$OS" = "macos" ]; then
        echo "  brew install python@3.12"
    elif [ "$OS" = "linux" ]; then
        echo "  sudo apt update && sudo apt install python3.12 python3.12-venv python3.12-dev"
        echo "  # or"
        echo "  sudo yum install python3.12 python3.12-devel"
    else
        echo "  Download from https://www.python.org/downloads/ (choose version 3.12.x)"
    fi
    
    echo ""
    echo "After installing, run this script again."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")')
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION ($PYTHON_CMD)${NC}"

# Check Node.js
echo -e "${YELLOW}Checking Node.js installation...${NC}"
if ! command_exists node; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo ""
    echo "To install Node.js:"
    
    if [ "$OS" = "macos" ]; then
        echo "  brew install node"
    elif [ "$OS" = "linux" ]; then
        echo "  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -"
        echo "  sudo apt-get install -y nodejs"
    else
        echo "  Download from https://nodejs.org/"
    fi
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Found Node.js $NODE_VERSION${NC}"

# Create requirements files based on Python version
create_requirements() {
    local py_major=$1
    local py_minor=$2
    
    # Base requirements that work with all versions
    cat > backend/requirements_base.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
httpx==0.25.2
EOF

    # Version-specific requirements
    if [ "$py_minor" -ge 13 ]; then
        # Python 3.13+ - use older pydantic without rust dependencies
        cat > backend/requirements_compat.txt << 'EOF'
pydantic==1.10.13
typing-extensions==4.8.0
EOF
    else
        # Python 3.9-3.12 - use modern pydantic
        cat > backend/requirements_compat.txt << 'EOF'
pydantic==2.5.0
pydantic-settings==2.1.0
EOF
    fi
    
    # Combine requirements
    cat backend/requirements_base.txt backend/requirements_compat.txt > backend/requirements.txt
    rm backend/requirements_base.txt backend/requirements_compat.txt
    
    # Add AI provider dependencies
    if [ -f .env ]; then
        source .env
        if [ "$AI_PROVIDER" = "openai" ]; then
            echo "openai==1.3.0" >> backend/requirements.txt
        elif [ "$AI_PROVIDER" = "claude" ]; then
            echo "anthropic==0.8.0" >> backend/requirements.txt
        elif [ "$AI_PROVIDER" = "gemini" ]; then
            echo "google-generativeai==0.3.0" >> backend/requirements.txt
        fi
    fi
}

# Setup backend
echo ""
echo -e "${YELLOW}Setting up backend...${NC}"
cd backend

# Clean any existing virtual environment
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Get Python version info
PY_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
PY_MAJOR=$(echo $PY_VERSION | cut -d. -f1)
PY_MINOR=$(echo $PY_VERSION | cut -d. -f2)

# Create appropriate requirements file
create_requirements $PY_MAJOR $PY_MINOR

# Create virtual environment
echo "Creating virtual environment with $PYTHON_CMD..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [ "$OS" = "windows" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip and install build tools
echo "Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

# Install requirements
echo "Installing Python packages..."
if [ "$PY_MINOR" -ge 13 ]; then
    echo -e "${YELLOW}Note: Using compatibility mode for Python 3.13+${NC}"
    # Install packages one by one for better error handling
    while IFS= read -r package; do
        if [ ! -z "$package" ]; then
            echo "Installing $package..."
            pip install "$package" || {
                echo -e "${RED}Failed to install $package${NC}"
                exit 1
            }
        fi
    done < requirements.txt
else
    pip install -r requirements.txt
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"
deactivate
cd ..

# Setup frontend
echo ""
echo -e "${YELLOW}Setting up frontend...${NC}"
cd frontend

# Remove any existing node_modules
if [ -d "node_modules" ]; then
    echo "Cleaning existing node_modules..."
    rm -rf node_modules package-lock.json
fi

# Install dependencies
echo "Installing frontend dependencies..."
npm install

cd ..
echo -e "${GREEN}✓ Frontend setup complete${NC}"

# Create a Python version info file
echo "$PYTHON_CMD" > .python_version

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Python version: $PYTHON_VERSION ($PYTHON_CMD)"
echo "Node.js version: $NODE_VERSION"
echo ""
echo "To run the application:"
echo "  ./run_local.sh"
echo ""
echo "Or run components separately:"
echo "  Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm start"

# Create a simple test script
cat > test_setup.sh << 'EOF'
#!/bin/bash
# Quick test to verify setup
echo "Testing backend setup..."
cd backend
source venv/bin/activate
python -c "import fastapi, pydantic; print('✓ Backend packages OK')"
deactivate
cd ..

echo "Testing frontend setup..."
cd frontend
npm list react > /dev/null 2>&1 && echo "✓ Frontend packages OK" || echo "✗ Frontend packages missing"
cd ..
EOF
chmod +x test_setup.sh

echo ""
echo "Run ./test_setup.sh to verify installation"
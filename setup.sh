#!/bin/bash

# Emma Incident Response System - Local Setup Script
# Sets up the system for local development

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Emma AI branding
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                                              ║${NC}"
echo -e "${PURPLE}║               Emma AI Incident Response System               ║${NC}"
echo -e "${PURPLE}║                     Local Development Setup                  ║${NC}"
echo -e "${PURPLE}║                                                              ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get OS type
get_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install Node.js
install_nodejs() {
    local os=$(get_os)
    print_status "Installing Node.js..."
    
    case $os in
        "macos")
            if command_exists brew; then
                brew install node
            else
                print_error "Homebrew not found. Please install Node.js manually from https://nodejs.org/"
                exit 1
            fi
            ;;
        "linux")
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y nodejs npm
            elif command_exists yum; then
                sudo yum install -y nodejs npm
            elif command_exists dnf; then
                sudo dnf install -y nodejs npm
            else
                print_error "Package manager not found. Please install Node.js manually from https://nodejs.org/"
                exit 1
            fi
            ;;
        *)
            print_error "Please install Node.js manually from https://nodejs.org/"
            exit 1
            ;;
    esac
}

# Function to install Python
install_python() {
    local os=$(get_os)
    print_status "Installing Python 3..."
    
    case $os in
        "macos")
            if command_exists brew; then
                brew install python@3.11
            else
                print_error "Homebrew not found. Please install Python manually from https://python.org/"
                exit 1
            fi
            ;;
        "linux")
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv
            elif command_exists yum; then
                sudo yum install -y python3 python3-pip
            elif command_exists dnf; then
                sudo dnf install -y python3 python3-pip
            else
                print_error "Package manager not found. Please install Python manually from https://python.org/"
                exit 1
            fi
            ;;
        *)
            print_error "Please install Python manually from https://python.org/"
            exit 1
            ;;
    esac
}

# Parse command line arguments
OPENAI_API_KEY=""
SKIP_DEPS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -k|--api-key)
            OPENAI_API_KEY="$2"
            shift 2
            ;;
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        -h|--help)
            echo "Emma AI Incident Response System - Local Setup"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -k, --api-key KEY     OpenAI API key (required)"
            echo "  --skip-deps           Skip dependency installation"
            echo "  -h, --help            Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 -k sk-your-openai-api-key"
            echo "  $0 --api-key sk-your-openai-api-key --skip-deps"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Check if API key is provided
if [[ -z "$OPENAI_API_KEY" ]]; then
    print_error "OpenAI API key is required!"
    echo ""
    echo "Usage: $0 -k YOUR_OPENAI_API_KEY"
    echo "Get your API key from: https://platform.openai.com/api-keys"
    echo ""
    exit 1
fi

# Validate API key format
if [[ ! "$OPENAI_API_KEY" =~ ^sk-[a-zA-Z0-9]+ ]]; then
    print_error "Invalid OpenAI API key format. It should start with 'sk-'"
    exit 1
fi

print_status "Starting Emma AI local development setup..."
print_status "API Key: ${OPENAI_API_KEY:0:10}..."

# Check if we're in the right directory
if [[ ! -d "frontend" ]] || [[ ! -d "backend" ]]; then
    print_error "This script must be run from the emma-incident-response directory"
    print_error "Make sure you've cloned the repository and are in the root directory"
    exit 1
fi

# Check and install dependencies
if [[ "$SKIP_DEPS" == false ]]; then
    print_status "Checking system dependencies..."

    # Check Node.js
    if ! command_exists node; then
        print_warning "Node.js not found"
        install_nodejs
    else
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    fi

    # Check Python
    if ! command_exists python3; then
        print_warning "Python 3 not found"
        install_python
    else
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
    fi
fi

# Create .env file
print_status "Creating environment configuration..."
cat > .env << EOF
# AI Provider Configuration
AI_PROVIDER=openai

# API Keys
OPENAI_API_KEY=$OPENAI_API_KEY

# Legacy support (for backward compatibility)
API_KEY=$OPENAI_API_KEY

# API Configuration
API_TITLE="Emma Incident Response System"
API_VERSION="1.0.0"

# Email Configuration
DEFAULT_SUPERVISOR_EMAIL=supervisor@emmacare.com
DEFAULT_RISK_ASSESSOR_EMAIL=riskassessment@emmacare.com
DEFAULT_FAMILY_CONTACT_EMAIL=family.contact@emmacare.com

# Feature Flags
ENABLE_AI_FALLBACK=true
ENABLE_EMAIL_NOTIFICATIONS=false
ENABLE_AUDIT_LOGGING=true
EOF

print_success "Environment file created"

# Setup backend
print_status "Setting up Python backend..."
cd backend

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

cd ..

# Setup frontend
print_status "Setting up React frontend..."
cd frontend

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

cd ..

print_success "Local development environment setup complete"

# Update the run script to be more robust
print_status "Creating run script..."
cat > run_local.sh << 'EOF'
#!/bin/bash

# Emma AI Incident Response System - Local Development Runner

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}Starting Emma AI Incident Response System${NC}"
echo -e "${PURPLE}Local Development Mode${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill %1 %2 2>/dev/null || true
    wait
    echo -e "${GREEN}Services stopped.${NC}"
    exit
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if we're in the right directory
if [[ ! -d "frontend" ]] || [[ ! -d "backend" ]]; then
    echo -e "${RED}Error: This script must be run from the emma-incident-response directory${NC}"
    exit 1
fi

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo -e "${RED}Error: .env file not found. Please run setup.sh first.${NC}"
    exit 1
fi

# Check if backend venv exists
if [[ ! -d "backend/venv" ]]; then
    echo -e "${RED}Error: Backend virtual environment not found. Please run setup.sh first.${NC}"
    exit 1
fi

# Check if frontend node_modules exists
if [[ ! -d "frontend/node_modules" ]]; then
    echo -e "${RED}Error: Frontend dependencies not found. Please run setup.sh first.${NC}"
    exit 1
fi

echo -e "${BLUE}Starting backend on http://localhost:8000...${NC}"
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo -e "${BLUE}Starting frontend on http://localhost:3000...${NC}"
cd ../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✅ Emma AI is starting up!${NC}"
echo -e "${GREEN}🌐 Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "${GREEN}🔗 Backend: ${BLUE}http://localhost:8000${NC}"
echo -e "${GREEN}📚 API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"
echo ""

# Wait for both processes
wait
EOF

chmod +x run_local.sh
print_success "Run script created: ./run_local.sh"

# Final setup summary
echo ""
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                                              ║${NC}"
echo -e "${PURPLE}║                   🎉 Setup Complete! 🎉                      ║${NC}"
echo -e "${PURPLE}║                                                              ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

print_success "Emma AI Incident Response System is ready for local development!"
echo ""
echo -e "${GREEN}To start the system:${NC}"
echo -e "  🚀 ${BLUE}./run_local.sh${NC}"
echo ""
echo -e "${GREEN}Access your application:${NC}"
echo -e "  🌐 Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "  🔗 Backend API: ${BLUE}http://localhost:8000${NC}"
echo -e "  📚 API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""

print_status "Your OpenAI API key has been configured"
print_status "You can also configure API keys through the web interface"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Run: ${BLUE}./run_local.sh${NC}"
echo "2. Open http://localhost:3000 in your browser"
echo "3. Paste a social care transcript in the input field"
echo "4. Click 'Analyze Transcript' to see Emma AI in action"
echo ""

print_success "Setup completed successfully! Enjoy using Emma AI! 🚀"
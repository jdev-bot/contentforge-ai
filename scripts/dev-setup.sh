#!/bin/bash
set -e

echo "🚀 ContentForge AI - Development Setup"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "PROJECT.md" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

PROJECT_ROOT=$(pwd)

echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.12"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python 3.12+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}Error: Node.js 18+ required (found $(node --version))${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node --version) found${NC}"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm $(npm --version) found${NC}"

# Check Docker (optional)
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker found (optional but recommended)${NC}"
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        echo -e "${GREEN}✓ Docker Compose found${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Docker not found (optional)${NC}"
fi

echo -e "${YELLOW}Step 2: Setting up Backend...${NC}"
cd "$PROJECT_ROOT/src/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install dev dependencies
echo "Installing development dependencies..."
pip install pytest pytest-asyncio httpx pytest-cov flake8 black isort bandit pip-audit

echo -e "${GREEN}✓ Backend setup complete${NC}"

echo -e "${YELLOW}Step 3: Setting up Frontend...${NC}"
cd "$PROJECT_ROOT/src/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm ci
else
    echo "node_modules already exists, skipping npm ci"
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"

echo -e "${YELLOW}Step 4: Setting up environment...${NC}"
cd "$PROJECT_ROOT"

# Copy .env.example if .env doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}⚠ Please update .env with your actual API keys and configuration${NC}"
    fi
fi

echo -e "${GREEN}✓ Environment setup complete${NC}"

echo -e "${YELLOW}Step 5: Verifying setup...${NC}"

# Check backend
cd "$PROJECT_ROOT/src/backend"
source venv/bin/activate
if python -c "import fastapi" 2>/dev/null; then
    echo -e "${GREEN}✓ Backend dependencies verified${NC}"
else
    echo -e "${RED}✗ Backend dependencies verification failed${NC}"
fi

# Check frontend
cd "$PROJECT_ROOT/src/frontend"
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓ Frontend dependencies verified${NC}"
else
    echo -e "${RED}✗ Frontend dependencies verification failed${NC}"
fi

echo ""
echo "======================================"
echo -e "${GREEN}🎉 Development setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Update .env with your API keys"
echo "  2. Run: ./scripts/dev-start.sh"
echo ""
echo "Or use Docker Compose:"
echo "  docker-compose up -d"

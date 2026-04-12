#!/bin/bash
set -e

# ContentForge AI - Development Start Script
# Start all services for local development

echo "🚀 Starting ContentForge AI development environment..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Parse arguments
SERVICES_ONLY=false
BACKEND_ONLY=false
FRONTEND_ONLY=false
N8N_ONLY=false

for arg in "$@"; do
    case $arg in
        --services-only)
            SERVICES_ONLY=true
            shift
            ;;
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        --n8n-only)
            N8N_ONLY=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./scripts/dev-start.sh [options]"
            echo ""
            echo "Options:"
            echo "  --services-only    Start only Docker services (PostgreSQL, Redis, n8n)"
            echo "  --backend-only     Start only the backend"
            echo "  --frontend-only    Start only the frontend"
            echo "  --n8n-only         Start only n8n"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Without options: starts all services"
            exit 0
            ;;
    esac
done

# Function to start Docker services
start_services() {
    echo -e "${BLUE}🐳 Starting Docker services...${NC}"
    
    # Check if docker-compose.yml exists
    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d postgres redis n8n
    elif [ -f "infra/docker/docker-compose.yml" ]; then
        docker-compose -f infra/docker/docker-compose.yml up -d
    else
        echo -e "${YELLOW}⚠️  No docker-compose.yml found. Make sure PostgreSQL and Redis are running manually.${NC}"
    fi
    
    echo -e "${GREEN}✅ Docker services started${NC}"
    echo ""
}

# Function to start backend
start_backend() {
    echo -e "${BLUE}🐍 Starting backend...${NC}"
    
    cd src/backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}⚠️  Virtual environment not found. Running dev-setup.sh first...${NC}"
        cd ../..
        ./scripts/dev-setup.sh
        cd src/backend
    fi
    
    # Activate virtual environment
    source venv/bin/activate 2>/dev/null || . venv/bin/activate
    
    # Check if alembic migrations need to be run
    echo -e "${BLUE}📊 Running database migrations...${NC}"
    alembic upgrade head 2>/dev/null || echo "No migrations configured or database not ready yet"
    
    # Start the backend server
    echo -e "${BLUE}🚀 Starting FastAPI server on http://localhost:8000${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ../..
    
    echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
    echo ""
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}⚡ Starting frontend...${NC}"
    
    cd src/frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠️  node_modules not found. Running npm install...${NC}"
        npm install
    fi
    
    # Start the frontend dev server
    echo -e "${BLUE}🚀 Starting Next.js dev server on http://localhost:3000${NC}"
    npm run dev &
    FRONTEND_PID=$!
    cd ../..
    
    echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
    echo ""
}

# Function to start n8n
start_n8n() {
    echo -e "${BLUE}🔗 Starting n8n...${NC}"
    
    # n8n is typically started via Docker Compose
    # But if it needs to be started separately, we can do it here
    
    echo -e "${GREEN}✅ n8n should be available at http://localhost:5678${NC}"
    echo ""
}

# Main execution
if [ "$SERVICES_ONLY" = true ]; then
    start_services
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Services started!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Services running:"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo "  - n8n: http://localhost:5678"
    echo ""
    echo "Run './scripts/dev-start.sh' without flags to start all services."
    exit 0
fi

if [ "$N8N_ONLY" = true ]; then
    start_services
    start_n8n
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ n8n started!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "n8n is available at: http://localhost:5678"
    echo ""
    echo "Press Ctrl+C to stop"
    wait
    exit 0
fi

if [ "$BACKEND_ONLY" = true ]; then
    start_backend
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Backend running!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Backend is available at: http://localhost:8000"
    echo "API documentation: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop"
    wait
    exit 0
fi

if [ "$FRONTEND_ONLY" = true ]; then
    start_frontend
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Frontend running!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Frontend is available at: http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop"
    wait
    exit 0
fi

# Start all services
echo -e "${BLUE}🔄 Starting all services...${NC}"
echo ""

start_services

# Wait a moment for services to be ready
sleep 3

start_backend
start_frontend

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ All services started!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend:    http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo "   n8n:         http://localhost:5678"
echo ""
echo "📝 Logs are available in:"
echo "   ./logs/"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for interrupt
trap 'echo -e "\n${YELLOW}🛑 Stopping services...${NC}"; docker-compose down 2>/dev/null || true; exit 0' INT
wait

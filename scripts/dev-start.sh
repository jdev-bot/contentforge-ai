#!/bin/bash
set -e

echo "🚀 ContentForge AI - Development Start"
echo "======================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "PROJECT.md" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

PROJECT_ROOT=$(pwd)

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    if [ -n "$WORKER_PID" ]; then
        kill $WORKER_PID 2>/dev/null || true
    fi
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/src/backend/venv" ]; then
    echo -e "${RED}Error: Virtual environment not found. Run ./scripts/dev-setup.sh first.${NC}"
    exit 1
fi

# Check if frontend dependencies exist
if [ ! -d "$PROJECT_ROOT/src/frontend/node_modules" ]; then
    echo -e "${RED}Error: Frontend dependencies not found. Run ./scripts/dev-setup.sh first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites verified${NC}"

# Start Backend
echo -e "${BLUE}Starting Backend (FastAPI)...${NC}"
cd "$PROJECT_ROOT/src/backend"
source venv/bin/activate

# Check if we have an app module
if [ -f "main.py" ]; then
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
elif [ -d "app" ]; then
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
else
    echo -e "${YELLOW}⚠ No main app found. Skipping backend startup.${NC}"
fi

if [ -n "$BACKEND_PID" ]; then
    echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID) - http://localhost:8000${NC}"
    echo -e "${GREEN}  API Docs: http://localhost:8000/docs${NC}"
fi

# Start Frontend
echo -e "${BLUE}Starting Frontend (Next.js)...${NC}"
cd "$PROJECT_ROOT/src/frontend"

npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID) - http://localhost:3000${NC}"

# Start Celery Worker (if Redis is available)
echo -e "${BLUE}Checking for Redis...${NC}"
if command -v redis-cli &> /dev/null && redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis found, starting Celery worker...${NC}"
    cd "$PROJECT_ROOT/src/backend"
    source venv/bin/activate
    celery -A app.core.celery worker --loglevel=info &
    WORKER_PID=$!
    echo -e "${GREEN}✓ Celery worker started (PID: $WORKER_PID)${NC}"
else
    echo -e "${YELLOW}⚠ Redis not available. Celery worker not started.${NC}"
fi

echo ""
echo "======================================="
echo -e "${GREEN}🎉 All services started!${NC}"
echo ""
echo -e "${BLUE}Services:${NC}"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
if [ -n "$WORKER_PID" ]; then
    echo "  Worker:   Running"
fi
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for all background processes
wait
